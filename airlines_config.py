# -*- coding: utf-8 -*-
"""
AeroLOPA航司配置文件
包含所有支持的航司IATA代码、中文名称和英文名称映射

数据来源：https://www.aerolopa.com/
更新时间：2025年1月
"""

# 航司映射字典
# 格式：'IATA代码': {'chinese': '中文名称', 'english': '英文名称'}
AIRLINES = {
    # A
    'a3': {'chinese': '爱琴海航空', 'english': 'Aegean Airlines'},
    'ei': {'chinese': '爱尔兰航空', 'english': 'Aer Lingus'},
    'xz': {'chinese': '意大利航空', 'english': 'Aeroitalia'},
    'ar': {'chinese': '阿根廷航空', 'english': 'Aerolíneas Argentinas'},
    'am': {'chinese': '墨西哥航空', 'english': 'Aeroméxico'},
    'ah': {'chinese': '阿尔及利亚航空', 'english': 'Air Algérie'},
    'g9': {'chinese': '阿拉伯航空', 'english': 'Air Arabia'},
    'ak': {'chinese': '亚洲航空', 'english': 'AirAsia'},
    'kc': {'chinese': '阿斯塔纳航空', 'english': 'Air Astana'},
    'uu': {'chinese': '南方航空', 'english': 'Air Austral'},
    'bt': {'chinese': '波罗的海航空', 'english': 'airBaltic'},
    'bx': {'chinese': '釜山航空', 'english': 'Air Busan'},
    'ac': {'chinese': '加拿大航空', 'english': 'Air Canada'},
    'tx': {'chinese': '加勒比海航空', 'english': 'Air Caraïbes'},
    'ca': {'chinese': '中国国际航空', 'english': 'Air China'},
    'en': {'chinese': '多洛米蒂航空', 'english': 'Air Dolomiti'},
    'ux': {'chinese': '欧洲航空', 'english': 'Air Europa'},
    'af': {'chinese': '法国航空', 'english': 'Air France'},
    'ai': {'chinese': '印度航空', 'english': 'Air India'},
    'nq': {'chinese': '日本航空', 'english': 'Air Japan'},
    '4z': {'chinese': '航联航空', 'english': 'Airlink'},
    'nx': {'chinese': '澳门航空', 'english': 'Air Macau'},
    'mk': {'chinese': '毛里求斯航空', 'english': 'Air Mauritius'},
    'nz': {'chinese': '新西兰航空', 'english': 'Air New Zealand'},
    'yp': {'chinese': '高丽航空', 'english': 'Air Premia'},
    'rs': {'chinese': '首尔航空', 'english': 'Air Seoul'},
    'ju': {'chinese': '塞尔维亚航空', 'english': 'Air Serbia'},
    'tn': {'chinese': '大溪地航空', 'english': 'Air Tahiti Nui'},
    'ts': {'chinese': '越洋航空', 'english': 'Air Transat'},
    'vf': {'chinese': 'AJet航空', 'english': 'AJet'},
    'as': {'chinese': '阿拉斯加航空', 'english': 'Alaska Airlines'},
    'g4': {'chinese': '忠实航空', 'english': 'Allegiant'},
    'aa': {'chinese': '美国航空', 'english': 'American Airlines'},
    'nh': {'chinese': '全日空', 'english': 'All Nippon Airways'},
    'dv': {'chinese': 'Arajet航空', 'english': 'Arajet'},
    'oz': {'chinese': '韩亚航空', 'english': 'Asiana Airlines'},
    'gv': {'chinese': '奥里尼航空', 'english': 'Aurigny'},
    'os': {'chinese': '奥地利航空', 'english': 'Austrian Airlines'},
    'av': {'chinese': '哥伦比亚航空', 'english': 'Avianca'},
    'j2': {'chinese': '阿塞拜疆航空', 'english': 'Azerbaijan Airlines'},
    's4': {'chinese': '亚速尔航空', 'english': 'Azores Airlines'},
    'ad': {'chinese': '蓝色巴西航空', 'english': 'Azul'},
    
    # B
    'pg': {'chinese': '曼谷航空', 'english': 'Bangkok Airways'},
    'id': {'chinese': '巴迪克航空', 'english': 'Batik Air'},
    'b4': {'chinese': 'BeOnd航空', 'english': 'BeOnd'},
    'bg': {'chinese': '孟加拉航空', 'english': 'Biman Bangladesh Airlines'},
    'nt': {'chinese': '加那利航空', 'english': 'Binter Canarias'},
    'si': {'chinese': '蓝岛航空', 'english': 'Blue Islands'},
    'oa': {'chinese': '玻利维亚航空', 'english': 'Boliviana de Aviación'},
    'mz': {'chinese': '微风航空', 'english': 'Breeze Airways'},
    'ba': {'chinese': '英国航空', 'english': 'British Airways'},
    'sn': {'chinese': '布鲁塞尔航空', 'english': 'Brussels Airlines'},
    
    # C
    'cx': {'chinese': '国泰航空', 'english': 'Cathay Pacific'},
    'ci': {'chinese': '中华航空', 'english': 'China Airlines'},
    'mu': {'chinese': '中国东方航空', 'english': 'China Eastern Airlines'},
    'cz': {'chinese': '中国南方航空', 'english': 'China Southern Airlines'},
    'cp': {'chinese': '康多尔航空', 'english': 'Condor'},
    'cm': {'chinese': '巴拿马航空', 'english': 'Copa Airlines'},
    'co': {'chinese': '大陆航空', 'english': 'Continental Airlines'},
    
    # D
    'dl': {'chinese': '达美航空', 'english': 'Delta Air Lines'},
    
    # E
    'ey': {'chinese': '阿提哈德航空', 'english': 'Etihad Airways'},
    'ek': {'chinese': '阿联酋航空', 'english': 'Emirates'},
    'et': {'chinese': '埃塞俄比亚航空', 'english': 'Ethiopian Airlines'},
    'ew': {'chinese': '欧洲之翼', 'english': 'Eurowings'},
    'br': {'chinese': '长荣航空', 'english': 'EVA Air'},
    
    # F
    'ay': {'chinese': '芬兰航空', 'english': 'Finnair'},
    'be': {'chinese': 'FlyBe航空', 'english': 'Flybe'},
    'f9': {'chinese': '边疆航空', 'english': 'Frontier Airlines'},
    
    # G
    'ga': {'chinese': '印尼鹰航', 'english': 'Garuda Indonesia'},
    'de': {'chinese': '神鹰航空', 'english': 'Condor'},
    
    # H
    'ha': {'chinese': '夏威夷航空', 'english': 'Hawaiian Airlines'},
    'hu': {'chinese': '海南航空', 'english': 'Hainan Airlines'},
    'hx': {'chinese': '香港航空', 'english': 'Hong Kong Airlines'},
    
    # I
    'ib': {'chinese': '伊比利亚航空', 'english': 'Iberia'},
    'fi': {'chinese': '冰岛航空', 'english': 'Icelandair'},
    'in': {'chinese': '印度航空快运', 'english': 'IndiGo'},
    'ir': {'chinese': '伊朗航空', 'english': 'Iran Air'},
    
    # J
    'jl': {'chinese': '日本航空', 'english': 'Japan Airlines'},
    'gk': {'chinese': '捷星航空', 'english': 'Jetstar Airways'},
    'b6': {'chinese': '捷蓝航空', 'english': 'JetBlue Airways'},
    
    # K
    'kl': {'chinese': '荷兰皇家航空', 'english': 'KLM'},
    'ke': {'chinese': '肯尼亚航空', 'english': 'Kenya Airways'},
    'ka': {'chinese': '大韩航空', 'english': 'Korean Air'},
    'ku': {'chinese': '科威特航空', 'english': 'Kuwait Airways'},
    
    # L
    'la': {'chinese': '智利南美航空', 'english': 'LATAM Airlines'},
    'lh': {'chinese': '汉莎航空', 'english': 'Lufthansa'},
    
    # M
    'mh': {'chinese': '马来西亚航空', 'english': 'Malaysia Airlines'},
    'me': {'chinese': '中东航空', 'english': 'Middle East Airlines'},
    'ms': {'chinese': '埃及航空', 'english': 'EgyptAir'},
    
    # N
    'dy': {'chinese': '挪威航空', 'english': 'Norwegian Air'},
    
    # O
    'om': {'chinese': '蒙古航空', 'english': 'MIAT Mongolian Airlines'},
    
    # P
    'pr': {'chinese': '菲律宾航空', 'english': 'Philippine Airlines'},
    'pk': {'chinese': '巴基斯坦国际航空', 'english': 'Pakistan International Airlines'},
    
    # Q
    'qr': {'chinese': '卡塔尔航空', 'english': 'Qatar Airways'},
    'qf': {'chinese': '澳洲航空', 'english': 'Qantas'},
    
    # R
    'fr': {'chinese': '瑞安航空', 'english': 'Ryanair'},
    'ro': {'chinese': '罗马尼亚航空', 'english': 'TAROM'},
    'su': {'chinese': '俄罗斯航空', 'english': 'Aeroflot'},
    
    # S
    'sk': {'chinese': '北欧航空', 'english': 'SAS'},
    'sv': {'chinese': '沙特航空', 'english': 'Saudia'},
    'tr': {'chinese': '酷航', 'english': 'Scoot'},
    'fm': {'chinese': '上海航空', 'english': 'Shanghai Airlines'},
    'zh': {'chinese': '深圳航空', 'english': 'Shenzhen Airlines'},
    '3u': {'chinese': '四川航空', 'english': 'Sichuan Airlines'},
    'sq': {'chinese': '新加坡航空', 'english': 'Singapore Airlines'},
    'bc': {'chinese': '天马航空', 'english': 'Skymark Airlines'},
    'qs': {'chinese': '智能翼航空', 'english': 'Smartwings'},
    'sa': {'chinese': '南非航空', 'english': 'South African Airways'},
    'wn': {'chinese': '西南航空', 'english': 'Southwest Airlines'},
    'nk': {'chinese': '精神航空', 'english': 'Spirit Airlines'},
    '9c': {'chinese': '春秋航空', 'english': 'Spring Airlines'},
    'ul': {'chinese': '斯里兰卡航空', 'english': 'SriLankan Airlines'},
    '7g': {'chinese': '星悦航空', 'english': 'StarFlyer'},
    'jx': {'chinese': '星宇航空', 'english': 'Starlux Airlines'},
    'sy': {'chinese': '太阳城航空', 'english': 'Sun Country Airlines'},
    'xq': {'chinese': '太阳快运', 'english': 'SunExpress'},
    'lx': {'chinese': '瑞士国际航空', 'english': 'Swiss International Air Lines'},
    
    # T
    'tg': {'chinese': '泰国国际航空', 'english': 'Thai Airways'},
    'tk': {'chinese': '土耳其航空', 'english': 'Turkish Airlines'},
    'tp': {'chinese': '葡萄牙航空', 'english': 'TAP Air Portugal'},
    'tu': {'chinese': '突尼斯航空', 'english': 'Tunisair'},
    
    # U
    'ua': {'chinese': '美国联合航空', 'english': 'United Airlines'},
    'ps': {'chinese': '乌克兰国际航空', 'english': 'Ukraine International Airlines'},
    
    # V
    'vs': {'chinese': '维珍航空', 'english': 'Virgin Atlantic'},
    'va': {'chinese': '维珍澳洲航空', 'english': 'Virgin Australia'},
    'vn': {'chinese': '越南航空', 'english': 'Vietnam Airlines'},
    'vj': {'chinese': '越捷航空', 'english': 'VietJet Air'},
    'vu': {'chinese': '瓦努阿图航空', 'english': 'Air Vanuatu'},
    
    # W
    'ws': {'chinese': '西捷航空', 'english': 'WestJet'},
    'wy': {'chinese': '阿曼航空', 'english': 'Oman Air'},
    
    # X
    'xj': {'chinese': '泰国亚洲航空', 'english': 'Thai AirAsia X'},
    
    # Y
    'yn': {'chinese': '也门航空', 'english': 'Yemenia'},
    
    # Z
    'zb': {'chinese': '君主航空', 'english': 'Monarch Airlines'},
}

# 获取航司信息的辅助函数
def get_airline_info(iata_code):
    """
    根据IATA代码获取航司信息
    
    Args:
        iata_code (str): 航司IATA代码
        
    Returns:
        dict: 包含中文名和英文名的字典，如果未找到则返回默认值
    """
    return AIRLINES.get(iata_code.lower(), {
        'chinese': f'未知航司({iata_code.upper()})',
        'english': f'Unknown Airline ({iata_code.upper()})'
    })

def get_all_airlines():
    """
    获取所有支持的航司列表
    
    Returns:
        dict: 完整的航司映射字典
    """
    return AIRLINES

def get_supported_iata_codes():
    """
    获取所有支持的IATA代码列表
    
    Returns:
        list: IATA代码列表
    """
    return list(AIRLINES.keys())