# src/data_collection/world_athletics_scraper.py
"""World Athletics 专用爬虫"""
import logging
import re
from datetime import date
from typing import List, Optional, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.data_collection.scraper import Scraper

logger = logging.getLogger(__name__)

# 国家名称到 WA URL slug 的映射
COUNTRY_TO_SLUG = {
    "Kenya": "kenya",
    "Ethiopia": "ethiopia",
    "Eritrea": "eritrea",
    "Uganda": "uganda",
    "Tanzania": "tanzania",
    "Morocco": "morocco",
    "Egypt": "egypt",
    "Algeria": "algeria",
    "Tunisia": "tunisia",
    "Jamaica": "jamaica",
    "Bahamas": "bahamas",
    "United States": "usa",
    "Trinidad and Tobago": "trinidad-and-tobago",
    "Japan": "japan",
    "China": "china",
    "Korea": "korea",
    "North Korea": "prk",
    "Mongolia": "mongolia",
    "Thailand": "thailand",
    "Vietnam": "vietnam",
    "Indonesia": "indonesia",
    "Philippines": "philippines",
    "India": "india",
    "Pakistan": "pakistan",
    "Bangladesh": "bangladesh",
    "Sri Lanka": "sri-lanka",
    "Qatar": "qatar",
    "Bahrain": "bahrain",
    "United Arab Emirates": "uae",
    "Saudi Arabia": "saudi-arabia",
    "United Kingdom": "great-britain",
    "France": "france",
    "Germany": "germany",
    "Italy": "italy",
    "Spain": "spain",
    "Netherlands": "netherlands",
    "Belgium": "belgium",
    "Switzerland": "switzerland",
    "Sweden": "sweden",
    "Poland": "poland",
    "Russia": "russia",
    "Australia": "australia",
    "New Zealand": "new-zealand",
    "Canada": "canada",
    "Mexico": "mexico",
    "Brazil": "brazil",
}


class WorldAthleticsScraper(Scraper):
    """World Athletics 专用爬虫"""

    BASE_URL = "https://worldathletics.org"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("min_interval", 1.0)
        super().__init__(*args, **kwargs)

    def build_country_url(self, country: str) -> str:
        """构建国家运动员列表页 URL"""
        slug = COUNTRY_TO_SLUG.get(country, country.lower().replace(" ", "-"))
        return f"{self.BASE_URL}/athletes/{slug}/"

    def search_athletes(self, country: str, page: int = 1) -> List[str]:
        """
        搜索指定国家的运动员列表
        返回运动员 profile 页 URL 列表
        """
        url = self.build_country_url(country)
        if page > 1:
            url = f"{url}?page={page}"

        html = self.fetch(url)
        if not html:
            return []

        soup = self.parse_html(html)
        athlete_urls = []

        # 查找运动员列表项
        for a in soup.select("a[href*='/athletes/']"):
            href = a.get("href", "")
            if href and "/athletes/" in href and not href.endswith("/athletes/"):
                full_url = urljoin(self.BASE_URL, href)
                if full_url not in athlete_urls:
                    athlete_urls.append(full_url)

        return athlete_urls

    def get_athlete_profile(self, url: str) -> Optional[dict]:
        """
        获取单个运动员档案
        返回 dict: {name, gender, birth_year, nationality, country}
        """
        html = self.fetch(url)
        if not html:
            return None

        soup = self.parse_html(html)

        # 解析姓名
        name_elem = soup.select_one("h1[data-testid='athlete-name'], h1.athlete-name")
        name = name_elem.text.strip() if name_elem else ""

        # 解析性别（从 URL 或页面判断）
        gender = "M" if "/men/" in url else "F"

        # 解析出生日期
        dob_elem = soup.select_one("[data-testid='date-of-birth'], .dob")
        birth_year = None
        if dob_elem:
            dob_text = dob_elem.text.strip()
            year_match = re.search(r"\b(19\d{2}|20\d{2})\b", dob_text)
            if year_match:
                birth_year = int(year_match.group(1))

        # 解析国籍
        nat_elem = soup.select_one("[data-testid='nationality'], .nationality")
        nationality = nat_elem.text.strip() if nat_elem else ""

        return {
            "name": name,
            "gender": gender,
            "birth_year": birth_year,
            "nationality": nationality,
            "country": nationality,
            "url": url,
        }

    def parse_results(self, html: str, runner_id: str) -> List[dict]:
        """
        解析运动员成绩列表
        返回 List[dict]: {runner_id, race_name, race_date, finish_time_seconds, is_certified}
        """
        soup = self.parse_html(html)
        results = []

        # WA 成绩表格结构
        for row in soup.select("table.results tbody tr, table.athlete-results tbody tr"):
            cols = row.select("td")
            if len(cols) < 4:
                continue

            # 提取赛事名称
            race_elem = row.select_one("td:nth-child(2) a, td.event a")
            race_name = race_elem.text.strip() if race_elem else ""

            # 提取日期
            date_elem = row.select_one("td:nth-child(3), td.date")
            race_date_str = date_elem.text.strip() if date_elem else ""

            # 提取成绩
            time_elem = row.select_one("td:nth-child(4) .time, td.time")
            time_str = time_elem.text.strip() if time_elem else ""

            if not race_name or not time_str:
                continue

            # 解析日期
            race_date = None
            if race_date_str:
                try:
                    # 尝试多种日期格式
                    for fmt in ["%d %b %Y", "%d %b %y", "%Y-%m-%d", "%d/%m/%Y"]:
                        try:
                            race_date = date.fromisoformat(race_date_str.replace(" ", "-"))
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass

            # 解析成绩（秒）
            finish_seconds = self.parse_time(time_str)

            results.append({
                "runner_id": runner_id,
                "race_name": race_name,
                "race_date": race_date,
                "finish_time_seconds": finish_seconds,
                "is_certified": True,
            })

        return results

    def parse_time(self, time_str: str) -> Optional[int]:
        """将时间字符串转为秒数"""
        time_str = time_str.strip().replace(":", ":")

        # 尝试 HH:MM:SS 格式
        parts = time_str.split(":")
        try:
            if len(parts) == 3:
                h, m, s = parts
                return int(h) * 3600 + int(m) * 60 + int(s)
            elif len(parts) == 2:
                m, s = parts
                return int(m) * 60 + int(s)
        except ValueError:
            pass
        return None

    def infer_ethnicity(self, nationality: str) -> str:
        """根据国籍推断 ethnicity"""
        return super().infer_ethnicity(nationality)