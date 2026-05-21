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

        两种异常情况：
        1. 步进高度不一致（step_std 很大）→ 训练不规律或数据问题
        2. 当前值显著偏离线性趋势预测的置信区间

        只有当步进一致且当前值在置信区间内，才算正常。
        """
        if len(self.times) < 2:
            return False

        # 计算所有 step improvements
        steps = np.diff(self.times)
        step_std = float(np.std(steps))
        mean_step = float(np.mean(steps))

        # 如果步进标准差很大（>200秒），说明提升不稳定，这是异常的
        # 即使线性回归拟合得好，步进不一致本身就是一个信号
        if step_std > 200:
            return True

        # 如果只有1个 step，使用置信区间判断
        if len(steps) == 1:
            predicted, (lower, upper) = self.predict_next(ci=ci)
            return not (lower <= actual_time <= upper)

        # 当前 improvement = actual_time - 最后一个历史时间
        current_improvement = actual_time - int(self.times[-1])

        # 如果 step std 很小（稳定趋势），检查当前 improvement 是否偏离 mean_step
        if step_std < 50:
            improvement_diff = abs(current_improvement - mean_step)
            if abs(mean_step) > 0:
                ratio = improvement_diff / abs(mean_step)
                return bool(ratio > 1.5)
            else:
                return bool(improvement_diff > 50)

        # step std 中等时，使用 z-score 判断
        z_score = abs(current_improvement - mean_step) / step_std if step_std > 0 else 0.0
        return bool(z_score > 2.0)