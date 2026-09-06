"""
輔助腳本：新聞圖片下載與智慧等比例裁切為 516x292 (約 16:9 比例)
使用方式：python scripts/crop_news_images.py
"""

import os
import urllib.request
from PIL import Image

def download_and_crop(url, out_path, target_w=516, target_h=292):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    temp_path = out_path + ".temp"
    try:
        with urllib.request.urlopen(req) as resp, open(temp_path, 'wb') as f:
            f.write(resp.read())
        
        with Image.open(temp_path) as img:
            img = img.convert("RGB")
            w, h = img.size
            target_ratio = target_w / target_h
            current_ratio = w / h
            
            if current_ratio > target_ratio:
                # 裁切寬度兩側
                new_w = int(h * target_ratio)
                left = (w - new_w) // 2
                box = (left, 0, left + new_w, h)
            else:
                # 裁切高度上下
                new_h = int(w / target_ratio)
                top = (h - new_h) // 2
                box = (0, top, w, top + new_h)
                
            cropped = img.crop(box)
            resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
            resized.save(out_path, "JPEG", quality=95)
            print(f"[成功] 圖片已裁切輸出至: {out_path}，尺寸為: {resized.size}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    print("圖片裁切工具模組已就緒。")
