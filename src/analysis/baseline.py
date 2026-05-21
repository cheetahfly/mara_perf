"""横向基准分析：比较同条件人群的提升幅度分布"""
import numpy as np
from typing import List

class BaselineAnalyzer:
    """
    按性别+年龄组+人种分组，计算该人群的提升幅度分布
    """

    def __init__(self, runner_times: List[List[int]]):
        self.runner_times = runner_times

    def compute_improvement_distribution(self, window: int = 1) -> np.ndarray:
        """
        计算相邻 window 个成绩之间的变化量（秒）
        负值表示成绩提升（时间减少）
        只取每个runner的第一次window跨度
        """
        improvements = []
        for times in self.runner_times:
            if len(times) > window:
                improvement = times[window] - times[0]
                improvements.append(improvement)
        return np.array(improvements)

    def get_percentile(self, target_improvement: int, window: int = 1) -> float:
        """
        计算目标提升幅度在分布中的百分位
        百分位越低说明越罕见（提升越大）
        """
        distribution = self.compute_improvement_distribution(window)
        if len(distribution) == 0:
            raise ValueError("No enough data points to compute distribution")
        return float(np.sum(distribution <= target_improvement)) / len(distribution) * 100