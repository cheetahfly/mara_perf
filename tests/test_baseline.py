import pytest
import numpy as np
from src.analysis.baseline import BaselineAnalyzer

class TestBaselineAnalyzer:
    def test_compute_improvement_distribution(self):
        """测试提升幅度分布计算"""
        times = [[8400, 8250, 8100] for _ in range(100)]
        analyzer = BaselineAnalyzer(times)
        distribution = analyzer.compute_improvement_distribution(window=1)

        assert len(distribution) == 100
        assert distribution[0] == -150

    def test_percentile_position(self):
        """测试百分位计算"""
        times = [[8400, 8100, 7950] for _ in range(100)]
        analyzer = BaselineAnalyzer(times)

        target_improvement = -600
        percentile = analyzer.get_percentile(target_improvement, window=1)

        assert percentile < 10

    def test_empty_timeseries(self):
        """测试单条时间序列无法计算"""
        times = [[8400]]
        analyzer = BaselineAnalyzer(times)
        distribution = analyzer.compute_improvement_distribution(window=1)
        assert len(distribution) == 0