"""端到端测试：模拟真实分析流程"""
import pytest
from src.analysis.detector import AnomalyDetector
from src.data_collection.database import Database
from src.data_collection.loader import CSVLoader
import tempfile
import os
import csv
from datetime import date

class TestIntegration:
    def test_full_pipeline(self):
        """完整流程：从数据到判定"""
        # 1. 准备基准数据（模拟100个同龄男性黄种人跑者）
        baseline_times = []
        for _ in range(100):
            baseline_times.append([8400, 8200, 8000])

        # 2. 目标跑者：异常情况——从8400突然跳到7500
        target_times = [8400, 7500, 7400]

        # 3. 执行检测
        detector = AnomalyDetector(baseline_times, target_times)
        result = detector.detect()

        # 4. 验证
        assert result.is_abnormal is True
        assert result.verdict == "异常"

    def test_normal_breakthrough_integration(self):
        """正常突破案例"""
        baseline_times = [[8400, 8350, 8250] for _ in range(100)]
        target_times = [8400, 8200, 8000]

        detector = AnomalyDetector(baseline_times, target_times)
        result = detector.detect()

        assert result.is_longitudinal_anomaly is False
        assert result.verdict == "正常（训练突破）"
