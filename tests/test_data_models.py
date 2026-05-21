import pytest
from datetime import date
from src.data_collection.data_models import Runner, RaceResult

class TestRunner:
    def test_create_runner(self):
        runner = Runner(
            name="张三",
            gender="M",
            birth_year=1990,
            ethnicity="Asian"
        )
        assert runner.name == "张三"
        assert runner.gender == "M"
        assert runner.age_group(2024) == 34  # 2024 - 1990

    def test_age_group_calculation(self):
        runner = Runner(name="李四", gender="F", birth_year=1985, ethnicity="Asian")
        assert runner.age_group(2025) == 40  # 2025 - 1985

class TestRaceResult:
    def test_create_race_result(self):
        result = RaceResult(
            runner_id="runner_001",
            race_name="北京马拉松",
            race_date=date(2024, 10, 20),
            finish_time_seconds=8400,
            is_certified=True
        )
        assert result.finish_time_seconds == 8400
        assert result.finish_time_formatted == "2:20:00"
