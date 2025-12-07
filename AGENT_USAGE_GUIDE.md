# Agent Usage Guide

Practical guide to using the Media Gathering Agent for media retrieval tasks.

## Table of Contents

1. [5-Minute Quick Start](#5-minute-quick-start)
2. [Installation & Setup](#installation--setup)
3. [Basic Usage Examples](#basic-usage-examples)
4. [Advanced Usage](#advanced-usage)
5. [Integration Patterns](#integration-patterns)
6. [Error Handling](#error-handling)
7. [Monitoring & Observability](#monitoring--observability)
8. [Troubleshooting](#troubleshooting)
9. [Performance Benchmarks](#performance-benchmarks)
10. [Best Practices](#best-practices)

---

## 5-Minute Quick Start

### 1. Install Dependencies

```bash
# Python 3.8+ required
python3 -m pip install requests
```

### 2. Create a Simple Request

```python
from media_gathering_agent import MediaGatheringAgent, MediaRequest

# Create agent (uses defaults)
agent = MediaGatheringAgent()

# Create a simple request
request = MediaRequest(
    query="children learning in classroom",
    media_type="image",
    quantity=3
)

# Process request
results = agent.process_request(request)

# View results
for result in results['results']:
    print(f"✓ {result['title']}")
    print(f"  Local: {result['local_path']}")
    print(f"  Score: {result['final_score']:.1f}")
```

### 3. Check Downloaded Media

```
media/
└── handout_other/
    ├── unsplash_xxx_1234567890.jpg
    ├── pexels_img_yyy_1234567891.jpg
    └── ...
```

### 4. Review Report

```python
import json

# Print summary
print(f"Retrieved: {results['summary']['total_retrieved']} media")
print(f"Quality avg: {results['summary']['quality_avg']}")
```

---

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- `requests` library (auto-installs if missing)
- Internet connection (for API access)

### Installation Steps

1. **Clone/download the project:**

```bash
cd /path/to/SLP_AutismAwarenessPresentation
```

2. **Install dependencies:**

```bash
python3 -m pip install requests
```

3. **Verify installation:**

```bash
python3 -c "import requests; print('✓ Requests installed')"
python3 media_gathering_agent.py  # Run example
```

### Configuration Setup (Optional)

1. **Copy a configuration template:**

```bash
# Copy the balanced config
cp agent_configs/.agent-config.balanced.json .agent-config.json

# Or copy a specialized config
cp agent_configs/.agent-config.cartoon.json .agent-config.json
```

2. **Modify `.agent-config.json` for your needs:**

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

3. **Load in your code (optional):**

```python
from media_gathering_agent import MediaGatheringAgent, AgentConfig
import json

config = AgentConfig(
    max_search_queries=5,
    min_final_score=50.0
)

agent = MediaGatheringAgent(config=config)
```

---

## Basic Usage Examples

### Example 1: Simple Image Request

Retrieve cartoon images for SLP presentation:

```python
from media_gathering_agent import (
    MediaGatheringAgent,
    MediaRequest,
    LogLevel
)

# Create agent with INFO logging
agent = MediaGatheringAgent(
    output_dir="media",
    log_level=LogLevel.INFO
)

# Create request
request = MediaRequest(
    query="children learning communication therapy",
    media_type="image",
    quantity=5,
    quality="professional",
    licensing="free"
)

# Process
results = agent.process_request(request)

# Summary
print(f"\n✓ Retrieved {results['summary']['total_retrieved']} images")
for r in results['results']:
    print(f"  - {r['title']}")
```

---

### Example 2: Cartoon-Focused Request

Request with specific style constraint:

```python
from media_gathering_agent import MediaRequest

# Create cartoon-specific request
cartoon_request = MediaRequest(
    query="diverse children in classroom learning",
    media_type="image",
    quantity=5,
    quality="professional",
    licensing="free",
    context={
        "handout": "1_slp_info",
        "purpose": "educational visual"
    },
    constraints={
        "style": "cartoon"  # Request cartoon style
    }
)

results = agent.process_request(cartoon_request)

# Check style confidence
for r in results['results']:
    print(f"{r['title']}: confidence={r['style_confidence']:.2f}")
```

---

### Example 3: High-Quality Request

Request with quality optimization:

```python
from media_gathering_agent import MediaGatheringAgent, MediaRequest, AgentConfig

# Use quality-focused config
quality_config = AgentConfig(
    min_final_score=65.0,
    quality_weight=0.6,
    quality_bonus_fhd=20.0,
    quality_bonus_hd=12.0
)

agent = MediaGatheringAgent(config=quality_config)

request = MediaRequest(
    query="autism awareness children education",
    media_type="image",
    quantity=5,
    quality="professional",
    constraints={"style": "photo"}
)

results = agent.process_request(request)

# Verify resolution
for r in results['results']:
    print(f"{r['title']}: {r['resolution']}")
```

---

### Example 4: Fast Retrieval

Quick request for prototyping:

```python
from media_gathering_agent import MediaGatheringAgent, MediaRequest, AgentConfig

# Use fast config
fast_config = AgentConfig(
    max_search_queries=2,
    results_per_source=2,
    min_final_score=40.0,
    max_retries=1
)

agent = MediaGatheringAgent(config=fast_config)

request = MediaRequest(
    query="children learning",
    quantity=1
)

import time
start = time.time()
results = agent.process_request(request)
elapsed = time.time() - start

print(f"Completed in {elapsed:.1f}s")
```

---

## Advanced Usage

### Custom Configuration

Load and modify configuration from file:

```python
import json
from pathlib import Path
from media_gathering_agent import MediaGatheringAgent, AgentConfig

# Load from file
config_path = Path(".agent-config.json")
with open(config_path) as f:
    config_dict = json.load(f)

# Modify specific settings
config_dict['scoring']['min_final_score'] = 60.0
config_dict['quality_bonuses']['quality_bonus_fhd'] = 20.0

# Create agent with modified config
config = AgentConfig(**config_dict)
agent = MediaGatheringAgent(config=config)
```

---

### Custom Style Validation

Add custom style keywords:

```python
from media_gathering_agent import MediaGatheringAgent, AgentConfig

config = AgentConfig()

# Add custom style
config.style_keywords['minimalist'] = {
    'positive': ['minimalist', 'simple', 'clean', 'minimal'],
    'negative': ['busy', 'cluttered', 'ornate']
}

agent = MediaGatheringAgent(config=config)

# Use custom style
from media_gathering_agent import MediaRequest

request = MediaRequest(
    query="children learning",
    constraints={"style": "minimalist"}
)

results = agent.process_request(request)
```

---

### Logging Configuration

Control verbosity with logging levels:

```python
from media_gathering_agent import (
    MediaGatheringAgent,
    MediaRequest,
    LogLevel
)

# DEBUG: Verbose output
agent = MediaGatheringAgent(log_level=LogLevel.DEBUG)
# Output: All scoring details, API calls, retries, etc.

# INFO: Standard output (recommended)
agent = MediaGatheringAgent(log_level=LogLevel.INFO)
# Output: Progress, results, key metrics

# WARNING: Warnings and errors only
agent = MediaGatheringAgent(log_level=LogLevel.WARNING)
# Output: Only warnings and errors

# ERROR: Critical errors only
agent = MediaGatheringAgent(log_level=LogLevel.ERROR)
# Output: Only critical failures
```

---

### Accessing Detailed Results

Get comprehensive information about each result:

```python
results = agent.process_request(request)

for result in results['results']:
    print(f"Title: {result['title']}")
    print(f"Source: {result['source']}")
    print(f"License: {result['license']}")
    print(f"Resolution: {result['resolution']}")
    print(f"File size: {result['file_size']} bytes")
    print(f"Quality score: {result['quality_score']:.1f}")
    print(f"Relevance score: {result['relevance_score']:.1f}")
    print(f"Style confidence: {result['style_confidence']:.2f}")
    print(f"Final score: {result['final_score']:.1f}")
    print(f"Local path: {result['local_path']}")
    print(f"Metadata: {result['metadata']}")
    print()
```

---

## Integration Patterns

### Pattern 1: Using with Handout Scripts

Integrate agent with existing handout retrieval scripts:

```python
# In handout_1_cartoon_retrieval.py
from media_gathering_agent import MediaGatheringAgent, MediaRequest, AgentConfig

def get_slp_cartoons():
    # Use cartoon-optimized config
    config = AgentConfig(
        style_confidence_weight=0.35,
        min_final_score=55.0,
        results_per_source=8
    )
    
    agent = MediaGatheringAgent(
        output_dir="media/handout_1_slp_info",
        config=config
    )
    
    request = MediaRequest(
        query="children learning communication speech therapy",
        media_type="image",
        quantity=5,
        context={"handout": "1_slp_info"},
        constraints={"style": "cartoon"}
    )
    
    return agent.process_request(request)

# Use it
if __name__ == "__main__":
    results = get_slp_cartoons()
    print(f"Retrieved {results['summary']['total_retrieved']} cartoons")
```

---

### Pattern 2: Batch Processing

Process multiple requests in sequence:

```python
from media_gathering_agent import MediaGatheringAgent, MediaRequest
import json

# Define batch of requests
requests = [
    {
        "query": "children learning classroom",
        "quantity": 3,
        "handout": "1_slp_info"
    },
    {
        "query": "communication strategies parent child",
        "quantity": 3,
        "handout": "2_communication"
    },
    {
        "query": "autism resources Ontario supports",
        "quantity": 3,
        "handout": "3_ontario_resources"
    }
]

# Process batch
agent = MediaGatheringAgent()
all_results = []

for req_data in requests:
    request = MediaRequest(
        query=req_data['query'],
        media_type="image",
        quantity=req_data['quantity'],
        context={"handout": req_data['handout']}
    )
    
    results = agent.process_request(request)
    all_results.append(results)
    
    print(f"✓ {req_data['handout']}: {results['summary']['total_retrieved']} images")

# Save combined report
with open("batch_results.json", "w") as f:
    json.dump(all_results, f, indent=2)
```

---

### Pattern 3: Error Handling & Fallbacks

Graceful error handling with fallback strategies:

```python
from media_gathering_agent import MediaGatheringAgent, MediaRequest
import logging

def safe_retrieve_media(query, quantity=5):
    """Retrieve media with graceful error handling"""
    
    agent = MediaGatheringAgent()
    
    try:
        request = MediaRequest(query=query, quantity=quantity)
        results = agent.process_request(request)
        
        retrieved = results['summary']['total_retrieved']
        
        if retrieved >= quantity:
            print(f"✓ Retrieved {retrieved}/{quantity} items")
            return results
        elif retrieved > 0:
            print(f"⚠ Partial retrieval: {retrieved}/{quantity}")
            return results
        else:
            print(f"✗ No items retrieved")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logging.exception("Media retrieval failed")
        return None

# Usage
results = safe_retrieve_media("autism awareness children")
if results:
    print(f"Success: {len(results['results'])} items")
else:
    print("Failed - using fallback images")
```

---

### Pattern 4: Saving Results to Database

Store results in structured format:

```python
import json
import sqlite3
from media_gathering_agent import MediaGatheringAgent, MediaRequest

def save_results_to_db(results, db_path="media.db"):
    """Save media results to SQLite database"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if needed
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS media (
            id TEXT PRIMARY KEY,
            url TEXT,
            local_path TEXT,
            title TEXT,
            source TEXT,
            license TEXT,
            quality_score REAL,
            relevance_score REAL,
            style_confidence REAL,
            final_score REAL,
            metadata TEXT,
            retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert results
    for result in results['results']:
        cursor.execute("""
            INSERT OR REPLACE INTO media VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result['id'],
            result['url'],
            result['local_path'],
            result['title'],
            result['source'],
            result['license'],
            result['quality_score'],
            result['relevance_score'],
            result['style_confidence'],
            result['final_score'],
            json.dumps(result['metadata'])
        ))
    
    conn.commit()
    conn.close()

# Usage
agent = MediaGatheringAgent()
request = MediaRequest(query="children learning", quantity=5)
results = agent.process_request(request)
save_results_to_db(results)
```

---

## Error Handling

### Common Errors & Solutions

#### Network Timeout

```python
from media_gathering_agent import AgentConfig

# Increase timeouts
config = AgentConfig(
    api_timeout=10,
    download_timeout=20
)

agent = MediaGatheringAgent(config=config)
```

#### API Rate Limiting

```python
from media_gathering_agent import AgentConfig
import time

# Reduce query volume and add delay
config = AgentConfig(
    max_search_queries=2,
    results_per_source=3,
    retry_delay_base=2.0
)

agent = MediaGatheringAgent(config=config)

# Add delay between requests
time.sleep(2)
results = agent.process_request(request)
```

#### No Results Found

```python
# Try broader search
request = MediaRequest(
    query="learning education children",  # Shorter query
    quantity=3
)

results = agent.process_request(request)

if not results['results']:
    # Fallback to generic search
    request2 = MediaRequest(
        query="education learning",
        quantity=3
    )
    results = agent.process_request(request2)
```

#### Low Quality Results

```python
# Increase quality threshold
config = AgentConfig(
    min_final_score=65.0,
    quality_weight=0.6,
    quality_bonus_fhd=20.0
)

agent = MediaGatheringAgent(config=config)
```

---

## Monitoring & Observability

### Logging Best Practices

```python
from media_gathering_agent import MediaGatheringAgent, LogLevel
import logging

# Set up file logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)

# Use agent with logging
agent = MediaGatheringAgent(log_level=LogLevel.INFO)
```

### Metrics Collection

```python
def analyze_results(results):
    """Analyze and report metrics"""
    
    summary = results['summary']
    
    print("\n📊 METRICS REPORT")
    print("=" * 50)
    print(f"Total Requested: {summary['total_requested']}")
    print(f"Total Retrieved: {summary['total_retrieved']}")
    print(f"Success Rate: {summary['retrieval_rate']}")
    print(f"\nQuality Score Avg: {summary['quality_avg']}")
    print(f"Relevance Score Avg: {summary['relevance_avg']}")
    print(f"Style Confidence Avg: {summary['style_confidence_avg']}")
    print(f"Final Score Avg: {summary['final_score_avg']}")
    print("=" * 50)

# Use it
results = agent.process_request(request)
analyze_results(results)
```

---

## Troubleshooting

### Issue: "No module named 'requests'"

**Solution:** Install requests

```bash
python3 -m pip install requests
```

### Issue: "API rate limiting (HTTP 429)"

**Solution:** Reduce query load

```python
config = AgentConfig(
    max_search_queries=2,
    results_per_source=3
)

# Add delay between requests
import time
time.sleep(3)
```

### Issue: "Timeout waiting for API response"

**Solution:** Increase timeouts

```python
config = AgentConfig(
    api_timeout=10,
    download_timeout=20
)
```

### Issue: "Downloaded file is corrupted"

**Solution:** Check file size and type

```python
result = results['results'][0]
print(f"File size: {result['file_size']}")
print(f"Content type expected based on URL")

# Verify file manually
from pathlib import Path
p = Path(result['local_path'])
if p.stat().st_size > 0:
    print("✓ File exists and has content")
```

### Issue: "Retrieved images don't match query"

**Solution:** Adjust relevance or keyword weights

```python
config = AgentConfig(
    keyword_match_weight=60.0,  # Increase keyword importance
    relevance_weight=0.8        # Increase relevance weight
)
```

### Issue: "Images are wrong style (cartoon vs photo)"

**Solution:** Increase style confidence weight

```python
config = AgentConfig(
    style_confidence_weight=0.4,  # Increase style importance
    min_final_score=60.0
)

# And add style constraint
request = MediaRequest(
    query="...",
    constraints={"style": "cartoon"}
)
```

---

## Performance Benchmarks

### Benchmarks for Different Configurations

#### Fast Config (Development/Testing)
```
Configuration:
- max_search_queries: 2
- results_per_source: 2
- max_retries: 1
- api_timeout: 3s
- download_timeout: 8s

Performance:
- Single request (1 image): 2-4 seconds
- 5 image batch: 5-12 seconds
- API calls: ~8-12 total
- Success rate: 70-80%
```

#### Balanced Config (Production)
```
Configuration:
- max_search_queries: 5
- results_per_source: 5
- max_retries: 3
- api_timeout: 5s
- download_timeout: 10s

Performance:
- Single request (1 image): 5-10 seconds
- 5 image batch: 15-25 seconds
- API calls: ~25-50 total
- Success rate: 85-95%
```

#### Quality Config (Premium Results)
```
Configuration:
- max_search_queries: 10
- results_per_source: 20
- max_retries: 4
- api_timeout: 5s
- download_timeout: 15s

Performance:
- Single request (1 image): 15-30 seconds
- 5 image batch: 45-90 seconds
- API calls: ~200-400 total
- Success rate: 95%+
```

### Optimization Tips

1. **Reduce `max_search_queries`** - Biggest performance impact (each query = multiple API calls)
2. **Reduce `results_per_source`** - Fewer candidates = faster scoring
3. **Reduce `max_retries`** - Fail fast instead of retrying
4. **Increase `min_final_score`** - Download fewer items
5. **Shorten `api_timeout`** - Fail faster on slow APIs

---

## Best Practices

### 1. Always Specify Context

```python
# Good - provides context
request = MediaRequest(
    query="children learning",
    context={"handout": "1_slp_info", "purpose": "cover_image"}
)

# Not as good - lacks context
request = MediaRequest(
    query="children learning"
)
```

### 2. Use Style Constraints When Appropriate

```python
# Good - explicitly specify style
request = MediaRequest(
    query="children learning",
    constraints={"style": "cartoon"}
)

# Only do this if you have a style preference
```

### 3. Set Realistic Quality Expectations

```python
# Realistic: mixed quality is normal
config = AgentConfig(min_final_score=50.0)

# Too strict: very few results
config = AgentConfig(min_final_score=90.0)

# Too lenient: lots of poor quality
config = AgentConfig(min_final_score=30.0)
```

### 4. Handle Partial Results Gracefully

```python
results = agent.process_request(request)

if results['summary']['total_retrieved'] == 0:
    print("⚠ No results found, try different keywords")
elif results['summary']['total_retrieved'] < request.quantity:
    print(f"✓ Partial success: got {results['summary']['total_retrieved']}/{request.quantity}")
else:
    print(f"✓ Full success: got all {request.quantity} items")
```

### 5. Save Results Regularly

```python
import json

results = agent.process_request(request)

# Save full results
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)

# Save summary
with open("results_summary.txt", "w") as f:
    f.write(f"Retrieved: {results['summary']['total_retrieved']}\n")
    f.write(f"Quality avg: {results['summary']['quality_avg']}\n")
```

### 6. Monitor Rate Limits

```python
import time

requests = [
    MediaRequest(query="query1", quantity=3),
    MediaRequest(query="query2", quantity=3),
    MediaRequest(query="query3", quantity=3),
]

for req in requests:
    results = agent.process_request(req)
    time.sleep(2)  # Delay between requests
    print(f"✓ Retrieved {results['summary']['total_retrieved']} items")
```

### 7. Version Your Configuration

```bash
# In your repo
agent_configs/
├── .agent-config.json              # Active config
├── .agent-config.v1.0.json         # Previous version
├── .agent-config.v0.9.json         # Even older
└── README.md                       # Config versioning notes
```

### 8. Test Before Going Live

```python
# Test with small query first
test_request = MediaRequest(
    query="test query",
    quantity=1
)

test_results = agent.process_request(test_request)

if test_results['summary']['total_retrieved'] > 0:
    print("✓ Agent is working")
    # Proceed with full requests
else:
    print("⚠ Agent has issues, check config/network")
    # Debug before proceeding
```

---

## Summary

This guide covers:

✅ Quick 5-minute setup  
✅ Complete installation steps  
✅ 4 common usage patterns  
✅ Advanced configurations  
✅ Integration examples  
✅ Error handling strategies  
✅ Monitoring and metrics  
✅ Troubleshooting guide  
✅ Performance benchmarks  
✅ Best practices checklist  

For detailed configuration options, see **AGENT_CONFIGURATION_GUIDE.md**.
For API reference, see **AGENT_API_REFERENCE.md**.
