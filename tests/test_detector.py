import pytest
from src.analysis.detector import AnomalyDetector, DetectionResult

class TestAnomalyDetector:
    def test_abnormal_case(self):
        """横向罕见 + 纵向异常 = 异常"""
        baseline_times = [[8400, 8300] for _ in range(100)]
        target_times = [8400, 7800]

        detector = AnomalyDetector(baseline_times, target_times)
        result = detector.detect()

        assert result.percentile < 5
        assert result.is_longitudinal_anomaly is True
        assert result.is_abnormal is True

    def test_normal_breakthrough(self):
        """横向罕见但纵向符合规律 = 正常突破"""
        baseline_times = [[8400, 8350] for _ in range(100)]
        target_times = [8400, 8100, 7800]

        detector = AnomalyDetector(baseline_times, target_times)
        result = detector.detect()

        assert result.percentile < 5
        assert result.is_longitudinal_anomaly is False
        assert result.is_abnormal is False

    def test_normal_case(self):
        """横向不罕见 = 正常"""
        baseline_times = [[8400, 8100] for _ in range(100)]
        target_times = [8400, 8100]

        detector = AnomalyDetector(baseline_times, target_times)
        result = detector.detect()

        assert result.percentile > 5
        assert result.is_abnormal is False