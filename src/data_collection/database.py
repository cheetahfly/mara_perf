"""SQLite 数据存储层"""
import sqlite3
import gc
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

@dataclass
class Runner:
    id: int
    name: str
    gender: str
    birth_year: int
    ethnicity: str

@dataclass
class RaceResult:
    id: int
    runner_id: int
    race_name: str
    race_date: date
    finish_time_seconds: int
    is_certified: bool

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn = None
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gender TEXT NOT NULL,
                birth_year INTEGER NOT NULL,
                ethnicity TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                runner_id INTEGER NOT NULL,
                race_name TEXT NOT NULL,
                race_date TEXT NOT NULL,
                finish_time_seconds INTEGER NOT NULL,
                is_certified INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (runner_id) REFERENCES runners(id)
            )
        """)
        conn.close()
        gc.collect()

    def insert_runner(self, name: str, gender: str, birth_year: int, ethnicity: str) -> int:
        conn = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
        cursor = conn.execute(
            "INSERT INTO runners (name, gender, birth_year, ethnicity) VALUES (?, ?, ?, ?)",
            (name, gender, birth_year, ethnicity)
        )
        result = cursor.lastrowid
        conn.close()
        gc.collect()
        return result

    def get_runner(self, runner_id: int) -> Optional[Runner]:
        conn = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM runners WHERE id = ?", (runner_id,))
        row = cursor.fetchone()
        result = None
        if row:
            result = Runner(id=row["id"], name=row["name"], gender=row["gender"],
                          birth_year=row["birth_year"], ethnicity=row["ethnicity"])
        conn.close()
        gc.collect()
        return result

    def insert_result(self, runner_id: int, race_name: str, race_date: date,
                     finish_time_seconds: int, is_certified: bool = True) -> int:
        conn = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
        cursor = conn.execute(
            "INSERT INTO results (runner_id, race_name, race_date, finish_time_seconds, is_certified) VALUES (?, ?, ?, ?, ?)",
            (runner_id, race_name, race_date.isoformat(), finish_time_seconds, int(is_certified))
        )
        result = cursor.lastrowid
        conn.close()
        gc.collect()
        return result

    def get_results_by_runner(self, runner_id: int) -> List[RaceResult]:
        conn = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM results WHERE runner_id = ? ORDER BY race_date",
            (runner_id,)
        )
        rows = cursor.fetchall()
        result = [RaceResult(
            id=row["id"], runner_id=row["runner_id"], race_name=row["race_name"],
            race_date=date.fromisoformat(row["race_date"]),
            finish_time_seconds=row["finish_time_seconds"],
            is_certified=bool(row["is_certified"])
        ) for row in rows]
        conn.close()
        gc.collect()
        return result