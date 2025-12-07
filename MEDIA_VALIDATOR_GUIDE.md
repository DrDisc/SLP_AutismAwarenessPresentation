# Media Validator Agent Documentation

## Overview

The **Media Validator Agent** (`media_validator.py`) is a production-ready validation system that verifies and scores retrieved media before integration into presentation handouts. It provides comprehensive quality gates with detailed reporting and recommendations.

### Key Features

- **Cartoon Style Verification**: Analyzes image properties to confirm cartoon/illustration style
- **Content Validation**: Verifies relevance to SLP, families, children, communication, and support
- **Visual Quality Checks**: Analyzes resolution, brightness, color schemes, and compression artifacts
- **Diversity Assessment**: Evaluates representation indicators across demographics
- **Autism Awareness Compliance**: Ensures content is respectful, positive, and affirming
- **Batch Processing**: Validates multiple images with detailed per-image reports
- **Configurable Thresholds**: Customize scoring requirements for different contexts
- **Integration Ready**: Works seamlessly with `media_gathering_agent.py`
- **Production Logging**: Detailed logging with emoji indicators for CLI output
- **JSON Reporting**: Generates comprehensive reports for analysis and archiving

## Installation & Dependencies

### Required Dependencies

```bash
# Pillow is auto-installed if missing
pip install Pillow
pip install pytest  # For running tests
```

### Auto-Installation

The validator automatically installs missing dependencies:

```python
from media_validator import MediaValidator

# If Pillow is missing, it will be installed automatically
validator = MediaValidator()
```

## Quick Start

### Basic Usage

```python
from media_validator import MediaValidator, LogLevel

# Initialize validator with default settings
validator = MediaValidator(log_level=LogLevel.INFO)

# Validate a single image
result = validator.validate_image("path/to/image.jpg")

print(f"Status: {result.pass_status}")
print(f"Score: {result.overall_score:.0f}/100")
print(f"Valid: {result.is_valid}")
```

### Batch Validation

```python
from pathlib import Path

# Validate all images in a directory
image_files = list(Path("media/handout_1").glob("*.{jpg,png}"))

valid, failed = validator.validate_batch(
    [str(f) for f in image_files],
    handout_name="handout_1"
)

print(f"Valid: {len(valid)}, Failed: {len(failed)}")
```

### Generate Reports

```python
# Create validation report
report = validator.generate_report(
    valid_results=valid,
    failed_results=failed,
    handout_name="handout_1",
    output_path="validation_report.json"
)

# Report contains:
# - Metadata (timestamp, handout name)
# - Summary statistics (pass rate, average scores)
# - Detailed validation results
# - Recommendations for improvement
```

## Configuration

### ValidatorConfig Parameters

```python
from media_validator import ValidatorConfig, MediaValidator

config = ValidatorConfig(
    # Style validation (0-1 scale)
    min_cartoon_confidence=0.6,
    
    # Content validation (0-100 scale)
    min_content_score=60.0,
    
    # Quality validation (0-100 scale)
    min_quality_score=50.0,
    min_resolution_width=400,
    min_resolution_height=300,
    
    # Diversity validation (0-100 scale)
    min_diversity_score=40.0,
    
    # Appropriateness validation (0-100 scale)
    min_appropriateness_score=70.0,
    
    # Overall threshold
    min_overall_score=65.0,
    
    # Scoring weights (sum should equal 1.0)
    cartoon_weight=0.15,
    content_weight=0.25,
    quality_weight=0.20,
    diversity_weight=0.15,
    appropriateness_weight=0.25,
)

validator = MediaValidator(config=config)
```

### Adjusting for Different Use Cases

**For high quality presentations:**
```python
config = ValidatorConfig(
    min_overall_score=80.0,
    min_cartoon_confidence=0.75,
    min_content_score=75.0,
    min_quality_score=75.0,
    min_appropriateness_score=85.0,
)
```

**For general content:**
```python
config = ValidatorConfig(
    min_overall_score=65.0,
    min_cartoon_confidence=0.6,
    min_content_score=60.0,
    min_quality_score=50.0,
)
```

**For diverse representation priority:**
```python
config = ValidatorConfig(
    min_diversity_score=70.0,
    diversity_weight=0.35,
    content_weight=0.20,  # Reduce other weights
)
```

## Scoring Methodology

### Overall Score Calculation

The overall score is a **weighted average** of five validation components:

```
Overall Score = 
    (Cartoon Confidence × 100) × 0.15 +
    Content Score × 0.25 +
    Quality Score × 0.20 +
    Diversity Score × 0.15 +
    Appropriateness Score × 0.25
```

### Component Scoring

#### 1. Cartoon Confidence (0-1 scale → 0-100 after weighting)

**Analyzed Properties:**
- Unique color count (cartoons: 1k-50k colors, photos: 100k+ colors)
- Color saturation (cartoons: higher saturation)
- Image characteristics

**Scoring:**
- Unique colors < 5,000: 0.9 confidence
- Unique colors < 20,000: 0.7 confidence
- Unique colors < 50,000: 0.5 confidence
- Unique colors ≥ 50,000: 0.2 confidence (likely photo)
- High saturation: +0.1 bonus
- Result clamped to [0.0, 1.0]

#### 2. Content Score (0-100)

**Validation Keywords:**
- Children: child, kid, toddler, baby, boy, girl, play, learn
- Families: family, parent, mother, father, caregiver, together
- Learning: learn, education, school, activity, development, growth
- Communication: talk, speech, language, listen, speak, communicate
- Support: help, support, care, therapy, resource, guide
- Positive: happy, joy, smile, fun, creative, inclusive, diverse

**Scoring Logic:**
- Base: 15 points per matched keyword
- Bonus: 5 points per category with matches
- Maximum: 100 points
- Default: 50 points if no matches

**Example:**
- Filename: `family_learning_children.png`
- Keywords matched: family, learning, child (3 keywords)
- Categories: 3 categories matched
- Score: min(100, 3×15 + 3×5) = 60

#### 3. Quality Score (0-100)

**Analyzed Properties:**
- Resolution
- Brightness
- Compression artifacts

**Resolution Scoring:**
- ≥ 1920×1080: 100 points
- ≥ 1280×720: 85 points
- ≥ 800×600: 70 points
- ≥ 400×300: 55 points
- < 400×300: 30 points

**Brightness Scoring (preferred: 60-180 range):**
- 60-180: 90 points
- 40-200: 75 points
- Outside: 50 points

**Artifact Detection:**
- Low variance (< 20): possible compression artifacts (-20 points)
- Excessive variance (> max): noise detected (-15 points)
- Normal: 0 point penalty

**Final Quality:** Weighted average of resolution (40%), brightness (35%), artifacts (25%)

#### 4. Diversity Score (0-100)

**Heuristic Analysis:**
- Baseline: 70 points
- Child/kid content: +10 points
- Family/group content: +5 points
- Flags potential homogeneity for manual review

**Note:** For complete diversity analysis, use LLM vision models or manual review.

#### 5. Appropriateness Score (0-100)

**Baseline:** 85 points

**Positive Indicators (+2 each):**
- play, learn, joy, happy, support, inclusive

**Red Flags (-10 each):**
- negative, struggle, deficit, broken, sad, sick

**Result:** Clamped to [0, 100]

### Pass Status Determination

| Status | Criteria | Notes |
|--------|----------|-------|
| **PASS** | All thresholds met & Overall ≥ min | Image approved for use |
| **FAIL** | One or more thresholds failed | Rejected, needs replacement |
| **REVIEW** | All thresholds met but Overall < min | Manually review, borderline quality |
| **BLOCKED** | Resolution too low or invalid file | Critical failure, unusable |

## MediaImage Data Structure

```python
@dataclass
class MediaImage:
    # File Information
    file_path: str          # Full path to image
    file_name: str          # Filename only
    file_size: int          # Size in bytes
    
    # Cartoon Style Results
    is_cartoon: bool        # Passes cartoon threshold
    cartoon_confidence: float  # 0-1 scale
    cartoon_analysis: str   # Details of analysis
    
    # Content Results
    content_score: float    # 0-100 scale
    content_analysis: str   # Details of analysis
    content_keywords_matched: List[str]  # Matched keywords
    
    # Quality Results
    quality_score: float    # 0-100 scale
    quality_analysis: str   # Details of analysis
    resolution_width: int   # Image width in pixels
    resolution_height: int  # Image height in pixels
    color_count: int        # Unique colors in image
    avg_brightness: float   # Average brightness (0-255)
    has_artifacts: bool     # Compression artifact detection
    
    # Diversity Results
    diversity_score: float  # 0-100 scale
    diversity_analysis: str # Details of analysis
    diversity_flags: List[str]  # Potential issues
    
    # Appropriateness Results
    appropriateness_score: float  # 0-100 scale
    appropriateness_analysis: str # Details of analysis
    appropriateness_flags: List[str]  # Potential issues
    
    # Overall Assessment
    overall_score: float    # Weighted final score
    is_valid: bool         # True if passes all thresholds
    pass_status: str       # "PASS", "FAIL", "REVIEW", "BLOCKED"
    reason: str            # Human-readable explanation
    
    # Metadata
    validated_at: str      # ISO timestamp
    validation_errors: List[str]  # Any errors during validation
    tags: List[str]        # Classification tags
```

## Integration with Media Gathering Agent

### Using Validation Filter

```python
from media_gathering_agent import MediaGatheringAgent
from media_validator import MediaValidator, create_validation_filter

# Initialize both agents
media_agent = MediaGatheringAgent()
validator = MediaValidator()

# Create validation filter
validation_filter = create_validation_filter(validator, strict=True)

# Gather and validate media in one workflow
media_results = media_agent.gather_media(queries)
validated_results = [r for r in media_results if validation_filter(r)]

# Validated results now include validation data
for result in validated_results:
    if 'validation' in result:
        validation = result['validation']
        print(f"{result['title']}: {validation['pass_status']}")
```

### Chaining Agents

```python
# Step 1: Gather media
media_agent = MediaGatheringAgent(output_dir="media")
results = media_agent.gather_media(
    queries=["cartoon family playing together"],
    quantity=20
)

# Step 2: Validate downloaded media
validator = MediaValidator()
valid, failed = validator.validate_batch(
    [r['local_path'] for r in results if r.get('local_path')]
)

# Step 3: Generate report
report = validator.generate_report(
    valid_results=valid,
    failed_results=failed,
    output_path="validation_report.json"
)

# Step 4: Use valid images in presentation
for image in valid:
    if image.pass_status == "PASS":
        # Copy to presentation media folder
        shutil.copy(image.file_path, "presentation/media/")
```

## Report Structure

### Report JSON Format

```json
{
  "metadata": {
    "generated_at": "2024-12-07T15:30:00",
    "handout_name": "handout_1",
    "total_images": 10
  },
  "summary": {
    "passed": 8,
    "failed": 2,
    "pass_rate": 80.0,
    "average_overall_score": 78.5,
    "average_cartoon_confidence": 0.82,
    "average_content_score": 75.2,
    "average_quality_score": 74.8,
    "average_diversity_score": 72.1,
    "average_appropriateness_score": 85.3
  },
  "passed_validations": [
    {
      "file_path": "media/image_001.png",
      "file_name": "image_001.png",
      "is_valid": true,
      "pass_status": "PASS",
      "overall_score": 82.5,
      "cartoon_confidence": 0.85,
      "content_score": 78.0,
      "quality_score": 80.0,
      "diversity_score": 75.0,
      "appropriateness_score": 87.0,
      "tags": ["high_quality", "strong_cartoon_style"]
    }
  ],
  "failed_validations": [
    {
      "file_path": "media/image_002.png",
      "file_name": "image_002.png",
      "is_valid": false,
      "pass_status": "FAIL",
      "reason": "Failed validation on: style (0.4)"
    }
  ],
  "recommendations": {
    "total_recommendations": 3,
    "items": [
      {
        "type": "pattern",
        "frequency": 2,
        "issue": "Low cartoon confidence",
        "recommendation": "Ensure downloaded images are cartoons/illustrations, not photographs"
      }
    ]
  }
}
```

## Logging Output

The validator provides detailed CLI output with emoji indicators:

```
✅ - Success/Valid image
❌ - Failure/Invalid image
⚠️  - Warning/Review needed
🔍 - Analyzing/Processing
📊 - Statistics/Results
📄 - Report generated
🔄 - Batch processing
📁 - Directory
🚫 - Blocked/Critical failure
```

Example output:
```
2024-12-07 15:30:00 - media_validator - INFO - ✅ Media Validator Agent initialized

======================================================================
🔄 Batch validating 10 images
   Handout: handout_1_slp_info
======================================================================

[1/10] Processing...
🔍 Validating: image_001.png
   ✅ PASS - Overall: 82 | Style: 85% | Content: 78 | Quality: 80

[2/10] Processing...
🔍 Validating: image_002.png
   ❌ FAIL - Overall: 45 | Style: 40% | Content: 50 | Quality: 60

======================================================================
📊 Batch Results:
   ✅ Valid: 8
   ❌ Failed: 2
   Average score: 78
======================================================================
```

## Running Tests

### Run All Tests

```bash
# Run complete test suite
pytest tests/test_media_validator.py -v

# Run with coverage
pytest tests/test_media_validator.py --cov=media_validator

# Run specific test class
pytest tests/test_media_validator.py::TestMediaImage -v

# Run specific test
pytest tests/test_media_validator.py::TestMediaImage::test_create_media_image -v
```

### Test Coverage

The test suite includes:
- **MediaImage dataclass**: Creation, serialization, defaults
- **ValidatorConfig**: Configuration management
- **Cartoon style validation**: Confidence scoring
- **Content validation**: Keyword matching
- **Quality validation**: Resolution, brightness, artifacts
- **Overall scoring**: Weighted average calculation
- **Pass status determination**: All status types
- **Batch validation**: Multiple image processing
- **Report generation**: Structure and contents
- **Integration**: Filter creation and usage
- **Edge cases**: Error handling, corrupted files
- **Scoring edge cases**: Zero values, max values, mixed

## Troubleshooting

### Issue: "Cannot open image" error

**Cause:** Image file is corrupted or unsupported format

**Solution:**
- Verify file is valid image (try opening in image viewer)
- Convert to PNG or JPG format
- Check file hasn't been partially downloaded

### Issue: Low cartoon confidence scores

**Cause:** Image is actually a photograph, not an illustration

**Solution:**
- Verify source is providing cartoons/illustrations
- Use more specific search queries: "cartoon children" instead of "children"
- Check downloaded images before validation

### Issue: Content scores are low

**Cause:** Keywords in filename don't match validation keywords

**Solution:**
- Ensure filenames contain relevant keywords
- File name examples: `family_learning.png`, `children_play_together.jpg`
- Alternatively, use LLM-based content verification for deeper analysis

### Issue: Quality scores are low

**Cause:** Image resolution is too low or has artifacts

**Solution:**
- Source higher resolution images (minimum 800×600, prefer 1280×720+)
- Check image isn't heavily compressed
- Verify brightness is in reasonable range (60-180)

### Issue: Diversity flags appear

**Cause:** Single-subject images detected or generic content

**Solution:**
- Include more images showing diverse groups
- Prioritize family/group scenes over single subjects
- Manually review images that score near threshold

### Issue: Memory error with large batches

**Cause:** Too many images processed simultaneously

**Solution:**
- Validate in smaller batches (< 100 images per batch)
- Increase system memory if possible
- Process sequentially instead of parallel

## Best Practices

### 1. Validation Workflow

```python
# Step 1: Gather media
# Step 2: Validate batch
# Step 3: Review failures and recommendations
# Step 4: Re-gather specific categories as needed
# Step 5: Generate final report
# Step 6: Archive validation data
```

### 2. Configuration Selection

- **High quality**: Use strict thresholds for important presentations
- **General use**: Use default thresholds for most content
- **Quick prototyping**: Lower thresholds for rapid iteration

### 3. Integration Best Practices

```python
# Initialize once, reuse for multiple batches
validator = MediaValidator(config=custom_config)

for handout_dir in handout_dirs:
    results = validator.validate_batch(images, handout_dir.name)
    # Process results
```

### 4. Manual Review Process

```python
# Flag images for manual review
review_images = [r for r in all_images 
                 if "manual_review_recommended" in r.tags]

# Review and move to final location
for image in review_images:
    # Manual review
    # Update tags if approved
    # Archive for records
```

### 5. Continuous Monitoring

```python
# Track validation statistics over time
validation_history = []

for batch_results in all_batches:
    stats = {
        'timestamp': datetime.now(),
        'pass_rate': len(batch_results['valid']) / len(all_results),
        'avg_score': batch_results['average_score'],
    }
    validation_history.append(stats)

# Analyze trends and adjust thresholds if needed
```

## Performance Considerations

### Memory Usage

- Per image: ~5-10 MB peak (during analysis)
- Batch processing: ~50-100 MB for 10 images
- Report generation: Minimal additional memory

### Processing Time

- Per image: 50-200 ms (depends on resolution)
- Batch of 10 images: ~0.5-2 seconds
- Report generation: < 100 ms

### Optimization Tips

- Use appropriate image resolution (don't oversample)
- Process in batches of 10-50 images
- Reuse validator instance for multiple batches
- Use logging level ERROR in production to reduce overhead

## Advanced Usage

### Custom Scoring Weights

```python
# Emphasize content relevance
config = ValidatorConfig(
    content_weight=0.40,
    cartoon_weight=0.10,
    quality_weight=0.20,
    diversity_weight=0.15,
    appropriateness_weight=0.15,
)
```

### Dynamic Configuration

```python
def get_config_for_handout(handout_type: str) -> ValidatorConfig:
    """Get appropriate config based on handout type"""
    configs = {
        'slp_info': ValidatorConfig(
            min_content_score=75.0,
            content_weight=0.35,
        ),
        'strategies': ValidatorConfig(
            min_cartoon_confidence=0.75,
            cartoon_weight=0.25,
        ),
        'resources': ValidatorConfig(
            min_diversity_score=70.0,
            diversity_weight=0.35,
        ),
    }
    return configs.get(handout_type, ValidatorConfig())
```

### Batch Processing with Progress Tracking

```python
from tqdm import tqdm

validator = MediaValidator()
images = [...]

results = []
for image_path in tqdm(images, desc="Validating"):
    result = validator.validate_image(image_path)
    results.append(result)

valid = [r for r in results if r.is_valid]
print(f"Validation complete: {len(valid)}/{len(results)} passed")
```

## Related Documentation

- [AGENTS.md](AGENTS.md) - Agent development guidelines
- [media_gathering_agent.py](media_gathering_agent.py) - Media retrieval agent
- [llm_image_verifier.py](llm_image_verifier.py) - LLM-based vision verification

## License & Attribution

This validator is part of the SLP Autism Awareness Presentation project.
