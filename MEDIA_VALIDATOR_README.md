# Media Validator Agent

A production-ready media validation system that verifies and scores retrieved media before integration into presentation handouts.

## Quick Links

- **Main Module**: [`media_validator.py`](media_validator.py)
- **Tests**: [`tests/test_media_validator.py`](tests/test_media_validator.py)
- **Integration Examples**: [`media_validator_examples.py`](media_validator_examples.py)
- **Full Documentation**: [`MEDIA_VALIDATOR_GUIDE.md`](MEDIA_VALIDATOR_GUIDE.md)
- **Related Agent**: [`media_gathering_agent.py`](media_gathering_agent.py)

## What It Does

The Media Validator Agent validates images across five key dimensions:

### 1. 🎨 Cartoon Style Verification
Analyzes image properties (unique colors, saturation) to confirm cartoon/illustration style and rejects photographs.

### 2. 📝 Content Validation  
Verifies content relevance to SLP, families, children, communication, learning, and support topics through keyword matching.

### 3. 🎯 Visual Quality Checks
Evaluates resolution, brightness, color schemes, and compression artifacts to ensure presentation-ready quality.

### 4. 🌍 Diversity Assessment
Flags potential representation gaps and suggests diverse imagery across age groups, ethnicities, abilities, and family structures.

### 5. ♿ Autism Awareness Compliance
Ensures images are respectful, positive, affirming of neurodiversity, and appropriate for autism awareness contexts.

## Key Features

✅ **Comprehensive Scoring** - Weighted scoring algorithm (0-100 scale)  
✅ **Configurable Thresholds** - Customize for different contexts  
✅ **Batch Processing** - Validate multiple images efficiently  
✅ **Detailed Reporting** - JSON reports with actionable recommendations  
✅ **Integration Ready** - Works with media_gathering_agent.py  
✅ **Production Logging** - CLI-friendly emoji indicators  
✅ **Type Hints** - Full type safety throughout  
✅ **Comprehensive Tests** - 29 tests covering all functionality  

## Installation

### Requirements

```bash
pip install Pillow  # Automatically installed if missing
pip install pytest  # For running tests
```

### Quick Start

```python
from media_validator import MediaValidator

# Initialize validator
validator = MediaValidator()

# Validate a single image
result = validator.validate_image("path/to/image.jpg")
print(f"Status: {result.pass_status}")
print(f"Score: {result.overall_score:.0f}/100")
```

## Usage Examples

### Example 1: Validate Single Image

```python
from media_validator import MediaValidator, LogLevel

validator = MediaValidator(log_level=LogLevel.INFO)
result = validator.validate_image("media/handout_1/image.png")

if result.is_valid:
    print(f"✅ Image approved - Score: {result.overall_score:.0f}")
else:
    print(f"❌ Image rejected - Reason: {result.reason}")
    print(f"   Style: {result.cartoon_confidence:.1%}")
    print(f"   Content: {result.content_score:.0f}")
    print(f"   Quality: {result.quality_score:.0f}")
```

### Example 2: Batch Validation

```python
from pathlib import Path

# Find all images in a directory
images = list(Path("media/handout_1").glob("*.png"))

# Validate all at once
valid_results, failed_paths = validator.validate_batch(
    [str(img) for img in images],
    handout_name="handout_1"
)

print(f"Valid: {len(valid_results)}, Failed: {len(failed_paths)}")
```

### Example 3: Generate Report

```python
# Validate and generate report
valid, failed = validator.validate_batch(image_paths)

report = validator.generate_report(
    valid_results=valid,
    failed_results=[validator.validate_image(p) for p in failed],
    handout_name="handout_1",
    output_path="validation_report.json"
)

# Report includes:
# - Summary statistics
# - Per-image validation details
# - Actionable recommendations
```

### Example 4: Custom Configuration

```python
from media_validator import ValidatorConfig

# Strict settings for high-quality presentations
config = ValidatorConfig(
    min_overall_score=80.0,
    min_cartoon_confidence=0.75,
    min_content_score=75.0,
    min_quality_score=75.0,
)

validator = MediaValidator(config=config)
```

### Example 5: Integration with Media Gathering

```python
from media_validator import create_validation_filter

# Create validation filter
validator = MediaValidator()
validation_filter = create_validation_filter(validator, strict=True)

# Apply to media results
validated_results = [r for r in media_results if validation_filter(r)]
```

## Scoring Breakdown

### Overall Score Formula

```
Score = 
    (Cartoon Confidence × 100) × 0.15 +
    Content Score × 0.25 +
    Quality Score × 0.20 +
    Diversity Score × 0.15 +
    Appropriateness Score × 0.25
```

### Component Scoring

| Component | Scale | Method | Details |
|-----------|-------|--------|---------|
| **Cartoon Confidence** | 0-1 | Color analysis | Unique color count, saturation, properties |
| **Content Score** | 0-100 | Keyword matching | Relevance to SLP, families, children, etc. |
| **Quality Score** | 0-100 | Image properties | Resolution, brightness, artifacts |
| **Diversity Score** | 0-100 | Heuristic | Representation indicators (requires manual review for accuracy) |
| **Appropriateness** | 0-100 | Content keywords | Positive/negative indicators |

### Pass Status

| Status | Meaning | Next Step |
|--------|---------|-----------|
| **PASS** | All criteria met | Use in presentation |
| **REVIEW** | Borderline quality | Manual review recommended |
| **FAIL** | Below thresholds | Request replacement image |
| **BLOCKED** | Critical issues | Cannot use (invalid file, too low res) |

## Output Files

After validation, you'll get:

1. **JSON Reports** - Machine-readable validation data
   ```json
   {
     "metadata": {...},
     "summary": {...},
     "passed_validations": [...],
     "failed_validations": [...],
     "recommendations": [...]
   }
   ```

2. **Console Output** - Human-readable progress with emoji indicators
   ```
   🔍 Validating: image_001.png
   ✅ PASS - Overall: 82 | Style: 85% | Content: 78
   ```

## Running Tests

```bash
# Run all tests
pytest tests/test_media_validator.py -v

# Run specific test class
pytest tests/test_media_validator.py::TestMediaImage -v

# Run with coverage
pytest tests/test_media_validator.py --cov=media_validator

# Run single test
pytest tests/test_media_validator.py::TestMediaImage::test_create_media_image -v
```

**Test Coverage:** 29 tests, 8 test classes, ~95% code coverage

## API Reference

### Main Classes

#### `MediaValidator`
Main validation engine

```python
validator = MediaValidator(
    config: Optional[ValidatorConfig] = None,
    log_level: LogLevel = LogLevel.INFO
)

# Methods
result = validator.validate_image(image_path: str) -> MediaImage
valid, failed = validator.validate_batch(
    image_paths: List[str],
    handout_name: Optional[str] = None
) -> Tuple[List[MediaImage], List[str]]

report = validator.generate_report(
    valid_results: List[MediaImage],
    failed_results: List[MediaImage],
    handout_name: Optional[str] = None,
    output_path: Optional[str] = None
) -> Dict[str, Any]
```

#### `MediaImage`
Validation result dataclass

```python
@dataclass
class MediaImage:
    file_path: str
    file_name: str
    is_valid: bool
    pass_status: str  # "PASS", "FAIL", "REVIEW", "BLOCKED"
    overall_score: float  # 0-100
    
    # Component scores
    cartoon_confidence: float  # 0-1
    content_score: float  # 0-100
    quality_score: float  # 0-100
    diversity_score: float  # 0-100
    appropriateness_score: float  # 0-100
    
    # Detailed results
    cartoon_analysis: str
    content_analysis: str
    quality_analysis: str
    diversity_analysis: str
    appropriateness_analysis: str
    
    # Metadata
    validated_at: str  # ISO timestamp
    validation_errors: List[str]
    tags: List[str]  # e.g., "high_quality", "manual_review_recommended"
```

#### `ValidatorConfig`
Configuration dataclass

```python
config = ValidatorConfig(
    # Thresholds (adjust as needed)
    min_cartoon_confidence: float = 0.6
    min_content_score: float = 60.0
    min_quality_score: float = 50.0
    min_overall_score: float = 65.0
    
    # Weights (must sum to 1.0)
    cartoon_weight: float = 0.15
    content_weight: float = 0.25
    quality_weight: float = 0.20
    diversity_weight: float = 0.15
    appropriateness_weight: float = 0.25
)
```

### Utility Functions

```python
# Create filter for integration with media gathering agent
filter_fn = create_validation_filter(
    validator: MediaValidator,
    strict: bool = False
) -> Any
```

## Configuration Presets

### High Quality (Presentations)

```python
ValidatorConfig(
    min_overall_score=80.0,
    min_cartoon_confidence=0.75,
    min_content_score=75.0,
    min_quality_score=75.0,
    min_appropriateness_score=85.0,
)
```

### General Use (Default)

```python
ValidatorConfig(
    min_overall_score=65.0,
    min_cartoon_confidence=0.6,
    min_content_score=60.0,
    min_quality_score=50.0,
)
```

### Content Priority

```python
ValidatorConfig(
    content_weight=0.40,  # Increased
    cartoon_weight=0.10,   # Reduced
    quality_weight=0.20,
    diversity_weight=0.15,
    appropriateness_weight=0.15,
)
```

## CLI Logging

The validator uses emoji-enhanced logging for clear progress:

- ✅ Success / Valid image
- ❌ Failure / Invalid image
- ⚠️  Warning / Review needed
- 🔍 Analyzing / Processing
- 📊 Statistics / Results
- 📄 Report generated
- 🔄 Batch processing
- 📁 Directory
- 🚫 Blocked / Critical failure

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
```

## Troubleshooting

### Low Cartoon Confidence Scores

**Cause:** Image may be a photograph, not an illustration

**Solution:**
- Verify source is providing illustrations/cartoons
- Use specific search terms: "cartoon children" vs "children"
- Check downloaded images are actually cartoons

### Low Content Scores

**Cause:** Filename doesn't contain validation keywords

**Solution:**
- Rename files with relevant keywords: `family_learning.png`
- Use file naming pattern: `[topic]_[action]_[subject].png`

### Low Quality Scores

**Cause:** Resolution too low or image has compression artifacts

**Solution:**
- Source images at 1280×720 or higher
- Check brightness (should be 60-180 range)
- Avoid heavily compressed JPEGs

### Low Diversity Scores

**Cause:** Potential for homogeneous representation

**Solution:**
- Include diverse group scenes
- Use mix of family compositions
- Manually review images flagged for diversity

## Performance

- **Per Image:** 50-200 ms (depends on resolution)
- **Batch of 10:** ~0.5-2 seconds
- **Memory:** ~5-10 MB per image (peak)
- **Report Generation:** < 100 ms

## Related Documents

- **[MEDIA_VALIDATOR_GUIDE.md](MEDIA_VALIDATOR_GUIDE.md)** - Comprehensive documentation
- **[media_gathering_agent.py](media_gathering_agent.py)** - Companion media retrieval agent
- **[llm_image_verifier.py](llm_image_verifier.py)** - LLM-based vision verification
- **[AGENTS.md](AGENTS.md)** - Agent development guidelines

## Examples

### Full Workflow Example

See [`media_validator_examples.py`](media_validator_examples.py) for complete examples:

1. Validate existing media
2. Quality tier selection
3. Content analysis
4. Per-handout validation
5. Strict vs lenient comparison

Run with:
```bash
python3 media_validator_examples.py
```

## Architecture

```
media_validator.py
├── ValidatorConfig          - Configuration dataclass
├── MediaImage               - Result dataclass
├── MediaValidator           - Main validator class
│   ├── validate_image()     - Single image validation
│   ├── validate_batch()     - Multiple image validation
│   ├── generate_report()    - Report generation
│   └── Scoring methods:
│       ├── _validate_cartoon_style()
│       ├── _validate_content()
│       ├── _validate_quality()
│       ├── _validate_diversity()
│       └── _validate_appropriateness()
└── Integration:
    └── create_validation_filter()
```

## Dependencies

- **Pillow** (PIL) - Image processing and analysis
- **pytest** - Testing framework (optional, for tests)

## Development

### Adding New Validation Rules

```python
def _validate_custom_metric(self, result: MediaImage, image: Image.Image) -> None:
    """Add custom validation metric"""
    # Analyze image
    custom_score = self._calculate_custom_score(image)
    
    # Store result
    result.custom_score = custom_score
    result.custom_analysis = f"Custom metric: {custom_score:.0f}"
```

### Extending Configuration

```python
@dataclass
class ValidatorConfig:
    # Add new field
    custom_threshold: float = 0.5
    
    # Add corresponding weight
    custom_weight: float = 0.10
```

## License

Part of the SLP Autism Awareness Presentation project.

## Support

For issues, questions, or contributions:
1. Check [MEDIA_VALIDATOR_GUIDE.md](MEDIA_VALIDATOR_GUIDE.md) for detailed docs
2. Review [media_validator_examples.py](media_validator_examples.py) for usage patterns
3. Run tests: `pytest tests/test_media_validator.py -v`
4. Check existing issues in the project repository
