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
        try:
            profile = scraper.get_athlete_profile(url)
            if not profile:
                continue

            # 推断 ethnicity
            ethnicity = scraper.infer_ethnicity(profile.get("nationality", ""))

            # 插入运动员
            runner_id = db.insert_runner(
                name=profile["name"],
                gender=profile["gender"],
                birth_year=profile.get("birth_year"),
                ethnicity=ethnicity,
            )

            new_athletes += 1
        except Exception as e:
            logger.warning(f"Error processing {url}: {e}")
            continue

    # 更新状态
    db.save_scrape_state(country, len(athlete_urls), 0)
    logger.info(f"  {country}: {len(athlete_urls)} athletes found, {new_athletes} processed")
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