# Handout 1 Media Guide
## What is a Speech-Language Pathologist? - Cartoon Media Retrieval

---

## Overview

This guide provides instructions for retrieving high-quality cartoon and illustration images for the "What is a Speech-Language Pathologist?" handout. The accompanying Python script (`handout_1_cartoon_retrieval.py`) automates the retrieval process with optimized cartoon detection.

### Handout Sections Covered

1. **Who Are We?** - SLPs with children
2. **How SLPs Help Children with Autism** - Learning/communication
3. **What Makes SLP Services Unique?** - Collaborative care
4. **What to Expect from SLP Services** - Assessment/therapy

---

## Required Cartoon Types & Themes

### Section 1: Who Are We? (3 images)

**Theme:** Professional SLPs engaged with children in interactive, friendly settings

**Ideal Characteristics:**
- Speech/language pathologist or therapist with child(ren)
- Diverse representation (gender, ethnicity, abilities)
- Clinical but warm environment (therapy room, playroom)
- One-on-one or small group interaction
- Smiling, engaged, positive interactions
- Age range: children (toddlers to school-age)

**Query Suggestions:**
```
"speech pathologist working with children cartoon illustration"
"therapist helping child communicate fun playful illustration"
"diverse children learning with adult support cartoon"
"SLP assessment session cartoon illustration"
"professional woman working with kids educational cartoon"
```

**Quality Checklist:**
- ✓ Clear illustration style (not photograph)
- ✓ Child's face visible or partially visible
- ✓ Professional yet approachable appearance
- ✓ Diverse representation of families
- ✓ Positive/encouraging interaction

---

### Section 2: How SLPs Help Children with Autism (3 images)

**Theme:** Communication development and learning support

**Ideal Characteristics:**
- Child engaged in learning activity
- Visual supports or communication tools present
- Play-based learning environment
- Therapist/educator supporting child
- Diverse learner representation
- Autism-affirming imagery

**Query Suggestions:**
```
"child learning communication skills cartoon illustration"
"autism communication therapy playful cartoon"
"children developing language skills fun illustration"
"visual supports communication learning cartoon"
"social communication skills development cartoon"
```

**Quality Checklist:**
- ✓ Clear cartoon/illustration style
- ✓ Communication-focused activity
- ✓ Positive, supportive environment
- ✓ Neurodiversity-affirming representation
- ✓ Age-appropriate children depicted

---

### Section 3: What Makes SLP Services Unique? (2 images)

**Theme:** Collaboration and family-centered approach

**Ideal Characteristics:**
- Multiple professionals working together
- Parents/caregivers included in process
- Teamwork emphasis
- Family involvement visible
- Supportive, collaborative atmosphere
- Diverse team composition

**Query Suggestions:**
```
"team collaboration healthcare professionals cartoon"
"family centered care parents children illustration"
"multidisciplinary team working together cartoon"
"therapist explaining to parents illustration"
"collaborative support network children cartoon"
```

**Quality Checklist:**
- ✓ Cartoon/illustration style
- ✓ Shows teamwork/collaboration
- ✓ Family/caregiver involvement evident
- ✓ Professional but approachable
- ✓ Diverse representation

---

### Section 4: What to Expect from SLP Services (2 images)

**Theme:** Assessment and therapy processes

**Ideal Characteristics:**
- Assessment or therapy activity in progress
- Child actively participating
- Age-appropriate activity depicted
- Professional conducting assessment/therapy
- Positive interaction
- Clear clinical context

**Query Suggestions:**
```
"therapy assessment children cartoon illustration"
"speech therapist assessing child communication"
"progress monitoring therapy session cartoon"
"play-based learning therapy illustration"
"individualized treatment plan cartoon"
```

**Quality Checklist:**
- ✓ Cartoon illustration style
- ✓ Clinical context clear but warm
- ✓ Child engaged and comfortable
- ✓ Professional interaction quality
- ✓ Assessment/therapy activity evident

---

## Expected Image Specifications

### Image Format & Size
- **Format:** PNG, JPG, or WebP
- **Minimum Resolution:** 1280x720 pixels (HD)
- **Recommended Resolution:** 1920x1080 pixels (Full HD)
- **Aspect Ratio:** 16:9 or 4:3 preferred

### File Organization
```
media/
└── handout_1_slp_info/
    ├── who_are_we/
    │   ├── image_1.jpg
    │   ├── image_2.jpg
    │   └── image_3.jpg
    ├── how_slps_help_autism/
    │   ├── image_1.jpg
    │   ├── image_2.jpg
    │   └── image_3.jpg
    ├── what_makes_unique/
    │   ├── image_1.jpg
    │   └── image_2.jpg
    └── what_to_expect/
        ├── image_1.jpg
        └── image_2.jpg
```

### Total Images Required
- **Total Target:** 10 cartoon/illustration images
- **Time Estimate:** 15-30 minutes for script to complete
- **Success Rate:** 70-90% (depends on search availability)

---

## Running the Script

### Prerequisites
- Python 3.8+
- `media_gathering_agent.py` in same directory
- Internet connection

### Basic Usage

```bash
# Run with defaults (downloads media)
python3 handout_1_cartoon_retrieval.py

# Preview queries without downloading
python3 handout_1_cartoon_retrieval.py --dry-run

# Verbose debug output
python3 handout_1_cartoon_retrieval.py --verbose

# Combine options
python3 handout_1_cartoon_retrieval.py --dry-run --verbose --output my_media
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Show search queries without downloading |
| `--verbose` | Show detailed debug/logging output |
| `--output DIR` | Custom output directory (default: `media`) |
| `--help-examples` | Show usage examples |

### Output Files

1. **Media Directory:** `media/handout_1_slp_info/[section]/`
   - Downloaded cartoon images organized by section
   
2. **Report File:** `handout_1_retrieval_report.json`
   - Detailed retrieval results with metadata
   - Quality/relevance scores for each image
   - Search queries used
   - Completion statistics

---

## Optimization Tips

### For Better Results

1. **Run During Off-Peak Hours**
   - API rate limits may affect results
   - Run early morning or late evening
   - Reduces competition for bandwidth

2. **Multiple Runs**
   - Script may retrieve different images on subsequent runs
   - Run 2-3 times if you need more variety
   - Different search terms may yield better results

3. **Manual Curation**
   - Review generated images before use
   - Ensure diversity in handout visuals
   - Verify alignment with presentation tone

4. **Quality Settings**
   - Script prioritizes professional quality
   - Uses high resolution preferences
   - Focuses on CC0/free licenses

### Adjusting Configuration

Edit `handout_1_cartoon_retrieval.py` to modify:

```python
# Change target quantity per section
Section(
    name="Who Are We?",
    ...
    target_quantity=5,  # Increase from 3
    ...
)

# Adjust quality/licensing requirements
request = MediaRequest(
    ...
    quality="high",  # or "professional"
    licensing="free"  # or "cc0", "commercial", "any"
)
```

---

## Integration into Handout

### Size Recommendations

| Usage | Size |
|-------|------|
| Full-page image | 1920x1440 or 1600x1200 |
| Half-page | 960x720 |
| Quarter-page | 640x480 |
| Thumbnail | 300x225 |

### Placement Suggestions

**Who Are We? Section:**
- Large image (full/half page) at top
- Shows professional interaction

**How SLPs Help Children with Autism:**
- 2-3 medium images
- Distributed through section
- Show variety of support approaches

**What Makes SLP Services Unique?:**
- Collaboration/teamwork image
- Insert before key bullet points

**What to Expect from SLP Services:**
- Assessment and therapy images
- Visual timeline of process

---

## Quality Checklist Before Use

### Visual Quality
- [ ] Image is cartoon/illustration style (not photograph)
- [ ] Resolution is at least 1280x720
- [ ] Colors are vibrant and age-appropriate
- [ ] Text overlay is minimal/absent

### Content Appropriateness
- [ ] Depicts diverse families and professionals
- [ ] Shows positive, supportive interactions
- [ ] Autism/neurodiversity-affirming
- [ ] Family-friendly and professional tone

### Licensing & Rights
- [ ] License is CC0 or free commercial use
- [ ] No watermarks visible
- [ ] Source is noted in credits
- [ ] Photographer/artist credited if required

### Handout Alignment
- [ ] Matches handout color scheme
- [ ] Supports message of section
- [ ] Appropriate for parent audience
- [ ] Culturally respectful and inclusive

---

## Troubleshooting

### No Images Retrieved
**Problem:** Script completes but retrieves 0 images

**Solutions:**
1. Run with `--verbose` to see detailed errors
2. Check internet connection
3. Try again later (API rate limits)
4. Manually adjust search queries
5. Lower `min_final_score` in config

### Low Quality Images
**Problem:** Retrieved images don't look like cartoons

**Solutions:**
1. Run again - search results vary
2. Increase `style_confidence_weight` in config
3. Use more specific queries
4. Try `--dry-run` first to verify queries

### Script Hangs/Timeouts
**Problem:** Script appears frozen or times out

**Solutions:**
1. Check internet connection
2. Increase timeout values in config
3. Reduce `quantity` or `results_per_source`
4. Try running with fewer sections

### API Rate Limiting
**Problem:** Getting HTTP 429 errors

**Solutions:**
1. Wait 15-30 minutes before retrying
2. Space out runs by several hours
3. Use different search terms
4. Reduce search frequency

---

## Advanced Configuration

### Custom Style Keywords

Edit the `create_cartoon_optimized_config()` function to customize:

```python
'cartoon': {
    'positive': [
        # Add your keywords here
        'animation', 'drawing', 'cute', ...
    ],
    'negative': [
        # Keywords to exclude
        'photo', 'realistic', ...
    ]
}
```

### Scoring Adjustments

```python
config = AgentConfig(
    # Style weight - higher = prioritize cartoons more
    style_confidence_weight=0.4,  # Default: 0.3
    
    # Minimum score threshold - lower = accept more results
    min_final_score=40.0,  # Default: 45.0
    
    # Quality emphasis
    quality_weight=0.4,  # Default: 0.3
)
```

---

## File License Information

### Generated Report Structure

```json
{
  "handout": "HANDOUT_1_What_Is_SLP",
  "sections": {
    "Who Are We?": {
      "results": [
        {
          "title": "Image Title",
          "source": "unsplash",
          "license": "cc0",
          "quality_score": 85.0,
          "relevance_score": 75.0,
          "style_confidence": 0.92,
          "final_score": 80.3
        }
      ]
    }
  },
  "summary": {
    "completion_rate": "100%",
    "total_retrieved": 10,
    "total_requested": 10
  }
}
```

---

## Credits & Attribution

### Sources Used
- **Unsplash:** High-quality free images
- **Pexels:** Professional photos and illustrations
- **CC0 License:** All images free to use commercially

### In Handout Footer
```
Images sourced from:
- Unsplash (unsplash.com)
- Pexels (pexels.com)

Licensed under Creative Commons CC0
Free for commercial and personal use
```

---

## Support & Next Steps

### If You Need Help
1. Check script output for specific error messages
2. Review troubleshooting section above
3. Check `media_gathering_agent.py` documentation
4. Examine JSON report for detailed metadata

### Alternative Approaches
- Manually search on Unsplash/Pexels
- Use Google Images with CC0/creative commons filter
- Purchase from microstock sites (Shutterstock, Getty)
- Commission custom illustrations

### For Multiple Handouts
Run scripts in sequence:
```bash
python3 handout_1_cartoon_retrieval.py
python3 handout_2_cartoon_retrieval.py  
python3 handout_3_cartoon_retrieval.py
```

Each creates organized subdirectories and separate reports.

---

## Document Metadata

| Property | Value |
|----------|-------|
| Created | 2025-12-07 |
| Version | 1.0 |
| Handout | HANDOUT_1_What_Is_SLP.md |
| Media Type | Cartoon/Illustration |
| Total Images | 10 |
| Estimated Time | 15-30 minutes |

---

**Need more information?** Check the comments in `handout_1_cartoon_retrieval.py` for implementation details.
