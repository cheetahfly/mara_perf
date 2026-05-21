import pytest
import tempfile
import os
import csv
from datetime import date
from src.data_collection.loader import CSVLoader

class TestCSVLoader:
    def test_load_runner_csv(self):
        import io
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["name", "gender", "birth_year", "ethnicity"])
            writer.writerow(["张三", "M", 1990, "Asian"])
            writer.writerow(["李四", "F", 1985, "White"])
            f_path = f.name

        try:
            runners = list(CSVLoader.load_runners(f_path))
            assert len(runners) == 2
            assert runners[0].name == "张三"
        finally:
            os.unlink(f_path)

    def test_load_results_csv(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["runner_id", "race_name", "race_date", "finish_time_seconds", "is_certified"])
            writer.writerow([1, "北京马拉松", "2024-10-20", 8400, 1])
            f_path = f.name

        try:
            results = list(CSVLoader.load_results(f_path))
            assert len(results) == 1
            assert results[0].finish_time_seconds == 8400
        finally:
            os.unlink(f_path)