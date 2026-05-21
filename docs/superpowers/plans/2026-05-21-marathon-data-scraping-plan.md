# World Athletics 马拉松数据爬取 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal：** 实现 World Athletics 马拉松数据爬虫，抓取 35 个国家的运动员数据并存储到 SQLite

**Architecture：**
- Scraper 基类：通用 HTTP 请求、反封延时、HTML 解析
- WorldAthleticsScraper 子类：WA 专用解析逻辑、ethnology 推断
- 数据存储：SQLite + CSV 双轨存储，支持断点续爬

**Tech Stack：** Python 3.10+ / requests / beautifulsoup4 / lxml / sqlite3

---

## 文件结构

```
F:\ai_data_ana\mara_perf\
├── src/data_collection/
│   ├── scraper.py                    # 基类 Scraper（新增）
│   └── world_athletics_scraper.py   # WA 爬虫（新增）
├── tests/
│   ├── test_scraper.py              # 爬虫基类测试（新增）
│   └── test_world_athletics_scraper.py  # WA 爬虫测试（新增）
├── data/
│   └── raw/html/                    # HTML 缓存目录
└── docs/superpowers/specs/          # 设计文档（已有）
```

---

## Task 1: Scraper 基类实现

**Files:**
- Create: `src/data_collection/scraper.py`
- Create: `tests/test_scraper.py`

- [ ] **Step 1: 写测试**

```python
# tests/test_scraper.py
import pytest
from unittest.mock import patch, MagicMock
from src.data_collection.scraper import Scraper

class TestScraper:
    def test_fetch_success(self):
        """测试成功获取页面"""
        scraper = Scraper()
        with patch('requests.get') as mock_get:
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
        with patch('requests.get') as mock_get:
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

    def test_ethicity_infer(self):
        """测试 ethnicity 推断"""
        scraper = Scraper()
        assert scraper.infer_ethnicity("Kenya") == "Black-African"
        assert scraper.infer_ethnicity("Japan") == "Asian"
        assert scraper.infer_ethnicity("Germany") == "White"
        assert scraper.infer_ethnicity("UnknownCountry") == "Unknown"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd F:\ai_data_ana\mara_perf && pytest tests/test_scraper.py -v
# 预期: FAIL - module not found
```

- [ ] **Step 3: 实现 scraper.py**

```python
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
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd F:\ai_data_ana\mara_perf && pytest tests/test_scraper.py -v
# 预期: PASS
```

- [ ] **Step 5: 提交**

```bash
git add tests/test_scraper.py src/data_collection/scraper.py
git commit -m "feat: add Scraper base class with HTTP requests and ethnicity inference"
```

---

## Task 2: WorldAthleticsScraper 实现

**Files:**
- Create: `src/data_collection/world_athletics_scraper.py`
- Create: `tests/test_world_athletics_scraper.py`

- [ ] **Step 1: 写测试**

```python
# tests/test_world_athletics_scraper.py
import pytest
from unittest.mock import patch, MagicMock
from src.data_collection.world_athletics_scraper import WorldAthleticsScraper

class TestWorldAthleticsScraper:
    def test_build_country_url(self):
        """测试国家列表 URL 构建"""
        scraper = WorldAthleticsScraper()
        url = scraper.build_country_url("kenya")
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
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd F:\ai_data_ana\mara_perf && pytest tests/test_world_athletics_scraper.py -v
# 预期: FAIL - module not found
```

- [ ] **Step 3: 实现 world_athletics_scraper.py**

```python
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
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd F:\ai_data_ana\mara_perf && pytest tests/test_world_athletics_scraper.py -v
# 预期: PASS
```

- [ ] **Step 5: 提交**

```bash
git add tests/test_world_athletics_scraper.py src/data_collection/world_athletics_scraper.py
git commit -m "feat: add WorldAthleticsScraper for marathon data collection"
```

---

## Task 3: 数据存储扩展 + 导出 CSV

**Files:**
- Modify: `src/data_collection/database.py`（添加 scrape_state 表）
- Create: `scripts/export_csv.py`

- [ ] **Step 1: 写测试**

```python
# tests/test_database_scrape.py
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
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd F:\ai_data_ana\mara_perf && pytest tests/test_database_scrape.py -v
# 预期: FAIL
```

- [ ] **Step 3: 修改 database.py 添加爬取状态表**

```python
# 在 Database 类中添加以下方法（在 _init_db 中添加 scrape_state 表）

# 表创建 SQL（添加到 _init_db）:
"""
CREATE TABLE IF NOT EXISTS scrape_state (
    country TEXT PRIMARY KEY,
    athletes_count INTEGER DEFAULT 0,
    results_count INTEGER DEFAULT 0,
    last_updated TEXT
)
"""

# 添加方法:
def save_scrape_state(self, country: str, athletes_count: int, results_count: int):
    with sqlite3.connect(self.db_path) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO scrape_state (country, athletes_count, results_count, last_updated)
            VALUES (?, ?, ?, datetime('now'))
        """, (country, athletes_count, results_count))

def get_scrape_state(self, country: str) -> Optional[dict]:
    with sqlite3.connect(self.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM scrape_state WHERE country = ?", (country,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def is_country_done(self, country: str) -> bool:
    state = self.get_scrape_state(country)
    return state is not None and state["athletes_count"] > 0
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd F:\ai_data_ana\mara_perf && pytest tests/test_database_scrape.py -v
# 预期: PASS
```

- [ ] **Step 5: 创建导出脚本**

```python
# scripts/export_csv.py
"""导出数据库数据到 CSV"""
import argparse
import csv
from src.data_collection.database import Database

def export_runners(db: Database, output_path: str):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "gender", "birth_year", "ethnicity", "country"])
        # 从数据库读取并写入
        # 实现...

def export_results(db: Database, output_path: str):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["runner_id", "race_name", "race_date", "finish_time_seconds", "is_certified"])
        # 实现...

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="data/marathon.db")
    parser.add_argument("--runners", default="data/processed/runners.csv")
    parser.add_argument("--results", default="data/processed/results.csv")
    args = parser.parse_args()

    db = Database(args.db)
    export_runners(db, args.runners)
    export_results(db, args.results)
    print(f"Exported to {args.runners} and {args.results}")
```

- [ ] **Step 6: 提交**

```bash
git add src/data_collection/database.py scripts/export_csv.py
git commit -m "feat: add scrape state tracking and CSV export"
```

---

## Task 4: 批量爬取主程序

**Files:**
- Create: `scripts/batch_scrape.py`

- [ ] **Step 1: 编写批量爬取脚本**

```python
# scripts/batch_scrape.py
"""
批量爬取 World Athletics 运动员数据

用法:
    python scripts/batch_scrape.py --db data/marathon.db --countries Kenya Ethiopia Japan
    python scripts/batch_scrape.py --db data/marathon.db --all  # 爬取全部 35 个国家
"""
import argparse
import logging
import sys
import os

# 确保 src 在 path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_collection.world_athletics_scraper import WorldAthleticsScraper
from src.data_collection.database import Database

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# 全部 35 个国家列表
ALL_COUNTRIES = [
    # 东非
    "Kenya", "Ethiopia", "Eritrea", "Uganda", "Tanzania",
    # 北非
    "Morocco", "Egypt", "Algeria", "Tunisia",
    # 西非/加勒比
    "Jamaica", "Bahamas", "United States", "Trinidad and Tobago",
    # 东亚
    "Japan", "China", "Korea", "North Korea", "Mongolia",
    # 东南亚
    "Thailand", "Vietnam", "Indonesia", "Philippines",
    # 南亚
    "India", "Pakistan", "Bangladesh", "Sri Lanka",
    # 中东
    "Qatar", "Bahrain", "United Arab Emirates", "Saudi Arabia",
    # 欧洲
    "United Kingdom", "France", "Germany", "Italy", "Spain",
    "Netherlands", "Belgium", "Switzerland", "Sweden", "Poland", "Russia",
    # 其他
    "Australia", "New Zealand", "Canada", "Mexico", "Brazil",
]

def scrape_country(scraper: WorldAthleticsScraper, db: Database, country: str) -> int:
    """爬取单个国家的数据，返回新增运动员数"""
    if db.is_country_done(country):
        logger.info(f"Skipping {country} (already done)")
        return 0

    logger.info(f"Scraping {country}...")
    athlete_urls = scraper.search_athletes(country)

    new_athletes = 0
    for url in athlete_urls:
        profile = scraper.get_athlete_profile(url)
        if not profile:
            continue

        # 插入运动员
        runner_id = db.insert_runner(
            name=profile["name"],
            gender=profile["gender"],
            birth_year=profile.get("birth_year"),
            ethnicity=profile.get("ethnicity", "Unknown"),
        )

        # 抓取成绩（简化：WA 页面需要额外请求）
        # TODO: 解析成绩
        new_athletes += 1

    # 更新状态
    db.save_scrape_state(country, len(athlete_urls), 0)
    logger.info(f"  {country}: {len(athlete_urls)} athletes")
    return new_athletes

def main():
    parser = argparse.ArgumentParser(description="World Athletics 批量爬取")
    parser.add_argument("--db", default="data/marathon.db", help="SQLite 数据库路径")
    parser.add_argument("--countries", nargs="+", help="指定国家列表")
    parser.add_argument("--all", action="store_true", help="爬取全部国家")
    args = parser.parse_args()

    countries = args.countries if not args.all else ALL_COUNTRIES
    if not countries:
        parser.error("请指定 --countries 或 --all")

    db = Database(args.db)
    scraper = WorldAthleticsScraper()

    total = 0
    for country in countries:
        try:
            total += scrape_country(scraper, db, country)
        except Exception as e:
            logger.error(f"Error scraping {country}: {e}")
            continue

    logger.info(f"Done! Total new athletes: {total}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 测试帮助信息**

```bash
cd F:\ai_data_ana\mara_perf && python scripts/batch_scrape.py --help
# 预期: 显示帮助信息
```

- [ ] **Step 3: 提交**

```bash
git add scripts/batch_scrape.py
git commit -m "feat: add batch scraping script for 35 countries"
```

---

## Task 5: 测试爬取单个运动员

**Files:**
- Modify: `tests/test_world_athletics_scraper.py`

- [ ] **Step 1: 添加真实请求测试（需要网络，可选）**

```python
# tests/test_world_athletics_scraper_live.py
import pytest

class TestLiveScraping:
    @pytest.mark.skip(reason="需要网络，CI 环境跳过")
    def test_scrape_eliud_kipchoge(self):
        """测试爬取真实运动员页面"""
        from src.data_collection.world_athletics_scraper import WorldAthleticsScraper

        scraper = WorldAthleticsScraper()
        # 肯尼亚运动员 Eliud Kipchoge 的页面
        profile = scraper.get_athlete_profile(
            "https://worldathletics.org/athletes/kenya/eliud-kipchoge-xxxxx"
        )
        assert profile is not None
        assert profile["birth_year"] is not None
```

- [ ] **Step 2: 提交**

```bash
git add tests/test_world_athletics_scraper.py
git commit -m "test: add live scraping test (skipped by default)"
```

---

## 实施顺序

1. Task 1: Scraper 基类实现
2. Task 2: WorldAthleticsScraper 实现
3. Task 3: 数据存储扩展 + 导出 CSV
4. Task 4: 批量爬取主程序
5. Task 5: 测试爬取单个运动员

---

## 注意事项

- **反封禁**：WA 可能有 Cloudflare 等保护，首次使用建议先测试 `--countries Japan`（小样本）
- **进度追踪**：每个国家完成后会记录状态，重启后可继续
- **HTML 解析**：WA 页面结构可能随版本变化，发现解析失败请记录具体 URL 和页面版本
- **成绩解析**：WA 页面需要额外 JavaScript 渲染，初步版本可能无法直接解析所有成绩
