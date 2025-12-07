#!/usr/bin/env python3
"""
Professional Media Gathering Agent
Retrieves accurate media (images, videos, audio) from the internet
Based on detailed requirements and context
"""

import os
import sys
import json
import time
import uuid
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urlencode

# Python imports for API calls
try:
    import requests
except ImportError:
    print("Installing requests...")
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests


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
    context: Dict = None
    constraints: Dict = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.constraints is None:
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
    metadata: Dict = None
    downloaded_at: str = ""

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.downloaded_at:
            self.downloaded_at = datetime.now().isoformat()


class MediaGatheringAgent:
    """Professional media gathering agent"""

    def __init__(self, output_dir: str = "media"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Professional Media Agent)'
        })
        
        self.results = []
        self.cache = {}
        self.request_id = str(uuid.uuid4())
        
        print(f"✅ Media Gathering Agent initialized")
        print(f"   Output directory: {self.output_dir}")
        print(f"   Request ID: {self.request_id}")

    def process_request(self, request: MediaRequest) -> Dict:
        """Process a media request"""
        print(f"\n📥 Processing media request:")
        print(f"   Query: {request.query}")
        print(f"   Type: {request.media_type}")
        print(f"   Quantity: {request.quantity}")
        print(f"   Quality: {request.quality}")
        print(f"   Licensing: {request.licensing}")

        # Stage 1: Parse request
        search_queries = self._generate_search_queries(request.query)
        print(f"\n🔍 Generated {len(search_queries)} search queries")

        # Stage 2: Search
        candidates = self._search_media(request, search_queries)
        print(f"   Found {len(candidates)} candidates")

        # Stage 3: Validate & Score
        validated = self._validate_and_score(candidates, request)
        print(f"   Validated: {len(validated)} media assets")

        # Stage 4: Download
        results = self._download_media(validated[:request.quantity], request)
        print(f"   Downloaded: {len(results)} media assets")

        # Generate report
        report = self._generate_report(request, results)
        return report

    def _generate_search_queries(self, query: str) -> List[str]:
        """Generate multiple search queries from user input"""
        queries = [query]
        
        # Add variations
        variations = [
            query.replace("children", "kids"),
            query.replace("children", "students"),
            f"educational {query}",
            f"learning {query}",
        ]
        
        queries.extend([q for q in variations if q not in queries])
        return queries[:5]  # Limit to 5 queries

    def _search_media(self, request: MediaRequest, queries: List[str]) -> List[Dict]:
        """Search for media across platforms"""
        candidates = []

        print(f"\n🌐 Searching across platforms...")
        
        # Search Unsplash
        for query in queries:
            try:
                unsplash_results = self._search_unsplash(query, request.media_type)
                candidates.extend(unsplash_results)
                print(f"   ✓ Unsplash: {len(unsplash_results)} results")
            except Exception as e:
                print(f"   ⚠️  Unsplash: {str(e)[:50]}")

        # Search Pexels
        for query in queries:
            try:
                pexels_results = self._search_pexels(query, request.media_type)
                candidates.extend(pexels_results)
                print(f"   ✓ Pexels: {len(pexels_results)} results")
            except Exception as e:
                print(f"   ⚠️  Pexels: {str(e)[:50]}")

        # Remove duplicates by URL
        seen = set()
        unique_candidates = []
        for c in candidates:
            if c.get('url') not in seen:
                seen.add(c.get('url'))
                unique_candidates.append(c)

        return unique_candidates

    def _search_unsplash(self, query: str, media_type: str) -> List[Dict]:
        """Search Unsplash API"""
        if media_type not in ["image"]:
            return []

        try:
            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": query,
                "per_page": 5,
                "order_by": "relevant"
            }
            
            # Try without auth key first (limited)
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                for photo in data.get('results', []):
                    results.append({
                        'id': f"unsplash_{photo.get('id')}",
                        'url': photo.get('urls', {}).get('regular'),
                        'title': photo.get('description', 'Unsplash Photo'),
                        'source': 'unsplash',
                        'license': 'cc0',
                        'resolution': f"{photo.get('width')}x{photo.get('height')}",
                        'metadata': {
                            'photographer': photo.get('user', {}).get('name'),
                            'description': photo.get('description'),
                            'tags': [t.get('title') for t in photo.get('tags', [])][:5]
                        }
                    })
                return results
        except Exception as e:
            pass
        
        return []

    def _search_pexels(self, query: str, media_type: str) -> List[Dict]:
        """Search Pexels API"""
        if media_type not in ["image", "video"]:
            return []

        try:
            if media_type == "image":
                url = "https://api.pexels.com/v1/search"
            else:
                url = "https://api.pexels.com/videos/search"

            params = {
                "query": query,
                "per_page": 5
            }
            
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                if media_type == "image":
                    for photo in data.get('photos', []):
                        results.append({
                            'id': f"pexels_img_{photo.get('id')}",
                            'url': photo.get('src', {}).get('original'),
                            'title': f"Pexels Photo {photo.get('id')}",
                            'source': 'pexels',
                            'license': 'free-commercial',
                            'resolution': f"{photo.get('width')}x{photo.get('height')}",
                            'metadata': {
                                'photographer': photo.get('photographer'),
                                'page': photo.get('photographer_url')
                            }
                        })
                else:
                    for video in data.get('videos', []):
                        results.append({
                            'id': f"pexels_vid_{video.get('id')}",
                            'url': video.get('video_files', [{}])[0].get('link'),
                            'title': f"Pexels Video {video.get('id')}",
                            'source': 'pexels',
                            'license': 'free-commercial',
                            'metadata': {
                                'duration': video.get('duration'),
                                'width': video.get('width'),
                                'height': video.get('height')
                            }
                        })
                
                return results
        except Exception as e:
            pass
        
        return []

    def _validate_and_score(self, candidates: List[Dict], request: MediaRequest) -> List[Dict]:
        """Validate and score candidates"""
        scored = []

        for candidate in candidates:
            try:
                # Style validation (check if media matches style constraints)
                style_valid = self._validate_style(candidate, request)
                if not style_valid:
                    print(f"   ⚠️  Skipped (style mismatch): {candidate.get('title')[:50]}")
                    continue
                
                # Quality score
                quality_score = self._calculate_quality_score(candidate, request)
                
                # Relevance score
                relevance_score = self._calculate_relevance_score(
                    candidate, request.query
                )
                
                # Final score
                final_score = (relevance_score * 0.6) + (quality_score * 0.4)
                
                candidate['quality_score'] = quality_score
                candidate['relevance_score'] = relevance_score
                candidate['final_score'] = final_score
                
                if final_score >= 50:  # Minimum threshold
                    scored.append(candidate)
            except Exception as e:
                continue

        # Sort by final score
        scored.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        return scored

    def _calculate_quality_score(self, candidate: Dict, request: MediaRequest) -> float:
        """Calculate quality score (0-100)"""
        score = 75.0  # Base score

        # Resolution bonus
        resolution = candidate.get('resolution', '')
        if 'x' in resolution:
            try:
                w, h = map(int, resolution.split('x'))
                if w >= 1920 and h >= 1080:
                    score += 15
                elif w >= 1280 and h >= 720:
                    score += 10
            except:
                pass

        # License bonus
        license_type = candidate.get('license', '')
        if license_type == 'cc0':
            score += 10
        elif 'free' in license_type.lower():
            score += 5

        return min(100, max(0, score))

    def _calculate_relevance_score(self, candidate: Dict, query: str) -> float:
        """Calculate relevance score (0-100)"""
        score = 50.0  # Base score

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
            keyword_score = (matched / len(query_words)) * 40
            score += keyword_score

        return min(100, max(0, score))

    def _validate_style(self, candidate: Dict, request: MediaRequest) -> bool:
        """Validate that media matches required style (e.g., cartoons)"""
        style = request.constraints.get('style', '')
        
        if not style:
            return True  # No style constraint, accept all
        
        # Check metadata and tags for style indicators
        title = candidate.get('title', '').lower()
        tags = [str(t).lower() for t in candidate.get('metadata', {}).get('tags', [])]
        description = candidate.get('metadata', {}).get('description', '').lower()
        source = candidate.get('source', '').lower()
        
        # Combine all text to check
        combined_text = f"{title} {' '.join(tags)} {description} {source}"
        
        if 'cartoon' in style.lower():
            # Cartoon indicators
            cartoon_keywords = [
                'cartoon', 'illustration', 'animated', 'illustrated', 'comic',
                'drawing', 'vector', 'art', 'sketch', 'hand-drawn', 'cute'
            ]
            # Photo/real rejection keywords
            photo_keywords = [
                'photo', 'photograph', 'real', 'stock photo', 'people', 'person',
                'portrait', 'candid', 'camera', 'photographer'
            ]
            
            # Check if it looks like a cartoon
            has_cartoon = any(kw in combined_text for kw in cartoon_keywords)
            looks_like_photo = any(kw in combined_text for kw in photo_keywords)
            
            # Reject if it looks like a photo
            if looks_like_photo and not has_cartoon:
                return False
            
            # Accept if has cartoon indicators
            if has_cartoon:
                return True
            
            # If unclear, we need more info - be conservative and reject
            return False
        
        return True

    def _download_media(self, candidates: List[Dict], request: MediaRequest) -> List[MediaResult]:
        """Download media files"""
        results = []

        for i, candidate in enumerate(candidates):
            try:
                print(f"\n📥 Downloading {i+1}/{len(candidates)}: {candidate.get('title')}")
                
                url = candidate.get('url')
                if not url:
                    print(f"   ❌ No URL found")
                    continue

                # Download file
                response = self.session.get(url, timeout=10)
                if response.status_code != 200:
                    print(f"   ❌ Download failed (HTTP {response.status_code})")
                    continue

                # Determine file extension
                content_type = response.headers.get('content-type', '')
                ext = self._get_file_extension(content_type, url)

                # Create subdirectory by handout
                subdir = self.output_dir / f"handout_{request.context.get('handout', 'other')}"
                subdir.mkdir(exist_ok=True)

                # Save file
                filename = f"{candidate.get('id')}_{int(time.time())}{ext}"
                filepath = subdir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)

                file_size = filepath.stat().st_size
                print(f"   ✅ Saved: {filepath} ({file_size/1024:.0f}KB)")

                # Create result
                result = MediaResult(
                    id=candidate.get('id'),
                    url=url,
                    local_path=str(filepath),
                    title=candidate.get('title'),
                    license=candidate.get('license'),
                    source=candidate.get('source'),
                    media_type=request.media_type,
                    resolution=candidate.get('resolution'),
                    file_size=file_size,
                    quality_score=candidate.get('quality_score', 0),
                    relevance_score=candidate.get('relevance_score', 0),
                    metadata=candidate.get('metadata', {})
                )

                results.append(result)

            except Exception as e:
                print(f"   ❌ Error: {str(e)[:100]}")
                continue

        return results

    def _get_file_extension(self, content_type: str, url: str) -> str:
        """Determine file extension from content type or URL"""
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

    def _generate_report(self, request: MediaRequest, results: List[MediaResult]) -> Dict:
        """Generate comprehensive report"""
        report = {
            'request_id': self.request_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'success' if results else 'partial',
            'request': asdict(request),
            'results': [asdict(r) for r in results],
            'summary': {
                'total_requested': request.quantity,
                'total_retrieved': len(results),
                'retrieval_rate': f"{(len(results)/request.quantity*100):.0f}%" if request.quantity > 0 else "0%",
                'quality_avg': f"{sum(r.quality_score for r in results)/len(results):.1f}" if results else 0,
                'relevance_avg': f"{sum(r.relevance_score for r in results)/len(results):.1f}" if results else 0,
            }
        }

        return report


def main():
    """Example usage"""
    agent = MediaGatheringAgent(output_dir="media")

    # Example request with cartoon style validation
    request = MediaRequest(
        query="children learning with teacher in classroom diverse",
        media_type="image",
        quantity=5,
        quality="professional",
        licensing="free",
        context={"handout": "1_slp_info"},
        constraints={"style": "cartoon"}  # Validate for cartoon/illustration style
    )

    # Process request
    report = agent.process_request(request)

    # Save report
    report_path = Path("media_gathering_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✨ Complete!")
    print(f"   Report: {report_path}")
    print(f"   Retrieved: {report['summary']['total_retrieved']} media assets")


if __name__ == "__main__":
    main()
