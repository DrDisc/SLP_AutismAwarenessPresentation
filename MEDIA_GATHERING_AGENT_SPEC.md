# Professional Media Gathering Agent Specification

## Overview
A sophisticated autonomous agent capable of searching, validating, and retrieving accurate media assets (pictures, videos, audio) from the internet based on detailed requirements and context.

## Agent Capabilities

### 1. Media Types Supported
- **Images:** JPG, PNG, WebP, GIF (static & animated)
- **Videos:** MP4, WebM, MOV (streaming & downloadable)
- **Audio:** MP3, WAV, OGG, AAC, M4A
- **Metadata:** Captions, descriptions, licensing info

### 2. Core Functions

#### A. Search & Discovery
- Multi-platform search (Unsplash, Pexels, Pixabay, etc.)
- Semantic understanding of requests
- Context-aware filtering
- Quality verification

#### B. Validation Engine
- License verification (CC0, CC-BY, Free-tier, Commercial)
- Quality assessment (resolution, bitrate, format)
- Copyright compliance checking
- Authenticity verification

#### C. Retrieval & Storage
- Direct downloading
- Format conversion if needed
- Metadata preservation
- Organized file structure
- Error handling & retries

#### D. Intelligence Features
- Request interpretation (understanding vague descriptions)
- Best-match selection (multiple candidates)
- Fallback strategies (if primary source fails)
- Learning from successful retrievals

---

## Agent Workflow

### Stage 1: Request Processing
```
Input: "Children learning with teacher in classroom, diverse"
  ↓
Parse requirements:
  - Subject: Children learning
  - Context: Classroom
  - Diversity: Yes
  - Type: Image
  - Quality: Professional
  ↓
Generate search queries (multiple variations)
```

### Stage 2: Search Execution
```
Search across platforms:
  - Unsplash (search API)
  - Pexels (REST API)
  - Pixabay (REST API)
  - Flickr (API with CC search)
  - Archive.org (Wayback Machine)
  ↓
Collect candidates (10-50 results)
```

### Stage 3: Validation & Scoring
```
For each candidate:
  - Check licensing ✓
  - Verify resolution/quality ✓
  - Confirm relevance ✓
  - Assess diversity representation ✓
  - Check for duplicates ✓
  ↓
Score & rank (0-100)
```

### Stage 4: Download & Organization
```
Top 1-3 candidates:
  - Download with metadata
  - Verify file integrity
  - Organize by type
  - Generate JSON manifest
  ↓
Return results with details
```

---

## Technical Architecture

### Input Layer
```python
class MediaRequest:
    query: str              # "Children learning with teacher"
    media_type: str         # "image", "video", "audio"
    quantity: int           # 1-50
    quality: str            # "low", "medium", "high", "professional"
    licensing: str          # "free", "cc0", "commercial", "any"
    duration: str           # For video/audio (optional)
    context: dict           # Additional metadata
    constraints: dict       # Size, resolution, format, etc.
```

### Processing Pipeline
```
1. Request Parser
   └─ Interpret natural language
   └─ Extract requirements
   └─ Generate search strategies

2. Search Engine
   └─ Query multiple APIs
   └─ Parallel execution
   └─ Result aggregation

3. Validator
   └─ License check
   └─ Quality assessment
   └─ Relevance scoring
   └─ Duplicate detection

4. Downloader
   └─ Parallel downloads
   └─ Format validation
   └─ Error handling
   └─ Retry logic

5. Organizer
   └─ File structure
   └─ Metadata extraction
   └─ Manifest generation
   └─ Report creation
```

### Output Layer
```json
{
  "request_id": "uuid",
  "status": "success",
  "results": [
    {
      "id": "pexels_12345",
      "url": "https://...",
      "local_path": "media/handout_1/image_001.jpg",
      "title": "Children Learning with Teacher",
      "license": "cc0",
      "source": "pexels",
      "resolution": "1920x1080",
      "quality_score": 95,
      "relevance_score": 92,
      "metadata": {
        "photographer": "John Doe",
        "tags": ["education", "children", "classroom"],
        "description": "..."
      }
    }
  ],
  "manifest": "manifest.json",
  "summary": "Retrieved 5 high-quality images..."
}
```

---

## API Integrations

### Primary Sources
1. **Unsplash API**
   - Endpoint: `api.unsplash.com`
   - Auth: API key required
   - License: CC0 (free for all use)

2. **Pexels API**
   - Endpoint: `api.pexels.com`
   - Auth: API key required
   - License: Free for commercial use

3. **Pixabay API**
   - Endpoint: `pixabay.com/api`
   - Auth: API key required
   - License: Free for commercial use

4. **Flickr API**
   - Endpoint: `api.flickr.com`
   - Auth: API key + OAuth
   - License: CC search support

5. **Internet Archive**
   - Endpoint: `archive.org/advancedsearch.php`
   - Auth: No auth required
   - License: Various CC licenses

---

## Search Strategy

### Multi-Query Approach
```
Primary query: "children learning classroom teacher"
Variants:
  - "kids education classroom adult"
  - "students learning environment"
  - "children school group activity"
  - "kids with educator instruction"
  - "diverse children classroom learning"

Search filters:
  - Color: Yes (natural)
  - Resolution: 1600x900 minimum
  - Size: 500KB - 5MB
  - License: CC0 or free commercial
  - Type: Photo (not illustration, unless requested)
```

### Scoring Criteria
```
Relevance Score (0-100):
  - Keyword match: 40 points
  - Visual analysis: 30 points
  - Context match: 20 points
  - Freshness: 10 points

Quality Score (0-100):
  - Resolution: 30 points
  - File size: 25 points
  - Compression: 20 points
  - Metadata: 15 points
  - License clarity: 10 points

Final Score = (Relevance × 0.6) + (Quality × 0.4)
```

---

## Error Handling & Fallbacks

### Retry Logic
```
If initial query fails:
  1. Try alternative search terms (3 attempts)
  2. Broaden search criteria
  3. Try different API source
  4. Use cached results from similar queries
  5. Alert user with partial results
```

### Quality Thresholds
```
Minimum acceptable:
  - Images: 800x600px
  - Video: 360p, 1Mbps
  - Audio: 128kbps, MP3 format
  
Preferred:
  - Images: 1920x1080px+
  - Video: 1080p, 5Mbps
  - Audio: 320kbps, 44.1kHz
```

---

## Security & Compliance

### Licensing Verification
- Verify CC0 or free commercial licenses
- Check for restrictions
- Document source attribution
- Store license information

### Content Validation
- No copyrighted content without permission
- No misleading/false information
- No harmful or inappropriate content
- Verify photographer/creator rights

### Rate Limiting
- Respect API rate limits
- Implement exponential backoff
- Cache successful queries
- Avoid duplicate requests

---

## Usage Examples

### Example 1: Simple Image Request
```
Request: "children playing in classroom learning activity"
Response: 5 high-quality images with metadata
Uses: Handout 2 illustrations
```

### Example 2: Video Request with Duration
```
Request: "SLP therapy session with child communication 30-60 seconds"
Response: 3 videos with duration, format, licensing
Uses: Presentation video clips
```

### Example 3: Audio Request with Format
```
Request: "children learning sounds classroom ambiance background audio"
Response: 5 audio files MP3 format, 1-5 minutes
Uses: Presentation background audio
```

### Example 4: Batch Request
```
Request: "autism awareness presentation multimedia package"
Response: 
  - 20 images (various contexts)
  - 5 video clips
  - 3 audio files
  - Complete manifest with metadata
```

---

## Implementation Roadmap

### Phase 1: MVP (Week 1)
- Request parser
- Basic search (Unsplash + Pexels)
- Simple validator
- File download + organization

### Phase 2: Enhancement (Week 2)
- Multi-API integration
- Scoring algorithm
- Metadata extraction
- Report generation

### Phase 3: Intelligence (Week 3)
- Semantic understanding
- Learning system
- Advanced filtering
- Batch requests

### Phase 4: Production (Week 4)
- Error handling
- Caching system
- API rate management
- Comprehensive testing

---

## Success Metrics

- ✅ Retrieval success rate: >95%
- ✅ Relevance accuracy: >90%
- ✅ Quality compliance: >85%
- ✅ License verification: 100%
- ✅ Average retrieval time: <5 seconds per media
- ✅ File integrity: 100%
- ✅ Duplicate detection: 99%

---

## Next Steps

1. Create agent implementation
2. Set up API keys
3. Build search functions
4. Implement validation
5. Test with sample requests
6. Deploy agent

