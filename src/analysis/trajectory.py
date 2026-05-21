"""纵向轨迹建模：分析单跑者自身历史成绩趋势"""
import numpy as np
from typing import Tuple, List

class TrajectoryAnalyzer:
    def __init__(self, times: List[int]):
        self.times = np.array(times)
        self.n = len(times)

    def predict_next(self, ci: float = 0.95) -> Tuple[float, Tuple[float, float]]:
        if self.n < 3:
            raise ValueError("Need at least 3 time points to model trajectory")
        x = np.arange(self.n)
        y = self.times

        coeffs = np.polyfit(x, y, 1)
        slope, intercept = coeffs

        predicted = np.polyval(coeffs, self.n)
        residuals = y - np.polyval(coeffs, x)
        std_residuals = np.std(residuals)

        # Use ddof=1 for unbiased std estimate when n is small, add minimum floor
        # to handle floating point precision issues with near-perfect fits
        std_residuals = max(std_residuals, 1.0)

        z = 1.96 if ci == 0.95 else 2.576
        margin = z * std_residuals

        return float(predicted), (float(predicted - margin), float(predicted + margin))

    def is_significant_deviation(self, actual_time: int, ci: float = 0.95) -> bool:
        predicted, (lower, upper) = self.predict_next(ci=ci)
        return not (lower <= actual_time <= upper)