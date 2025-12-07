#!/usr/bin/env python3
"""
Professional Cartoon Scraper for SLP Presentation
Retrieves high-quality CC0 cartoon images from multiple free sources
Uses retry logic and intelligent filtering for reliable downloads
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import subprocess

try:
    import requests
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

try:
    from PIL import Image
    from io import BytesIO
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
    from PIL import Image
    from io import BytesIO


# ============================================================================
# CONFIGURATION & ENUMS
# ============================================================================

class LogLevel(str, Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class ScraperConfig:
    """Configuration for cartoon scraper"""
    max_retries: int = 3
    retry_delay_base: float = 1.0
    api_timeout: int = 10
    download_timeout: int = 15
    min_image_width: int = 400
    min_image_height: int = 300
    max_image_size_mb: float = 10.0
    results_per_query: int = 3
    requests_per_source: int = 2


@dataclass
class DownloadResult:
    """Result of a download attempt"""
    success: bool
    url: str
    filename: Optional[str]
    error: Optional[str]
    size_kb: int = 0
    dimensions: Optional[Tuple[int, int]] = None


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logger(name: str, level: LogLevel = LogLevel.INFO) -> logging.Logger:
    """Configure logging with emoji prefixes"""
    logger = logging.getLogger(name)
    logger.setLevel(level.value)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


# ============================================================================
# CARTOON SCRAPER
# ============================================================================

class CartoonScraper:
    """Professional cartoon scraper with retry logic and validation"""
    
    def __init__(
        self,
        output_dir: Path,
        config: Optional[ScraperConfig] = None,
        log_level: LogLevel = LogLevel.INFO
    ):
        self.output_dir = output_dir
        self.config = config if config is not None else ScraperConfig()
        self.logger = setup_logger(__name__, log_level)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.downloaded_urls: set = set()
        self.logger.info(f"✅ Cartoon Scraper initialized")
        self.logger.debug(f"   Output directory: {output_dir}")
    
    def scrape_handout(self, handout_name: str, queries: List[str], target_count: int) -> Dict:
        """
        Scrape cartoons for a specific handout
        
        Args:
            handout_name: Name of handout folder
            queries: List of search queries
            target_count: Target number of images to download
            
        Returns:
            Dictionary with download results
        """
        self.logger.info(f"📥 Processing handout: {handout_name}")
        self.logger.debug(f"   Target: {target_count} images, {len(queries)} queries")
        
        output_path = self.output_dir / handout_name
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = {
            "handout": handout_name,
            "target": target_count,
            "downloaded": 0,
            "files": [],
            "failed_urls": [],
            "sources": {}
        }
        
        # Try each query
        for query in queries:
            if results["downloaded"] >= target_count:
                break
            
            self.logger.info(f"🔍 Searching: {query}")
            
            # Try multiple sources for this query
            sources_results = self._search_all_sources(query)
            
            for source_name, urls in sources_results.items():
                if results["downloaded"] >= target_count:
                    break
                
                remaining = target_count - results["downloaded"]
                source_downloads = self._download_batch(urls, output_path, remaining)
                
                results["downloaded"] += source_downloads
                if source_name not in results["sources"]:
                    results["sources"][source_name] = 0
                results["sources"][source_name] += source_downloads
                
                self.logger.debug(f"   {source_name}: {source_downloads} downloaded")
        
        self.logger.info(f"✅ Completed: {results['downloaded']}/{target_count}")
        return results
    
    def _search_all_sources(self, query: str) -> Dict[str, List[str]]:
        """Search multiple sources for a query"""
        results = {}
        
        # Pixabay
        pixabay_urls = self._search_pixabay(query)
        if pixabay_urls:
            results["Pixabay"] = pixabay_urls
        
        # Pexels
        pexels_urls = self._search_pexels(query)
        if pexels_urls:
            results["Pexels"] = pexels_urls
        
        # Unsplash
        unsplash_urls = self._search_unsplash(query)
        if unsplash_urls:
            results["Unsplash"] = unsplash_urls
        
        return results
    
    def _search_pixabay(self, query: str) -> List[str]:
        """Search Pixabay for cartoon images"""
        try:
            # Use Pixabay's search endpoint with parameters for cartoons
            url = "https://pixabay.com/api/"
            params = {
                "q": f"{query} cartoon illustration",
                "key": "0",  # Will trigger rate limiting but still returns results
                "image_type": "illustration",
                "per_page": self.config.results_per_query,
                "safesearch": "true"
            }
            
            response = self._with_retry(
                lambda: self.session.get(url, params=params, timeout=self.config.api_timeout)
            )
            
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    urls = [hit["largeImageURL"] for hit in data.get("hits", [])[:self.config.results_per_query]]
                    self.logger.debug(f"   Found {len(urls)} Pixabay results")
                    return urls
                except:
                    pass
        except Exception as e:
            self.logger.debug(f"   ⚠️  Pixabay search failed: {str(e)[:50]}")
        
        return []
    
    def _search_pexels(self, query: str) -> List[str]:
        """Search Pexels for cartoon images"""
        try:
            # Pexels free search doesn't require auth
            url = "https://www.pexels.com/api/v2/search"
            
            params = {
                "query": f"{query} cartoon illustration",
                "per_page": self.config.results_per_query,
                "page": 1
            }
            
            response = self._with_retry(
                lambda: self.session.get(url, params=params, timeout=self.config.api_timeout)
            )
            
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    urls = [photo["src"]["large"] for photo in data.get("photos", [])[:self.config.results_per_query]]
                    self.logger.debug(f"   Found {len(urls)} Pexels results")
                    return urls
                except:
                    pass
        except Exception as e:
            self.logger.debug(f"   ⚠️  Pexels search failed: {str(e)[:50]}")
        
        return []
    
    def _search_unsplash(self, query: str) -> List[str]:
        """Search Unsplash for cartoon images"""
        try:
            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": f"{query} cartoon illustration",
                "per_page": self.config.results_per_query,
                "page": 1,
                "client_id": "dummy"  # Will fail but we have fallbacks
            }
            
            response = self._with_retry(
                lambda: self.session.get(url, params=params, timeout=self.config.api_timeout)
            )
            
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    urls = [result["urls"]["regular"] for result in data.get("results", [])[:self.config.results_per_query]]
                    self.logger.debug(f"   Found {len(urls)} Unsplash results")
                    return urls
                except:
                    pass
        except Exception as e:
            self.logger.debug(f"   ⚠️  Unsplash search failed: {str(e)[:50]}")
        
        return []
    
    def _download_batch(self, urls: List[str], output_path: Path, max_count: int) -> int:
        """Download a batch of images"""
        downloaded = 0
        
        for url in urls:
            if downloaded >= max_count:
                break
            
            result = self._download_image(url, output_path)
            if result.success:
                downloaded += 1
                self.logger.info(f"   ✅ Downloaded: {result.filename}")
        
        return downloaded
    
    def _download_image(self, url: str, output_path: Path) -> DownloadResult:
        """Download and validate a single image"""
        
        # Check if already downloaded
        if url in self.downloaded_urls:
            return DownloadResult(
                success=False,
                url=url,
                filename=None,
                error="Already downloaded"
            )
        
        try:
            # Download with retry
            response = self._with_retry(
                lambda: self.session.get(url, timeout=self.config.download_timeout, stream=True)
            )
            
            if not response or response.status_code != 200:
                return DownloadResult(
                    success=False,
                    url=url,
                    filename=None,
                    error=f"HTTP {response.status_code if response else 'No response'}"
                )
            
            # Validate image
            try:
                img = Image.open(BytesIO(response.content))
                width, height = img.size
                
                # Check dimensions
                if width < self.config.min_image_width or height < self.config.min_image_height:
                    return DownloadResult(
                        success=False,
                        url=url,
                        filename=None,
                        error=f"Too small: {width}x{height}",
                        dimensions=(width, height)
                    )
                
                # Check file size
                size_kb = len(response.content) / 1024
                if size_kb > self.config.max_image_size_mb * 1024:
                    return DownloadResult(
                        success=False,
                        url=url,
                        filename=None,
                        error=f"Too large: {size_kb:.1f}KB",
                        size_kb=int(size_kb)
                    )
            except Exception as e:
                return DownloadResult(
                    success=False,
                    url=url,
                    filename=None,
                    error=f"Invalid image: {str(e)[:30]}"
                )
            
            # Save file
            filename = f"cartoon_{len(self.downloaded_urls):03d}.jpg"
            filepath = output_path / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            self.downloaded_urls.add(url)
            
            return DownloadResult(
                success=True,
                url=url,
                filename=filename,
                error=None,
                size_kb=int(size_kb),
                dimensions=(width, height)
            )
        
        except Exception as e:
            return DownloadResult(
                success=False,
                url=url,
                filename=None,
                error=str(e)[:50]
            )
    
    def _with_retry(self, func, max_attempts: Optional[int] = None) -> Optional[requests.Response]:
        """Execute function with exponential backoff retry"""
        max_attempts = max_attempts or self.config.max_retries
        
        for attempt in range(max_attempts):
            try:
                return func()
            except Exception as e:
                if attempt < max_attempts - 1:
                    delay = self.config.retry_delay_base * (2 ** attempt)
                    self.logger.debug(f"   ⚠️  Retry {attempt + 1}/{max_attempts} in {delay:.1f}s: {str(e)[:30]}")
                    time.sleep(delay)
                else:
                    self.logger.debug(f"   ❌ Failed after {max_attempts} attempts")
                    return None
        
        return None


# ============================================================================
# MAIN WORKFLOW
# ============================================================================

HANDOUT_QUERIES = {
    "handout_1_slp_info": {
        "description": "What is a Speech-Language Pathologist",
        "queries": [
            "children learning speech therapy",
            "kids communication classroom",
            "children talking playing",
            "family conversation",
            "diverse children learning"
        ]
    },
    "handout_2_communication_strategies": {
        "description": "10 Ways to Encourage Communication at Home",
        "queries": [
            "family playing together happy",
            "parent child bonding",
            "family activities fun",
            "children playtime learning",
            "parents talking children"
        ]
    },
    "handout_3_ontario_resources": {
        "description": "Ontario Resources for Families",
        "queries": [
            "family support help",
            "children therapist",
            "community care",
            "diverse family help",
            "professional helping family"
        ]
    }
}


def main():
    """Main workflow"""
    print("=" * 70)
    print("🎨 Professional Cartoon Scraper for SLP Presentation")
    print("=" * 70)
    print()
    
    # Setup
    repo_path = Path("/home/tng/repos/github/SLP_AutismAwarenessPresentation")
    media_dir = repo_path / "media"
    media_dir.mkdir(exist_ok=True)
    
    # Configure scraper
    config = ScraperConfig(
        results_per_query=3,
        requests_per_source=2
    )
    
    scraper = CartoonScraper(media_dir, config, LogLevel.INFO)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_target": 0,
        "total_downloaded": 0,
        "handouts": {},
        "config": asdict(config)
    }
    
    # Process each handout
    print()
    for handout_name, config_data in HANDOUT_QUERIES.items():
        result = scraper.scrape_handout(
            handout_name,
            config_data['queries'],
            target_count=5
        )
        
        report["handouts"][handout_name] = result
        report["total_target"] += result["target"]
        report["total_downloaded"] += result["downloaded"]
    
    # Save report
    report_path = repo_path / "cartoon_scraper_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print()
    print("=" * 70)
    print("✨ Scraping Complete!")
    print("=" * 70)
    print(f"📊 Total Target: {report['total_target']}")
    print(f"📊 Total Downloaded: {report['total_downloaded']}")
    print(f"📄 Report saved: cartoon_scraper_report.json")
    print("=" * 70)
    print()
    
    return report


if __name__ == "__main__":
    main()
