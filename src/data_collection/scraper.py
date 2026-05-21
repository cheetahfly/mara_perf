# src/data_collection/scraper.py
"""爬虫基类：通用 HTTP 请求、反封延时、HTML 解析"""
import time
import logging
from typing import Optional
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# World Athletics 国家代码到标准国家名映射
COUNTRY_CODE_MAP = {
    "kenya": "Kenya",
    "ethiopia": "Ethiopia",
    "eritrea": "Eritrea",
    "uganda": "Uganda",
    "tanzania": "Tanzania",
    "morocco": "Morocco",
    "egypt": "Egypt",
    "algeria": "Algeria",
    "tunisia": "Tunisia",
    "jamaica": "Jamaica",
    "bahamas": "Bahamas",
    "usa": "United States",
    "trinidad-and-tobago": "Trinidad and Tobago",
    "japan": "Japan",
    "china": "China",
    "korea": "Korea",
    "prk": "North Korea",
    "mongolia": "Mongolia",
    "thailand": "Thailand",
    "vietnam": "Vietnam",
    "indonesia": "Indonesia",
    "philippines": "Philippines",
    "india": "India",
    "pakistan": "Pakistan",
    "bangladesh": "Bangladesh",
    "sri-lanka": "Sri Lanka",
    "qatar": "Qatar",
    "bahrain": "Bahrain",
    "uae": "United Arab Emirates",
    "saudi-arabia": "Saudi Arabia",
    "great-britain": "United Kingdom",
    "france": "France",
    "germany": "Germany",
    "italy": "Italy",
    "spain": "Spain",
    "netherlands": "Netherlands",
    "belgium": "Belgium",
    "switzerland": "Switzerland",
    "sweden": "Sweden",
    "poland": "Poland",
    "russia": "Russia",
    "australia": "Australia",
    "new-zealand": "New Zealand",
    "canada": "Canada",
    "mexico": "Mexico",
    "brazil": "Brazil",
}

# Ethnicity 推断映射
ETHNICITY_MAP = {
    # 东非
    "Kenya": "Black-African",
    "Ethiopia": "Black-African",
    "Eritrea": "Black-African",
    "Uganda": "Black-African",
    "Tanzania": "Black-African",
    # 北非
    "Morocco": "Black-Maghrebi",
    "Egypt": "Black-Maghrebi",
    "Algeria": "Black-Maghrebi",
    "Tunisia": "Black-Maghrebi",
    "Libya": "Black-Maghrebi",
    # 西非/加勒比
    "Jamaica": "Black-Caribbean",
    "Bahamas": "Black-Caribbean",
    "Trinidad and Tobago": "Black-Caribbean",
    "United States": "Black-Caribbean",
    # 东亚/东南亚
    "Japan": "Asian",
    "Korea": "Asian",
    "China": "Asian",
    "North Korea": "Asian",
    "Mongolia": "Asian",
    "Vietnam": "Asian",
    "Thailand": "Asian",
    "Philippines": "Asian",
    "Indonesia": "Asian",
    # 南亚
    "India": "Asian-South",
    "Pakistan": "Asian-South",
    "Bangladesh": "Asian-South",
    "Sri Lanka": "Asian-South",
    "Nepal": "Asian-South",
    # 中东
    "Qatar": "Asian-MiddleEast",
    "Bahrain": "Asian-MiddleEast",
    "United Arab Emirates": "Asian-MiddleEast",
    "Saudi Arabia": "Asian-MiddleEast",
    "Kuwait": "Asian-MiddleEast",
    "Oman": "Asian-MiddleEast",
    # 欧洲
    "United Kingdom": "White",
    "France": "White",
    "Germany": "White",
    "Italy": "White",
    "Spain": "White",
    "Netherlands": "White",
    "Belgium": "White",
    "Switzerland": "White",
    "Sweden": "White",
    "Poland": "White",
    "Russia": "White",
    "Portugal": "White",
    "Greece": "White",
    # 其他
    "Australia": "Other",
    "New Zealand": "Other",
    "Canada": "Other",
    "Mexico": "Other",
    "Brazil": "Other",
    "Argentina": "Other",
    "Peru": "Other",
    "Chile": "Other",
}


class Scraper:
    """爬虫基类"""

    def __init__(self, min_interval: float = 1.0, timeout: int = 30):
        self.min_interval = min_interval
        self.timeout = timeout
        self._last_request_time = 0.0
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def fetch(self, url: str, max_retries: int = 3) -> Optional[str]:
        """HTTP GET 请求，带重试"""
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 2s, 4s, 8s
        logger.error(f"All {max_retries} attempts failed for {url}")
        return None

    def _rate_limit(self):
        """请求间隔控制"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last_request_time = time.time()

    def parse_html(self, html: str) -> BeautifulSoup:
        """解析 HTML"""
        return BeautifulSoup(html, "lxml")

    @staticmethod
    def infer_ethnicity(country: str) -> str:
        """根据国家推断 ethnicity"""
        return ETHNICITY_MAP.get(country, "Unknown")

    @staticmethod
    def normalize_country(code: str) -> str:
        """将 URL 中的国家代码转为标准国家名"""
        return COUNTRY_CODE_MAP.get(code.lower(), code)
