// .github/workflows/daily_wallpaper.yml
/*
name: Daily Wallpaper Update

on:
  schedule:
    # Run every day at 00:00 UTC (= 08:00 CST/北京时间)
    - cron: '0 0 * * *' 
  workflow_dispatch:

jobs:
  update_wallpaper:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repo
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: Install requirements
        run: |
          pip install requests

      - name: Run wallpaper update script
        run: |
          python scripts/daily_wallpaper_update.py

      - name: Commit and Push wallpapers
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add daily_updates/
          git commit -m "Daily update: Add new wallpapers" || echo "Nothing to commit"
          git push
*/

// scripts/daily_wallpaper_update.py
/*
import os
import requests
from datetime import datetime, timedelta, timezone

# Constants
WALLHAVEN_API = "https://wallhaven.cc/api/v1/search?sorting=date_added&order=desc"
DOWNLOAD_COUNT = 5
DAILY_DIR = "daily_updates"

def fetch_latest_wallpapers():
    resp = requests.get(WALLHAVEN_API)
    resp.raise_for_status()
    data = resp.json()
    wallpapers = data.get('data', [])[:DOWNLOAD_COUNT]
    image_urls = []
    for wp in wallpapers:
        image_urls.append(wp['path'])
    return image_urls

def save_wallpapers(image_urls, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    for url in image_urls:
        fname = url.split('/')[-1]
        path = os.path.join(save_dir, fname)
        if not os.path.exists(path):
            r = requests.get(url, stream=True)
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)

def clean_old_directories(base_dir, keep_days=7):
    today = datetime.now(timezone.utc).date()
    for d in os.listdir(base_dir):
        dir_path = os.path.join(base_dir, d)
        try:
            date_obj = datetime.strptime(d, "%Y-%m-%d").date()
        except Exception:
            continue
        if (today - date_obj).days > keep_days:
            # Delete old directory
            for root, dirs, files in os.walk(dir_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(dir_path)

def main():
    # Convert UTC now to Beijing Time (UTC+8)
    utc_now = datetime.utcnow()
    bj_now = utc_now + timedelta(hours=8)
    today_str = bj_now.strftime("%Y-%m-%d")

    target_dir = os.path.join(DAILY_DIR, today_str)
    image_urls = fetch_latest_wallpapers()
    save_wallpapers(image_urls, target_dir)
    clean_old_directories(DAILY_DIR, keep_days=7)

if __name__ == '__main__':
    main()
*/
