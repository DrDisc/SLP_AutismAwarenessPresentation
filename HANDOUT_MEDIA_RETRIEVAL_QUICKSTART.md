# Handout Media Retrieval System - Quick Start Guide

## What Was Created

This package includes production-ready scripts and comprehensive guides for retrieving cartoon and illustration media for three SLP handouts.

### Files Created (6 Total)

#### Python Scripts (3)
1. **handout_1_cartoon_retrieval.py** (15 KB)
   - Retrieves images for: "What is a Speech-Language Pathologist?"
   - Targets: 10 cartoon images across 4 sections
   - Time: 15-30 minutes
   - Sections: Who Are We, How SLPs Help, Unique Services, What to Expect

2. **handout_2_cartoon_retrieval.py** (15 KB)
   - Retrieves images for: "10 Ways to Encourage Communication at Home"
   - Targets: 11 cartoon images across 4 strategies
   - Time: 20-35 minutes
   - Strategies: Eye Level, Follow Lead, Celebrate Communication, Create Routines

3. **handout_3_cartoon_retrieval.py** (15 KB)
   - Retrieves images for: "Ontario Resources for Families"
   - Targets: 8 cartoon images across 4 resource categories
   - Time: 15-25 minutes
   - Resources: Government Programs, Organizations, Training, Support Groups

#### Markdown Guides (3)
1. **HANDOUT_1_MEDIA_GUIDE.md** (13 KB)
   - Complete guide for Handout 1 media retrieval
   - Cartoon types & themes required
   - Query suggestions for each section
   - Quality checklist & troubleshooting

2. **HANDOUT_2_MEDIA_GUIDE.md** (16 KB)
   - Complete guide for Handout 2 media retrieval
   - Family-friendly cartoon focus
   - Diversity & representation checklist
   - Integration tips for handout layout

3. **HANDOUT_3_MEDIA_GUIDE.md** (17 KB)
   - Complete guide for Handout 3 media retrieval
   - Community & accessibility focus
   - Diversity verification checklist
   - Integration strategies

---

## Quick Start (2 Minutes)

### Run All Three Scripts in Sequence

```bash
# Navigate to project directory
cd /home/tng/repos/github/SLP_AutismAwarenessPresentation

# Run all three in order
python3 handout_1_cartoon_retrieval.py
python3 handout_2_cartoon_retrieval.py
python3 handout_3_cartoon_retrieval.py
```

### Expected Output

- **Media Files:** `media/handout_1_slp_info/`, `media/handout_2_communication_strategies/`, `media/handout_3_ontario_resources/`
- **Reports:** `handout_1_retrieval_report.json`, `handout_2_retrieval_report.json`, `handout_3_retrieval_report.json`
- **Total Media:** ~29 cartoon/illustration images (10 + 11 + 8)

---

## Features

### Scripts Include:

✅ **Cartoon-Optimized Detection**
- Style confidence scoring (0-1 scale)
- Keyword matching for illustration vs. photography
- Automatic filtering of non-cartoon images

✅ **Error Handling & Retry Logic**
- Exponential backoff retry (1s, 2s, 4s, etc.)
- Graceful handling of API failures
- Comprehensive logging

✅ **Organized Output**
- Media organized by section/strategy/resource
- JSON reports with quality metrics
- Metadata tracking for each image

✅ **Configurable Behavior**
- Adjust target quantities
- Customize quality preferences
- Modify style keywords
- Control logging levels

✅ **Production-Ready**
- Type hints throughout
- Comprehensive docstrings
- Error handling best practices
- Configurable via dataclasses

### Guides Include:

✅ **Detailed Requirements**
- Ideal characteristics for each section
- Multiple query suggestions
- Quality checklists

✅ **Integration Tips**
- Size recommendations by usage
- Strategic placement suggestions
- Color scheme guidance

✅ **Comprehensive Checklists**
- Visual quality verification
- Content appropriateness
- Licensing & rights confirmation
- Diversity & representation

✅ **Troubleshooting**
- Common issues and solutions
- Advanced customization
- Alternative sources
- API rate limit handling

---

## Script Usage Examples

### Basic Retrieval (Standard)
```bash
python3 handout_1_cartoon_retrieval.py
```
- Downloads media directly
- Saves JSON report
- Creates organized media directories

### Dry Run (Preview Queries)
```bash
python3 handout_1_cartoon_retrieval.py --dry-run
```
- Shows all search queries without downloading
- Good for previewing before running

### Verbose Output (Debug)
```bash
python3 handout_1_cartoon_retrieval.py --verbose
```
- Detailed logging
- Shows scoring calculations
- Helpful for troubleshooting

### Custom Output Directory
```bash
python3 handout_1_cartoon_retrieval.py --output my_media
```
- Saves to custom location
- Good for organization

### Combine Options
```bash
python3 handout_1_cartoon_retrieval.py --dry-run --verbose
```
- Preview with detailed output

---

## Output Structure

After running scripts, you'll have:

```
media/
├── handout_1_slp_info/
│   ├── Who Are We/
│   │   ├── image_1.jpg
│   │   ├── image_2.jpg
│   │   └── image_3.jpg
│   ├── How SLPs Help Children with Autism/
│   ├── What Makes SLP Services Unique?/
│   └── What to Expect from SLP Services/
│
├── handout_2_communication_strategies/
│   ├── Get Down to Their Level/
│   ├── Follow Your Child's Lead/
│   ├── Celebrate ALL Communication/
│   └── Create Routines and Rituals/
│
└── handout_3_ontario_resources/
    ├── Government-Funded Programs/
    ├── Autism Organizations/
    ├── Parent Training Programs/
    └── Support Groups & Community/

Reports:
├── handout_1_retrieval_report.json
├── handout_2_retrieval_report.json
└── handout_3_retrieval_report.json
```

---

## Key Features by Handout

### Handout 1: SLP Introduction
**Focus:** Professional, educational cartoon style
- Shows SLP-child interactions
- Emphasizes expertise and family involvement
- Images: 10 total (organized by section)
- Style: Professional yet warm

**Key Queries:**
- Speech pathologist working with children
- Therapy assessment and progress monitoring
- Team collaboration and family involvement

---

### Handout 2: Communication Strategies
**Focus:** Family-friendly, playful cartoon style
- Shows parent-child interactions
- Emphasizes connection and joy
- Images: 11 total (organized by strategy)
- Style: Warm, inviting, celebratory

**Key Queries:**
- Parent at child's eye level
- Child exploring interests
- Family celebrations and routines
- Diverse family types

---

### Handout 3: Ontario Resources
**Focus:** Community and accessibility-focused style
- Shows group support and resources
- Emphasizes inclusion and connection
- Images: 8 total (organized by resource type)
- Style: Professional yet welcoming

**Key Queries:**
- Community support services
- Autism advocacy organizations
- Parent training workshops
- Family support networks

---

## Configuration Details

### All Scripts Use:

**Agent Configuration:**
```python
AgentConfig(
    max_search_queries=5,
    results_per_source=5,
    min_final_score=45.0,
    style_confidence_weight=0.3,  # Cartoon emphasis
    quality_weight=0.3,
    relevance_weight=0.5,
    max_retries=3,
    retry_delay_base=1.0,
)
```

**Search Sources:**
- Unsplash (primary)
- Pexels (secondary)

**Licensing:**
- CC0 (no attribution required)
- Free commercial use

**Quality Targets:**
- Minimum resolution: 1280x720 (HD)
- Preferred: 1920x1080 (Full HD)
- Format: PNG, JPG, WebP

---

## Customization Guide

### Modify Script Behavior

**Change Quantity per Section:**
Edit the `Section` or `Strategy` or `Resource` dataclass:
```python
Section(
    name="Who Are We?",
    ...
    target_quantity=5,  # Change from 3
)
```

**Adjust Quality Requirements:**
Edit the `MediaRequest`:
```python
request = MediaRequest(
    ...
    quality="high",  # or "professional", "medium"
    licensing="cc0"  # or "free", "commercial", "any"
)
```

**Modify Style Keywords:**
Edit the `create_*_optimized_config()` function to add/remove keywords.

**Change Scoring Weights:**
Edit `AgentConfig` parameters:
```python
style_confidence_weight=0.4,  # Higher = stricter cartoon detection
min_final_score=40.0,  # Lower = accept more results
```

---

## Requirements

### System Requirements
- Python 3.8+
- Internet connection
- ~500MB disk space for media

### Dependencies
- `requests` (auto-installed by media_gathering_agent.py)
- No additional packages needed

### Estimated Time
- **Per Script:** 15-35 minutes
- **All Three:** 50-90 minutes
- **Review & Curation:** 30-60 minutes
- **Integration:** 30-60 minutes
- **Total Project:** 2-4 hours

---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| No images retrieved | Run with `--verbose`, check internet, try again later |
| Wrong image style | Run again (results vary), increase `style_confidence_weight` |
| Script times out | Check connection, reduce quantities, increase timeouts |
| Low diversity | Run multiple times, manually supplement, curate selection |
| API rate limiting | Wait 15-30 minutes, space out runs by hours |

---

## Best Practices

### Before Integration:
1. ✅ Run all three scripts
2. ✅ Review generated JSON reports
3. ✅ Verify image quality and style
4. ✅ Check diversity representation
5. ✅ Confirm licenses (CC0/free)

### During Integration:
1. ✅ Match color scheme to handout
2. ✅ Maintain consistent illustration style
3. ✅ Use strategic placement
4. ✅ Add descriptive captions
5. ✅ Test print quality

### Final QA:
1. ✅ Verify all images display properly
2. ✅ Check file sizes (optimize if needed)
3. ✅ Confirm diverse representation
4. ✅ Review captions and context
5. ✅ Test on different devices/browsers

---

## Next Steps

1. **Review Guides**
   - Read HANDOUT_1_MEDIA_GUIDE.md
   - Read HANDOUT_2_MEDIA_GUIDE.md
   - Read HANDOUT_3_MEDIA_GUIDE.md

2. **Run Scripts** (In Order)
   ```bash
   python3 handout_1_cartoon_retrieval.py
   python3 handout_2_cartoon_retrieval.py
   python3 handout_3_cartoon_retrieval.py
   ```

3. **Review Results**
   - Check `media/` directory
   - Review JSON reports
   - Verify image quality

4. **Curate Selection**
   - Choose best images for each section
   - Verify diversity
   - Confirm alignment with handout

5. **Integrate into Handouts**
   - Add images to documents
   - Add captions/context
   - Adjust layout as needed
   - Verify print quality

---

## File Manifest

### Python Scripts
- `handout_1_cartoon_retrieval.py` - 15 KB - Production ready ✅
- `handout_2_cartoon_retrieval.py` - 15 KB - Production ready ✅
- `handout_3_cartoon_retrieval.py` - 15 KB - Production ready ✅

### Markdown Guides
- `HANDOUT_1_MEDIA_GUIDE.md` - 13 KB - Production ready ✅
- `HANDOUT_2_MEDIA_GUIDE.md` - 16 KB - Production ready ✅
- `HANDOUT_3_MEDIA_GUIDE.md` - 17 KB - Production ready ✅

### Total Size
- **Scripts:** 45 KB
- **Guides:** 46 KB
- **Total Documentation:** 91 KB

---

## Support

### For Technical Issues:
1. Check script output and error messages
2. Run with `--verbose` flag
3. Review guide troubleshooting section
4. Check JSON report for metadata

### For Media Issues:
1. Run multiple times for variety
2. Adjust style keywords in script
3. Modify search queries
4. Manually supplement from sources

### For Integration Issues:
1. Review placement suggestions in guides
2. Check color scheme matching
3. Verify image resolution/quality
4. Ensure diversity representation

---

**Ready to get started? Run:**
```bash
python3 handout_1_cartoon_retrieval.py
```

Good luck with your SLP awareness presentation! 🎉
