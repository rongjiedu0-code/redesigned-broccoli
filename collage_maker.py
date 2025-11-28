import os
import requests
import time
import random

# ==========================================
# 👇 配置区域
# ==========================================
KEYWORD = "nature"            # 关键词
TOTAL_IMAGES = 500            # 最多抓取 500 张
MAX_PAGES = 20                # 最多抓取 20 页
PER_PAGE = 24                 # 每页数量（Wallhaven API 默认最多 24）

# 自动获取桌面路径，将文件夹创建在桌面上，避免权限问题
def get_desktop_dir():
    # 兼容多平台，此方法适用于大多数 Windows
    return os.path.join(os.path.expanduser("~"), 'Desktop')

SAVE_DIR = os.path.join(get_desktop_dir(), "Wallpapers_Download")
# ==========================================

def download_wallpapers():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    print(f"🔍 开始批量下载壁纸，关键词: '{KEYWORD}'，保存目录: {SAVE_DIR}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    total_downloaded = 0
    file_index = 1
    for page in range(1, MAX_PAGES + 1):
        if total_downloaded >= TOTAL_IMAGES:
            break
        api_url = (
            f"https://wallhaven.cc/api/v1/search?"
            f"q={KEYWORD}&sorting=random&atleast=1920x1080"
            f"&page={page}&purity=100"
        )
        try:
            response = requests.get(api_url, headers=headers, timeout=15)
            data = response.json()
            image_list = data.get('data', [])
        except Exception as e:
            print(f"❌ 第 {page} 页 API 请求失败: {e}")
            # 即使失败，也 sleep 防止短时间大流量
            sleep_time = random.uniform(3, 5)
            time.sleep(sleep_time)
            continue

        for item in image_list:
            if total_downloaded >= TOTAL_IMAGES:
                break
            hd_url = item.get('path')
            if not hd_url:
                continue
            ext = hd_url.split('.')[-1].split('?')[0]  # 防止 url 带参数
            file_path = os.path.join(SAVE_DIR, f"wallpaper_{file_index}.{ext}")
            try:
                img_data = requests.get(hd_url, headers=headers, timeout=30).content
                with open(file_path, "wb") as f:
                    f.write(img_data)
                total_downloaded += 1
                print(f"正在下载第 {total_downloaded}/{TOTAL_IMAGES} 张: {hd_url.split('/')[-1]}")
                file_index += 1
            except Exception as e:
                print(f"   ⚠️ 下载失败: {e}")
                continue

        # 页内抓图结束，防止封号：随机等待 3~5 秒
        if total_downloaded < TOTAL_IMAGES:
            sleep_time = random.uniform(3, 5)
            print(f"第 {page} 页处理完，休眠 {sleep_time:.1f} 秒防止被封...")
            time.sleep(sleep_time)
    print(f"🎉 下载完成！共抓取 {total_downloaded} 张壁纸，目录: {SAVE_DIR}")

if __name__ == "__main__":
    download_wallpapers()


