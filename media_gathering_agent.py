#!/usr/bin/env python3
"""
Professional Media Gathering Agent
Retrieves accurate media (images, videos, audio) from the internet
Based on detailed requirements and context

Improvements:
- Style validation with confidence scoring (0-1 scale)
- Structured logging with configurable levels
- Exponential backoff retry logic for resilience
- Extracted configuration via AgentConfig dataclass
"""

import os
import sys
import json
import time
import uuid
import logging
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict, field
from urllib.parse import urlencode
from enum import Enum

# Python imports for API calls
try:
    import requests
except ImportError:
    print("Installing requests...")
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR


def setup_logger(
    name: str,
    level: LogLevel = LogLevel.INFO,
    use_emoji: bool = True
) -> logging.Logger:
    """
    Setup logger with emoji support for CLI output
    
    Args:
        name: Logger name (typically __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        use_emoji: Whether to include emoji in output
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level.value)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


logger = setup_logger(__name__, LogLevel.INFO)


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class AgentConfig:
    """Configuration for media gathering agent"""
    # Search configuration
    max_search_queries: int = 5
    results_per_source: int = 5
    
    # Scoring thresholds
    min_final_score: float = 50.0
    style_confidence_weight: float = 0.2
    quality_weight: float = 0.4
    relevance_weight: float = 0.6
    
    # Scoring defaults
    base_quality_score: float = 75.0
    base_relevance_score: float = 50.0
    base_style_confidence: float = 0.5
    
    # Quality bonuses
    quality_bonus_fhd: float = 15.0  # 1920×1080+
    quality_bonus_hd: float = 10.0   # 1280×720+
    quality_bonus_cc0: float = 10.0  # CC0 license
    quality_bonus_free: float = 5.0  # Free license
    
    # Relevance calculation
    keyword_match_weight: float = 40.0  # Of base score
    
    # Download configuration
    download_timeout: int = 10
    api_timeout: int = 5
    
    # Retry configuration
    max_retries: int = 3
    retry_delay_base: float = 1.0  # Exponential backoff base (seconds)
    
    # Style validation keywords
    style_keywords: Dict[str, Dict[str, List[str]]] = field(default_factory=lambda: {
        'cartoon': {
            'positive': [
                'cartoon', 'illustration', 'animated', 'illustrated', 'comic',
                'drawing', 'vector', 'art', 'sketch', 'hand-drawn', 'cute',
                'stylized', 'graphic', 'design'
            ],
            'negative': [
                'photo', 'photograph', 'real', 'stock photo', 'people', 'person',
                'portrait', 'candid', 'camera', 'photographer'
            ]
        },
        'photo': {
            'positive': [
                'photo', 'photograph', 'real', 'stock photo', 'professional',
                'portrait', 'landscape', 'scene', 'candid'
            ],
            'negative': [
                'cartoon', 'illustration', 'animated', 'drawn', 'vector'
            ]
        },
        'watercolor': {
            'positive': [
                'watercolor', 'watercolour', 'painting', 'artistic', 'brush',
                'painted', 'ink', 'wash'
            ],
            'negative': [
                'photo', 'photograph', 'vector', 'digital'
            ]
        }
    })


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class MediaRequest:
    """Structure for media requests"""
    query: str
    media_type: str  # "image", "video", "audio"
    quantity: int = 5
    quality: str = "high"  # low, medium, high, professional
    licensing: str = "free"  # free, cc0, commercial, any
    duration_min: Optional[int] = None  # For video/audio
    duration_max: Optional[int] = None
    context: Dict = field(default_factory=dict)
    constraints: Dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize defaults"""
        if not self.context:
            self.context = {}
        if not self.constraints:
            self.constraints = {}


@dataclass
class MediaResult:
    """Structure for media results"""
    id: str
    url: str
    local_path: str
    title: str
    license: str
    source: str
    media_type: str
    resolution: Optional[str] = None
    file_size: Optional[int] = None
    quality_score: float = 0.0
    relevance_score: float = 0.0
    style_confidence: float = 0.0
    final_score: float = 0.0
    metadata: Dict = field(default_factory=dict)
    downloaded_at: str = ""

    def __post_init__(self) -> None:
        """Initialize defaults"""
        if not self.metadata:
            self.metadata = {}
        if not self.downloaded_at:
            self.downloaded_at = datetime.now().isoformat()


# ============================================================================
# CORE AGENT CLASS
# ============================================================================

class MediaGatheringAgent:
    """Professional media gathering agent with advanced features"""

    def __init__(
        self,
        output_dir: str = "media",
        config: Optional[AgentConfig] = None,
        log_level: LogLevel = LogLevel.INFO
    ) -> None:
        """
        Initialize media gathering agent
        
        Args:
            output_dir: Directory for downloaded media
            config: Optional AgentConfig instance (uses defaults if None)
            log_level: Logging level for output
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.config = config or AgentConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Professional Media Agent)'
        })
        
        self.results: List[MediaResult] = []
        self.cache: Dict = {}
        self.request_id = str(uuid.uuid4())
        
        # Configure logging
        global logger
        logger = setup_logger(__name__, log_level)
        
        logger.info(f"✅ Media Gathering Agent initialized")
        logger.debug(f"   Output directory: {self.output_dir}")
        logger.debug(f"   Request ID: {self.request_id}")
        logger.debug(f"   Config: {asdict(self.config)}")

    def process_request(self, request: MediaRequest) -> Dict:
        """
        Process a media request through the complete pipeline
        
        Args:
            request: MediaRequest with query and constraints
        
        Returns:
            Dictionary report with results and metadata
        """
        logger.info(f"\n📥 Processing media request:")
        logger.info(f"   Query: {request.query}")
        logger.info(f"   Type: {request.media_type}")
        logger.info(f"   Quantity: {request.quantity}")
        logger.info(f"   Quality: {request.quality}")
        logger.info(f"   Licensing: {request.licensing}")
        logger.debug(f"   Constraints: {request.constraints}")

        # Stage 1: Parse request
        search_queries = self._generate_search_queries(request.query)
        logger.info(f"\n🔍 Generated {len(search_queries)} search queries")

        # Stage 2: Search
        candidates = self._search_media(request, search_queries)
        logger.info(f"   Found {len(candidates)} candidates")

        # Stage 3: Validate & Score
        validated = self._validate_and_score(candidates, request)
        logger.info(f"   Validated: {len(validated)} media assets")

        # Stage 4: Download
        results = self._download_media(validated[:request.quantity], request)
        logger.info(f"   Downloaded: {len(results)} media assets")

        # Generate report
        report = self._generate_report(request, results)
        return report

    # ========================================================================
    # STAGE 1: SEARCH QUERY GENERATION
    # ========================================================================

    def _generate_search_queries(self, query: str) -> List[str]:
        """
        Generate multiple search query variations
        
        Args:
            query: Original search query
        
        Returns:
            List of search query variations
        """
        queries = [query]
        
        # Add variations
        variations = [
            query.replace("children", "kids"),
            query.replace("children", "students"),
            f"educational {query}",
            f"learning {query}",
        ]
        
        queries.extend([q for q in variations if q not in queries])
        return queries[:self.config.max_search_queries]

    # ========================================================================
    # STAGE 2: MULTI-SOURCE SEARCH
    # ========================================================================

    def _search_media(self, request: MediaRequest, queries: List[str]) -> List[Dict]:
        """
        Search for media across platforms
        
        Args:
            request: MediaRequest with search parameters
            queries: List of search queries
        
        Returns:
            List of candidate media dictionaries
        """
        candidates: List[Dict] = []

        logger.info(f"\n🌐 Searching across platforms...")
        
        # Search Unsplash
        for query in queries:
            try:
                unsplash_results = self._search_unsplash(query, request.media_type)
                candidates.extend(unsplash_results)
                logger.info(f"   ✓ Unsplash: {len(unsplash_results)} results")
            except Exception as e:
                logger.warning(f"   ⚠️  Unsplash: {str(e)[:50]}")

        # Search Pexels
        for query in queries:
            try:
                pexels_results = self._search_pexels(query, request.media_type)
                candidates.extend(pexels_results)
                logger.info(f"   ✓ Pexels: {len(pexels_results)} results")
            except Exception as e:
                logger.warning(f"   ⚠️  Pexels: {str(e)[:50]}")

        # Remove duplicates by URL
        seen = set()
        unique_candidates = []
        for c in candidates:
            if c.get('url') not in seen:
                seen.add(c.get('url'))
                unique_candidates.append(c)

        logger.debug(f"   Deduplicated to {len(unique_candidates)} unique candidates")
        return unique_candidates

    def _search_unsplash(self, query: str, media_type: str) -> List[Dict]:
        """
        Search Unsplash API with retry logic
        
        Args:
            query: Search query
            media_type: Type of media (image, video, audio)
        
        Returns:
            List of media candidates from Unsplash
        """
        if media_type not in ["image"]:
            return []

        def _do_search() -> List[Dict]:
            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": query,
                "per_page": self.config.results_per_source,
                "order_by": "relevant"
            }
            
            response = self.session.get(
                url,
                params=params,
                timeout=self.config.api_timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                results: List[Dict] = []
                for photo in data.get('results', []):
                    photo_id = photo.get('id') or 'unknown'
                    photo_url = photo.get('urls', {}).get('regular') or ''
                    photo_title = photo.get('description') or 'Unsplash Photo'
                    photo_width = photo.get('width') or 0
                    photo_height = photo.get('height') or 0
                    results.append({
                        'id': f"unsplash_{photo_id}",
                        'url': photo_url,
                        'title': photo_title,
                        'source': 'unsplash',
                        'license': 'cc0',
                        'resolution': f"{photo_width}x{photo_height}",
                        'metadata': {
                            'photographer': photo.get('user', {}).get('name'),
                            'description': photo.get('description'),
                            'tags': [t.get('title') for t in photo.get('tags', [])][:5]
                        }
                    })
                return results
            else:
                raise Exception(f"HTTP {response.status_code}")
        
        try:
            result = self._with_retry(_do_search)
            return result if result else []
        except Exception:
            return []

    def _search_pexels(self, query: str, media_type: str) -> List[Dict]:
        """
        Search Pexels API with retry logic
        
        Args:
            query: Search query
            media_type: Type of media (image, video, audio)
        
        Returns:
            List of media candidates from Pexels
        """
        if media_type not in ["image", "video"]:
            return []

        def _do_search() -> List[Dict]:
            if media_type == "image":
                url = "https://api.pexels.com/v1/search"
            else:
                url = "https://api.pexels.com/videos/search"

            params = {
                "query": query,
                "per_page": self.config.results_per_source
            }
            
            response = self.session.get(
                url,
                params=params,
                timeout=self.config.api_timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                results: List[Dict] = []
                
                if media_type == "image":
                    for photo in data.get('photos', []):
                        photo_id = photo.get('id') or 0
                        photo_url = photo.get('src', {}).get('original') or ''
                        photo_width = photo.get('width') or 0
                        photo_height = photo.get('height') or 0
                        results.append({
                            'id': f"pexels_img_{photo_id}",
                            'url': photo_url,
                            'title': f"Pexels Photo {photo_id}",
                            'source': 'pexels',
                            'license': 'free-commercial',
                            'resolution': f"{photo_width}x{photo_height}",
                            'metadata': {
                                'photographer': photo.get('photographer'),
                                'page': photo.get('photographer_url')
                            }
                        })
                else:
                    for video in data.get('videos', []):
                        video_id = video.get('id') or 0
                        video_url = video.get('video_files', [{}])[0].get('link') or ''
                        results.append({
                            'id': f"pexels_vid_{video_id}",
                            'url': video_url,
                            'title': f"Pexels Video {video_id}",
                            'source': 'pexels',
                            'license': 'free-commercial',
                            'metadata': {
                                'duration': video.get('duration'),
                                'width': video.get('width'),
                                'height': video.get('height')
                            }
                        })
                
                return results
            else:
                raise Exception(f"HTTP {response.status_code}")
        
        try:
            result = self._with_retry(_do_search)
            return result if result else []
        except Exception:
            return []

    # ========================================================================
    # STAGE 3: VALIDATION & SCORING WITH CONFIDENCE SCORES
    # ========================================================================

    def _validate_and_score(
        self,
        candidates: List[Dict],
        request: MediaRequest
    ) -> List[Dict]:
        """
        Validate and score candidates with confidence-based style validation
        
        Args:
            candidates: List of candidate media dictionaries
            request: MediaRequest with constraints
        
        Returns:
            Sorted list of validated and scored candidates
        """
        scored: List[Dict] = []

        for candidate in candidates:
            try:
                # Calculate style confidence (0-1 scale)
                style_confidence = self._calculate_style_confidence(
                    candidate,
                    request
                )
                
                # Quality score (0-100)
                quality_score = self._calculate_quality_score(candidate, request)
                
                # Relevance score (0-100)
                relevance_score = self._calculate_relevance_score(
                    candidate,
                    request.query
                )
                
                # Final score combining all components
                final_score = self._calculate_final_score(
                    quality_score,
                    relevance_score,
                    style_confidence
                )
                
                candidate['quality_score'] = quality_score
                candidate['relevance_score'] = relevance_score
                candidate['style_confidence'] = style_confidence
                candidate['final_score'] = final_score
                
                logger.debug(
                    f"   Scored {candidate.get('title')[:40]}: "
                    f"final={final_score:.1f}, style_conf={style_confidence:.2f}"
                )
                
                if final_score >= self.config.min_final_score:
                    scored.append(candidate)
                else:
                    logger.debug(
                        f"   ⚠️  Skipped (score {final_score:.1f} < "
                        f"{self.config.min_final_score}): "
                        f"{candidate.get('title')[:50]}"
                    )
            except Exception as e:
                logger.error(f"   ❌ Error scoring candidate: {str(e)[:100]}")
                continue

        # Sort by final score (descending)
        scored.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        return scored

    def _calculate_style_confidence(
        self,
        candidate: Dict,
        request: MediaRequest
    ) -> float:
        """
        Calculate style confidence score (0-1 scale) instead of binary gate
        
        Supports multiple style types: cartoon, photo, watercolor, etc.
        Gracefully handles missing metadata.
        
        Args:
            candidate: Media candidate dictionary
            request: MediaRequest with constraints
        
        Returns:
            Confidence score from 0.0 (definitely wrong style) to 1.0 (perfect match)
        """
        style = request.constraints.get('style', '').lower()
        
        # No style constraint means neutral confidence
        if not style:
            return self.config.base_style_confidence

        # Extract text from candidate
        title = candidate.get('title', '').lower()
        tags = [str(t).lower() for t in candidate.get('metadata', {}).get('tags', [])]
        description = candidate.get('metadata', {}).get('description', '').lower()
        source = candidate.get('source', '').lower()
        
        combined_text = f"{title} {' '.join(tags)} {description} {source}"
        
        # Get keywords for this style
        keywords_config = self.config.style_keywords.get(
            style,
            {}
        )
        
        if not keywords_config:
            logger.warning(f"Unknown style: {style}")
            return self.config.base_style_confidence
        
        positive_keywords = keywords_config.get('positive', [])
        negative_keywords = keywords_config.get('negative', [])
        
        # Start with base confidence
        confidence = self.config.base_style_confidence
        
        # Check for positive indicators
        positive_matches = sum(1 for kw in positive_keywords if kw in combined_text)
        if positive_keywords:
            positive_ratio = positive_matches / len(positive_keywords)
            confidence += 0.3 * positive_ratio  # Up to +0.3
        
        # Check for negative indicators (reduce confidence)
        negative_matches = sum(1 for kw in negative_keywords if kw in combined_text)
        if negative_keywords:
            negative_ratio = negative_matches / len(negative_keywords)
            confidence -= 0.3 * negative_ratio  # Down to -0.3
        
        # Clamp to valid range
        confidence = max(0.0, min(1.0, confidence))
        
        logger.debug(
            f"   Style confidence for '{style}': {confidence:.2f} "
            f"(pos={positive_matches}, neg={negative_matches})"
        )
        
        return confidence

    def _calculate_quality_score(
        self,
        candidate: Dict,
        request: MediaRequest
    ) -> float:
        """
        Calculate quality score (0-100)
        
        Args:
            candidate: Media candidate dictionary
            request: MediaRequest with quality preference
        
        Returns:
            Quality score from 0 to 100
        """
        score = self.config.base_quality_score

        # Resolution bonus
        resolution = candidate.get('resolution', '')
        if 'x' in resolution:
            try:
                w, h = map(int, resolution.split('x'))
                if w >= 1920 and h >= 1080:
                    score += self.config.quality_bonus_fhd
                    logger.debug(f"   +{self.config.quality_bonus_fhd} for FHD resolution")
                elif w >= 1280 and h >= 720:
                    score += self.config.quality_bonus_hd
                    logger.debug(f"   +{self.config.quality_bonus_hd} for HD resolution")
            except Exception as e:
                logger.debug(f"   Could not parse resolution: {str(e)[:50]}")

        # License bonus
        license_type = candidate.get('license', '')
        if license_type == 'cc0':
            score += self.config.quality_bonus_cc0
            logger.debug(f"   +{self.config.quality_bonus_cc0} for CC0 license")
        elif 'free' in license_type.lower():
            score += self.config.quality_bonus_free
            logger.debug(f"   +{self.config.quality_bonus_free} for free license")

        return min(100.0, max(0.0, score))

    def _calculate_relevance_score(self, candidate: Dict, query: str) -> float:
        """
        Calculate relevance score (0-100) based on keyword matching
        
        Args:
            candidate: Media candidate dictionary
            query: Search query
        
        Returns:
            Relevance score from 0 to 100
        """
        score = self.config.base_relevance_score

        # Keyword matching
        title = candidate.get('title', '').lower()
        tags = [str(t).lower() for t in candidate.get('metadata', {}).get('tags', [])]
        description = candidate.get('metadata', {}).get('description', '').lower()

        query_words = query.lower().split()
        
        matched = 0
        for word in query_words:
            if word in title or any(word in tag for tag in tags) or word in description:
                matched += 1

        if query_words:
            keyword_score = (matched / len(query_words)) * self.config.keyword_match_weight
            score += keyword_score
            logger.debug(
                f"   Keyword match: {matched}/{len(query_words)} (+{keyword_score:.0f})"
            )

        return min(100.0, max(0.0, score))

    def _calculate_final_score(
        self,
        quality_score: float,
        relevance_score: float,
        style_confidence: float
    ) -> float:
        """
        Calculate final combined score with style confidence
        
        Combines:
        - Relevance (60% weight)
        - Quality (40% weight)
        - Style confidence (20% additional weight)
        
        Args:
            quality_score: Quality score 0-100
            relevance_score: Relevance score 0-100
            style_confidence: Style confidence 0-1
        
        Returns:
            Final score 0-100
        """
        # Base technical score
        technical_score = (
            (relevance_score * self.config.relevance_weight) +
            (quality_score * self.config.quality_weight)
        )
        
        # Adjust by style confidence (convert 0-1 to 0-100 contribution)
        style_contribution = style_confidence * 100.0 * self.config.style_confidence_weight
        
        # Combine: technical_score is 0-100, style adds up to 20 points
        final_score = technical_score + style_contribution
        
        return min(100.0, max(0.0, final_score))

    # ========================================================================
    # STAGE 4: DOWNLOAD & FILE MANAGEMENT
    # ========================================================================

    def _download_media(
        self,
        candidates: List[Dict],
        request: MediaRequest
    ) -> List[MediaResult]:
        """
        Download media files with retry logic
        
        Args:
            candidates: List of validated candidate dictionaries
            request: MediaRequest with context
        
        Returns:
            List of MediaResult objects
        """
        results: List[MediaResult] = []

        for i, candidate in enumerate(candidates):
            try:
                logger.info(
                    f"\n📥 Downloading {i+1}/{len(candidates)}: "
                    f"{candidate.get('title')}"
                )
                
                url = candidate.get('url')
                if not url or not isinstance(url, str):
                    logger.warning(f"   ❌ No valid URL found")
                    continue

                # Download file with retry
                def _do_download() -> requests.Response:
                    response = self.session.get(
                        url,
                        timeout=self.config.download_timeout
                    )
                    if response.status_code != 200:
                        raise Exception(f"HTTP {response.status_code}")
                    return response
                
                response = self._with_retry(_do_download)
                if not response:
                    logger.warning(f"   ❌ Failed to download")
                    continue

                # Determine file extension
                content_type = response.headers.get('content-type', '') if response.headers else ''
                ext = self._get_file_extension(content_type, url)

                # Create subdirectory by handout
                handout_dir = request.context.get('handout', 'other') if request.context else 'other'
                subdir = self.output_dir / f"handout_{handout_dir}"
                subdir.mkdir(exist_ok=True)

                # Save file
                filename = f"{candidate.get('id', 'unknown')}_{int(time.time())}{ext}"
                filepath = subdir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)

                file_size = filepath.stat().st_size
                logger.info(f"   ✅ Saved: {filepath} ({file_size/1024:.0f}KB)")

                # Create result
                result = MediaResult(
                    id=candidate.get('id', 'unknown'),
                    url=url,
                    local_path=str(filepath),
                    title=candidate.get('title', 'Unknown'),
                    license=candidate.get('license', 'unknown'),
                    source=candidate.get('source', 'unknown'),
                    media_type=request.media_type,
                    resolution=candidate.get('resolution'),
                    file_size=file_size,
                    quality_score=float(candidate.get('quality_score', 0)),
                    relevance_score=float(candidate.get('relevance_score', 0)),
                    style_confidence=float(candidate.get('style_confidence', 0)),
                    final_score=float(candidate.get('final_score', 0)),
                    metadata=candidate.get('metadata', {})
                )

                results.append(result)

            except Exception as e:
                logger.error(f"   ❌ Error: {str(e)[:100]}")
                continue

        return results

    def _get_file_extension(self, content_type: str, url: str) -> str:
        """
        Determine file extension from content type or URL
        
        Args:
            content_type: HTTP content-type header
            url: Resource URL
        
        Returns:
            File extension including dot (e.g., ".jpg")
        """
        content_type = content_type.lower()
        
        if 'jpeg' in content_type or 'jpg' in content_type:
            return '.jpg'
        elif 'png' in content_type:
            return '.png'
        elif 'webp' in content_type:
            return '.webp'
        elif 'gif' in content_type:
            return '.gif'
        elif 'mp4' in content_type:
            return '.mp4'
        elif 'webm' in content_type:
            return '.webm'
        elif 'mpeg' in content_type:
            return '.mpeg'
        elif 'mp3' in content_type:
            return '.mp3'
        elif 'wav' in content_type:
            return '.wav'
        
        # Fall back to URL extension
        if '.' in url.split('?')[0]:
            return '.' + url.split('?')[0].split('.')[-1][:4]
        
        return '.bin'

    # ========================================================================
    # REPORTING
    # ========================================================================

    def _generate_report(
        self,
        request: MediaRequest,
        results: List[MediaResult]
    ) -> Dict:
        """
        Generate comprehensive report of processing results
        
        Args:
            request: Original MediaRequest
            results: List of MediaResult objects
        
        Returns:
            Dictionary with report data
        """
        report = {
            'request_id': self.request_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'success' if results else 'partial',
            'request': asdict(request),
            'results': [asdict(r) for r in results],
            'summary': {
                'total_requested': request.quantity,
                'total_retrieved': len(results),
                'retrieval_rate': (
                    f"{(len(results)/request.quantity*100):.0f}%"
                    if request.quantity > 0 else "0%"
                ),
                'quality_avg': (
                    f"{sum(r.quality_score for r in results)/len(results):.1f}"
                    if results else 0
                ),
                'relevance_avg': (
                    f"{sum(r.relevance_score for r in results)/len(results):.1f}"
                    if results else 0
                ),
                'style_confidence_avg': (
                    f"{sum(r.style_confidence for r in results)/len(results):.2f}"
                    if results else 0
                ),
                'final_score_avg': (
                    f"{sum(r.final_score for r in results)/len(results):.1f}"
                    if results else 0
                ),
            }
        }

        return report

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _with_retry(
        self,
        func: Callable,
        max_attempts: Optional[int] = None
    ) -> any:
        """
        Execute function with exponential backoff retry logic
        
        Retries up to max_attempts times on transient failures.
        Uses exponential backoff: 1s, 2s, 4s, etc.
        Does not retry on 4xx HTTP errors (client errors).
        
        Args:
            func: Callable to execute
            max_attempts: Max attempts (defaults to config.max_retries)
        
        Returns:
            Result from successful function execution
        
        Raises:
            Last exception if all retries exhausted
        """
        if max_attempts is None:
            max_attempts = self.config.max_retries
        
        last_exception: Optional[Exception] = None
        
        for attempt in range(max_attempts):
            try:
                return func()
            except requests.exceptions.HTTPError as e:
                # Don't retry on 4xx errors (client errors)
                if 400 <= e.response.status_code < 500:
                    logger.error(
                        f"❌ Client error (HTTP {e.response.status_code}), "
                        f"not retrying"
                    )
                    raise
                last_exception = e
            except (requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError) as e:
                last_exception = e
            except Exception as e:
                last_exception = e
            
            # If this was the last attempt, raise
            if attempt == max_attempts - 1:
                if last_exception:
                    logger.error(
                        f"❌ Failed after {max_attempts} attempts: "
                        f"{str(last_exception)[:100]}"
                    )
                    raise last_exception
                break
            
            # Exponential backoff
            wait_time = self.config.retry_delay_base ** attempt
            logger.warning(
                f"⚠️  Retry attempt {attempt + 1}/{max_attempts} "
                f"in {wait_time:.1f}s: {str(last_exception)[:50]}"
            )
            time.sleep(wait_time)
        
        if last_exception:
            raise last_exception


# ============================================================================
# MAIN / EXAMPLES
# ============================================================================

def main() -> None:
    """
    Example usage demonstrating all features:
    - Custom configuration
    - Logging levels
    - Style constraints with confidence scoring
    - Multiple media type requests
    """
    # Create custom config (optional)
    custom_config = AgentConfig(
        max_search_queries=5,
        min_final_score=50.0,
        style_confidence_weight=0.2,
        max_retries=3,
        retry_delay_base=1.0,
    )
    
    # Create agent with custom config
    agent = MediaGatheringAgent(
        output_dir="media",
        config=custom_config,
        log_level=LogLevel.INFO
    )

    # Example 1: Cartoon style request
    logger.info("\n" + "="*70)
    logger.info("EXAMPLE 1: Cartoon/Illustration style")
    logger.info("="*70)
    
    cartoon_request = MediaRequest(
        query="children learning with teacher in classroom diverse",
        media_type="image",
        quantity=5,
        quality="professional",
        licensing="free",
        context={"handout": "1_slp_info"},
        constraints={"style": "cartoon"}  # New confidence-based style validation
    )

    report1 = agent.process_request(cartoon_request)
    
    # Save report
    report_path = Path("media_gathering_report_cartoon.json")
    with open(report_path, 'w') as f:
        json.dump(report1, f, indent=2)

    logger.info(f"\n✨ Cartoon request complete!")
    logger.info(f"   Report: {report_path}")
    logger.info(f"   Retrieved: {report1['summary']['total_retrieved']} media assets")
    logger.info(f"   Quality avg: {report1['summary']['quality_avg']}")
    logger.info(f"   Style confidence avg: {report1['summary']['style_confidence_avg']}")

    # Example 2: Photo style request
    logger.info("\n" + "="*70)
    logger.info("EXAMPLE 2: Photo style")
    logger.info("="*70)
    
    photo_request = MediaRequest(
        query="children communication therapy",
        media_type="image",
        quantity=3,
        quality="high",
        licensing="free",
        context={"handout": "2_communication"},
        constraints={"style": "photo"}  # Photo style validation
    )

    report2 = agent.process_request(photo_request)
    
    report_path2 = Path("media_gathering_report_photo.json")
    with open(report_path2, 'w') as f:
        json.dump(report2, f, indent=2)

    logger.info(f"\n✨ Photo request complete!")
    logger.info(f"   Report: {report_path2}")
    logger.info(f"   Retrieved: {report2['summary']['total_retrieved']} media assets")

    # Example 3: No style constraint (accepts anything)
    logger.info("\n" + "="*70)
    logger.info("EXAMPLE 3: No style constraint")
    logger.info("="*70)
    
    any_request = MediaRequest(
        query="autism awareness education",
        media_type="image",
        quantity=2,
        quality="medium",
        licensing="free",
        context={"handout": "3_resources"},
        constraints={}  # No style constraint
    )

    report3 = agent.process_request(any_request)
    
    report_path3 = Path("media_gathering_report_any.json")
    with open(report_path3, 'w') as f:
        json.dump(report3, f, indent=2)

    logger.info(f"\n✨ Any-style request complete!")
    logger.info(f"   Report: {report_path3}")
    logger.info(f"   Retrieved: {report3['summary']['total_retrieved']} media assets")

    logger.info("\n" + "="*70)
    logger.info("✅ All examples complete!")
    logger.info("="*70)


if __name__ == "__main__":
    main()
