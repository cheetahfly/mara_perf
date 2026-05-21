"""CSV 数据导入工具"""
import csv
from datetime import date
from typing import Iterator, List
from src.data_collection.data_models import Runner, RaceResult

class CSVLoader:
    @staticmethod
    def load_runners(csv_path: str) -> Iterator[Runner]:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield Runner(
                    name=row["name"],
                    gender=row["gender"],
                    birth_year=int(row["birth_year"]),
                    ethnicity=row["ethnicity"]
                )

    @staticmethod
    def load_results(csv_path: str) -> Iterator[RaceResult]:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield RaceResult(
                    runner_id=row["runner_id"],
                    race_name=row["race_name"],
                    race_date=date.fromisoformat(row["race_date"]),
                    finish_time_seconds=int(row["finish_time_seconds"]),
                    is_certified=bool(int(row.get("is_certified", 1)))
                )