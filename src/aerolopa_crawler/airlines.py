"""Airlines configuration and management.

Centralized management of supported airlines with IATA codes,
Chinese and English names, and utility functions.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple


# Airlines configuration with IATA code, Chinese name, and English name
AIRLINES: Dict[str, Tuple[str, str]] = {
    # A
    "3K": ("捷星亚洲航空", "Jetstar Asia Airways"),
    "9W": ("捷特航空", "Jet Airways"),
    "AA": ("美国航空", "American Airlines"),
    "AB": ("柏林航空", "Air Berlin"),
    "AC": ("加拿大航空", "Air Canada"),
    "AD": ("蓝翼航空", "Azul Brazilian Airlines"),
    "AF": ("法国航空", "Air France"),
    "AI": ("印度航空", "Air India"),
    "AK": ("亚洲航空", "AirAsia"),
    "AM": ("墨西哥国际航空", "Aeromexico"),
    "AR": ("阿根廷航空", "Aerolineas Argentinas"),
    "AS": ("阿拉斯加航空", "Alaska Airlines"),
    "AT": ("摩洛哥皇家航空", "Royal Air Maroc"),
    "AV": ("哥伦比亚航空", "Avianca"),
    "AY": ("芬兰航空", "Finnair"),
    "AZ": ("意大利航空", "Alitalia"),
    
    # B
    "BA": ("英国航空", "British Airways"),
    "BI": ("文莱皇家航空", "Royal Brunei Airlines"),
    "BL": ("捷星太平洋航空", "Jetstar Pacific Airlines"),
    "BR": ("长荣航空", "EVA Air"),
    "BX": ("釜山航空", "Air Busan"),
    
    # C
    "CA": ("中国国际航空", "Air China"),
    "CI": ("中华航空", "China Airlines"),
    "CK": ("中国货运航空", "China Cargo Airlines"),
    "CM": ("巴拿马航空", "Copa Airlines"),
    "CX": ("国泰航空", "Cathay Pacific"),
    "CZ": ("中国南方航空", "China Southern Airlines"),
    
    # D
    "D7": ("亚洲航空X", "AirAsia X"),
    "DL": ("达美航空", "Delta Air Lines"),
    "DY": ("挪威航空", "Norwegian Air Shuttle"),
    
    # E
    "EI": ("爱尔兰航空", "Aer Lingus"),
    "EK": ("阿联酋航空", "Emirates"),
    "ET": ("埃塞俄比亚航空", "Ethiopian Airlines"),
    "EY": ("阿提哈德航空", "Etihad Airways"),
    
    # F
    "FD": ("亚洲航空", "Thai AirAsia"),
    "FI": ("冰岛航空", "Icelandair"),
    "FM": ("上海航空", "Shanghai Airlines"),
    "FR": ("瑞安航空", "Ryanair"),
    
    # G
    "GA": ("印尼鹰航", "Garuda Indonesia"),
    "GF": ("海湾航空", "Gulf Air"),
    "GS": ("天津航空", "Tianjin Airlines"),
    
    # H
    "HO": ("吉祥航空", "Juneyao Airlines"),
    "HU": ("海南航空", "Hainan Airlines"),
    "HX": ("香港航空", "Hong Kong Airlines"),
    
    # I
    "IB": ("西班牙国家航空", "Iberia"),
    "IT": ("台湾虎航", "Tigerair Taiwan"),
    
    # J
    "JD": ("首都航空", "Beijing Capital Airlines"),
    "JJ": ("巴西天马航空", "TAM Airlines"),
    "JL": ("日本航空", "Japan Airlines"),
    "JQ": ("捷星航空", "Jetstar Airways"),
    "JX": ("星悦航空", "Starlux Airlines"),
    
    # K
    "KA": ("港龙航空", "Dragonair"),
    "KE": ("大韩航空", "Korean Air"),
    "KL": ("荷兰皇家航空", "KLM Royal Dutch Airlines"),
    "KQ": ("肯尼亚航空", "Kenya Airways"),
    
    # L
    "LA": ("南美航空", "LATAM Airlines"),
    "LH": ("汉莎航空", "Lufthansa"),
    "LO": ("波兰航空", "LOT Polish Airlines"),
    "LX": ("瑞士国际航空", "Swiss International Air Lines"),
    
    # M
    "MF": ("厦门航空", "Xiamen Airlines"),
    "MH": ("马来西亚航空", "Malaysia Airlines"),
    "MS": ("埃及航空", "EgyptAir"),
    "MU": ("中国东方航空", "China Eastern Airlines"),
    
    # N
    "NH": ("全日空航空", "All Nippon Airways"),
    "NX": ("澳门航空", "Air Macau"),
    "NZ": ("新西兰航空", "Air New Zealand"),
    
    # O
    "OD": ("马来西亚马印航空", "Malindo Air"),
    "OK": ("捷克航空", "Czech Airlines"),
    "OM": ("蒙古民用航空", "MIAT Mongolian Airlines"),
    "OS": ("奥地利航空", "Austrian Airlines"),
    "OZ": ("韩亚航空", "Asiana Airlines"),
    
    # P
    "PG": ("曼谷航空", "Bangkok Airways"),
    "PR": ("菲律宾航空", "Philippine Airlines"),
    "PX": ("新几内亚航空", "Air Niugini"),
    
    # Q
    "QF": ("澳洲航空", "Qantas"),
    "QR": ("卡塔尔航空", "Qatar Airways"),
    
    # R
    "RJ": ("约旦皇家航空", "Royal Jordanian"),
    "RO": ("罗马尼亚航空", "TAROM"),
    
    # S
    "SA": ("南非航空", "South African Airways"),
    "SJ": ("山东航空", "Shandong Airlines"),
    "SK": ("北欧航空", "Scandinavian Airlines"),
    "SN": ("布鲁塞尔航空", "Brussels Airlines"),
    "SQ": ("新加坡航空", "Singapore Airlines"),
    "SU": ("俄罗斯航空", "Aeroflot"),
    "SV": ("沙特阿拉伯航空", "Saudi Arabian Airlines"),
    
    # T
    "TG": ("泰国国际航空", "Thai Airways International"),
    "TK": ("土耳其航空", "Turkish Airlines"),
    "TP": ("葡萄牙航空", "TAP Air Portugal"),
    "TR": ("酷航", "Scoot"),
    "TZ": ("胜安航空", "SilkAir"),
    
    # U
    "UA": ("美国联合航空", "United Airlines"),
    "UL": ("斯里兰卡航空", "SriLankan Airlines"),
    "UN": ("乌拉尔航空", "Ural Airlines"),
    "UO": ("香港快运航空", "HK Express"),
    "US": ("全美航空", "US Airways"),
    
    # V
    "VA": ("维珍澳洲航空", "Virgin Australia"),
    "VN": ("越南航空", "Vietnam Airlines"),
    "VS": ("维珍航空", "Virgin Atlantic"),
    
    # W
    "WF": ("宽体航空", "Wideroe"),
    "WN": ("西南航空", "Southwest Airlines"),
    
    # X
    "XJ": ("泰国亚洲航空", "Thai AirAsia X"),
    
    # Y
    "Y8": ("超翔航空", "Suparna Airlines"),
    
    # Z
    "ZH": ("深圳航空", "Shenzhen Airlines"),
}


class AirlineManager:
    """Manager for airline information and operations."""
    
    def __init__(self, airlines_data: Optional[Dict[str, Tuple[str, str]]] = None):
        """Initialize with airlines data.
        
        Args:
            airlines_data: Dictionary mapping IATA codes to (Chinese name, English name) tuples.
                          If None, uses the default AIRLINES data.
        """
        self._airlines = airlines_data or AIRLINES
    
    def get_airline_info(self, iata_code: str) -> Optional[Tuple[str, str, str]]:
        """Get airline information by IATA code.
        
        Args:
            iata_code: IATA airline code (e.g., 'CA', 'CZ')
            
        Returns:
            Tuple of (IATA code, Chinese name, English name) or None if not found
        """
        iata_code = iata_code.upper().strip()
        if iata_code in self._airlines:
            chinese_name, english_name = self._airlines[iata_code]
            return iata_code, chinese_name, english_name
        return None
    
    def get_chinese_name(self, iata_code: str) -> Optional[str]:
        """Get Chinese name of airline by IATA code."""
        info = self.get_airline_info(iata_code)
        return info[1] if info else None
    
    def get_english_name(self, iata_code: str) -> Optional[str]:
        """Get English name of airline by IATA code."""
        info = self.get_airline_info(iata_code)
        return info[2] if info else None
    
    def get_all_airlines(self) -> List[Tuple[str, str, str]]:
        """Get all airlines information.
        
        Returns:
            List of tuples (IATA code, Chinese name, English name)
        """
        return [
            (iata_code, chinese_name, english_name)
            for iata_code, (chinese_name, english_name) in self._airlines.items()
        ]
    
    def get_supported_iata_codes(self) -> List[str]:
        """Get list of all supported IATA codes."""
        return sorted(self._airlines.keys())
    
    def is_supported(self, iata_code: str) -> bool:
        """Check if an IATA code is supported."""
        return iata_code.upper().strip() in self._airlines
    
    def search_by_name(self, name: str, language: str = 'both') -> List[Tuple[str, str, str]]:
        """Search airlines by name (Chinese or English).
        
        Args:
            name: Name to search for (partial match supported)
            language: 'chinese', 'english', or 'both'
            
        Returns:
            List of matching airlines as (IATA code, Chinese name, English name) tuples
        """
        name = name.lower().strip()
        results = []
        
        for iata_code, (chinese_name, english_name) in self._airlines.items():
            match = False
            
            if language in ('chinese', 'both'):
                if name in chinese_name.lower():
                    match = True
            
            if language in ('english', 'both'):
                if name in english_name.lower():
                    match = True
            
            if match:
                results.append((iata_code, chinese_name, english_name))
        
        return results
    
    def add_airline(self, iata_code: str, chinese_name: str, english_name: str) -> None:
        """Add a new airline to the configuration."""
        iata_code = iata_code.upper().strip()
        self._airlines[iata_code] = (chinese_name.strip(), english_name.strip())
    
    def remove_airline(self, iata_code: str) -> bool:
        """Remove an airline from the configuration.
        
        Returns:
            True if airline was removed, False if not found
        """
        iata_code = iata_code.upper().strip()
        if iata_code in self._airlines:
            del self._airlines[iata_code]
            return True
        return False
    
    def get_airlines_by_prefix(self, prefix: str) -> List[Tuple[str, str, str]]:
        """Get airlines whose IATA code starts with given prefix."""
        prefix = prefix.upper().strip()
        return [
            (iata_code, chinese_name, english_name)
            for iata_code, (chinese_name, english_name) in self._airlines.items()
            if iata_code.startswith(prefix)
        ]


# Global airline manager instance
_airline_manager = AirlineManager()


# Convenience functions for backward compatibility
def get_airline_info(iata_code: str) -> Optional[Tuple[str, str, str]]:
    """Get airline information by IATA code."""
    return _airline_manager.get_airline_info(iata_code)


def get_all_airlines() -> List[Tuple[str, str, str]]:
    """Get all airlines information."""
    return _airline_manager.get_all_airlines()


def get_supported_iata_codes() -> List[str]:
    """Get list of all supported IATA codes."""
    return _airline_manager.get_supported_iata_codes()


def is_supported_airline(iata_code: str) -> bool:
    """Check if an IATA code is supported."""
    return _airline_manager.is_supported(iata_code)