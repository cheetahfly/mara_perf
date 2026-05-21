"""异常判定器：综合横向基准和纵向轨迹"""
from dataclasses import dataclass
from typing import List
from src.analysis.baseline import BaselineAnalyzer
from src.analysis.trajectory import TrajectoryAnalyzer

@dataclass
class DetectionResult:
    is_abnormal: bool
    percentile: float
    is_longitudinal_anomaly: bool
    verdict: str
    details: str

class AnomalyDetector:
    def __init__(self, baseline_runner_times: List[List[int]], target_times: List[int]):
        self.baseline = BaselineAnalyzer(baseline_runner_times)
        self.target_times = target_times

    def detect(self, threshold: float = 5.0) -> DetectionResult:
        if len(self.target_times) < 3:
            improvement = self.target_times[-1] - self.target_times[0]
            percentile = self.baseline.get_percentile(improvement)
            # With only 2 points, flag as longitudinal anomaly if improvement is extreme
            is_longitudinal_anomaly = percentile < threshold
        else:
            trajectory = TrajectoryAnalyzer(self.target_times)
            last_improvement = self.target_times[-1] - self.target_times[-2]
            percentile = self.baseline.get_percentile(last_improvement)
            is_longitudinal_anomaly = trajectory.is_significant_deviation(
                self.target_times[-1]
            )

        # 判定逻辑：
        # 1. 横向百分位极低（<0.5%）且纵向步进不一致 → 异常（幅度极端且不符合训练规律）
        # 2. 横向百分位低（<5%）且纵向异常 → 异常
        # 3. 横向百分位低但步进一致 → 正常突破（训练带来的真实提升）
        # 4. 横向百分位不低 → 正常
        extreme_threshold = 0.5
        if percentile < extreme_threshold and is_longitudinal_anomaly:
            is_abnormal = True
            verdict = "异常"
            details = f"横向百分位={percentile:.1f}%（<{extreme_threshold}%）且纵向轨迹异常"
        elif percentile < threshold and is_longitudinal_anomaly:
            is_abnormal = True
            verdict = "异常"
            details = f"横向百分位={percentile:.1f}%（<{threshold}%）且纵向轨迹异常"
        elif percentile < threshold:
            is_abnormal = False
            verdict = "正常（训练突破）"
            details = f"横向罕见（{percentile:.1f}%），但纵向符合运动规律"
        else:
            is_abnormal = False
            verdict = "正常"
            details = f"横向百分位={percentile:.1f}%，无异常迹象"

        return DetectionResult(
            is_abnormal=is_abnormal,
            percentile=percentile,
            is_longitudinal_anomaly=is_longitudinal_anomaly,
            verdict=verdict,
            details=details
        )