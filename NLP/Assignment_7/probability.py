import math


def log_smoothed_probability(
    count: int, total: int, outcomes: int, alpha: float
) -> float:
    return math.log((count + alpha) / (total + alpha * outcomes))
