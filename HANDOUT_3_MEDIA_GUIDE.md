# Handout 3 Media Guide
## Ontario Resources for Families - Cartoon Media Retrieval

---

## Overview

This guide provides instructions for retrieving community-focused cartoon and illustration images for the "Ontario Resources for Families" handout. The accompanying Python script (`handout_3_cartoon_retrieval.py`) automates retrieval with emphasis on accessibility, support, and community connection themes.

### Handout Resource Categories Covered

1. **Government-Funded Programs** - Community services and public programs
2. **Autism Organizations** - Support groups and advocacy
3. **Parent Training Programs** - Workshops and education
4. **Support Groups & Community** - Family connections and support

---

## Required Cartoon Types & Themes

### Resource 1: Government-Funded Programs (2 images)

**Theme:** Accessible community healthcare and support services

**Ideal Characteristics:**
- Community center or healthcare setting
- Diverse families accessing services
- Inclusive, welcoming environment
- Professional yet approachable tone
- Resources/support visible
- Diverse family representation

**Query Suggestions:**
```
"community resources support services illustration"
"government health program family support cartoon"
"healthcare access children services illustration"
"public program accessibility diverse families cartoon"
"community care support system illustration"
```

**Quality Checklist:**
- ✓ Cartoon/illustration style
- ✓ Community/healthcare setting clear
- ✓ Diverse families shown
- ✓ Accessible and welcoming tone
- ✓ Professional appearance

---

### Resource 2: Autism Organizations (2 images)

**Theme:** Community support, connection, and advocacy

**Ideal Characteristics:**
- People coming together for support
- Group or network emphasis
- Diverse individuals/families
- Positive, supportive atmosphere
- Connection and collaboration visible
- Autism-affirming imagery

**Query Suggestions:**
```
"autism support community network illustration"
"advocacy organization helping families cartoon"
"support group people coming together illustration"
"community organization connection cartoon"
"autism awareness group illustration"
```

**Quality Checklist:**
- ✓ Clear cartoon style
- ✓ Group/community emphasis
- ✓ Supportive atmosphere shown
- ✓ Diverse representation
- ✓ Positive, affirming tone

---

### Resource 3: Parent Training Programs (2 images)

**Theme:** Learning, education, and skill-building workshops

**Ideal Characteristics:**
- Educational/workshop setting
- Parents learning or participating
- Professional facilitator/teacher
- Engagement and learning evident
- Diverse group of participants
- Knowledge-sharing focus

**Query Suggestions:**
```
"parent training workshop education illustration"
"family learning program teaching cartoon"
"educational workshop participants illustration"
"learning opportunity parent child illustration"
"professional training parent support cartoon"
```

**Quality Checklist:**
- ✓ Cartoon illustration style
- ✓ Learning/education setting clear
- ✓ Parents engaged in learning
- ✓ Professional atmosphere
- ✓ Diverse participants shown

---

### Resource 4: Support Groups & Community (2 images)

**Theme:** Family connections, mutual support, and community bonds

**Ideal Characteristics:**
- Multiple families or individuals together
- Supportive, caring interactions
- Community/group setting
- Emotional support and connection visible
- Diverse family types
- Warm, welcoming atmosphere

**Query Suggestions:**
```
"support group community connection illustration"
"family together supportive community cartoon"
"people supporting each other illustration"
"community care network family illustration"
"friends supporting friends cartoon"
```

**Quality Checklist:**
- ✓ Clear cartoon style
- ✓ Community/group setting
- ✓ Support and connection shown
- ✓ Diverse family types depicted
- ✓ Warm, caring tone evident

---

## Expected Image Specifications

### Image Format & Size
- **Format:** PNG, JPG, or WebP
- **Minimum Resolution:** 1280x720 pixels (HD)
- **Recommended Resolution:** 1920x1080 pixels (Full HD)
- **Aspect Ratio:** 16:9 or 4:3 preferred
- **File Size:** Under 2MB for optimal web use

### File Organization
```
media/
└── handout_3_ontario_resources/
    ├── government_funded_programs/
    │   ├── image_1.jpg
    │   └── image_2.jpg
    ├── autism_organizations/
    │   ├── image_1.jpg
    │   └── image_2.jpg
    ├── parent_training_programs/
    │   ├── image_1.jpg
    │   └── image_2.jpg
    └── support_groups_community/
        ├── image_1.jpg
        └── image_2.jpg
```

### Total Images Required
- **Total Target:** 8 cartoon/illustration images (2+2+2+2)
- **Time Estimate:** 15-25 minutes for script to complete
- **Success Rate:** 75-90% (search availability dependent)

---

## Running the Script

### Prerequisites
- Python 3.8+
- `media_gathering_agent.py` in same directory
- Internet connection

### Basic Usage

```bash
# Run with defaults (downloads media)
python3 handout_3_cartoon_retrieval.py

# Preview queries without downloading
python3 handout_3_cartoon_retrieval.py --dry-run

# Verbose debug output
python3 handout_3_cartoon_retrieval.py --verbose

# Custom output and dry run
python3 handout_3_cartoon_retrieval.py --dry-run --verbose --output my_media
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Show search queries without downloading |
| `--verbose` | Show detailed debug/logging output |
| `--output DIR` | Custom output directory (default: `media`) |
| `--help-examples` | Show usage examples |

### Output Files

1. **Media Directory:** `media/handout_3_ontario_resources/[resource]/`
   - Downloaded cartoon images organized by resource type
   
2. **Report File:** `handout_3_retrieval_report.json`
   - Detailed retrieval results with metadata
   - Quality/relevance scores for each image
   - Search queries used
   - Completion statistics

---

## Optimization Tips

### For Community & Accessibility Focus

1. **Emphasis on Inclusion**
   - Script prioritizes diverse representation
   - Keywords emphasize "community", "support", "inclusive"
   - Filters clinical/formal imagery
   - Focuses on accessibility themes

2. **Multiple Runs for Variety**
   - Run script 2-3 times for different selections
   - Results vary based on API availability
   - Allows curation of best options

3. **Diversity Verification**
   - After retrieval, verify:
     - Multiple ethnicities represented
     - Various family structures shown
     - People with visible disabilities included
     - Accessible settings depicted
     - Socioeconomic diversity visible

4. **Tone Matching**
   - Script avoids clinical/medical imagery
   - Emphasizes warm, welcoming appearance
   - Focuses on human connection
   - Supports resource accessibility message

### Adjusting Configuration

Edit `handout_3_cartoon_retrieval.py` to modify:

```python
# Change target quantity per resource
Resource(
    name="Government-Funded Programs",
    ...
    target_quantity=3,  # Increase from 2
    ...
)

# Adjust quality preferences
request = MediaRequest(
    ...
    quality="professional",  # or "high"
    licensing="free"  # free commercial use
)

# Enhance community keywords
style_keywords={
    'cartoon': {
        'positive': [
            'community', 'support', 'inclusive', 'diverse',
            'accessible', 'connection', 'together', ...
        ]
    }
}
```

---

## Integration into Handout

### Size Recommendations by Section

| Resource Category | Size | Notes |
|-------------------|------|-------|
| Programs header | 1920x1200 | Full visual impact |
| Organization intro | 1200x800 | Section emphasis |
| Training divider | 960x640 | Visual break |
| Support group intro | 800x600 | Medium emphasis |
| Inline reference | 400x300 | Supplementary |

### Strategic Placement

**Government-Funded Programs Section:**
- One image at top of section
- Shows accessibility/welcome
- Places before organization listings

**Autism Organizations:**
- Community/group image
- Emphasize network and support
- Insert before chapter information

**Parent Training Programs:**
- Learning/education image
- Emphasize active participation
- Place near program descriptions

**Support Groups & Community:**
- Connection-focused image
- Emphasize mutual support
- Use prominently (end of handout)

---

## Accessibility & Representation Checklist

### Diversity Verification
- [ ] Multiple ethnicities across all images
- [ ] Various family structures:
  - [ ] Two-parent families
  - [ ] Single-parent families
  - [ ] Same-sex couples/LGBTQ+ families
  - [ ] Grandparents/extended family
  - [ ] Adoptive families
- [ ] People with visible disabilities represented
- [ ] Age range varies (young to older parents)
- [ ] Socioeconomic diversity shown
- [ ] Cultural diversity visible

### Accessibility Considerations
- [ ] Inclusive facility/environment shown
- [ ] Wheelchair accessibility visible (where relevant)
- [ ] Sign language/AAC not tokenized
- [ ] Assistive devices respected
- [ ] Diverse body types represented
- [ ] No harmful stereotypes

### Resource Message Alignment
- [ ] Imagery shows resources are available
- [ ] Welcoming/accessible tone evident
- [ ] Professional yet approachable
- [ ] Support and connection emphasized
- [ ] Empowering not patronizing
- [ ] Forward-looking, hopeful tone

---

## Quality Checklist Before Integration

### Visual Quality
- [ ] Cartoon/illustration style (not photograph)
- [ ] Minimum 1280x720 resolution
- [ ] Clear, professional appearance
- [ ] Vibrant, appropriate colors
- [ ] No watermarks or text overlays
- [ ] High-quality illustration

### Content Appropriateness
- [ ] Community/support theme clear
- [ ] Diversity and inclusion evident
- [ ] Accessibility-conscious imagery
- [ ] Professional yet welcoming
- [ ] Free of harmful stereotypes
- [ ] Culturally respectful

### Licensing & Rights
- [ ] CC0 or free commercial license confirmed
- [ ] No watermarks visible
- [ ] Attribution/credit noted if required
- [ ] Source documented
- [ ] Rights verified before use

### Handout Alignment
- [ ] Color scheme matches handout
- [ ] Consistent illustration style
- [ ] Supports resource information
- [ ] Appropriate for parent audience
- [ ] Professional presentation
- [ ] Inclusive and welcoming

---

## Troubleshooting

### Script Issues

**Problem: Returns 0 images**
```
Solution:
1. Run with --verbose to see errors
2. Check internet connection
3. Verify media_gathering_agent.py location
4. Try running again later (API limits)
5. Review error messages in output
```

**Problem: Images don't look like community/support themes**
```
Solution:
1. Run multiple times for variety
2. Use --dry-run first to preview
3. Edit style_keywords for emphasis
4. Try alternative search terms
5. Lower min_final_score threshold
```

**Problem: Low diversity in images**
```
Solution:
1. Run script multiple times
2. Manually supplement selections
3. Curate diverse subset from results
4. Use custom search queries
5. Consider supplementing from Pixabay/Unsplash
```

**Problem: Script hangs/times out**
```
Solution:
1. Check internet connectivity
2. Verify API availability
3. Increase timeout values in config
4. Reduce quantity targets
5. Try running fewer resources at once
```

---

## Advanced Customization

### Community-Focused Keywords

Enhance the style_keywords configuration:

```python
'positive': [
    # Community themes
    'community', 'support', 'group', 'network',
    'connection', 'together', 'collaboration',
    'helping', 'caring', 'supportive',
    
    # Accessibility themes
    'inclusive', 'accessible', 'diverse',
    'welcoming', 'open', 'accepting',
    'disability-friendly', 'all abilities',
    
    # Healthcare/support
    'program', 'service', 'resource', 'care',
    'health', 'wellness', 'education', 'training',
    
    # Emotions
    'hope', 'positive', 'joy', 'connection',
    'understanding', 'empathetic', 'compassionate'
],
'negative': [
    'photo', 'photograph', 'real', 'realistic',
    'clinical', 'medical', 'formal', 'serious business',
    'corporate', 'stock photo', 'professional photo'
]
```

### Confidence Adjustment

For stronger community emphasis:

```python
config = AgentConfig(
    # Increase to prioritize cartoons
    style_confidence_weight=0.35,  # Default: 0.3
    
    # Lower to accept more variety
    min_final_score=42.0,  # Default: 45.0
    
    # Emphasize query relevance
    relevance_weight=0.55,  # Default: 0.5
)
```

---

## Document Integration

### Caption Examples

Include descriptive captions with images:

```
Government-Funded Programs:
"Ontario offers free and subsidized services to 
support families with autism. Discover what's 
available in your community."

Autism Organizations:
"Connect with other families and get support from 
autism advocacy organizations across Ontario."

Parent Training Programs:
"Attend workshops and training programs to learn 
evidence-based strategies for supporting your child."

Support Groups & Community:
"You're not alone. Find support groups and 
community resources near you."
```

### Color Scheme Harmony
- [ ] Complement handout primary colors
- [ ] Maintain consistency across all 8 images
- [ ] Use warm, welcoming tones
- [ ] Avoid too much contrast
- [ ] Professional but approachable palette

### Layout Integration Example
```
[Resource 1 - Header Image]
[Text content and resource list]

[Resource 2 - Integration with text]
Text flows around image
[Image 2]

[Text] [Resource 3 - Image in corner]

[Resource 4 - Full width image at bottom]
```

---

## File License & Attribution

### Generated Report Format

```json
{
  "handout": "HANDOUT_3_Ontario_Resources",
  "resources": {
    "Government-Funded Programs": {
      "results": [
        {
          "title": "Community Resources Image",
          "source": "unsplash",
          "license": "cc0",
          "quality_score": 84.0,
          "relevance_score": 79.0,
          "style_confidence": 0.90,
          "final_score": 81.2
        }
      ]
    }
  },
  "summary": {
    "completion_rate": "100%",
    "total_retrieved": 8
  }
}
```

### Required Attribution

Include at handout bottom or end:

```
Images sourced from:
- Unsplash (unsplash.com)
- Pexels (pexels.com)

Licensed under Creative Commons CC0
Free for commercial and personal use
```

---

## Next Steps & Workflow

### Post-Retrieval Workflow

1. **Selection & Review** (10 minutes)
   - Download all images to local folder
   - Review each for quality and relevance
   - Select best 8 images
   - Verify diversity and representation

2. **Optimization** (15 minutes)
   - Resize for handout layout
   - Optimize file sizes (max 2MB each)
   - Add subtle borders if desired
   - Test print quality

3. **Integration** (20 minutes)
   - Place images in handout document
   - Add captions and context
   - Adjust layout for best flow
   - Verify color scheme harmony

4. **Final QA** (10 minutes)
   - Review entire handout
   - Check image quality in print
   - Verify diversity and inclusion
   - Proofread captions

### Alternative Image Sources

If script results insufficient:

- **Pixabay** (pixabay.com) - Free stock images
- **Unsplash Direct** (unsplash.com/search) - Browse directly
- **Pexels Direct** (pexels.com/search) - Direct search
- **Freepik** (freepik.com) - With attribution
- **Iconfinder** (iconfinder.com) - Icons and illustrations

### Batch Processing

Run all three handouts in sequence:

```bash
# Script for batch retrieval
python3 handout_1_cartoon_retrieval.py
python3 handout_2_cartoon_retrieval.py  
python3 handout_3_cartoon_retrieval.py

# Generates three separate report files
# Each with organized media directories
```

---

## Document Metadata

| Property | Value |
|----------|-------|
| Created | 2025-12-07 |
| Version | 1.0 |
| Handout | HANDOUT_3_Ontario_Resources.md |
| Media Type | Community-Focused Cartoon/Illustration |
| Total Images | 8 |
| Estimated Time | 15-25 minutes |
| Emphasis | Accessibility, Diversity, Community |

---

## Support Resources

### For Questions About:
- **Script functionality:** See `handout_3_cartoon_retrieval.py` comments
- **Media gathering:** Check `media_gathering_agent.py` documentation
- **Style scoring:** Review confidence calculation in agent source
- **Configuration:** Edit AgentConfig in script for custom behavior

### Contact & Feedback
If you encounter issues or have suggestions:
1. Check script output and error messages
2. Review troubleshooting section above
3. Examine JSON report for metadata details
4. Consider running with `--verbose` flag

---

**Ready to retrieve community-focused media?** Start with:
```bash
python3 handout_3_cartoon_retrieval.py
```
