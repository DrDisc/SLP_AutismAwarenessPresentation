# Agent Configuration Guide

Comprehensive documentation for configuring the Media Gathering Agent system.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration File Location](#configuration-file-location)
3. [Complete Parameter Reference](#complete-parameter-reference)
4. [Scoring System Deep Dive](#scoring-system-deep-dive)
5. [Style Validation](#style-validation)
6. [Use Case Examples](#use-case-examples)
7. [Performance Tuning](#performance-tuning)
8. [Advanced Configuration](#advanced-configuration)

---

## Quick Start

### 1. Copy a Configuration Template

```bash
# For general use (recommended for most cases)
cp agent_configs/.agent-config.balanced.json .agent-config.json

# For cartoon/illustration-heavy content
cp agent_configs/.agent-config.cartoon.json .agent-config.json

# For maximum quality/resolution
cp agent_configs/.agent-config.quality.json .agent-config.json

# For fast retrieval with minimal API calls
cp agent_configs/.agent-config.fast.json .agent-config.json
```

### 2. Modify for Your Needs

Edit `.agent-config.json` with your preferred settings:

```json
{
  "search": {
    "max_search_queries": 5,
    "results_per_source": 5
  },
  "scoring": {
    "min_final_score": 50.0
  }
}
```

### 3. Load Configuration in Your Code

```python
import json
from pathlib import Path
from media_gathering_agent import MediaGatheringAgent, AgentConfig

# Load from JSON file
config_path = Path(".agent-config.json")
with open(config_path) as f:
    config_dict = json.load(f)

# Create AgentConfig from dictionary
config = AgentConfig(**config_dict)

# Create agent with custom config
agent = MediaGatheringAgent(config=config)
```

---

## Configuration File Location

The agent looks for configuration files in this order:

1. `.agent-config.json` (project root) - Your custom config
2. `agent_configs/.agent-config.json` (fallback)
3. Built-in defaults (if no file found)

### File Organization

```
project/
├── .agent-config.json                 # Your custom config (gitignored)
├── agent_configs/
│   ├── .agent-config.json            # Default/template
│   ├── .agent-config.balanced.json    # Balanced profile
│   ├── .agent-config.cartoon.json     # Cartoon-optimized
│   ├── .agent-config.quality.json     # Quality-focused
│   └── .agent-config.fast.json        # Speed-focused
```

---

## Complete Parameter Reference

### Search Configuration

#### `max_search_queries` (int, default: 5)
**Range:** 1-20 | **Performance Impact:** High

Number of search query variations generated from a single search term.

The agent generates variations to improve match rates. More queries = more API calls and slower processing.

**Values:**
- `1-2`: Minimal (fast, less comprehensive)
- `3-5`: Standard (good balance)
- `6-10`: Thorough (more API calls)
- `11-20`: Exhaustive (maximum coverage, slow)

**Example:**
For query "children learning", the agent generates:
```
1. "children learning"
2. "kids learning"
3. "students learning"
4. "educational learning"
5. "learning classroom"
```

---

#### `results_per_source` (int, default: 5)
**Range:** 1-50 | **Performance Impact:** Medium

Number of results to request from each API source per query.

- Lower values: Faster, fewer API calls, less deduplication needed
- Higher values: More comprehensive results, slower

**Typical Values:**
- `3-5`: Fast retrieval (good for speed-optimized)
- `5-10`: Balanced (general use)
- `10-20`: Comprehensive (when quality candidates are sparse)

---

### Scoring Configuration

The agent uses a weighted scoring system to rank media candidates from 0-100:

```
Final Score = (Relevance × relevance_weight) + (Quality × quality_weight) 
            + (Style Confidence × style_confidence_weight × 100)
```

#### `min_final_score` (float, default: 50.0)
**Range:** 0.0-100.0 | **Impact:** Quality gate

Minimum score required to accept a media asset. Assets below this threshold are rejected.

**Values:**
- `40-50`: Lenient (accept more, including lower quality)
- `50-60`: Standard (good balance)
- `60-75`: Strict (only top candidates)
- `75+`: Very strict (only perfect matches)

**Use Cases:**
```python
# For Handout 1 (SLP Info) - cartoon required, quality critical
min_final_score = 55.0

# For general use - accept good enough results
min_final_score = 50.0

# For presentation slides - only premium quality
min_final_score = 65.0
```

---

#### `relevance_weight` (float, default: 0.6)
**Range:** 0.0-1.0 | **Impact:** Scoring emphasis

Weight of relevance in final score. Higher = relevance is more important.

**Calculation:** `relevance_score × relevance_weight`

**Values:**
- `0.3-0.4`: Low (quality/style more important)
- `0.5-0.6`: Standard (balanced with quality)
- `0.7-0.8`: High (relevance is critical)

**When to Increase:**
- User specified exact keywords that must match
- Searching for very specific scenarios
- Results are too generic

**When to Decrease:**
- Quality/resolution is most important
- Searching for style (cartoon vs photo)
- Any relevant result is acceptable

---

#### `quality_weight` (float, default: 0.4)
**Range:** 0.0-1.0 | **Impact:** Scoring emphasis

Weight of quality metrics in final score.

**Calculation:** `quality_score × quality_weight`

**Values:**
- `0.2-0.3`: Low (relevance/style more important)
- `0.35-0.45`: Standard (balanced)
- `0.5-0.7`: High (quality is critical)

**When to Increase:**
- Presentation slides (professional appearance required)
- Print materials (resolution matters)
- Large displays (visible quality issues matter)

**When to Decrease:**
- Web use (lower resolution acceptable)
- Thumbnails or small images
- Quality varies by source

---

#### `style_confidence_weight` (float, default: 0.2)
**Range:** 0.0-1.0 | **Impact:** Scoring emphasis

Weight of style confidence (cartoon vs photo vs watercolor) in final score.

**Calculation:** `style_confidence × 100 × style_confidence_weight`

**Values:**
- `0.1-0.15`: Low (style is flexible)
- `0.2-0.25`: Standard (style matters but not critical)
- `0.3-0.4`: High (style is critical)
- `0.4-0.5`: Very High (only exact style acceptable)

**When to Increase:**
- Handout 1: Cartoon/illustration style required
- Consistent visual style needed
- Brand/design requirements
- User explicitly requested style

**When to Decrease:**
- Any style acceptable
- Relevance more important than aesthetics
- Diverse visual styles desired

---

#### `base_quality_score` (float, default: 75.0)
**Range:** 0.0-100.0

Starting quality score before bonuses are applied.

Higher values give quality a head start. Useful for platforms known to have good quality.

**Values:**
- `60-70`: Pessimistic (start low, require bonuses)
- `75-80`: Standard (neutral starting point)
- `85-90`: Optimistic (platform has good quality)

---

#### `base_relevance_score` (float, default: 50.0)
**Range:** 0.0-100.0

Starting relevance score before keyword matching.

Higher values assume results from search APIs are already relevant.

**Values:**
- `30-40`: Pessimistic (assume poor initial relevance)
- `50-60`: Standard (API results are relevant)
- `70+`: Optimistic (API already handles relevance)

---

#### `base_style_confidence` (float, default: 0.5)
**Range:** 0.0-1.0

Starting style confidence when no specific style constraint.

Used when user doesn't specify style preference.

**Values:**
- `0.3-0.4`: Neutral (style is open)
- `0.5-0.6`: Slightly positive (any style acceptable)
- `0.7+`: Confident (assume current content style is fine)

---

### Quality Bonuses

These are points added to the quality score for specific attributes.

#### `quality_bonus_fhd` (float, default: 15.0)

Bonus points for Full HD or higher resolution (1920×1080 or greater).

**Suggested Values:**
- `8-12`: Modest bonus (quality configs)
- `15-20`: Significant bonus (quality-focused)
- `25-30`: Premium bonus (only for presentation-critical)

**Use Case:** Increase for print, presentations, or high-visibility displays.

---

#### `quality_bonus_hd` (float, default: 10.0)

Bonus points for HD resolution (1280×720 or greater).

**Suggested Values:**
- `5-8`: Modest bonus
- `10-15`: Standard
- `20+`: Strong incentive for HD

**Use Case:** Increase for web/screen display, decrease for thumbnails.

---

#### `quality_bonus_cc0` (float, default: 10.0)

Bonus points for CC0 (public domain) license.

CC0 is the most permissive: free commercial use, attribution optional.

**Suggested Values:**
- `8-12`: Standard (prefer CC0)
- `15-20`: Strong preference for CC0
- `25+`: Strongly prioritize CC0

**Use Case:** Increase if you need absolute licensing certainty.

---

#### `quality_bonus_free` (float, default: 5.0)

Bonus points for free or free-commercial license.

Includes Pexels, Unsplash, and similar platforms' licenses.

**Suggested Values:**
- `3-5`: Standard
- `8-12`: Prefer free licenses
- `15+`: Strongly prefer free

**Use Case:** Increase if cost is factor, decrease if premium content needed.

---

### Relevance Configuration

#### `keyword_match_weight` (float, default: 40.0)
**Range:** 0.0-100.0

Maximum points (out of base relevance score) for keyword matching.

If user searches for "children classroom teacher", system counts how many keywords appear in result metadata.

**Calculation:**
```
keyword_bonus = (matched_keywords / total_keywords) × keyword_match_weight
final_relevance = base_relevance_score + keyword_bonus
```

**Example:**
```
Query: "children classroom teacher diverse"  (4 keywords)
Result has: "children", "teacher", "classroom" (3 matches)
Match ratio: 3/4 = 0.75 = 75%

keyword_bonus = 0.75 × 40 = 30 points
final_relevance = 50 + 30 = 80
```

**Suggested Values:**
- `20-30`: Keyword match is less important
- `40-50`: Standard (keyword match important)
- `60-80`: Keyword match is critical

---

## Scoring System Deep Dive

### How Scoring Works

The agent scores each candidate media using three independent metrics:

#### 1. Quality Score (0-100)
**Factors:**
- Base quality score (default: 75)
- Resolution bonus (HD or FHD)
- License bonus (CC0 or free)

**Example Calculation:**
```
Base quality: 75
+ FHD bonus (1920×1080): +15
+ CC0 license: +10
= Final quality score: 100
```

#### 2. Relevance Score (0-100)
**Factors:**
- Base relevance score (default: 50)
- Keyword matching in title/tags/description

**Example Calculation:**
```
Query: "children learning classroom"
Base relevance: 50
Keyword matches: 3/3 = 100% match
Keyword bonus: 1.0 × 40 = 40
= Final relevance score: 90
```

#### 3. Style Confidence (0-1)
**Factors:**
- Base confidence (default: 0.5 if no style specified)
- Positive keyword matches
- Negative keyword matches

**Example Calculation for "cartoon" style:**
```
Base: 0.5
Positive keywords matched: 5 out of 13 = +0.12 (5/13 × 0.3)
Negative keywords matched: 0 out of 10 = -0.0
= Final style confidence: 0.62
```

### Combining Scores

The final score combines all three metrics:

```python
final_score = (relevance_score × relevance_weight) + 
              (quality_score × quality_weight) + 
              (style_confidence × 100 × style_confidence_weight)

# Example with default weights:
# relevance_weight = 0.6, quality_weight = 0.4, style_confidence_weight = 0.2
# With scores: relevance=90, quality=100, style_confidence=0.62

final_score = (90 × 0.6) + (100 × 0.4) + (0.62 × 100 × 0.2)
            = 54 + 40 + 12.4
            = 106.4
            
# Clamped to max 100: 100
```

---

## Style Validation

The agent supports multiple style types with configurable keywords.

### Built-in Styles

#### Cartoon
Used for: Illustrations, animated content, educational artwork

```json
{
  "positive": ["cartoon", "illustration", "vector", "hand-drawn", ...],
  "negative": ["photo", "realistic", "camera", ...]
}
```

#### Photo
Used for: Real photographs, professional photos, portraits

```json
{
  "positive": ["photo", "photograph", "professional", ...],
  "negative": ["cartoon", "illustrated", "vector", ...]
}
```

#### Watercolor
Used for: Painted artwork, watercolor paintings, artistic renders

```json
{
  "positive": ["watercolor", "painting", "brush", ...],
  "negative": ["photo", "realistic", ...]
}
```

### How to Add Custom Styles

Edit your `.agent-config.json`:

```json
{
  "style_validation": {
    "your_custom_style": {
      "positive": [
        "keyword1", "keyword2", "keyword3"
      ],
      "negative": [
        "bad_keyword1", "bad_keyword2"
      ]
    }
  }
}
```

Then use in requests:

```python
request = MediaRequest(
    query="...",
    constraints={"style": "your_custom_style"}
)
```

### Style Confidence Calculation

For each style, the agent:

1. Extracts text from candidate (title, tags, description)
2. Counts positive keyword matches
3. Counts negative keyword matches
4. Calculates confidence: `base_confidence + (pos_ratio × 0.3) - (neg_ratio × 0.3)`
5. Clamps to 0.0-1.0 range

**Formula:**
```
confidence = base_confidence 
           + (positive_matches / total_positive_keywords) × 0.3
           - (negative_matches / total_negative_keywords) × 0.3
           
# Clamp to [0.0, 1.0]
confidence = max(0.0, min(1.0, confidence))
```

---

## Use Case Examples

### Use Case 1: Handout 1 (SLP Info) - Cartoon Focused

**Goal:** Find colorful cartoon/illustration content about SLP and communication.

**Configuration:**

```json
{
  "search": {
    "max_search_queries": 6,
    "results_per_source": 8
  },
  "scoring": {
    "min_final_score": 55.0,
    "style_confidence_weight": 0.35,
    "quality_weight": 0.35,
    "relevance_weight": 0.55,
    "base_style_confidence": 0.6
  },
  "quality_bonuses": {
    "quality_bonus_fhd": 12.0,
    "quality_bonus_cc0": 12.0
  }
}
```

**Why these settings:**
- Higher `style_confidence_weight` (0.35) ensures cartoon style is critical
- Higher `base_style_confidence` (0.6) gives cartoon content preference
- More search queries (6) for better cartoon discovery
- Higher minimum score (55) ensures quality results

**Usage:**
```python
from media_gathering_agent import MediaGatheringAgent, MediaRequest

config = AgentConfig(
    style_confidence_weight=0.35,
    base_style_confidence=0.6,
    min_final_score=55.0
)

agent = MediaGatheringAgent(config=config)

request = MediaRequest(
    query="children learning communication SLP speech",
    media_type="image",
    quantity=5,
    constraints={"style": "cartoon"}
)

results = agent.process_request(request)
```

---

### Use Case 2: Quality-Focused (Presentations)

**Goal:** High-resolution images for presentation slides.

**Configuration:**

```json
{
  "scoring": {
    "min_final_score": 65.0,
    "quality_weight": 0.6,
    "style_confidence_weight": 0.15
  },
  "quality_bonuses": {
    "quality_bonus_fhd": 20.0,
    "quality_bonus_hd": 12.0,
    "quality_bonus_cc0": 15.0
  },
  "retry": {
    "max_retries": 4
  }
}
```

**Why these settings:**
- High minimum score (65) filters for premium quality
- Doubled FHD bonus (20) heavily incentivizes high resolution
- High quality weight (0.6) makes resolution critical
- More retries for resilience

**Usage:**
```python
request = MediaRequest(
    query="autism awareness children education",
    media_type="image",
    quantity=10,
    quality="professional"
)
```

---

### Use Case 3: Speed-Optimized (Development/Testing)

**Goal:** Fast retrieval for testing or prototyping.

**Configuration:**

```json
{
  "search": {
    "max_search_queries": 2,
    "results_per_source": 2
  },
  "scoring": {
    "min_final_score": 40.0,
    "style_confidence_weight": 0.1
  },
  "timeouts": {
    "api_timeout": 3,
    "download_timeout": 8
  },
  "retry": {
    "max_retries": 1
  }
}
```

**Why these settings:**
- Minimal queries (2) and results (2 per source)
- Lower quality gate (40) accepts more candidates
- Short timeouts (3s API, 8s download)
- No retries to fail fast

**Usage:**
```python
# Perfect for CI/CD pipelines
request = MediaRequest(
    query="children learning",
    quantity=1
)
```

---

### Use Case 4: Relevance-Focused (Exact Matching)

**Goal:** Only results that closely match the search query.

**Configuration:**

```json
{
  "scoring": {
    "relevance_weight": 0.8,
    "quality_weight": 0.2,
    "style_confidence_weight": 0.1,
    "keyword_match_weight": 60.0
  },
  "search": {
    "max_search_queries": 8,
    "results_per_source": 10
  }
}
```

**Why these settings:**
- Very high relevance weight (0.8)
- Very high keyword match weight (60)
- More search queries to find exact matches
- Quality and style are secondary

**Usage:**
```python
request = MediaRequest(
    query="autism spectrum disorder diagnosis assessment evaluation",
    quantity=5
)
```

---

## Performance Tuning

### Speed Optimization

To maximize speed (minimum API calls and time):

```json
{
  "search": {
    "max_search_queries": 2,
    "results_per_source": 2
  },
  "timeouts": {
    "api_timeout": 3,
    "download_timeout": 8
  },
  "retry": {
    "max_retries": 1,
    "retry_delay_base": 0.5
  }
}
```

**Expected Performance:** 2-5 seconds per request

---

### Quality Optimization

To maximize quality and thoroughness:

```json
{
  "search": {
    "max_search_queries": 10,
    "results_per_source": 20
  },
  "quality_bonuses": {
    "quality_bonus_fhd": 25.0,
    "quality_bonus_cc0": 15.0
  },
  "retry": {
    "max_retries": 5,
    "retry_delay_base": 2.0
  }
}
```

**Expected Performance:** 30-60 seconds per request

---

### Balanced Configuration

For most production uses:

```json
{
  "search": {
    "max_search_queries": 5,
    "results_per_source": 5
  },
  "scoring": {
    "min_final_score": 50.0
  },
  "retry": {
    "max_retries": 3
  }
}
```

**Expected Performance:** 8-15 seconds per request

---

## Advanced Configuration

### Custom Style Keywords

Add specialized styles for your domain:

```json
{
  "style_validation": {
    "minimalist": {
      "positive": [
        "minimalist", "simple", "minimal", "clean",
        "whitespace", "uncluttered", "geometric"
      ],
      "negative": [
        "complex", "busy", "ornate", "detailed",
        "cluttered", "noisy"
      ]
    },
    "playful": {
      "positive": [
        "playful", "fun", "colorful", "vibrant",
        "whimsical", "cheerful", "happy"
      ],
      "negative": [
        "serious", "professional", "corporate",
        "muted", "dull", "formal"
      ]
    }
  }
}
```

---

### Adjusting for Different API Sources

Different APIs have different characteristics:

**Unsplash** (High quality, curated)
```json
{
  "results_per_source": 5,
  "base_quality_score": 80.0,
  "quality_bonus_fhd": 20.0
}
```

**Pexels** (Good quality, commercial friendly)
```json
{
  "results_per_source": 8,
  "quality_bonus_free": 10.0,
  "base_quality_score": 75.0
}
```

**Mixed sources** (Aggregate quality varies)
```json
{
  "results_per_source": 10,
  "min_final_score": 55.0,
  "base_quality_score": 70.0
}
```

---

### Logging Configuration

#### Log Levels

- **DEBUG:** Verbose output, all scoring details (for debugging)
- **INFO:** Standard output, results and progress (recommended)
- **WARNING:** Only warnings and errors
- **ERROR:** Only critical errors

```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

---

## Summary Table

Quick reference for all parameters:

| Parameter | Default | Min | Max | Impact |
|-----------|---------|-----|-----|--------|
| max_search_queries | 5 | 1 | 20 | High (API calls) |
| results_per_source | 5 | 1 | 50 | Medium (API calls) |
| min_final_score | 50.0 | 0 | 100 | Quality gate |
| style_confidence_weight | 0.2 | 0.0 | 1.0 | Scoring |
| quality_weight | 0.4 | 0.0 | 1.0 | Scoring |
| relevance_weight | 0.6 | 0.0 | 1.0 | Scoring |
| quality_bonus_fhd | 15.0 | 0 | 100 | Quality bonus |
| quality_bonus_hd | 10.0 | 0 | 100 | Quality bonus |
| quality_bonus_cc0 | 10.0 | 0 | 100 | License bonus |
| quality_bonus_free | 5.0 | 0 | 100 | License bonus |
| keyword_match_weight | 40.0 | 0 | 100 | Relevance bonus |
| api_timeout | 5 | 1 | 30 | Performance |
| download_timeout | 10 | 5 | 60 | Performance |
| max_retries | 3 | 0 | 10 | Resilience |
| retry_delay_base | 1.0 | 0.5 | 5.0 | Backoff |

---

## Next Steps

1. Copy an example config (`agent_configs/.agent-config.*.json`)
2. Modify to match your use case
3. Load and test with sample requests
4. Monitor results and adjust thresholds
5. Document your final configuration

For practical examples, see **AGENT_USAGE_GUIDE.md**.
