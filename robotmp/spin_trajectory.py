"""Bounded, continuous pre-rotation profiles; angles are never wrapped/reset."""
from __future__ import annotations

import math


def accelerate(t, distance, speed):
    """Constant acceleration from rest, reaching speed at distance (radians)."""
    duration = 2 * distance / speed
    t = max(0., min(t, duration))
    acceleration = speed / duration
    return .5 * acceleration * t * t, acceleration * t


def coast_and_brake(t, speed, brake_start, brake_duration):
    """Continue the incoming speed, then smoothly reduce it to zero."""
    t = max(0., t)
    if t <= brake_start:
        return speed * t, speed
    braking = min(t - brake_start, brake_duration)
    return (speed * (brake_start + braking - braking**2 / (2 * brake_duration)),
            speed * (1 - braking / brake_duration))


def periodic_state(t, center, sine, cosine, turns, rate):
    """Closed joint loops can repeat without consuming revolute joint travel."""
    phase, phase_rate = accelerate(t, 2 * math.pi * turns, rate)
    q = [c + a*math.sin(phase) + b*math.cos(phase) for c, a, b in zip(center, sine, cosine)]
    qd = [phase_rate * (a*math.cos(phase) - b*math.sin(phase)) for a, b in zip(sine, cosine)]
    return q, qd, phase


def plan_spin(prepared, lower, upper, limits, turns, joints, directions,
              *, brake_start=.25, brake_duration=.20):
    """Fit all pre-rotation and braking travel inside original joint limits.

    Base yaw has arbitrary terminal phase because the task is vertical. Wrist
    joints retain the selected launch phase, shifted only by integer turns.
    These are target angles reached by physical motion, never state resets.
    """
    if not math.isfinite(turns) or turns <= 0:
        raise ValueError("turns must be finite and positive")
    if brake_start < 0 or brake_duration <= 0:
        raise ValueError("invalid braking times")
    if not joints or len(set(joints)) != len(joints) or len(joints) != len(directions):
        raise ValueError("supply unique joints with one direction each")
    distance = turns * 2 * math.pi
    result = {"turns": turns, "brake_start_s": brake_start,
              "brake_duration_s": brake_duration, "joints": {}}
    start, launch = list(prepared), list(prepared)
    for index, direction in zip(joints, directions):
        if index not in (0, 3, 5) or direction not in (-1, 1):
            raise ValueError("only bounded J1/J4/J6 rotations in direction +/-1")
        speed = limits[index] * .95
        extra = speed * (brake_start + brake_duration / 2)
        lo, hi = lower[index] + .02, upper[index] - .02
        if distance + extra > hi - lo:
            raise ValueError(f"J{index+1}: {turns} turns plus braking exceed angle range")
        if index == 0:
            end = (lo + hi + direction * (distance - extra)) / 2
        else:
            ends = [prepared[index] + k * 2 * math.pi for k in range(-2, 3)]
            ends = [q for q in ends if lo <= q - direction * distance <= hi
                    and lo <= q + direction * extra <= hi]
            if not ends:
                raise ValueError(f"J{index+1}: selected phase cannot fit {turns} turns and braking")
            end = max(ends, key=lambda q: min(q - direction*distance - lo,
                                            hi - q + direction*distance,
                                            q + direction*extra - lo,
                                            hi - q - direction*extra))
        start[index] = end - direction * distance
        launch[index] = end
        result["joints"][index] = {"direction": direction, "speed_rad_s": speed,
                                  "distance_rad": distance, "duration_s": 2 * distance / speed}
    result.update(start_q=start, launch_q=launch,
                  duration_s=max(s["duration_s"] for s in result["joints"].values()))
    return result
