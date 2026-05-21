"""马拉松数据模型"""
from dataclasses import dataclass
from datetime import date
from typing import Optional
from src.utils.time_converter import format_time

@dataclass
class Runner:
    name: str
    gender: str  # "M" or "F"
    birth_year: int
    ethnicity: str  # "Black", "White", "Asian", etc.

    def age_group(self, reference_year: int) -> int:
        return reference_year - self.birth_year

@dataclass
class RaceResult:
    runner_id: str
    race_name: str
    race_date: date
    finish_time_seconds: int
    is_certified: bool = True
    notes: Optional[str] = None

    @property
    def finish_time_formatted(self) -> str:
        return format_time(self.finish_time_seconds)
