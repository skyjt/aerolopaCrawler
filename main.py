#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AeroLOPA网站爬虫程序
用于爬取航司机型座位图
"""

import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
import logging
from tqdm import tqdm
from retrying import retry
from PIL import Image
import json
import csv
from airlines_config import get_airline_info, get_all_airlines, get_supported_iata_codes

# 确保logs目录存在
Path('logs').mkdir(exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AerolopaCrawler:
    def __init__(self):
        self.base_url = "https://www.aerolopa.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 从配置文件获取航司信息
        self.airlines = get_supported_iata_codes()
        self.airline_names = get_all_airlines()
        
        # CSV文件路径
        self.csv_file = Path("aircraft_data.csv")
        self.init_csv_file()
    
    def init_csv_file(self):
        """初始化CSV文件，写入表头"""
        if not self.csv_file.exists():
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['航司中文', '航司英文', '航司英文代码', '机型名称', '图片路径'])
            logger.info(f"创建CSV文件: {self.csv_file}")
    
    def record_aircraft_data(self, airline_code, aircraft_type, image_path):
        """记录飞机数据到CSV文件"""
        try:
            airline_info = get_airline_info(airline_code)
            
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    airline_info['chinese'],
                    airline_info['english'],
                    airline_code.upper(),
                    aircraft_type,
                    str(image_path)
                ])
            logger.info(f"记录数据到CSV: {airline_code.upper()} - {aircraft_type}")
        except Exception as e:
            logger.error(f"记录CSV数据失败: {e}")
    
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def fetch_page(self, url):
        """获取网页内容，带重试机制"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"获取页面失败: {url}, 错误: {e}")
            raise
    
    def parse_airline_page(self, airline_code):
        """解析航司页面，获取机型详细页面链接"""
        url = f"{self.base_url}/{airline_code}"
        
        try:
            response = self.fetch_page(url)
            if not response:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找所有包含机型图片的链接
            aircraft_links = []
            images = soup.find_all('img')
            
            for img in images:
                src = img.get('src', '')
                
                # 找到Gallery_开头的机型图片
                if (src and 
                    'creatorcdn.com' in src and 
                    'Gallery_' in src and
                    not 'logo' in src.lower()):
                    
                    # 获取父级<a>标签的href
                    parent_link = img.find_parent('a')
                    if parent_link and parent_link.get('href'):
                        detail_url = parent_link.get('href')
                        
                        # 确保是完整URL
                        if detail_url.startswith('/'):
                            detail_url = self.base_url + detail_url
                        elif not detail_url.startswith('http'):
                            detail_url = f"{self.base_url}/{detail_url}"
                        
                        # 从URL提取机型信息
                        aircraft_type = detail_url.split('/')[-1]  # 如 'ca-332-2'
                        
                        aircraft_links.append({
                            'detail_url': detail_url,
                            'aircraft_type': aircraft_type,
                            'thumbnail_src': src
                        })
            
            logger.info(f"从 {airline_code.upper()} 页面找到 {len(aircraft_links)} 个机型详细页面")
            return aircraft_links
            
        except Exception as e:
            logger.error(f"解析 {airline_code} 页面失败: {e}")
            return []
    
    def parse_aircraft_detail_page(self, detail_url, aircraft_type):
        """解析机型详细页面，获取高分辨率座位图"""
        try:
            response = requests.get(detail_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找座位图（通常是尺寸较大的图片）
            images = soup.find_all('img')
            
            for img in images:
                src = img.get('src', '')
                width = img.get('width')
                height = img.get('height')
                
                # 查找高分辨率座位图（通常有lazyload类且尺寸较大）
                if (src and 
                    'creatorcdn.com' in src and
                    not 'logo' in src.lower() and
                    'lazyload' in img.get('class', [])):
                    
                    # 构建完整URL并移除尺寸限制以获取原始高分辨率图片
                    if src.startswith('//'):
                        full_url = 'https:' + src
                    elif src.startswith('/'):
                        full_url = self.base_url + src
                    else:
                        full_url = src
                    
                    # 检查是否有srcset属性，优先使用最高分辨率版本
                    srcset = img.get('data-srcset') or img.get('srcset')
                    if srcset:
                        # 解析srcset，找到最高分辨率的图片
                        import re
                        srcset_entries = []
                        # 先替换&amp;为&，然后按逗号分割
                        srcset_clean = srcset.replace('&amp;', '&')
                        entries = re.split(r',\s*(?=https://)', srcset_clean)  # 按逗号分割，但保留完整URL
                        
                        for entry in entries:
                            entry = entry.strip()
                            if 'w' in entry and 'h' in entry:
                                # 提取宽度信息
                                width_match = re.search(r'(\d+)w', entry)
                                if width_match:
                                    width = int(width_match.group(1))
                                    # 提取URL - 在第一个空格之前的部分
                                    parts = entry.split(' ')
                                    if len(parts) > 0:
                                        url = parts[0]
                                        srcset_entries.append((width, url))
                        
                        if srcset_entries:
                            # 选择最高分辨率的图片
                            highest_res = max(srcset_entries, key=lambda x: x[0])
                            full_url = highest_res[1]
                            logger.info(f"使用srcset中的最高分辨率图片: {highest_res[0]}w")
                        else:
                            logger.info(f"使用原始图片URL: {full_url}")
                    else:
                        # 修改URL以获取真正的高分辨率图片
                        # URL格式: .../0,0,800,3750,800,300/0-0-0/...
                        # 参数含义: /x,y,width,height,output_width,output_height/
                        # 需要将输出尺寸改为与源尺寸相同以获取原始分辨率
                        pattern = r'/(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)/'
                        match = re.search(pattern, full_url)
                        if match:
                            x, y, src_width, src_height, out_width, out_height = match.groups()
                            # 将输出尺寸设置为源尺寸以获取原始分辨率
                            new_params = f"/{x},{y},{src_width},{src_height},{src_width},{src_height}/"
                            full_url = re.sub(pattern, new_params, full_url)
                            logger.info(f"修改URL以获取原始分辨率: {src_width}x{src_height}")
                        else:
                            logger.warning(f"URL不包含尺寸参数，可能不是高分辨率: {full_url}")
                    
                    # 从URL提取文件名
                    import re
                    filename_match = re.search(r'/([^/]+\.png)', src)
                    if filename_match:
                        filename = filename_match.group(1)
                    else:
                        filename = f"{aircraft_type}.png"
                    
                    return {
                        'url': full_url,
                        'aircraft_type': aircraft_type,
                        'filename': filename,
                        'width': width,
                        'height': height
                    }
            
            logger.warning(f"在详细页面 {detail_url} 中未找到座位图")
            return None
            
        except Exception as e:
            logger.error(f"解析详细页面 {detail_url} 失败: {e}")
            return None
    
    def normalize_aircraft_name(self, name):
        """标准化机型名称"""
        name = name.upper()
        
        # 标准化映射
        mappings = {
            '319': 'A319',
            '320': 'A320', 
            '321': 'A321',
            '330': 'A330',
            '350': 'A350',
            '380': 'A380',
            '737': 'B737',
            '747': 'B747',
            '757': 'B757',
            '767': 'B767',
            '777': 'B777',
            '787': 'B787'
        }
        
        # 检查是否需要标准化
        for key, value in mappings.items():
            if name.startswith(key):
                return name.replace(key, value, 1)
        
        return name
    
    def extract_aircraft_type(self, alt_text, src_url):
        """从alt文本或URL中提取机型名称（保留兼容性）"""
        # 常见机型代码
        aircraft_types = [
            'A319', 'A320', 'A321', 'A330', 'A340', 'A350', 'A380',
            'B737', 'B747', 'B757', 'B767', 'B777', 'B787',
            '737', '747', '757', '767', '777', '787',
            'CRJ', 'ERJ', 'E190', 'DHC', 'ATR'
        ]
        
        text_to_check = f"{alt_text} {src_url}".upper()
        
        for aircraft_type in aircraft_types:
            if aircraft_type in text_to_check:
                return aircraft_type
        
        # 如果没有找到，使用文件名
        filename = os.path.basename(urlparse(src_url).path)
        return os.path.splitext(filename)[0]
    
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def download_image(self, image_url, save_path):
        """下载图片"""
        try:
            response = self.session.get(image_url, timeout=30)
            response.raise_for_status()
            
            # 创建目录
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存图片
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"图片下载成功: {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"图片下载失败: {image_url}, 错误: {e}")
            return False
    
    def get_image_extension(self, url, content_type=None):
        """获取图片扩展名"""
        if content_type:
            if 'jpeg' in content_type or 'jpg' in content_type:
                return '.jpg'
            elif 'png' in content_type:
                return '.png'
            elif 'gif' in content_type:
                return '.gif'
            elif 'webp' in content_type:
                return '.webp'
        
        # 从URL获取扩展名
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        if path.endswith(('.jpg', '.jpeg')):
            return '.jpg'
        elif path.endswith('.png'):
            return '.png'
        elif path.endswith('.gif'):
            return '.gif'
        elif path.endswith('.webp'):
            return '.webp'
        else:
            return '.jpg'  # 默认使用jpg
    
    def crawl_airline(self, airline_code):
        """爬取指定航司的座位图"""
        logger.info(f"开始爬取航司: {airline_code.upper()}")
        
        # 解析航司页面，获取机型详细页面链接
        aircraft_links = self.parse_airline_page(airline_code)
        
        if not aircraft_links:
            logger.warning(f"航司 {airline_code} 没有找到机型页面")
            return 0
        
        # 创建航司目录
        airline_dir = self.data_dir / airline_code.upper()
        airline_dir.mkdir(exist_ok=True)
        
        downloaded_count = 0
        
        # 访问每个机型详细页面并下载座位图
        for link_info in tqdm(aircraft_links, desc=f"处理 {airline_code.upper()} 机型"):
            try:
                logger.info(f"正在处理机型: {link_info['aircraft_type']}")
                
                # 解析机型详细页面
                seat_map = self.parse_aircraft_detail_page(
                    link_info['detail_url'], 
                    link_info['aircraft_type']
                )
                
                if seat_map:
                    # 获取图片扩展名
                    ext = self.get_image_extension(seat_map['url'])
                    
                    # 构建保存路径
                    filename = f"{seat_map['aircraft_type']}{ext}"
                    save_path = airline_dir / filename
                    
                    # 检查文件是否已存在且为有效的高分辨率图片
                    if save_path.exists():
                        file_size = save_path.stat().st_size
                        # 如果文件大小小于50KB，认为可能是低分辨率图片，需要重新下载
                        if file_size < 50 * 1024:  # 50KB
                            logger.info(f"文件存在但可能是低分辨率({file_size} bytes)，重新下载: {save_path}")
                        else:
                            logger.info(f"高分辨率文件已存在({file_size} bytes)，跳过: {save_path}")
                            continue
                    
                    # 下载图片
                    logger.info(f"下载座位图: {seat_map['url']}")
                    if seat_map.get('width') and seat_map.get('height'):
                        logger.info(f"图片尺寸: {seat_map['width']}x{seat_map['height']}")
                    
                    if self.download_image(seat_map['url'], save_path):
                        downloaded_count += 1
                        # 记录数据到CSV文件
                        self.record_aircraft_data(airline_code, seat_map['aircraft_type'], save_path)
                else:
                    logger.warning(f"机型 {link_info['aircraft_type']} 未找到座位图")
                
                # 添加延迟
                time.sleep(0.5)
                    
            except Exception as e:
                logger.error(f"处理机型失败: {link_info}, 错误: {e}")
                continue
        
        logger.info(f"航司 {airline_code.upper()} 完成，下载了 {downloaded_count} 张座位图")
        return downloaded_count
    
    def crawl_airline_seatmaps(self, airline_code, aircraft_model=None):
        """爬取指定航司和机型的座位图（API兼容方法）
        
        Args:
            airline_code (str): 航司IATA代码
            aircraft_model (str, optional): 机型名称，如果为None则爬取该航司所有机型
            
        Returns:
            list: 包含座位图信息的列表
        """
        logger.info(f"开始爬取航司座位图: {airline_code.upper()}")
        
        # 解析航司页面，获取机型详细页面链接
        aircraft_links = self.parse_airline_page(airline_code)
        
        if not aircraft_links:
            logger.warning(f"航司 {airline_code} 没有找到机型页面")
            return []
        
        # 如果指定了机型，过滤结果
        if aircraft_model:
            aircraft_model_normalized = aircraft_model.upper().replace(' ', '').replace('-', '')
            filtered_links = []
            for link in aircraft_links:
                link_model = link['aircraft_type'].upper().replace(' ', '').replace('-', '')
                if aircraft_model_normalized in link_model or link_model in aircraft_model_normalized:
                    filtered_links.append(link)
            aircraft_links = filtered_links
        
        results = []
        
        # 处理每个机型
        for link_info in aircraft_links:
            try:
                logger.info(f"正在处理机型: {link_info['aircraft_type']}")
                
                # 解析机型详细页面
                seat_map = self.parse_aircraft_detail_page(
                    link_info['detail_url'], 
                    link_info['aircraft_type']
                )
                
                if seat_map:
                    results.append({
                        'airline_code': airline_code.upper(),
                        'aircraft_type': seat_map['aircraft_type'],
                        'image_url': seat_map['url'],
                        'filename': seat_map['filename'],
                        'width': seat_map.get('width'),
                        'height': seat_map.get('height'),
                        'detail_url': link_info['detail_url']
                    })
                
                # 添加延迟
                time.sleep(0.5)
                    
            except Exception as e:
                logger.error(f"处理机型失败: {link_info}, 错误: {e}")
                continue
        
        logger.info(f"航司 {airline_code.upper()} 找到 {len(results)} 个座位图")
        return results
    
    def crawl_all_airlines(self):
        """爬取所有航司的机型图片"""
        logger.info("开始爬取AeroLOPA网站")
        
        total_downloaded = 0
        
        for airline_code in tqdm(self.airlines, desc="处理航司"):
            downloaded_count = self.crawl_airline(airline_code)
            total_downloaded += downloaded_count
        
        logger.info(f"爬取完成！总共下载了 {total_downloaded} 张图片")
        return total_downloaded

def main():
    """主函数"""
    import sys
    
    crawler = AerolopaCrawler()
    
    try:
        # 检查命令行参数
        if len(sys.argv) > 1:
            # 爬取指定航司
            airline_code = sys.argv[1].lower()
            if airline_code in crawler.airlines:
                downloaded_count = crawler.crawl_airline(airline_code)
                print(f"\n爬取完成！航司 {airline_code.upper()} 下载了 {downloaded_count} 张图片")
                print(f"图片保存在 {crawler.data_dir.absolute() / airline_code.upper()} 目录下")
            else:
                print(f"不支持的航司代码: {airline_code}")
                print(f"支持的航司代码: {', '.join(crawler.airlines)}")
        else:
            # 爬取所有航司
            total_downloaded = crawler.crawl_all_airlines()
            print(f"\n爬取完成！总共下载了 {total_downloaded} 张图片")
            print(f"图片保存在 {crawler.data_dir.absolute()} 目录下")
        
    except KeyboardInterrupt:
        logger.info("用户中断程序")
        print("\n程序被用户中断")
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        print(f"\n程序执行出错: {e}")

if __name__ == "__main__":
    main()