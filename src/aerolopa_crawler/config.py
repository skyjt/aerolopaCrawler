"""Configuration management for AeroLOPA Crawler.

Unified configuration that supports both web crawling and API service settings.
Loads from environment variables with sensible defaults.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CrawlerConfig:
    """Configuration for web crawling functionality."""
    base_url: str = "https://www.aerolopa.com"
    timeout: float = 15.0
    retries: int = 3
    delay: float = 1.0  # polite crawl delay (seconds)
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    output_dir: str = "data"
    max_workers: int = 4
    

@dataclass
class APIConfig:
    """Configuration for API service."""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cache_timeout: int = 3600  # seconds
    max_content_length: int = 16 * 1024 * 1024  # 16MB
    

@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    log_dir: str = "logs"
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    

@dataclass
class ImageConfig:
    """Configuration for image processing."""
    cache_dir: str = "images"
    max_size: tuple[int, int] = (1920, 1080)
    quality: int = 85
    formats: List[str] = field(default_factory=lambda: ["JPEG", "PNG", "WEBP"])
    

@dataclass
class Config:
    """Main configuration container."""
    crawler: CrawlerConfig = field(default_factory=CrawlerConfig)
    api: APIConfig = field(default_factory=APIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    image: ImageConfig = field(default_factory=ImageConfig)
    
    # Aircraft model keywords for recognition
    aircraft_keywords: Dict[str, List[str]] = field(default_factory=lambda: {
        "A320": ["A320", "A319", "A321", "A318"],
        "A330": ["A330", "A332", "A333"],
        "A340": ["A340", "A342", "A343", "A345"],
        "A350": ["A350", "A359"],
        "A380": ["A380"],
        "B737": ["B737", "737", "B738", "B739"],
        "B747": ["B747", "747", "B744", "B748"],
        "B757": ["B757", "757"],
        "B767": ["B767", "767"],
        "B777": ["B777", "777", "B772", "B773", "B77W"],
        "B787": ["B787", "787", "B788", "B789"]
    })


def _maybe_load_dotenv() -> None:
    """Load .env file if python-dotenv is available."""
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except ImportError:
        # Optional dependency; ignore if not installed.
        pass


def _getenv_float(name: str, default: float) -> float:
    """Get float value from environment variable."""
    val = os.getenv(name)
    if val is None:
        return default
    try:
        return float(val)
    except ValueError:
        return default


def _getenv_int(name: str, default: int) -> int:
    """Get integer value from environment variable."""
    val = os.getenv(name)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        return default


def _getenv_bool(name: str, default: bool) -> bool:
    """Get boolean value from environment variable."""
    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() in ("true", "1", "yes", "on")


def _getenv_list(name: str, default: List[str], separator: str = ",") -> List[str]:
    """Get list value from environment variable."""
    val = os.getenv(name)
    if val is None:
        return default
    return [item.strip() for item in val.split(separator) if item.strip()]


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from environment variables.
    
    Environment variables use AEROLOPA_ prefix:
    - AEROLOPA_BASE_URL: Base URL for crawling
    - AEROLOPA_TIMEOUT: HTTP timeout in seconds
    - AEROLOPA_RETRIES: Number of retries
    - AEROLOPA_DELAY: Crawl delay in seconds
    - AEROLOPA_USER_AGENT: Custom user agent
    - AEROLOPA_OUTPUT_DIR: Output directory
    - AEROLOPA_API_HOST: API host
    - AEROLOPA_API_PORT: API port
    - AEROLOPA_API_DEBUG: Enable debug mode
    - AEROLOPA_LOG_LEVEL: Logging level
    - AEROLOPA_LOG_FILE: Log file path
    - AEROLOPA_LOG_DIR: Log directory path
    """
    _maybe_load_dotenv()
    
    # Crawler configuration
    crawler_config = CrawlerConfig(
        base_url=os.getenv("AEROLOPA_BASE_URL", "https://www.aerolopa.com"),
        timeout=_getenv_float("AEROLOPA_TIMEOUT", 15.0),
        retries=_getenv_int("AEROLOPA_RETRIES", 3),
        delay=_getenv_float("AEROLOPA_DELAY", 1.0),
        user_agent=os.getenv(
            "AEROLOPA_USER_AGENT",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ),
        output_dir=os.getenv("AEROLOPA_OUTPUT_DIR", "data"),
        max_workers=_getenv_int("AEROLOPA_MAX_WORKERS", 4)
    )
    
    # API configuration
    api_config = APIConfig(
        host=os.getenv("AEROLOPA_API_HOST", "0.0.0.0"),
        port=_getenv_int("AEROLOPA_API_PORT", 5000),
        debug=_getenv_bool("AEROLOPA_API_DEBUG", False),
        cors_origins=_getenv_list("AEROLOPA_CORS_ORIGINS", ["*"]),
        cache_timeout=_getenv_int("AEROLOPA_CACHE_TIMEOUT", 3600),
        max_content_length=_getenv_int("AEROLOPA_MAX_CONTENT_LENGTH", 16 * 1024 * 1024)
    )
    
    # Logging configuration
    logging_config = LoggingConfig(
        level=os.getenv("AEROLOPA_LOG_LEVEL", "INFO"),
        format=os.getenv(
            "AEROLOPA_LOG_FORMAT",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ),
        file_path=os.getenv("AEROLOPA_LOG_FILE"),
        log_dir=os.getenv("AEROLOPA_LOG_DIR", "logs"),
        max_bytes=_getenv_int("AEROLOPA_LOG_MAX_BYTES", 10 * 1024 * 1024),
        backup_count=_getenv_int("AEROLOPA_LOG_BACKUP_COUNT", 5)
    )
    
    # Image configuration
    image_config = ImageConfig(
        cache_dir=os.getenv("AEROLOPA_IMAGE_CACHE_DIR", "images"),
        quality=_getenv_int("AEROLOPA_IMAGE_QUALITY", 85)
    )
    
    return Config(
        crawler=crawler_config,
        api=api_config,
        logging=logging_config,
        image=image_config
    )


# Backward compatibility
def get_config() -> Config:
    """Get configuration instance (backward compatibility)."""
    return load_config()

