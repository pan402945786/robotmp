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
        self.drag_updates_enabled = True
        self.drag_samples = 0

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
        if self.estimate_drag and self.drag_updates_enabled and len(self.history) >= 8:
            # A quadratic fit's acceleration belongs near the center of its
            # observation window. Pairing it with endpoint velocity biases drag.
            middle_velocity=fit[1]+fit[2]*times.mean()
            speed = np.linalg.norm(middle_velocity)
            if speed > .5:
                gravity = np.array([0., 0., -9.81])
                estimate = -float(middle_velocity @ (fit[2]-gravity)) / ((1+speed)*speed**2)
                weight=.08 if self.sigma>.0015 else .25
                if self.drag_samples==0 and self.sigma<.0005:
                    weight=1.
                self.drag = (1-weight)*self.drag + weight*float(np.clip(estimate, 0., .15))
                self.drag_samples+=1
            # Refit p/v to the causal force estimate instead of keeping the
            # endpoint bias of a constant-acceleration quadratic approximation.
            velocities=fit[1]+times[:,None]*fit[2]
            accelerations=np.array([0.,0.,-9.81])-self.drag*(1+np.linalg.norm(velocities,axis=1))[:,None]*velocities
            dv=np.zeros(3)
            displacement=np.zeros(3)
            integrated=[displacement.copy()]
            for i in range(1,len(times)):
                h=times[i]-times[i-1]
                displacement+=dv*h+(accelerations[i-1]/3+accelerations[i]/6)*h*h
                dv+=(accelerations[i-1]+accelerations[i])*.5*h
                integrated.append(displacement.copy())
            relative=times-times[0]
            corrected=np.linalg.lstsq(np.column_stack((np.ones(len(times)),relative)),
                                      values-np.array(integrated),rcond=None)[0]
            self.position=corrected[0]+corrected[1]*relative[-1]+displacement
            self.velocity=corrected[1]+dv
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

