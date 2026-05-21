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


# tests/test_world_athletics_scraper_live.py
import pytest

class TestLiveScraping:
    @pytest.mark.skip(reason="需要网络，CI 环境跳过，仅供本地测试")
    def test_scrape_japan_athlete(self):
        """测试爬取日本运动员页面"""
        from src.data_collection.world_athletics_scraper import WorldAthleticsScraper

        scraper = WorldAthleticsScraper()
        # 日本运动员，大迫杰
        url = "https://worldathletics.org/athletes/japan/sho-obara-12345"

        profile = scraper.get_athlete_profile(url)
        # 允许返回 None（如果运动员不存在）
        if profile:
            assert profile["name"] is not None
            assert profile["gender"] in ("M", "F")

    @pytest.mark.skip(reason="需要网络，CI 环境跳过，仅供本地测试")
    def test_search_japan_athletes(self):
        """测试搜索日本运动员列表"""
        from src.data_collection.world_athletics_scraper import WorldAthleticsScraper

        scraper = WorldAthleticsScraper()
        urls = scraper.search_athletes("Japan", page=1)

        # 应该返回 URL 列表
        assert isinstance(urls, list)