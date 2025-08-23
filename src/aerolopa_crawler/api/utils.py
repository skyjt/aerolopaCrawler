"""API工具模块

提供图片处理、缓存管理等工具函数。
"""

import os
import io
import re
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

from PIL import Image, ImageOps


def standardize_aircraft_model(aircraft_model: str) -> str:
    """标准化机型名称

    Args:
        aircraft_model: 原始机型名称

    Returns:
        标准化后的机型名称
    """
    if not aircraft_model:
        return ""

    # 转换为大写并去除多余空格
    standardized = re.sub(r"\s+", " ", aircraft_model.upper().strip())

    # 标准化常见机型名称
    replacements = {
        "AIRBUS A": "A",
        "BOEING ": "B",
        "B737-": "B737",
        "B777-": "B777",
        "B787-": "B787",
        "A320-": "A320",
        "A330-": "A330",
        "A350-": "A350",
    }

    for old, new in replacements.items():
        standardized = standardized.replace(old, new)

    return standardized


def generate_cache_key(iata_code: str, filename: str, **kwargs) -> str:
    """生成缓存键

    Args:
        iata_code: 航空公司代码
        filename: 文件名
        **kwargs: 额外参数

    Returns:
        MD5哈希的缓存键
    """
    key_data = f"{iata_code}_{filename}"
    for k, v in sorted(kwargs.items()):
        key_data += f"_{k}_{v}"
    return hashlib.md5(key_data.encode()).hexdigest()


def optimize_image(
    image_path: str,
    quality: Optional[int] = None,
    max_size: Optional[Tuple[int, int]] = None,
    default_quality: int = 85,
) -> bytes:
    """优化图片：压缩和调整尺寸

    Args:
        image_path: 图片文件路径
        quality: 图片质量 (1-100)
        max_size: 最大尺寸 (width, height)
        default_quality: 默认质量

    Returns:
        优化后的图片数据
    """
    try:
        with Image.open(image_path) as img:
            # 转换为RGB模式（如果需要）
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(
                    img, mask=img.split()[-1] if img.mode == "RGBA" else None
                )
                img = background

            # 调整尺寸
            if max_size and (img.width > max_size[0] or img.height > max_size[1]):
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # 自动旋转
            img = ImageOps.exif_transpose(img)

            # 保存到内存
            output = io.BytesIO()
            img_format = "JPEG"
            save_kwargs = {
                "format": img_format,
                "quality": quality or default_quality,
                "optimize": True,
            }

            img.save(output, **save_kwargs)
            return output.getvalue()

    except Exception:
        # 如果优化失败，返回原始文件内容
        with open(image_path, "rb") as f:
            return f.read()


def get_cached_image(
    cache_dir: str, cache_key: str, cache_timeout: int
) -> Optional[bytes]:
    """从缓存获取图片

    Args:
        cache_dir: 缓存目录
        cache_key: 缓存键
        cache_timeout: 缓存超时时间（秒）

    Returns:
        缓存的图片数据，如果不存在或过期则返回None
    """
    try:
        cache_file = os.path.join(cache_dir, f"{cache_key}.jpg")
        if os.path.exists(cache_file):
            # 检查缓存是否过期
            cache_time = os.path.getmtime(cache_file)
            if datetime.now().timestamp() - cache_time < cache_timeout:
                with open(cache_file, "rb") as f:
                    return f.read()
            else:
                # 删除过期缓存
                os.remove(cache_file)
        return None
    except Exception:
        return None


def save_cached_image(cache_dir: str, cache_key: str, image_data: bytes) -> bool:
    """保存图片到缓存

    Args:
        cache_dir: 缓存目录
        cache_key: 缓存键
        image_data: 图片数据

    Returns:
        是否保存成功
    """
    try:
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, f"{cache_key}.jpg")
        with open(cache_file, "wb") as f:
            f.write(image_data)
        return True
    except Exception:
        return False


def check_local_seatmap_cache(
    data_dir: str, iata_code: str, aircraft_model: str, image_formats: List[str]
) -> List[Dict[str, Any]]:
    """检查本地座位图缓存

    Args:
        data_dir: 数据目录
        iata_code: 航空公司代码
        aircraft_model: 机型
        image_formats: 支持的图片格式

    Returns:
        匹配的图片信息列表
    """
    try:
        airline_dir = os.path.join(data_dir, iata_code)
        if not os.path.exists(airline_dir):
            return []

        images = []
        for filename in os.listdir(airline_dir):
            if any(filename.lower().endswith(ext) for ext in image_formats):
                # 检查文件名是否包含机型信息
                if is_aircraft_match(filename, aircraft_model):
                    file_path = os.path.join(airline_dir, filename)
                    file_stats = os.stat(file_path)

                    images.append(
                        {
                            "filename": filename,
                            "file_path": file_path,
                            "url": f"/api/v1/image/{iata_code}/{filename}",
                            "optimized_urls": {
                                "thumbnail": f"/api/v1/image/{iata_code}/{filename}?width=300&compress=true",
                                "medium": f"/api/v1/image/{iata_code}/{filename}?width=800&compress=true",
                                "high_quality": f"/api/v1/image/{iata_code}/{filename}?quality=95&compress=true",
                            },
                            "size": file_stats.st_size,
                            "modified_time": datetime.fromtimestamp(
                                file_stats.st_mtime
                            ).isoformat(),
                            "aircraft_match": True,
                        }
                    )

        return images
    except Exception:
        return []


def filter_aircraft_images(
    crawl_result: Dict, aircraft_model: str
) -> List[Dict[str, Any]]:
    """从爬取结果中过滤匹配的机型图片

    Args:
        crawl_result: 爬取结果
        aircraft_model: 机型

    Returns:
        匹配的图片信息列表
    """
    images = []

    try:
        # crawl_result 应该包含爬取到的图片信息
        if "images" in crawl_result:
            for img_info in crawl_result["images"]:
                if is_aircraft_match(img_info.get("filename", ""), aircraft_model):
                    images.append(
                        {
                            "filename": img_info.get("filename", ""),
                            "file_path": img_info.get("file_path", ""),
                            "url": img_info.get("url", ""),
                            "size": img_info.get("size", 0),
                            "modified_time": img_info.get("modified_time", ""),
                            "aircraft_match": True,
                            "source_url": img_info.get("source_url", ""),
                        }
                    )

        return images
    except Exception:
        return []


def is_aircraft_match(filename: str, aircraft_model: str) -> bool:
    """检查文件名是否匹配指定机型

    Args:
        filename: 文件名
        aircraft_model: 机型

    Returns:
        是否匹配
    """
    if not filename or not aircraft_model:
        return False

    # 将文件名和机型都转换为大写进行比较
    filename_upper = filename.upper()
    aircraft_upper = aircraft_model.upper()

    # 直接匹配
    if aircraft_upper in filename_upper:
        return True

    # 使用配置中的关键词进行匹配
    aircraft_keywords = [
        "A320",
        "A321",
        "A330",
        "A340",
        "A350",
        "A380",
        "B737",
        "B747",
        "B757",
        "B767",
        "B777",
        "B787",
        "E170",
        "E175",
        "E190",
        "E195",
        "CRJ",
        "ERJ",
        "ATR",
        "Q400",
    ]

    for keyword in aircraft_keywords:
        if keyword.upper() in aircraft_upper and keyword.upper() in filename_upper:
            return True

    # 提取数字部分进行匹配（如A320, B737等）
    aircraft_numbers = re.findall(r"\d+", aircraft_upper)
    filename_numbers = re.findall(r"\d+", filename_upper)

    if aircraft_numbers and filename_numbers:
        for num in aircraft_numbers:
            if num in filename_numbers:
                return True

    return False


def calculate_cache_stats(cache_dir: str) -> Dict[str, Any]:
    """计算缓存统计信息

    Args:
        cache_dir: 缓存目录

    Returns:
        缓存统计信息
    """
    cache_files = 0
    cache_size = 0

    try:
        if os.path.exists(cache_dir):
            for filename in os.listdir(cache_dir):
                file_path = os.path.join(cache_dir, filename)
                if os.path.isfile(file_path):
                    cache_files += 1
                    cache_size += os.path.getsize(file_path)
    except Exception:
        pass

    return {
        "files": cache_files,
        "size_bytes": cache_size,
        "size_mb": round(cache_size / 1024 / 1024, 2),
    }


def calculate_data_stats(data_dir: str) -> Dict[str, Any]:
    """计算数据目录统计信息

    Args:
        data_dir: 数据目录

    Returns:
        数据统计信息
    """
    data_files = 0
    data_size = 0

    try:
        if os.path.exists(data_dir):
            for root, dirs, files in os.walk(data_dir):
                if ".cache" in root:  # 跳过缓存目录
                    continue
                for file in files:
                    if any(
                        file.lower().endswith(ext)
                        for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]
                    ):
                        file_path = os.path.join(root, file)
                        data_files += 1
                        data_size += os.path.getsize(file_path)
    except Exception:
        pass

    return {
        "files": data_files,
        "size_bytes": data_size,
        "size_mb": round(data_size / 1024 / 1024, 2),
    }


def clear_cache_directory(cache_dir: str) -> int:
    """清理缓存目录

    Args:
        cache_dir: 缓存目录

    Returns:
        清理的文件数量
    """
    cleared_files = 0

    try:
        if os.path.exists(cache_dir):
            for filename in os.listdir(cache_dir):
                file_path = os.path.join(cache_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    cleared_files += 1
    except Exception:
        pass

    return cleared_files
