#!/usr/bin/env python3
"""
Test suite for Media Validator Agent
Tests validation functionality, scoring, and reporting
"""

import sys
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from media_validator import (
    MediaValidator,
    MediaImage,
    ValidatorConfig,
    LogLevel,
    create_validation_filter,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def validator_config() -> ValidatorConfig:
    """Create test validator config"""
    return ValidatorConfig(
        min_cartoon_confidence=0.6,
        min_content_score=60.0,
        min_quality_score=50.0,
        min_overall_score=65.0,
    )


@pytest.fixture
def validator(validator_config: ValidatorConfig) -> MediaValidator:
    """Create test validator instance"""
    return MediaValidator(
        config=validator_config,
        log_level=LogLevel.ERROR  # Suppress logging during tests
    )


@pytest.fixture
def sample_media_image() -> MediaImage:
    """Create sample media image for testing"""
    return MediaImage(
        file_path="/path/to/image.png",
        file_name="image.png",
        file_size=1024000,
        cartoon_confidence=0.85,
        is_cartoon=True,
        content_score=75.0,
        quality_score=80.0,
        resolution_width=1280,
        resolution_height=720,
    )


# ============================================================================
# TESTS - MEDIAIMAGE DATACLASS
# ============================================================================

class TestMediaImage:
    """Test MediaImage dataclass"""
    
    def test_create_media_image(self) -> None:
        """Test creating MediaImage instance"""
        img = MediaImage(
            file_path="/path/to/image.jpg",
            file_name="test.jpg"
        )
        
        assert img.file_path == "/path/to/image.jpg"
        assert img.file_name == "test.jpg"
        assert img.validated_at is not None
        assert img.pass_status == ""
    
    def test_media_image_to_dict(self, sample_media_image: MediaImage) -> None:
        """Test converting MediaImage to dict"""
        result_dict = sample_media_image.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['file_path'] == "/path/to/image.png"
        assert result_dict['cartoon_confidence'] == 0.85
        assert result_dict['content_score'] == 75.0
    
    def test_media_image_defaults(self) -> None:
        """Test MediaImage default values"""
        img = MediaImage(
            file_path="/test.png",
            file_name="test.png"
        )
        
        assert img.is_cartoon is False
        assert img.cartoon_confidence == 0.0
        assert img.content_score == 0.0
        assert img.quality_score == 0.0
        assert img.pass_status == ""


# ============================================================================
# TESTS - VALIDATOR CONFIG
# ============================================================================

class TestValidatorConfig:
    """Test ValidatorConfig"""
    
    def test_default_config(self) -> None:
        """Test default configuration values"""
        config = ValidatorConfig()
        
        assert config.min_cartoon_confidence == 0.6
        assert config.min_content_score == 60.0
        assert config.min_quality_score == 50.0
        assert config.cartoon_weight == 0.15
        assert config.content_weight == 0.25
    
    def test_custom_config(self) -> None:
        """Test creating custom configuration"""
        config = ValidatorConfig(
            min_cartoon_confidence=0.8,
            min_overall_score=75.0
        )
        
        assert config.min_cartoon_confidence == 0.8
        assert config.min_overall_score == 75.0


# ============================================================================
# TESTS - CARTOON STYLE VALIDATION
# ============================================================================

class TestCartoonValidation:
    """Test cartoon style validation"""
    
    def test_cartoon_confidence_bounds(self, validator: MediaValidator) -> None:
        """Test cartoon confidence stays within 0-1 bounds"""
        config = ValidatorConfig(min_cartoon_confidence=0.5)
        test_validator = MediaValidator(config=config, log_level=LogLevel.ERROR)
        
        result = MediaImage(
            file_path="/test.png",
            file_name="test.png"
        )
        
        # Mock PIL Image
        with patch('media_validator.Image.open') as mock_open:
            mock_image = MagicMock()
            mock_image.size = (1280, 720)
            mock_image.convert.return_value.getdata.return_value = [(255, 0, 0)] * 1000
            mock_open.return_value = mock_image
            
            # This should not raise an error and confidence should be bounded
            test_validator._validate_cartoon_style(result, mock_image)
            
            assert 0.0 <= result.cartoon_confidence <= 1.0


# ============================================================================
# TESTS - CONTENT VALIDATION
# ============================================================================

class TestContentValidation:
    """Test content relevance validation"""
    
    def test_content_keywords_matching(self, validator: MediaValidator) -> None:
        """Test keyword matching for content validation"""
        result = MediaImage(
            file_path="/path/child_learning.png",
            file_name="child_learning.png"
        )
        
        validator._validate_content(result)
        
        assert result.content_score > 0.0
        assert len(result.content_keywords_matched) > 0
        assert any('child' in k or 'learn' in k 
                   for k in result.content_keywords_matched)
    
    def test_generic_filename_content(self, validator: MediaValidator) -> None:
        """Test generic filename gets default content score"""
        result = MediaImage(
            file_path="/path/image123.png",
            file_name="image123.png"
        )
        
        validator._validate_content(result)
        
        # Generic files get default score
        assert result.content_score == 50.0
        assert len(result.content_keywords_matched) == 0
    
    def test_multiple_keyword_matches(self, validator: MediaValidator) -> None:
        """Test multiple keyword matching increases score"""
        result = MediaImage(
            file_path="/path/family_learning_children_play.png",
            file_name="family_learning_children_play.png"
        )
        
        validator._validate_content(result)
        
        assert len(result.content_keywords_matched) >= 3
        assert result.content_score >= 65.0


# ============================================================================
# TESTS - OVERALL SCORING
# ============================================================================

class TestOverallScoring:
    """Test overall score calculation"""
    
    def test_overall_score_calculation(self, validator: MediaValidator) -> None:
        """Test overall score is weighted average"""
        result = MediaImage(
            file_path="/test.png",
            file_name="test.png",
            cartoon_confidence=0.8,
            content_score=80.0,
            quality_score=70.0,
            diversity_score=75.0,
            appropriateness_score=85.0,
        )
        
        validator._calculate_overall_score(result)
        
        # Overall score should be weighted average
        expected = (
            0.8 * 100.0 * 0.15 +
            80.0 * 0.25 +
            70.0 * 0.20 +
            75.0 * 0.15 +
            85.0 * 0.25
        )
        
        assert result.overall_score == pytest.approx(expected, rel=0.01)
    
    def test_overall_score_range(self, validator: MediaValidator) -> None:
        """Test overall score stays within valid range"""
        result = MediaImage(
            file_path="/test.png",
            file_name="test.png",
            cartoon_confidence=1.0,
            content_score=100.0,
            quality_score=100.0,
            diversity_score=100.0,
            appropriateness_score=100.0,
        )
        
        validator._calculate_overall_score(result)
        
        # Max possible score
        assert result.overall_score <= 100.0


# ============================================================================
# TESTS - PASS STATUS DETERMINATION
# ============================================================================

class TestPassStatusDetermination:
    """Test pass/fail/review status determination"""
    
    def test_pass_status_valid(self, validator: MediaValidator) -> None:
        """Test image that passes all checks"""
        result = MediaImage(
            file_path="/test.png",
            file_name="test.png",
            resolution_width=1280,
            resolution_height=720,
            cartoon_confidence=0.85,
            content_score=80.0,
            quality_score=85.0,
            diversity_score=80.0,
            appropriateness_score=90.0,
        )
        
        result.overall_score = 85.0
        validator._determine_pass_status(result)
        
        assert result.pass_status == "PASS"
        assert result.is_valid is True
    
    def test_pass_status_low_resolution(self, validator: MediaValidator) -> None:
        """Test image with too low resolution"""
        result = MediaImage(
            file_path="/test.png",
            file_name="test.png",
            resolution_width=200,
            resolution_height=150,
            cartoon_confidence=0.85,
            content_score=80.0,
            quality_score=85.0,
            diversity_score=80.0,
            appropriateness_score=90.0,
        )
        
        result.overall_score = 85.0
        validator._determine_pass_status(result)
        
        assert result.pass_status == "BLOCKED"
        assert result.is_valid is False
        assert "Resolution" in result.reason
    
    def test_pass_status_fail(self, validator: MediaValidator) -> None:
        """Test image that fails quality threshold"""
        result = MediaImage(
            file_path="/test.png",
            file_name="test.png",
            resolution_width=1280,
            resolution_height=720,
            cartoon_confidence=0.3,  # Below threshold
            content_score=40.0,  # Below threshold
            quality_score=45.0,  # Below threshold
            diversity_score=80.0,
            appropriateness_score=90.0,
        )
        
        result.overall_score = 50.0
        validator._determine_pass_status(result)
        
        assert result.pass_status == "FAIL"
        assert result.is_valid is False
    
    def test_pass_status_review(self, validator: MediaValidator) -> None:
        """Test image that should be manually reviewed"""
        result = MediaImage(
            file_path="/test.png",
            file_name="test.png",
            resolution_width=1280,
            resolution_height=720,
            cartoon_confidence=0.65,
            content_score=65.0,
            quality_score=55.0,
            diversity_score=80.0,
            appropriateness_score=90.0,
        )
        
        result.overall_score = 64.0  # Just below threshold
        validator._determine_pass_status(result)
        
        assert result.pass_status == "REVIEW"
        assert result.is_valid is False
        assert "manual_review_recommended" in result.tags


# ============================================================================
# TESTS - BATCH VALIDATION
# ============================================================================

class TestBatchValidation:
    """Test batch validation workflow"""
    
    def test_batch_validation_empty_list(self, validator: MediaValidator) -> None:
        """Test batch validation with empty list"""
        valid, failed = validator.validate_batch([])
        
        assert len(valid) == 0
        assert len(failed) == 0
    
    def test_batch_validation_returns_tuples(
        self, 
        validator: MediaValidator,
        tmp_path: Path
    ) -> None:
        """Test batch validation returns correct types"""
        # Create a test image file
        test_image = tmp_path / "test.png"
        test_image.write_bytes(b"PNG_HEADER" + b"\x00" * 100)
        
        # Batch validation should handle file errors gracefully
        valid, failed = validator.validate_batch([str(test_image)])
        
        assert isinstance(valid, list)
        assert isinstance(failed, list)


# ============================================================================
# TESTS - REPORT GENERATION
# ============================================================================

class TestReportGeneration:
    """Test report generation"""
    
    def test_generate_report_structure(
        self,
        validator: MediaValidator,
        sample_media_image: MediaImage
    ) -> None:
        """Test report has correct structure"""
        report = validator.generate_report(
            valid_results=[sample_media_image],
            failed_results=[],
            handout_name="test_handout"
        )
        
        assert "metadata" in report
        assert "summary" in report
        assert "passed_validations" in report
        assert "failed_validations" in report
        assert "recommendations" in report
    
    def test_report_metadata(
        self,
        validator: MediaValidator,
        sample_media_image: MediaImage
    ) -> None:
        """Test report metadata is correct"""
        report = validator.generate_report(
            valid_results=[sample_media_image],
            failed_results=[],
            handout_name="test_handout"
        )
        
        assert report["metadata"]["handout_name"] == "test_handout"
        assert report["metadata"]["total_images"] == 1
        assert "generated_at" in report["metadata"]
    
    def test_report_summary(
        self,
        validator: MediaValidator,
        sample_media_image: MediaImage
    ) -> None:
        """Test report summary statistics"""
        report = validator.generate_report(
            valid_results=[sample_media_image],
            failed_results=[],
        )
        
        assert report["summary"]["passed"] == 1
        assert report["summary"]["failed"] == 0
        assert report["summary"]["pass_rate"] == 100.0
    
    def test_report_save_to_file(
        self,
        validator: MediaValidator,
        sample_media_image: MediaImage,
        tmp_path: Path
    ) -> None:
        """Test report is saved to file"""
        output_path = tmp_path / "test_report.json"
        
        report = validator.generate_report(
            valid_results=[sample_media_image],
            failed_results=[],
            output_path=str(output_path)
        )
        
        assert output_path.exists()
        
        # Verify file contents
        with open(output_path, 'r') as f:
            saved_report = json.load(f)
        
        assert saved_report["summary"]["passed"] == 1


# ============================================================================
# TESTS - INTEGRATION
# ============================================================================

class TestIntegration:
    """Test integration with media gathering agent"""
    
    def test_create_validation_filter(self, validator: MediaValidator) -> None:
        """Test creating validation filter"""
        filter_fn = create_validation_filter(validator)
        
        assert callable(filter_fn)
    
    def test_validation_filter_with_media_result(self, validator: MediaValidator) -> None:
        """Test filter with media result"""
        filter_fn = create_validation_filter(validator, strict=False)
        
        # Mock media result with no local path (should pass through)
        media_result = {
            'url': 'https://example.com/image.jpg',
            'title': 'Test Image'
        }
        
        # Should pass through if no local path
        assert filter_fn(media_result) is True


# ============================================================================
# TESTS - EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_validate_nonexistent_file(self, validator: MediaValidator) -> None:
        """Test validating non-existent file"""
        result = validator.validate_image("/nonexistent/file.jpg")
        
        assert result.is_valid is False
        assert result.pass_status == "BLOCKED"
        assert len(result.validation_errors) > 0
    
    def test_validate_corrupted_image(
        self,
        validator: MediaValidator,
        tmp_path: Path
    ) -> None:
        """Test validating corrupted image file"""
        corrupted_file = tmp_path / "corrupted.jpg"
        corrupted_file.write_bytes(b"NOT_A_REAL_IMAGE")
        
        result = validator.validate_image(str(corrupted_file))
        
        assert result.is_valid is False
        assert result.pass_status == "BLOCKED"
    
    def test_zero_file_size(self, validator: MediaValidator) -> None:
        """Test handling zero-size file"""
        result = MediaImage(
            file_path="/empty.png",
            file_name="empty.png",
            file_size=0
        )
        
        # Should handle gracefully
        validator._calculate_overall_score(result)
        validator._determine_pass_status(result)
        
        assert result.pass_status in ["BLOCKED", "FAIL", "REVIEW"]


# ============================================================================
# TESTS - SCORING EDGE CASES
# ============================================================================

class TestScoringEdgeCases:
    """Test scoring algorithm edge cases"""
    
    def test_all_zeros_score(self, validator: MediaValidator) -> None:
        """Test scoring with all zero values"""
        result = MediaImage(
            file_path="/test.png",
            file_name="test.png",
            cartoon_confidence=0.0,
            content_score=0.0,
            quality_score=0.0,
            diversity_score=0.0,
            appropriateness_score=0.0,
        )
        
        validator._calculate_overall_score(result)
        
        assert result.overall_score == 0.0
    
    def test_all_max_score(self, validator: MediaValidator) -> None:
        """Test scoring with all maximum values"""
        result = MediaImage(
            file_path="/test.png",
            file_name="test.png",
            cartoon_confidence=1.0,
            content_score=100.0,
            quality_score=100.0,
            diversity_score=100.0,
            appropriateness_score=100.0,
        )
        
        validator._calculate_overall_score(result)
        
        assert result.overall_score == 100.0
    
    def test_mixed_scores(self, validator: MediaValidator) -> None:
        """Test scoring with mixed values"""
        result = MediaImage(
            file_path="/test.png",
            file_name="test.png",
            cartoon_confidence=0.5,
            content_score=40.0,
            quality_score=70.0,
            diversity_score=60.0,
            appropriateness_score=80.0,
        )
        
        validator._calculate_overall_score(result)
        
        # Score should be between 0 and 100
        assert 0.0 <= result.overall_score <= 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
