#!/usr/bin/env python3
"""Download missing marathon results CSV files from GitHub via ghproxy."""
import os
import json
import urllib.request
import ssl
import time

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw", "marathon_results")
GITHUB_API = "https://api.github.com/repos/AndrewMillerOnline/marathon-results/contents"
GH_PROXY = "https://ghproxy.com/"
RETRIES = 5
ssl_ctx = ssl._create_unverified_context()

CITIES = {
    "Berlin": ["1999", "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019"],
    "Chicago": ["2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018"],
    "Honolulu": ["2015", "2016", "2017", "2018", "2019"],
    "Portland": ["2014", "2015", "2016", "2017", "2018", "2019"],
}


def download_file(url, dest, retries=RETRIES):
    if os.path.exists(dest):
        size = os.path.getsize(dest)
        if size > 1000:
            print(f"  SKIP (exists): {os.path.basename(dest)}")
            return True
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120, context=ssl_ctx) as src:
                data = src.read()
            with open(dest + ".tmp", "wb") as f:
                f.write(data)
            os.replace(dest + ".tmp", dest)
            print(f"  OK: {os.path.basename(dest)} ({len(data)//1024}KB)")
            return True
        except Exception as e:
            print(f"  Attempt {attempt+1}/{retries} failed: {e}")
            if attempt < retries - 1:
                time.sleep(5)
    print(f"  FAILED: {dest}")
    return False


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    total = 0
    for city, years in CITIES.items():
        city_dir = os.path.join(DATA_DIR, city)
        os.makedirs(city_dir, exist_ok=True)
        city_url = GITHUB_API + "/" + city.replace(" ", "%20")
        try:
            req = urllib.request.Request(city_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60, context=ssl_ctx) as resp:
                items = json.loads(resp.read())
            csv_map = {i["name"]: i for i in items if i["name"].endswith(".csv")}
        except Exception as e:
            print(f"Failed to list {city}: {e}")
            continue

        for year in years:
            fname = f"results-{year}.csv"
            dest = os.path.join(city_dir, fname)
            if fname in csv_map:
                proxy_url = GH_PROXY + csv_map[fname]["download_url"]
                print(f"{city}/{fname}...")
                if download_file(proxy_url, dest):
                    total += 1
            else:
                print(f"  NOT FOUND: {city}/{fname}")
        print()

    print(f"=== Downloaded {total} files ===")


if __name__ == "__main__":
    main()
