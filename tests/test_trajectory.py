import pytest
import numpy as np
from src.analysis.trajectory import TrajectoryAnalyzer

class TestTrajectoryAnalyzer:
    def test_predict_next_time(self):
        """测试成绩预测"""
        times = [8400, 8300, 8200, 8100]
        analyzer = TrajectoryAnalyzer(times)

        predicted, ci = analyzer.predict_next(ci=0.95)
        assert predicted < 8100
        assert ci[0] < ci[1]

    def test_is_significant_deviation(self):
        """测试偏离检测"""
        times = [8400, 8300, 8200, 8100]
        analyzer = TrajectoryAnalyzer(times)

        assert analyzer.is_significant_deviation(8000) is False
        assert analyzer.is_significant_deviation(7500) is True

    def test_insufficient_data(self):
        """数据点太少无法建模"""
        times = [8400]
        analyzer = TrajectoryAnalyzer(times)
        with pytest.raises(ValueError):
            analyzer.predict_next()