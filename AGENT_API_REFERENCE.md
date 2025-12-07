# Agent API Reference

Complete technical documentation for the Media Gathering Agent API.

## Table of Contents

1. [Overview](#overview)
2. [Core Classes](#core-classes)
3. [Data Structures](#data-structures)
4. [MediaGatheringAgent Class](#mediagatheringagent-class)
5. [Enumerations](#enumerations)
6. [Utility Functions](#utility-functions)
7. [Return Values](#return-values)
8. [Exception Handling](#exception-handling)
9. [Type Hints Reference](#type-hints-reference)
10. [Complete Examples](#complete-examples)

---

## Overview

The Media Gathering Agent provides a Python API for retrieving, validating, and downloading media from public sources.

**Key Components:**
- `MediaGatheringAgent`: Main orchestration class
- `MediaRequest`: Input specification
- `MediaResult`: Output item
- `AgentConfig`: Configuration parameters
- `LogLevel`: Logging control

**Design Pattern:** The agent follows a pipeline architecture:

```
Request → Search → Validate & Score → Download → Report
```

---

## Core Classes

### MediaGatheringAgent

Main orchestration class for media retrieval.

```python
class MediaGatheringAgent:
    """Professional media gathering agent with advanced features"""
    
    def __init__(
        self,
        output_dir: str = "media",
        config: Optional[AgentConfig] = None,
        log_level: LogLevel = LogLevel.INFO
    ) -> None:
        """Initialize the agent"""
```

**Parameters:**
- `output_dir` (str): Directory for downloaded media (default: "media")
- `config` (AgentConfig, optional): Custom configuration (uses defaults if None)
- `log_level` (LogLevel): Logging verbosity (default: LogLevel.INFO)

**Returns:** MediaGatheringAgent instance

**Example:**
```python
from media_gathering_agent import MediaGatheringAgent, LogLevel

agent = MediaGatheringAgent(
    output_dir="custom_media",
    log_level=LogLevel.DEBUG
)
```

---

### AgentConfig

Configuration dataclass for the agent.

```python
@dataclass
class AgentConfig:
    """Configuration for media gathering agent"""
    
    # Search
    max_search_queries: int = 5
    results_per_source: int = 5
    
    # Scoring
    min_final_score: float = 50.0
    style_confidence_weight: float = 0.2
    quality_weight: float = 0.4
    relevance_weight: float = 0.6
    
    # Defaults
    base_quality_score: float = 75.0
    base_relevance_score: float = 50.0
    base_style_confidence: float = 0.5
    
    # Quality bonuses
    quality_bonus_fhd: float = 15.0
    quality_bonus_hd: float = 10.0
    quality_bonus_cc0: float = 10.0
    quality_bonus_free: float = 5.0
    
    # Relevance
    keyword_match_weight: float = 40.0
    
    # Timeouts (seconds)
    api_timeout: int = 5
    download_timeout: int = 10
    
    # Retry
    max_retries: int = 3
    retry_delay_base: float = 1.0
    
    # Style keywords
    style_keywords: Dict[str, Dict[str, List[str]]] = field(
        default_factory=lambda: {...}
    )
```

**All Parameters:** See [AGENT_CONFIGURATION_GUIDE.md](AGENT_CONFIGURATION_GUIDE.md)

**Example:**
```python
config = AgentConfig(
    max_search_queries=5,
    min_final_score=55.0,
    style_confidence_weight=0.3
)

agent = MediaGatheringAgent(config=config)
```

---

## Data Structures

### MediaRequest

Input specification for media retrieval.

```python
@dataclass
class MediaRequest:
    """Structure for media requests"""
    
    query: str                          # Search query (required)
    media_type: str                     # "image", "video", "audio"
    quantity: int = 5                   # Number of items (1-50)
    quality: str = "high"               # "low", "medium", "high", "professional"
    licensing: str = "free"             # "free", "cc0", "commercial", "any"
    duration_min: Optional[int] = None  # Min duration (seconds, video/audio)
    duration_max: Optional[int] = None  # Max duration (seconds, video/audio)
    context: Dict = field(...)          # Additional metadata
    constraints: Dict = field(...)      # Constraints (style, format, etc)
```

**Parameters:**

#### `query` (str, required)
The search query for media retrieval.

**Type:** String, 1-500 characters  
**Examples:**
```python
"children learning in classroom"
"autism awareness education"
"SLP speech therapy communication"
```

---

#### `media_type` (str, required)
Type of media to retrieve.

**Type:** String (enum-like)  
**Valid Values:**
- `"image"` - Static images (JPG, PNG, WebP, GIF)
- `"video"` - Video files (MP4, WebM, MOV)
- `"audio"` - Audio files (MP3, WAV, OGG)

**Default:** None (must specify)  
**Example:**
```python
request = MediaRequest(
    query="children learning",
    media_type="image"
)
```

---

#### `quantity` (int)
Number of media items to retrieve.

**Type:** Integer  
**Valid Range:** 1-50  
**Default:** 5  
**Example:**
```python
request = MediaRequest(
    query="learning",
    quantity=10  # Retrieve 10 items
)
```

---

#### `quality` (str)
Quality preference for media.

**Type:** String  
**Valid Values:**
- `"low"` - Minimum quality acceptable
- `"medium"` - Moderate quality
- `"high"` - Good quality (recommended)
- `"professional"` - Premium quality

**Default:** `"high"`  
**Note:** Informational only; scoring system evaluates actual quality.

**Example:**
```python
request = MediaRequest(
    query="presentation images",
    quality="professional"
)
```

---

#### `licensing` (str)
License preference for media.

**Type:** String  
**Valid Values:**
- `"free"` - Free for any use
- `"cc0"` - Public domain, most permissive
- `"commercial"` - Allows commercial use
- `"any"` - No license preference

**Default:** `"free"`

**Example:**
```python
request = MediaRequest(
    query="autism resources",
    licensing="cc0"  # CC0 preferred
)
```

---

#### `duration_min` (int, optional)
Minimum duration for video/audio (seconds).

**Type:** Integer or None  
**Valid Range:** 1-3600  
**Default:** None  
**Example:**
```python
request = MediaRequest(
    query="therapy video",
    media_type="video",
    duration_min=30,
    duration_max=60
)
```

---

#### `duration_max` (int, optional)
Maximum duration for video/audio (seconds).

**Type:** Integer or None  
**Valid Range:** 1-3600  
**Default:** None

---

#### `context` (Dict)
Additional context for the request.

**Type:** Dictionary (key-value pairs)  
**Common Keys:**
- `"handout"` - Which handout (e.g., "1_slp_info")
- `"purpose"` - Intended use (e.g., "cover_image", "illustration")
- `"target_audience"` - Audience (e.g., "parents", "educators")

**Default:** `{}`  
**Example:**
```python
request = MediaRequest(
    query="children learning",
    context={
        "handout": "1_slp_info",
        "purpose": "educational visual",
        "target_audience": "parents"
    }
)
```

---

#### `constraints` (Dict)
Constraints on media selection.

**Type:** Dictionary  
**Common Keys:**
- `"style"` - Preferred style (e.g., "cartoon", "photo")
- `"format"` - Specific format (e.g., "jpg", "png")
- `"aspect_ratio"` - Aspect ratio (e.g., "16:9", "1:1")

**Default:** `{}`  
**Example:**
```python
request = MediaRequest(
    query="children learning",
    constraints={
        "style": "cartoon",
        "format": "png"
    }
)
```

---

### MediaResult

Result for a single retrieved media item.

```python
@dataclass
class MediaResult:
    """Structure for media results"""
    
    id: str                             # Unique ID
    url: str                            # Original source URL
    local_path: str                     # Path to downloaded file
    title: str                          # Title/description
    license: str                        # License type
    source: str                         # API source (unsplash, pexels, etc)
    media_type: str                     # image, video, audio
    resolution: Optional[str] = None    # Resolution (WxH)
    file_size: Optional[int] = None     # File size in bytes
    quality_score: float = 0.0          # Quality score (0-100)
    relevance_score: float = 0.0        # Relevance score (0-100)
    style_confidence: float = 0.0       # Style confidence (0-1)
    final_score: float = 0.0            # Final score (0-100)
    metadata: Dict = field(...)         # Additional metadata
    downloaded_at: str = ""             # ISO timestamp
```

**Fields:**

#### `id` (str)
Unique identifier for the result.

**Format:** `"source_id"` (e.g., `"pexels_img_12345"`)  
**Example:** `"unsplash_abc123def456"`

---

#### `url` (str)
Original URL of the media.

**Type:** URL string  
**Example:** `"https://images.unsplash.com/photo-..."`

---

#### `local_path` (str)
Local file path after download.

**Type:** Absolute file path  
**Example:** `"/home/user/media/handout_1_slp_info/pexels_123_1234567890.jpg"`

---

#### `title` (str)
Title or description of the media.

**Type:** String  
**Example:** `"Children Learning with Teacher in Classroom"`

---

#### `license` (str)
License information.

**Values:**
- `"cc0"` - Public domain
- `"free"` - Free for use
- `"free-commercial"` - Free for commercial use
- `"commercial"` - Requires purchase
- `"unknown"` - License unknown

---

#### `source` (str)
API source of the media.

**Values:**
- `"unsplash"` - Unsplash API
- `"pexels"` - Pexels API
- Others as supported

---

#### `resolution` (str, optional)
Media resolution.

**Format:** `"WIDTHxHEIGHT"` (e.g., `"1920x1080"`)  
**Type:** String or None  
**Example:** `"1280x720"`

---

#### `file_size` (int, optional)
Actual file size in bytes.

**Type:** Integer or None  
**Range:** 0+  
**Example:** `524288` (512 KB)

---

#### `quality_score` (float)
Quality assessment score.

**Type:** Float  
**Range:** 0.0-100.0  
**Factors:**
- Base quality score
- Resolution bonus
- License bonus

---

#### `relevance_score` (float)
Relevance to search query.

**Type:** Float  
**Range:** 0.0-100.0  
**Factors:**
- Base relevance score
- Keyword matching

---

#### `style_confidence` (float)
Confidence in matching requested style.

**Type:** Float  
**Range:** 0.0-1.0  
**Note:** Only populated if style constraint specified

---

#### `final_score` (float)
Combined final score.

**Type:** Float  
**Range:** 0.0-100.0  
**Calculation:** See [AGENT_CONFIGURATION_GUIDE.md](AGENT_CONFIGURATION_GUIDE.md)

---

#### `metadata` (Dict)
Additional metadata.

**Keys vary by source:**
```python
{
    "photographer": "John Doe",
    "description": "Full description text",
    "tags": ["tag1", "tag2", "tag3"],
    "page": "photographer_url"
}
```

---

#### `downloaded_at` (str)
ISO timestamp when downloaded.

**Format:** ISO 8601 (e.g., `"2024-01-15T14:30:45.123456"`)

---

## MediaGatheringAgent Class

### Methods

#### `__init__(...)`

Initialize the agent.

```python
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
```

**Example:**
```python
agent = MediaGatheringAgent(
    output_dir="media",
    config=AgentConfig(min_final_score=60.0),
    log_level=LogLevel.INFO
)
```

---

#### `process_request(request)`

Process a media request through the complete pipeline.

```python
def process_request(
    self,
    request: MediaRequest
) -> Dict:
    """
    Process a media request through the complete pipeline
    
    Args:
        request: MediaRequest with query and constraints
    
    Returns:
        Dictionary report with results and metadata
    """
```

**Parameters:**
- `request` (MediaRequest): The media request specification

**Returns:** Dictionary with structure:
```python
{
    "request_id": str,                  # Unique request ID
    "timestamp": str,                   # ISO timestamp
    "status": str,                      # "success" or "partial"
    "request": dict,                    # Original request
    "results": list[dict],              # MediaResult items
    "summary": {
        "total_requested": int,
        "total_retrieved": int,
        "retrieval_rate": str,          # e.g., "80%"
        "quality_avg": float,
        "relevance_avg": float,
        "style_confidence_avg": float,
        "final_score_avg": float
    }
}
```

**Example:**
```python
request = MediaRequest(
    query="children learning",
    media_type="image",
    quantity=5
)

results = agent.process_request(request)

print(f"Retrieved: {results['summary']['total_retrieved']} items")
for item in results['results']:
    print(f"  - {item['title']}: {item['final_score']:.1f}")
```

---

### Internal Methods (Reference)

These methods are called internally by `process_request()`. Documented for reference.

#### `_generate_search_queries(query)`

Generate search query variations.

```python
def _generate_search_queries(
    self,
    query: str
) -> List[str]:
    """Generate multiple search query variations"""
```

**Returns:** List of up to `max_search_queries` variations

**Example output:**
```python
["children learning", "kids learning", "students learning",
 "educational learning", "learning classroom"]
```

---

#### `_search_media(request, queries)`

Search for media across platforms.

```python
def _search_media(
    self,
    request: MediaRequest,
    queries: List[str]
) -> List[Dict]:
    """Search for media across platforms"""
```

**Returns:** List of candidate media dictionaries (unsorted, unscored)

---

#### `_validate_and_score(candidates, request)`

Validate and score candidates.

```python
def _validate_and_score(
    self,
    candidates: List[Dict],
    request: MediaRequest
) -> List[Dict]:
    """Validate and score candidates with confidence-based style validation"""
```

**Returns:** Sorted list of scored candidates (highest score first)

---

#### `_calculate_quality_score(candidate, request)`

Calculate quality score for a candidate.

```python
def _calculate_quality_score(
    self,
    candidate: Dict,
    request: MediaRequest
) -> float:
    """Calculate quality score (0-100)"""
```

**Returns:** Quality score (0.0-100.0)

---

#### `_calculate_relevance_score(candidate, query)`

Calculate relevance score.

```python
def _calculate_relevance_score(
    self,
    candidate: Dict,
    query: str
) -> float:
    """Calculate relevance score (0-100) based on keyword matching"""
```

**Returns:** Relevance score (0.0-100.0)

---

#### `_calculate_style_confidence(candidate, request)`

Calculate style confidence.

```python
def _calculate_style_confidence(
    self,
    candidate: Dict,
    request: MediaRequest
) -> float:
    """Calculate style confidence score (0-1 scale)"""
```

**Returns:** Style confidence (0.0-1.0)

---

#### `_calculate_final_score(quality, relevance, style_confidence)`

Combine component scores into final score.

```python
def _calculate_final_score(
    self,
    quality_score: float,
    relevance_score: float,
    style_confidence: float
) -> float:
    """Calculate final combined score with style confidence"""
```

**Returns:** Final score (0.0-100.0)

---

#### `_download_media(candidates, request)`

Download validated media.

```python
def _download_media(
    self,
    candidates: List[Dict],
    request: MediaRequest
) -> List[MediaResult]:
    """Download media files with retry logic"""
```

**Returns:** List of MediaResult objects for successfully downloaded items

---

#### `_with_retry(func, max_attempts)`

Execute function with exponential backoff retry logic.

```python
def _with_retry(
    self,
    func: Callable,
    max_attempts: Optional[int] = None
) -> any:
    """Execute function with exponential backoff retry logic"""
```

**Parameters:**
- `func` (Callable): Function to execute
- `max_attempts` (int, optional): Max attempts (defaults to config.max_retries)

**Returns:** Result from successful execution

**Retry Behavior:**
- Retries on timeout/connection errors
- Does NOT retry on 4xx errors
- Uses exponential backoff: 1s, 2s, 4s, ...
- Raises last exception if all attempts fail

---

## Enumerations

### LogLevel

Logging verbosity levels.

```python
class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = logging.DEBUG        # 10 - Verbose, all details
    INFO = logging.INFO          # 20 - Standard (recommended)
    WARNING = logging.WARNING    # 30 - Warnings and errors only
    ERROR = logging.ERROR        # 40 - Critical errors only
```

**Usage:**
```python
agent = MediaGatheringAgent(log_level=LogLevel.DEBUG)  # Verbose
agent = MediaGatheringAgent(log_level=LogLevel.INFO)   # Standard
agent = MediaGatheringAgent(log_level=LogLevel.WARNING) # Quiet
```

---

## Utility Functions

### setup_logger(name, level, use_emoji)

Configure logging for the agent.

```python
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
```

**Example:**
```python
from media_gathering_agent import setup_logger, LogLevel

logger = setup_logger(__name__, LogLevel.DEBUG)
logger.info("Processing request...")
```

---

## Return Values

### process_request() Return Structure

Complete structure returned by `process_request()`:

```python
{
    # Identification
    "request_id": "uuid-string",
    "timestamp": "2024-01-15T14:30:45.123456",
    
    # Status
    "status": "success",  # or "partial"
    
    # Original request (for reference)
    "request": {
        "query": "...",
        "media_type": "image",
        "quantity": 5,
        "quality": "high",
        "licensing": "free",
        "context": {},
        "constraints": {}
    },
    
    # Retrieved items
    "results": [
        {
            "id": "pexels_123",
            "url": "https://...",
            "local_path": "/path/to/file.jpg",
            "title": "Image Title",
            "license": "free-commercial",
            "source": "pexels",
            "media_type": "image",
            "resolution": "1920x1080",
            "file_size": 524288,
            "quality_score": 85.0,
            "relevance_score": 80.0,
            "style_confidence": 0.75,
            "final_score": 82.5,
            "metadata": {
                "photographer": "Name",
                "description": "...",
                "tags": ["tag1", "tag2"]
            },
            "downloaded_at": "2024-01-15T14:30:50.123456"
        },
        # ... more results
    ],
    
    # Summary statistics
    "summary": {
        "total_requested": 5,
        "total_retrieved": 4,
        "retrieval_rate": "80%",
        "quality_avg": "82.5",
        "relevance_avg": "78.3",
        "style_confidence_avg": "0.72",
        "final_score_avg": "80.4"
    }
}
```

---

## Exception Handling

### Exceptions Raised

The agent may raise the following exceptions:

#### `requests.exceptions.Timeout`
API or download timeout.

```python
try:
    results = agent.process_request(request)
except requests.exceptions.Timeout:
    print("API timeout - increase timeouts in config")
```

---

#### `requests.exceptions.ConnectionError`
Network connectivity issue.

```python
try:
    results = agent.process_request(request)
except requests.exceptions.ConnectionError:
    print("Network error - check internet connection")
```

---

#### `FileNotFoundError`
Output directory doesn't exist (created automatically by default).

---

#### Generic `Exception`
Various other errors during processing.

```python
try:
    results = agent.process_request(request)
except Exception as e:
    print(f"Error: {str(e)}")
    logging.exception("Full details:")
```

---

## Type Hints Reference

### Python Type Hints Used

```python
# Basic types
str              # String
int              # Integer
float            # Floating point
bool             # Boolean

# Optional
Optional[T]      # T or None
Optional[str]    # String or None

# Collections
List[T]          # List of T
Dict[K, V]       # Dictionary with keys K and values V
Tuple[T, ...]    # Tuple of T items

# Callable
Callable          # Any callable function
Callable[..., R]  # Callable returning R

# Union types
Union[A, B]      # Either A or B
```

### Type Hint Examples

```python
# Functions
def process(name: str, count: int = 5) -> Dict[str, float]:
    """Process something"""
    pass

# Optional parameters
def search(
    query: str,
    filters: Optional[Dict[str, str]] = None
) -> List[Dict]:
    """Search with optional filters"""
    pass

# Dataclass
@dataclass
class Request:
    query: str
    results: List[str] = field(default_factory=list)
```

---

## Complete Examples

### Example 1: Basic Request

```python
from media_gathering_agent import MediaGatheringAgent, MediaRequest

agent = MediaGatheringAgent()

request = MediaRequest(
    query="children learning communication",
    media_type="image",
    quantity=3
)

results = agent.process_request(request)

for result in results['results']:
    print(f"✓ {result['title']}")
    print(f"  Score: {result['final_score']:.1f}")
    print(f"  Path: {result['local_path']}")
```

---

### Example 2: Advanced Configuration

```python
from media_gathering_agent import (
    MediaGatheringAgent,
    MediaRequest,
    AgentConfig,
    LogLevel
)

config = AgentConfig(
    max_search_queries=6,
    results_per_source=8,
    min_final_score=55.0,
    style_confidence_weight=0.35,
    quality_weight=0.35,
    quality_bonus_fhd=15.0
)

agent = MediaGatheringAgent(
    output_dir="media/handout_1",
    config=config,
    log_level=LogLevel.DEBUG
)

request = MediaRequest(
    query="diverse children in classroom learning",
    media_type="image",
    quantity=5,
    quality="professional",
    licensing="free",
    context={"handout": "1_slp_info"},
    constraints={"style": "cartoon"}
)

results = agent.process_request(request)

print(f"Retrieved: {results['summary']['total_retrieved']}/{request.quantity}")
print(f"Avg quality: {results['summary']['quality_avg']}")
print(f"Avg style confidence: {results['summary']['style_confidence_avg']}")
```

---

### Example 3: Error Handling

```python
from media_gathering_agent import MediaGatheringAgent, MediaRequest
import requests
import logging

logging.basicConfig(level=logging.INFO)

agent = MediaGatheringAgent()

try:
    request = MediaRequest(
        query="specific content",
        media_type="image",
        quantity=5
    )
    
    results = agent.process_request(request)
    
    if results['summary']['total_retrieved'] == 0:
        print("⚠ No results found")
    else:
        print(f"✓ Retrieved {results['summary']['total_retrieved']} items")
        
except requests.exceptions.Timeout:
    print("❌ Request timeout - try increasing timeouts")
except requests.exceptions.ConnectionError:
    print("❌ Network error - check internet connection")
except Exception as e:
    print(f"❌ Error: {e}")
    logging.exception("Full details:")
```

---

### Example 4: Batch Processing

```python
from media_gathering_agent import MediaGatheringAgent, MediaRequest
import json

agent = MediaGatheringAgent()

requests_batch = [
    ("children learning", "1_slp_info"),
    ("communication strategies", "2_communication"),
    ("autism resources", "3_ontario_resources"),
]

all_results = []

for query, handout in requests_batch:
    request = MediaRequest(
        query=query,
        media_type="image",
        quantity=3,
        context={"handout": handout}
    )
    
    results = agent.process_request(request)
    all_results.append(results)
    
    retrieved = results['summary']['total_retrieved']
    print(f"✓ {handout}: {retrieved} items")

# Save all results
with open("batch_results.json", "w") as f:
    json.dump(all_results, f, indent=2)
```

---

## API Stability

### Version Information

**Current Version:** 1.0  
**Status:** Stable  
**Last Updated:** 2024-01-15

### Backward Compatibility

- All public methods and dataclasses follow semantic versioning
- `MediaRequest` and `MediaResult` fields are stable
- `AgentConfig` parameters may be extended with new defaults (backward compatible)
- Exceptions and return types are stable

---

## For More Information

- See **AGENT_CONFIGURATION_GUIDE.md** for configuration details
- See **AGENT_USAGE_GUIDE.md** for practical examples
- See **AGENTS.md** for development guidelines
