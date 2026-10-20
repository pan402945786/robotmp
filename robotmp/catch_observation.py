"""Causal position-only flight estimation. No environment, files or replay input."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math

import numpy as np


@dataclass(frozen=True)
class PositionObservation:
    captured_at: float
    delivered_at: float
    position: tuple[float, float, float]

    def __post_init__(self):
        if (not math.isfinite(self.captured_at) or not math.isfinite(self.delivered_at)
                or self.captured_at > self.delivered_at + 1e-9
                or len(self.position) != 3 or not all(math.isfinite(x) for x in self.position)):
            raise ValueError("invalid timestamped position observation")


class FlightEstimator:
    """Fit only observations already delivered; estimate drag from position history."""

    def __init__(self, *, window=10, estimate_drag=False, stale_s=.075):
        self.history = deque(maxlen=window)
        self.estimate_drag = estimate_drag
        self.stale_s = stale_s
        self.drag = 0.
        self.position = self.velocity = None
        self.sigma = math.inf
        self.rejected = 0

    def observe(self, observation: PositionObservation, now: float) -> bool:
        if observation.delivered_at > now + 1e-9:
            raise ValueError("future observation is not available")
        if self.history and observation.captured_at <= self.history[-1].captured_at:
            self.rejected += 1
            return False
        if self.position is not None:
            predicted, _ = self.predict(observation.captured_at)
            if np.linalg.norm(predicted - observation.position) > .15:
                self.rejected += 1
                return False
        self.history.append(observation)
        if len(self.history) < 4:
            return True
        times = np.array([o.captured_at - observation.captured_at for o in self.history])
        values = np.array([o.position for o in self.history])
        design = np.column_stack((np.ones(len(times)), times, .5 * times**2))
        fit = np.linalg.lstsq(design, values, rcond=None)[0]
        self.position, self.velocity = fit[:2]
        self.sigma = float(np.sqrt(np.mean((design @ fit - values)**2)))
        if self.estimate_drag and len(self.history) >= 8:
            speed = np.linalg.norm(self.velocity)
            if speed > .5:
                gravity = np.array([0., 0., -9.81])
                estimate = -float(self.velocity @ (fit[2]-gravity)) / ((1+speed)*speed**2)
                self.drag = .75*self.drag + .25*float(np.clip(estimate, 0., .15))
        return True

    def ready(self, now):
        return bool(self.position is not None and 0 <= now-self.history[-1].captured_at <= self.stale_s)

    def predict(self, timestamp):
        if self.position is None:
            raise RuntimeError("four observed frames are required")
        duration = timestamp-self.history[-1].captured_at
        if duration < -1e-8:
            raise ValueError("prediction precedes the estimator state")
        position, velocity = self.position.copy(), self.velocity.copy()
        steps = max(1, math.ceil(max(0., duration)*120))
        step = max(0., duration)/steps
        gravity = np.array([0.,0.,-9.81])
        for _ in range(steps):
            acceleration = gravity-self.drag*(1+np.linalg.norm(velocity))*velocity
            position += velocity*step + .5*acceleration*step**2
            velocity += acceleration*step
        return position, velocity

