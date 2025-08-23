"""AeroLOPA specific crawler implementation.

Integrates the original AerolopaCrawler functionality with the modular
crawler architecture, providing seat map crawling capabilities.
"""
from __future__ import annotations

import csv
import logging
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .config import Config
from .airlines import AirlineManager


class AerolopaCrawler:
    """AeroLOPA seat map crawler with enhanced functionality.
    
    Provides comprehensive seat map crawling capabilities including:
    - Multi-airline support
    - Aircraft model detection
    - Image downloading and processing
    - CSV data management
    - Progress tracking
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the AeroLOPA crawler.
        
        Args:
            config: Configuration object. If None, loads default config.
        """
        from .config import load_config
        
        self.config = config or load_config()
        self.airline_manager = AirlineManager()
        self.session = self._create_session()
        self.logger = self._setup_logging()
        
        # Create output directories
        self._ensure_directories()
        
        # Initialize CSV file
        self.csv_file = os.path.join(self.config.crawler.output_dir, "seatmaps.csv")
        self._init_csv_file()
        
        # Track processed URLs to avoid duplicates
        self.processed_urls: Set[str] = set()
        
    def _create_session(self) -> requests.Session:
        """Create and configure requests session."""
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.config.crawler.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        return session
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('aerolopa_crawler')
        logger.setLevel(getattr(logging, self.config.logging.level.upper()))
        
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(self.config.logging.format)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            # File handler if specified
            if self.config.logging.file_path:
                from logging.handlers import RotatingFileHandler
                file_handler = RotatingFileHandler(
                    self.config.logging.file_path,
                    maxBytes=self.config.logging.max_bytes,
                    backupCount=self.config.logging.backup_count
                )
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
        
        return logger
    
    def _ensure_directories(self) -> None:
        """Ensure output directories exist."""
        os.makedirs(self.config.crawler.output_dir, exist_ok=True)
        os.makedirs(self.config.image.cache_dir, exist_ok=True)
    
    def _init_csv_file(self) -> None:
        """Initialize CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'airline_iata', 'airline_name_cn', 'airline_name_en',
                    'aircraft_model', 'seat_map_url', 'image_url', 'image_path',
                    'crawl_time', 'page_title', 'description'
                ])
    
    def _write_to_csv(self, data: Dict[str, str]) -> None:
        """Write data to CSV file."""
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                data.get('airline_iata', ''),
                data.get('airline_name_cn', ''),
                data.get('airline_name_en', ''),
                data.get('aircraft_model', ''),
                data.get('seat_map_url', ''),
                data.get('image_url', ''),
                data.get('image_path', ''),
                data.get('crawl_time', ''),
                data.get('page_title', ''),
                data.get('description', '')
            ])
    
    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page.
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            self.logger.debug(f"Fetching: {url}")
            response = self.session.get(
                url, 
                timeout=self.config.crawler.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Detect encoding
            response.encoding = response.apparent_encoding or 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing {url}: {e}")
            return None
    
    def _extract_airline_links(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, str]]:
        """Extract airline links from the main page.
        
        Args:
            soup: BeautifulSoup object of the main page
            base_url: Base URL for resolving relative links
            
        Returns:
            List of (airline_name, airline_url) tuples
        """
        airline_links = []
        
        # Look for airline links in various patterns
        patterns = [
            'a[href*="airline"]',
            'a[href*="carrier"]',
            '.airline-link',
            '.carrier-link'
        ]
        
        for pattern in patterns:
            links = soup.select(pattern)
            for link in links:
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    airline_name = link.get_text(strip=True)
                    if airline_name and full_url not in [url for _, url in airline_links]:
                        airline_links.append((airline_name, full_url))
        
        return airline_links
    
    def _extract_aircraft_links(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, str]]:
        """Extract aircraft model links from airline page.
        
        Args:
            soup: BeautifulSoup object of the airline page
            base_url: Base URL for resolving relative links
            
        Returns:
            List of (aircraft_model, aircraft_url) tuples
        """
        aircraft_links = []
        
        # Look for aircraft links
        patterns = [
            'a[href*="aircraft"]',
            'a[href*="seatmap"]',
            'a[href*="seat-map"]',
            '.aircraft-link',
            '.seatmap-link'
        ]
        
        for pattern in patterns:
            links = soup.select(pattern)
            for link in links:
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    # Try to extract aircraft model from text or URL
                    aircraft_model = self._extract_aircraft_model(link.get_text(strip=True), href)
                    if aircraft_model and full_url not in [url for _, url in aircraft_links]:
                        aircraft_links.append((aircraft_model, full_url))
        
        return aircraft_links
    
    def _extract_aircraft_model(self, text: str, url: str = "") -> str:
        """Extract aircraft model from text or URL.
        
        Args:
            text: Text to analyze
            url: URL to analyze (optional)
            
        Returns:
            Standardized aircraft model or original text
        """
        combined_text = f"{text} {url}".upper()
        
        # Check against known aircraft keywords
        for model, keywords in self.config.aircraft_keywords.items():
            for keyword in keywords:
                if keyword.upper() in combined_text:
                    return model
        
        # If no match found, return cleaned text
        return re.sub(r'[^A-Z0-9]', '', text.upper()) or text
    
    def _extract_seat_map_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract seat map image URLs from aircraft page.
        
        Args:
            soup: BeautifulSoup object of the aircraft page
            base_url: Base URL for resolving relative links
            
        Returns:
            List of image URLs
        """
        image_urls = []
        
        # Look for images in various patterns
        img_selectors = [
            'img[src*="seat"]',
            'img[src*="map"]',
            'img[alt*="seat"]',
            'img[alt*="map"]',
            '.seatmap img',
            '.seat-map img',
            '.aircraft-layout img'
        ]
        
        for selector in img_selectors:
            images = soup.select(selector)
            for img in images:
                src = img.get('src')
                if src:
                    full_url = urljoin(base_url, src)
                    if self._is_valid_image_url(full_url):
                        image_urls.append(full_url)
        
        return list(set(image_urls))  # Remove duplicates
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Check if URL points to a valid image.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL appears to be a valid image
        """
        if not url:
            return False
        
        # Check file extension
        parsed = urlparse(url.lower())
        path = parsed.path
        
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        if any(path.endswith(ext) for ext in valid_extensions):
            return True
        
        # Check for image-related keywords in URL
        image_keywords = ['seat', 'map', 'layout', 'cabin', 'aircraft']
        return any(keyword in url.lower() for keyword in image_keywords)
    
    def _download_image(self, image_url: str, filename: str) -> Optional[str]:
        """Download image from URL.
        
        Args:
            image_url: URL of the image to download
            filename: Local filename to save the image
            
        Returns:
            Local file path if successful, None otherwise
        """
        try:
            response = self.session.get(
                image_url, 
                timeout=self.config.crawler.timeout,
                stream=True
            )
            response.raise_for_status()
            
            file_path = os.path.join(self.config.image.cache_dir, filename)
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.debug(f"Downloaded image: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Failed to download image {image_url}: {e}")
            return None
    
    def _generate_image_filename(self, airline_iata: str, aircraft_model: str, image_url: str) -> str:
        """Generate a standardized filename for downloaded images.
        
        Args:
            airline_iata: IATA code of the airline
            aircraft_model: Aircraft model
            image_url: Original image URL
            
        Returns:
            Standardized filename
        """
        # Extract file extension
        parsed = urlparse(image_url)
        ext = os.path.splitext(parsed.path)[1] or '.jpg'
        
        # Create filename
        timestamp = int(time.time())
        filename = f"{airline_iata}_{aircraft_model}_{timestamp}{ext}"
        
        # Clean filename
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        return filename
    
    def crawl_airline_seatmaps(self, airline_iata: str) -> int:
        """Crawl seat maps for a specific airline.
        
        Args:
            airline_iata: IATA code of the airline
            
        Returns:
            Number of seat maps processed
        """
        airline_info = self.airline_manager.get_airline_info(airline_iata)
        if not airline_info:
            self.logger.error(f"Airline {airline_iata} not supported")
            return 0
        
        iata_code, chinese_name, english_name = airline_info
        self.logger.info(f"Crawling seat maps for {chinese_name} ({iata_code})")
        
        # Construct airline URL (this may need adjustment based on actual site structure)
        airline_url = f"{self.config.crawler.base_url}/airline/{airline_iata.lower()}"
        
        soup = self._fetch_page(airline_url)
        if not soup:
            self.logger.error(f"Failed to fetch airline page: {airline_url}")
            return 0
        
        # Extract aircraft links
        aircraft_links = self._extract_aircraft_links(soup, airline_url)
        
        processed_count = 0
        for aircraft_model, aircraft_url in aircraft_links:
            if aircraft_url in self.processed_urls:
                continue
            
            self.logger.info(f"Processing {aircraft_model}: {aircraft_url}")
            
            # Fetch aircraft page
            aircraft_soup = self._fetch_page(aircraft_url)
            if not aircraft_soup:
                continue
            
            # Extract seat map images
            image_urls = self._extract_seat_map_images(aircraft_soup, aircraft_url)
            
            for image_url in image_urls:
                # Generate filename and download image
                filename = self._generate_image_filename(iata_code, aircraft_model, image_url)
                image_path = self._download_image(image_url, filename)
                
                # Prepare data for CSV
                data = {
                    'airline_iata': iata_code,
                    'airline_name_cn': chinese_name,
                    'airline_name_en': english_name,
                    'aircraft_model': aircraft_model,
                    'seat_map_url': aircraft_url,
                    'image_url': image_url,
                    'image_path': image_path or '',
                    'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'page_title': aircraft_soup.title.string if aircraft_soup.title else '',
                    'description': ''
                }
                
                # Write to CSV
                self._write_to_csv(data)
                processed_count += 1
                
                self.logger.info(f"Processed seat map: {aircraft_model} - {image_url}")
            
            self.processed_urls.add(aircraft_url)
            
            # Respect crawl delay
            time.sleep(self.config.crawler.delay)
        
        self.logger.info(f"Completed crawling {chinese_name}: {processed_count} seat maps processed")
        return processed_count
    
    def crawl_all_airlines(self) -> int:
        """Crawl seat maps for all supported airlines.
        
        Returns:
            Total number of seat maps processed
        """
        supported_airlines = self.airline_manager.get_supported_iata_codes()
        total_processed = 0
        
        self.logger.info(f"Starting crawl for {len(supported_airlines)} airlines")
        
        for airline_iata in supported_airlines:
            try:
                count = self.crawl_airline_seatmaps(airline_iata)
                total_processed += count
                
                # Longer delay between airlines
                time.sleep(self.config.crawler.delay * 2)
                
            except KeyboardInterrupt:
                self.logger.info("Crawl interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Error crawling airline {airline_iata}: {e}")
                continue
        
        self.logger.info(f"Crawl completed: {total_processed} total seat maps processed")
        return total_processed
    
    def get_crawl_statistics(self) -> Dict[str, int]:
        """Get crawling statistics.
        
        Returns:
            Dictionary with crawl statistics
        """
        stats = {
            'total_airlines': len(self.airline_manager.get_supported_iata_codes()),
            'processed_urls': len(self.processed_urls),
            'csv_records': 0
        }
        
        # Count CSV records
        if os.path.exists(self.csv_file):
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                stats['csv_records'] = sum(1 for line in f) - 1  # Subtract header
        
        return stats