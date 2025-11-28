import os
import requests
import time
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# --- 配置区域 ---
# 目标：Wallhaven 热门榜单 (动漫/风景)
API_URL = "https://wallhaven.cc/api/v1/search"
PARAMS = {
    "categories": "111", # General/Anime/People
    "purity": "100",     # SFW (安全模式)
    "sorting": "toplist",
    "order": "desc",
    "page": 1
}

# 伪装成浏览器
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 拼图设置
GRID_SIZE = 3   # 3x3
IMG_COUNT = GRID_SIZE * GRID_SIZE
TILE_SIZE = 400 # 单张小图尺寸
SPACING = 10    # 图片间距

# --- 核心逻辑 ---

def get_wallpapers():
    """获取壁纸链接"""
    print("🚀 正在连接 Wallhaven...")
    try:
        resp = requests.get(API_URL, params=PARAMS, headers=HEADERS, timeout=30)
        data = resp.json()
        if "data" not in data:
            print("❌ API 返回异常")
            return []
        
        img_urls = []
        for item in data["data"][:IMG_COUNT]:
            img_urls.append(item["path"])
        return img_urls
    except Exception as e:
        print(f"❌ 网络请求失败: {e}")
        return []

def create_collage(image_urls):
    """下载图片并制作拼图"""
    if not image_urls:
        return

    # 1. 准备画布
    canvas_w = TILE_SIZE * GRID_SIZE + SPACING * (GRID_SIZE - 1)
    canvas_h = canvas_w # 正方形
    # 创建一个白色底图
    canvas = Image.new('RGB', (canvas_w, canvas_h), (255, 255, 255))
    
    print(f"🎨 开始制作拼图，共 {len(image_urls)} 张...")

    for i, url in enumerate(image_urls):
        try:
            # 下载图片
            print(f"  ⬇️ 下载第 {i+1} 张: {url}")
            resp = requests.get(url, headers=HEADERS, timeout=20)
            img = Image.open(BytesIO(resp.content)).convert('RGB')
            
            # 裁剪成正方形
            img = resize_and_crop(img, TILE_SIZE)
            
            # 计算位置
            x = (i % GRID_SIZE) * (TILE_SIZE + SPACING)
            y = (i // GRID_SIZE) * (TILE_SIZE + SPACING)
            
            # 贴图
            canvas.paste(img, (x, y))
            
            # 礼貌休眠，防止封号
            time.sleep(1)
            
        except Exception as e:
            print(f"  ⚠️ 第 {i+1} 张处理失败: {e}")

    # 2. 添加标题栏 (半透明黑底 + 文字)
    draw = ImageDraw.Draw(canvas)
    
    # 绘制半透明黑色矩形
    bar_height = 80
    bar_y = (canvas_h - bar_height) // 2
    # 注意：PIL 需要 RGBA 模式才能画半透明，这里简单处理画实心黑条
    draw.rectangle([(0, bar_y), (canvas_w, bar_y + bar_height)], fill=(0, 0, 0))
    
    # 添加文字
    text = "Wallhaven Daily Top"
    try:
        # 尝试加载 GitHub 容器里的默认字体
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        # 如果找不到，就用 PIL 默认字体 (虽然丑点但能用)
        font = ImageFont.load_default()
    
    # 计算文字位置居中
    # (这里做个简化处理，直接大概居中，防止计算报错)
    draw.text((canvas_w//2 - 150, bar_y + 20), text, font=font, fill=(255, 255, 255))

    # 3. 保存结果
    # 确保文件夹存在
    save_dir = "daily_results"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 按日期命名
    date_str = time.strftime("%Y-%m-%d")
    save_path = f"{save_dir}/wallpaper_{date_str}.jpg"
    
    canvas.save(save_path, quality=95)
    print(f"✅ 拼图制作完成！已保存到: {save_path}")

def resize_and_crop(img, size):
    """把图片智能裁剪成正方形"""
    # 简单的缩放裁剪逻辑
    ratio = max(size / img.size[0], size / img.size[1])
    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
    img = img.resize(new_size, Image.LANCZOS)
    
    # 中心裁剪
    left = (img.size[0] - size) / 2
    top = (img.size[1] - size) / 2
    return img.crop((left, top, left + size, top + size))

if __name__ == "__main__":
    urls = get_wallpapers()
    create_collage(urls)
