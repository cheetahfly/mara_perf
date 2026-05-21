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

        predicted = slope * self.n
        residuals = y - np.polyval(coeffs, x)
        std_residuals = np.std(residuals)

        # 防止 std_residuals 为 0 导致置信区间坍缩
        if std_residuals < 1.0:
            std_residuals = 1.0

        z = 1.96 if ci == 0.95 else 2.576
        margin = z * std_residuals

        return float(predicted), (float(predicted - margin), float(predicted + margin))

    def is_significant_deviation(self, actual_time: int, ci: float = 0.95) -> bool:
        """
        判断实际成绩是否显著偏离纵向轨迹规律。

        逻辑：检查 step improvement 是否与历史 pattern 一致。
        如果所有 step improvements 都接近（标准差小），说明是稳定趋势，
        即使单个点偏离回归预测也不算异常。
        如果 step improvements 差异巨大（有的很大有的很小），则是异常。
        """
        if len(self.times) < 2:
            return False

        # 计算所有 step improvements
        steps = np.diff(self.times)  # e.g., [-300, -300] for [8400, 8100, 7800]

        # 如果只有1个 step，无法判断一致性
        if len(steps) == 1:
            predicted, (lower, upper) = self.predict_next(ci=ci)
            return not (lower <= actual_time <= upper)

        # 计算 step improvements 的标准差
        step_std = float(np.std(steps))

        # 当前 improvement = actual_time - 最后一个历史时间
        current_improvement = actual_time - int(self.times[-1])
        mean_step = float(np.mean(steps))

        # 如果 step std 很小（稳定趋势），检查当前 improvement 是否偏离 mean_step
        # 使用相对阈值：improvement_diff / |mean_step| > 1.5 表示显著偏离
        if step_std < 50:
            improvement_diff = abs(current_improvement - mean_step)
            if abs(mean_step) > 0:
                ratio = improvement_diff / abs(mean_step)
                return bool(ratio > 1.5)
            else:
                # mean_step = 0 的情况（不应该发生）
                return bool(improvement_diff > 50)

        # step std 较大时，使用 z-score 判断
        if step_std > 0:
            z_score = abs(current_improvement - mean_step) / step_std
        else:
            z_score = 0.0 if current_improvement == mean_step else float('inf')

        # z-score > 2 认为显著偏离
        return bool(z_score > 2.0)