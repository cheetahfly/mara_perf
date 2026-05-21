import pytest
from unittest.mock import patch, MagicMock
from src.data_collection.world_athletics_scraper import WorldAthleticsScraper

class TestWorldAthleticsScraper:
    def test_build_country_url(self):
        """测试国家列表 URL 构建"""
        scraper = WorldAthleticsScraper()
        url = scraper.build_country_url("Kenya")
        assert "worldathletics.org" in url
        assert "/athletes/kenya/" in url

    def test_infer_ethnicity_from_nationality(self):
        """测试 nationality 到 ethnicity 的推断"""
        scraper = WorldAthleticsScraper()
        assert scraper.infer_ethnicity("Kenya") == "Black-African"
        assert scraper.infer_ethnicity("Japan") == "Asian"

    def test_parse_time_to_seconds(self):
        """测试时间字符串解析"""
        scraper = WorldAthleticsScraper()
        assert scraper.parse_time("2:08:38") == 7718
        assert scraper.parse_time("1:02:44") == 3764
        assert scraper.parse_time("28:45") == 1725  # 场地赛格式