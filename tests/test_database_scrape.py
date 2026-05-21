import pytest
import tempfile
import os
from datetime import date
from src.data_collection.database import Database

class TestScrapeState:
    def test_save_and_load_scrape_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            db = Database(db_path)

            # 记录爬取状态
            db.save_scrape_state("Kenya", 100, 500)
            state = db.get_scrape_state("Kenya")

            assert state["country"] == "Kenya"
            assert state["athletes_count"] == 100
            assert state["results_count"] == 500

    def test_is_country_done(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            db = Database(db_path)

            assert db.is_country_done("Kenya") is False
            db.save_scrape_state("Kenya", 10, 50)
            assert db.is_country_done("Kenya") is True
