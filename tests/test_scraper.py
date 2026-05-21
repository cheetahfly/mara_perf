import pytest
from unittest.mock import patch, MagicMock
from src.data_collection.scraper import Scraper

class TestScraper:
    def test_fetch_success(self):
        """测试成功获取页面"""
        scraper = Scraper()
        with patch('requests.Session.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>test</body></html>"
            mock_get.return_value = mock_response

            html = scraper.fetch("http://example.com")
            assert "test" in html
            mock_get.assert_called_once()

    def test_fetch_retry_on_failure(self):
        """测试失败自动重试"""
        scraper = Scraper()
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = [Exception("fail"), Exception("fail"), MagicMock(status_code=200, text="ok")]
            html = scraper.fetch("http://example.com", max_retries=3)
            assert html == "ok"
            assert mock_get.call_count == 3

    def test_rate_limit(self):
        """测试请求间隔控制"""
        import time
        scraper = Scraper(min_interval=0.1)
        start = time.time()
        for _ in range(3):
            scraper._rate_limit()
        elapsed = time.time() - start
        assert elapsed >= 0.2  # 至少 0.1 * 2 次间隔

    def test_parse_html(self):
        """测试 HTML 解析"""
        scraper = Scraper()
        soup = scraper.parse_html("<html><body><div id='test'>content</div></body></html>")
        assert soup.select_one("#test").text == "content"

    def test_ethnicity_infer(self):
        """测试 ethnicity 推断"""
        scraper = Scraper()
        assert scraper.infer_ethnicity("Kenya") == "Black-African"
        assert scraper.infer_ethnicity("Japan") == "Asian"
        assert scraper.infer_ethnicity("Germany") == "White"
        assert scraper.infer_ethnicity("UnknownCountry") == "Unknown"
