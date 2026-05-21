# scripts/export_csv.py
"""导出数据库数据到 CSV"""
import argparse
import csv
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_collection.database import Database


def export_runners(db: Database, output_path: str):
    """导出运动员数据"""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "gender", "birth_year", "ethnicity", "country"])

        # 读取所有运动员
        with __import__('sqlite3').connect(db.db_path) as conn:
            conn.row_factory = __import__('sqlite3').Row
            cursor = conn.execute("SELECT * FROM runners ORDER BY id")
            for row in cursor:
                writer.writerow([
                    row["id"],
                    row["name"],
                    row["gender"],
                    row["birth_year"],
                    row["ethnicity"],
                    row["ethnicity"],  # country 字段复用 ethnicity 的映射值
                ])


def export_results(db: Database, output_path: str):
    """导出比赛成绩数据"""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["runner_id", "race_name", "race_date", "finish_time_seconds", "is_certified"])

        with __import__('sqlite3').connect(db.db_path) as conn:
            conn.row_factory = __import__('sqlite3').Row
            cursor = conn.execute("SELECT * FROM results ORDER BY runner_id")
            for row in cursor:
                writer.writerow([
                    row["runner_id"],
                    row["race_name"],
                    row["race_date"],
                    row["finish_time_seconds"],
                    row["is_certified"],
                ])


def main():
    parser = argparse.ArgumentParser(description="导出马拉松数据到 CSV")
    parser.add_argument("--db", default="data/marathon.db", help="SQLite 数据库路径")
    parser.add_argument("--runners", default="data/processed/runners.csv", help="运动员 CSV 输出路径")
    parser.add_argument("--results", default="data/processed/results.csv", help="成绩 CSV 输出路径")
    args = parser.parse_args()

    # 确保输出目录存在
    os.makedirs(os.path.dirname(args.runners), exist_ok=True)
    os.makedirs(os.path.dirname(args.results), exist_ok=True)

    db = Database(args.db)
    export_runners(db, args.runners)
    export_results(db, args.results)
    print(f"导出完成: {args.runners}, {args.results}")


if __name__ == "__main__":
    main()