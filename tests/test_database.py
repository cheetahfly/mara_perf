import pytest
import tempfile
import os
from src.data_collection.database import Database

class TestDatabase:
    def test_init_and_insert_runner(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            db = Database(db_path)
            runner_id = db.insert_runner("张三", "M", 1990, "Asian")
            assert runner_id == 1

            runner = db.get_runner(runner_id)
            assert runner.name == "张三"
            assert runner.gender == "M"

    def test_insert_and_query_results(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            db = Database(db_path)

            runner_id = db.insert_runner("李四", "F", 1985, "Asian")
            from datetime import date
            db.insert_result(runner_id, "上海马拉松", date(2024, 10, 20), 8400, True)

            results = db.get_results_by_runner(runner_id)
            assert len(results) == 1
            assert results[0].finish_time_seconds == 8400