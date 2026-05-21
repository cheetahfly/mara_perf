#!/usr/bin/env python3
"""Download marathon datasets from GitHub (with China mirror proxy)."""
import os
import json
import urllib.request
import ssl
import time

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
CITIES = ["Boston", "London", "New York City", "Berlin", "Chicago", "Honolulu", "Portland"]
GITHUB_API = "https://api.github.com/repos/AndrewMillerOnline/marathon-results/contents"
GH_PROXY = "https://ghproxy.com/"
WA_URL = GH_PROXY + "https://raw.githubusercontent.com/thomascamminady/world-athletics-database/main/data/data.csv"
RETRIES = 5
ssl_ctx = ssl._create_unverified_context()


def download_file(url, dest, retries=RETRIES):
    if os.path.exists(dest):
        size = os.path.getsize(dest)
        print(f"  EXISTS: {os.path.basename(dest)} ({size} bytes)")
        return True
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            print(f"  Downloading...")
            with urllib.request.urlopen(req, timeout=300, context=ssl_ctx) as src:
                data = src.read()
            with open(dest + ".tmp", "wb") as f:
                f.write(data)
            os.replace(dest + ".tmp", dest)
            print(f"  OK: {os.path.basename(dest)} ({len(data)} bytes)")
            return True
        except Exception as e:
            print(f"  Attempt {attempt+1}/{retries} failed: {e}")
            if attempt < retries - 1:
                time.sleep(5)
    return False


def download_marathon_results():
    target = os.path.join(DATA_DIR, "marathon_results")
    os.makedirs(target, exist_ok=True)
    total = 0
    for city in CITIES:
        city_dir = os.path.join(target, city)
        os.makedirs(city_dir, exist_ok=True)
        city_url = GITHUB_API + "/" + city.replace(" ", "%20")
        try:
            req = urllib.request.Request(city_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60, context=ssl_ctx) as resp:
                items = json.loads(resp.read())
            csv_files = [i for i in items if i["name"].endswith(".csv")]
            for item in csv_files:
                dest = os.path.join(city_dir, item["name"])
                proxy_url = GH_PROXY + item["download_url"]
                if download_file(proxy_url, dest):
                    total += 1
                else:
                    print(f"  FAILED: {city}/{item['name']}")
                    # try direct as fallback
                    print(f"  Retrying direct...")
                    download_file(item["download_url"], dest)
        except Exception as e:
            print(f"  FAILED to list {city}: {e}")
    print(f"\n  Downloaded {total} files total")


def download_world_athletics():
    dest = os.path.join(DATA_DIR, "world_athletics_db.csv")
    try:
        os.remove(os.path.join(DATA_DIR, "world_athletics_db.csv.lock"))
    except:
        pass
    if os.path.exists(dest):
        size = os.path.getsize(dest)
        if size > 48000000:  # nearly complete
            print(f"  EXISTS: world_athletics_db.csv ({size} bytes)")
            return
        else:
            print(f"  Partial file ({size} bytes), re-downloading...")
            try:
                os.remove(dest)
            except:
                print("  Cannot remove lock, will download to temp name")
                dest = os.path.join(DATA_DIR, "world_athletics_db_v2.csv")
    download_file(WA_URL, dest)


if __name__ == "__main__":
    print("=== Downloading World Athletics DB ===")
    download_world_athletics()
    print("\n=== Downloading Marathon Results ===")
    download_marathon_results()
    print("\n=== All Done ===")
