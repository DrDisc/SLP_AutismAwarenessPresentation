#!/usr/bin/env python3
"""
Production-Ready Media Validator Agent
Validates and verifies retrieved media before integration into handouts.

Features:
- Cartoon style verification with confidence scoring (0-1 scale)
- Content validation (relevance to SLP, families, children)
- Visual quality checks (resolution, color scheme, artifacts)
- Diversity & representation analysis
- Autism awareness appropriateness scoring
- Batch verification workflow with detailed reporting
- Integration with media_gathering_agent.py
- Configurable thresholds and scoring
- Production logging and error handling
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import Counter

try:
    from PIL import Image
    from PIL import ImageStat
except ImportError:
    print("Installing Pillow for image analysis...")
    subprocess.run([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
    from PIL import Image
    from PIL import ImageStat


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR


def setup_logger(
    name: str,
    level: LogLevel = LogLevel.INFO
) -> logging.Logger:
    """Setup logger with emoji support for CLI output"""
    logger = logging.getLogger(name)
    logger.setLevel(level.value)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


logger = setup_logger(__name__, LogLevel.INFO)


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class ValidatorConfig:
    """Configuration for media validator agent"""
    # Style validation thresholds (0-1 scale)
    min_cartoon_confidence: float = 0.6
    
    # Content validation thresholds (0-100 scale)
    min_content_score: float = 60.0
    
    # Quality validation thresholds (0-100 scale)
    min_quality_score: float = 50.0
    min_resolution_width: int = 400
    min_resolution_height: int = 300
    
    # Diversity thresholds (0-100 scale)
    min_diversity_score: float = 40.0
    
    # Appropriateness thresholds (0-100 scale)
    min_appropriateness_score: float = 70.0
    
    # Overall pass threshold (weighted score)
    min_overall_score: float = 65.0
    
    # Scoring weights
    cartoon_weight: float = 0.15
    content_weight: float = 0.25
    quality_weight: float = 0.20
    diversity_weight: float = 0.15
    appropriateness_weight: float = 0.25
    
    # Quality analysis
    max_color_variance: float = 120.0  # For artifact detection
    min_unique_colors: int = 50
    
    # Manual review thresholds
    flag_for_review_confidence: float = 0.5  # Confidence between 0.5-0.6
    flag_for_review_quality: float = 50.0    # Quality between 50-60


@dataclass
class MediaImage:
    """Dataclass for validated media image data"""
    # File information
    file_path: str
    file_name: str
    file_size: int = 0
    
    # Validation results
    is_cartoon: bool = False
    cartoon_confidence: float = 0.0
    cartoon_analysis: str = ""
    
    content_score: float = 0.0
    content_analysis: str = ""
    content_keywords_matched: List[str] = field(default_factory=list)
    
    quality_score: float = 0.0
    quality_analysis: str = ""
    resolution_width: int = 0
    resolution_height: int = 0
    color_count: int = 0
    avg_brightness: float = 0.0
    has_artifacts: bool = False
    
    diversity_score: float = 0.0
    diversity_analysis: str = ""
    diversity_flags: List[str] = field(default_factory=list)
    
    appropriateness_score: float = 0.0
    appropriateness_analysis: str = ""
    appropriateness_flags: List[str] = field(default_factory=list)
    
    # Overall assessment
    overall_score: float = 0.0
    is_valid: bool = False
    pass_status: str = ""  # "PASS", "FAIL", "REVIEW", "BLOCKED"
    reason: str = ""
    
    # Metadata
    validated_at: str = ""
    validation_errors: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Initialize defaults"""
        if not self.validated_at:
            self.validated_at = datetime.now().isoformat()
        if not self.file_name:
            self.file_name = Path(self.file_path).name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


# ============================================================================
# MEDIA VALIDATOR AGENT
# ============================================================================

class MediaValidator:
    """Production-ready media validator agent"""
    
    # Keywords for content validation
    CONTENT_KEYWORDS = {
        'children': ['child', 'kid', 'toddler', 'baby', 'boy', 'girl', 'play', 'learn'],
        'families': ['family', 'parent', 'mother', 'father', 'caregiver', 'together'],
        'learning': ['learn', 'education', 'school', 'activity', 'development', 'growth'],
        'communication': ['talk', 'speech', 'language', 'listen', 'speak', 'communicate'],
        'support': ['help', 'support', 'care', 'therapy', 'resource', 'guide'],
        'positive': ['happy', 'joy', 'smile', 'fun', 'creative', 'inclusive', 'diverse'],
    }
    
    # Color thresholds for autism-friendly (warm, inviting)
    WARM_COLOR_RANGE = {
        'warm_hues': (15, 60),  # Orange, yellow, reds
        'neutral_hues': (0, 15),  # Reds
        'cool_hues': (180, 360),  # Blues, greens
    }
    
    def __init__(
        self,
        config: Optional[ValidatorConfig] = None,
        log_level: LogLevel = LogLevel.INFO
    ) -> None:
        """
        Initialize media validator agent
        
        Args:
            config: Optional ValidatorConfig (uses defaults if None)
            log_level: Logging level for output
        """
        self.config = config or ValidatorConfig()
        
        # Configure logging
        global logger
        logger = setup_logger(__name__, log_level)
        
        logger.info(f"✅ Media Validator Agent initialized")
        logger.debug(f"   Cartoon confidence threshold: {self.config.min_cartoon_confidence}")
        logger.debug(f"   Content score threshold: {self.config.min_content_score}")
        logger.debug(f"   Quality score threshold: {self.config.min_quality_score}")
        logger.debug(f"   Overall score threshold: {self.config.min_overall_score}")
    
    def validate_image(self, image_path: str) -> MediaImage:
        """
        Validate a downloaded image against all requirements
        
        Args:
            image_path: Path to image file
        
        Returns:
            MediaImage with validation results
        """
        image_path_obj = Path(image_path)
        
        # Create result object
        result = MediaImage(file_path=str(image_path), file_name=image_path_obj.name)
        
        # Check if file exists
        if not image_path_obj.exists():
            error_msg = f"Image not found: {image_path}"
            logger.warning(f"⚠️  {error_msg}")
            result.validation_errors.append(error_msg)
            result.pass_status = "BLOCKED"
            result.reason = "File not found"
            return result
        
        try:
            result.file_size = image_path_obj.stat().st_size
            logger.info(f"\n🔍 Validating: {result.file_name}")
            
            # Open image
            try:
                image = Image.open(image_path)
            except Exception as e:
                error_msg = f"Cannot open image: {str(e)}"
                logger.error(f"❌ {error_msg}")
                result.validation_errors.append(error_msg)
                result.pass_status = "BLOCKED"
                result.reason = "Invalid image file"
                return result
            
            # Extract basic image properties
            result.resolution_width, result.resolution_height = image.size
            
            # Run validation checks
            self._validate_cartoon_style(result, image)
            self._validate_content(result)
            self._validate_quality(result, image)
            self._validate_diversity(result)
            self._validate_appropriateness(result)
            
            # Calculate overall score (weighted average)
            self._calculate_overall_score(result)
            
            # Determine pass status
            self._determine_pass_status(result)
            
            # Log result
            self._log_validation_result(result)
            
            return result
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            result.validation_errors.append(error_msg)
            result.pass_status = "BLOCKED"
            result.reason = "Unexpected error during validation"
            return result
    
    def _validate_cartoon_style(self, result: MediaImage, image: Image.Image) -> None:
        """Verify image is cartoon/illustration style"""
        try:
            # Analyze image characteristics for cartoon detection
            # Cartoons typically have: distinct colors, clear edges, limited palette
            
            image_rgb = image.convert('RGB')
            pixels = list(image_rgb.getdata())  # type: ignore
            
            # Count unique colors
            unique_colors = len(set(pixels))  # type: ignore
            result.color_count = unique_colors
            
            # Cartoons typically have fewer unique colors than photos
            # Photos: 100,000+ colors; Cartoons: 1,000-50,000 colors
            if unique_colors < 5000:
                cartoon_confidence = 0.9
            elif unique_colors < 20000:
                cartoon_confidence = 0.7
            elif unique_colors < 50000:
                cartoon_confidence = 0.5
            else:
                cartoon_confidence = 0.2  # Likely a photo
            
            # Check color saturation (cartoons often have more vibrant colors)
            img_hsv = image.convert('HSV')
            pixels_hsv = list(img_hsv.getdata())  # type: ignore
            saturations = [p[1] for p in pixels_hsv if len(p) >= 2]  # type: ignore
            avg_saturation = sum(saturations) / len(saturations) if saturations else 128
            
            if avg_saturation > 150:
                cartoon_confidence += 0.1
            
            # Clamp confidence to 0-1
            cartoon_confidence = max(0.0, min(1.0, cartoon_confidence))
            
            result.is_cartoon = cartoon_confidence >= self.config.min_cartoon_confidence
            result.cartoon_confidence = cartoon_confidence
            result.cartoon_analysis = (
                f"Unique colors: {unique_colors} | "
                f"Avg saturation: {avg_saturation:.0f} | "
                f"Confidence: {cartoon_confidence:.1%}"
            )
            
            logger.debug(f"   Cartoon style: {cartoon_confidence:.1%}")
            
        except Exception as e:
            logger.warning(f"⚠️  Cartoon style analysis failed: {str(e)[:50]}")
            result.cartoon_confidence = 0.5
            result.cartoon_analysis = f"Analysis error: {str(e)[:50]}"
    
    def _validate_content(self, result: MediaImage) -> None:
        """Verify content relevance to SLP/families/children"""
        # Since we can't deeply analyze image content without vision AI,
        # we use file name analysis and heuristics based on known good patterns
        
        file_name = result.file_name.lower()
        
        # Score based on content keywords in filename
        matched_keywords = []
        category_matches = {category: 0 for category in self.CONTENT_KEYWORDS}
        
        for category, keywords in self.CONTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in file_name:
                    category_matches[category] += 1
                    if keyword not in matched_keywords:
                        matched_keywords.append(keyword)
        
        # Calculate content score
        if matched_keywords:
            # Base score from matches
            match_score = min(100.0, len(matched_keywords) * 15.0)
            
            # Boost if multiple categories matched
            category_count = sum(1 for v in category_matches.values() if v > 0)
            category_boost = category_count * 5.0
            
            content_score = min(100.0, match_score + category_boost)
        else:
            # Default score for unknown files
            content_score = 50.0
        
        result.content_score = content_score
        result.content_keywords_matched = matched_keywords
        result.content_analysis = (
            f"Keywords matched: {', '.join(matched_keywords[:3]) if matched_keywords else 'generic'} | "
            f"Score: {content_score:.0f}/100"
        )
        
        logger.debug(f"   Content relevance: {content_score:.0f}/100")
    
    def _validate_quality(self, result: MediaImage, image: Image.Image) -> None:
        """Analyze resolution, clarity, color scheme"""
        try:
            # Resolution score
            resolution_score = 0.0
            if result.resolution_width >= 1920 or result.resolution_height >= 1080:
                resolution_score = 100.0
            elif result.resolution_width >= 1280 or result.resolution_height >= 720:
                resolution_score = 85.0
            elif result.resolution_width >= 800 or result.resolution_height >= 600:
                resolution_score = 70.0
            elif result.resolution_width >= 400 and result.resolution_height >= 300:
                resolution_score = 55.0
            else:
                resolution_score = 30.0
            
            # Analyze brightness and contrast
            image_rgb = image.convert('RGB')
            stat = ImageStat.Stat(image_rgb)
            
            avg_r, avg_g, avg_b = stat.mean[:3]
            result.avg_brightness = (avg_r + avg_g + avg_b) / 3.0
            
            # Brightness score (warm, inviting tone preferred for family content)
            # Slightly bright and warm (not too dark, not overly bright)
            if 60 <= result.avg_brightness <= 180:
                brightness_score = 90.0
            elif 40 <= result.avg_brightness <= 200:
                brightness_score = 75.0
            else:
                brightness_score = 50.0
            
            # Analyze color variance (for artifact detection)
            std_dev_r, std_dev_g, std_dev_b = stat.stddev[:3]
            color_variance = (std_dev_r + std_dev_g + std_dev_b) / 3.0
            
            # Lower variance indicates possible compression artifacts
            if color_variance < 20:
                has_artifacts = True
                artifact_penalty = 20.0
            elif color_variance > self.config.max_color_variance:
                # Excessive variance might indicate noise
                has_artifacts = True
                artifact_penalty = 15.0
            else:
                has_artifacts = False
                artifact_penalty = 0.0
            
            result.has_artifacts = has_artifacts
            
            # Combine quality factors (weighted average)
            quality_score = (
                resolution_score * 0.4 +
                brightness_score * 0.35 +
                (100.0 - artifact_penalty) * 0.25
            )
            
            result.quality_score = quality_score
            result.quality_analysis = (
                f"Resolution: {result.resolution_width}x{result.resolution_height} ({resolution_score:.0f}) | "
                f"Brightness: {result.avg_brightness:.0f} | "
                f"Artifacts: {'Yes' if has_artifacts else 'No'} | "
                f"Score: {quality_score:.0f}/100"
            )
            
            logger.debug(f"   Quality score: {quality_score:.0f}/100")
            
        except Exception as e:
            logger.warning(f"⚠️  Quality analysis failed: {str(e)[:50]}")
            result.quality_score = 50.0
            result.quality_analysis = f"Analysis error: {str(e)[:50]}"
    
    def _validate_diversity(self, result: MediaImage) -> None:
        """Check for diverse representation (age, ethnicity, abilities)"""
        # Since we can't perform deep visual analysis without vision AI,
        # we use a heuristic approach based on content patterns
        
        diversity_flags = []
        diversity_score = 70.0  # Default baseline
        
        file_name = result.file_name.lower()
        
        # Check for potential homogeneity signals
        if 'child' in file_name or 'kid' in file_name:
            diversity_score += 10.0  # Child content shows potential diversity
        
        if 'family' in file_name or 'group' in file_name:
            diversity_score += 5.0  # Group content likely has diversity
        
        # Flag for manual review if unclear
        if 'adult' in file_name or 'person' in file_name:
            diversity_flags.append("single_subject_detected")
        
        # File name analysis for potential issues
        if diversity_score < self.config.min_diversity_score:
            diversity_flags.append("low_diversity_indicator")
        
        result.diversity_score = min(100.0, diversity_score)
        result.diversity_flags = diversity_flags
        result.diversity_analysis = (
            f"Diversity score: {result.diversity_score:.0f}/100 | "
            f"Flags: {', '.join(diversity_flags) if diversity_flags else 'none'}"
        )
        
        logger.debug(f"   Diversity score: {result.diversity_score:.0f}/100")
    
    def _validate_appropriateness(self, result: MediaImage) -> None:
        """Ensure respectful and positive content for autism awareness"""
        appropriateness_flags = []
        appropriateness_score = 85.0  # Default baseline
        
        file_name = result.file_name.lower()
        
        # Positive indicators
        positive_indicators = ['play', 'learn', 'joy', 'happy', 'support', 'inclusive']
        for indicator in positive_indicators:
            if indicator in file_name:
                appropriateness_score += 2.0
        
        # Red flags for inappropriate content
        red_flags = ['negative', 'struggle', 'deficit', 'broken', 'sad', 'sick']
        for flag in red_flags:
            if flag in file_name:
                appropriateness_score -= 10.0
                appropriateness_flags.append(f"potential_{flag}_content")
        
        # Ensure positive framing
        if 'autism' not in file_name and 'neurodiverse' not in file_name:
            # Content doesn't explicitly mention autism, which is fine for general content
            pass
        
        result.appropriateness_score = max(0.0, min(100.0, appropriateness_score))
        result.appropriateness_flags = appropriateness_flags
        result.appropriateness_analysis = (
            f"Appropriateness score: {result.appropriateness_score:.0f}/100 | "
            f"Flags: {', '.join(appropriateness_flags) if appropriateness_flags else 'none'}"
        )
        
        logger.debug(f"   Appropriateness score: {result.appropriateness_score:.0f}/100")
    
    def _calculate_overall_score(self, result: MediaImage) -> None:
        """Calculate weighted overall validation score"""
        # Weighted average of all components
        overall_score = (
            result.cartoon_confidence * 100.0 * self.config.cartoon_weight +
            result.content_score * self.config.content_weight +
            result.quality_score * self.config.quality_weight +
            result.diversity_score * self.config.diversity_weight +
            result.appropriateness_score * self.config.appropriateness_weight
        )
        
        result.overall_score = overall_score
    
    def _determine_pass_status(self, result: MediaImage) -> None:
        """Determine pass/fail/review status based on validation results"""
        # Check individual thresholds first
        fails = []
        
        if result.cartoon_confidence < self.config.min_cartoon_confidence:
            fails.append(f"style ({result.cartoon_confidence:.1%})")
        
        if result.content_score < self.config.min_content_score:
            fails.append(f"content ({result.content_score:.0f})")
        
        if result.quality_score < self.config.min_quality_score:
            fails.append(f"quality ({result.quality_score:.0f})")
        
        if result.diversity_score < self.config.min_diversity_score:
            fails.append(f"diversity ({result.diversity_score:.0f})")
        
        if result.appropriateness_score < self.config.min_appropriateness_score:
            fails.append(f"appropriateness ({result.appropriateness_score:.0f})")
        
        # Determine status
        if result.resolution_width < self.config.min_resolution_width or \
           result.resolution_height < self.config.min_resolution_height:
            result.pass_status = "BLOCKED"
            result.reason = f"Resolution too low: {result.resolution_width}x{result.resolution_height}"
            result.is_valid = False
        elif fails:
            result.pass_status = "FAIL"
            result.reason = f"Failed validation on: {', '.join(fails)}"
            result.is_valid = False
        elif result.overall_score < self.config.min_overall_score:
            result.pass_status = "REVIEW"
            result.reason = f"Overall score below threshold: {result.overall_score:.0f}"
            result.is_valid = False
            result.tags.append("manual_review_recommended")
        else:
            result.pass_status = "PASS"
            result.reason = "Passed all validation checks"
            result.is_valid = True
            
            # Add quality tags
            if result.overall_score >= 85.0:
                result.tags.append("high_quality")
            if result.cartoon_confidence >= 0.8:
                result.tags.append("strong_cartoon_style")
            if result.diversity_score >= 80.0:
                result.tags.append("diverse_representation")
    
    def _log_validation_result(self, result: MediaImage) -> None:
        """Log validation result with appropriate emoji"""
        emoji_map = {
            "PASS": "✅",
            "FAIL": "❌",
            "REVIEW": "⚠️ ",
            "BLOCKED": "🚫",
        }
        
        emoji = emoji_map.get(result.pass_status, "📌")
        logger.info(
            f"   {emoji} {result.pass_status} - Overall: {result.overall_score:.0f} | "
            f"Style: {result.cartoon_confidence:.1%} | "
            f"Content: {result.content_score:.0f} | "
            f"Quality: {result.quality_score:.0f}"
        )
    
    def validate_batch(
        self,
        image_paths: List[str],
        handout_name: Optional[str] = None
    ) -> Tuple[List[MediaImage], List[str]]:
        """
        Validate multiple images
        
        Args:
            image_paths: List of image file paths
            handout_name: Optional handout name for logging
        
        Returns:
            Tuple of (valid MediaImage results, failed file paths)
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🔄 Batch validating {len(image_paths)} images")
        if handout_name:
            logger.info(f"   Handout: {handout_name}")
        logger.info(f"{'='*70}")
        
        valid_results: List[MediaImage] = []
        failed_paths: List[str] = []
        
        for i, image_path in enumerate(image_paths, 1):
            logger.info(f"\n[{i}/{len(image_paths)}] Processing...")
            result = self.validate_image(image_path)
            
            if result.is_valid:
                valid_results.append(result)
            else:
                failed_paths.append(image_path)
        
        # Summary
        logger.info(f"\n{'='*70}")
        logger.info(f"📊 Batch Results:")
        logger.info(f"   ✅ Valid: {len(valid_results)}")
        logger.info(f"   ❌ Failed: {len(failed_paths)}")
        logger.info(f"   Average score: {self._calculate_average_score(valid_results):.0f}")
        logger.info(f"{'='*70}")
        
        return valid_results, failed_paths
    
    def _calculate_average_score(self, results: List[MediaImage]) -> float:
        """Calculate average overall score"""
        if not results:
            return 0.0
        return sum(r.overall_score for r in results) / len(results)
    
    def generate_report(
        self,
        valid_results: List[MediaImage],
        failed_results: List[MediaImage],
        handout_name: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive validation report
        
        Args:
            valid_results: List of passing MediaImage results
            failed_results: List of failing MediaImage results
            handout_name: Optional handout identifier
            output_path: Optional path to save JSON report
        
        Returns:
            Dictionary with report data
        """
        all_results = valid_results + failed_results
        
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "handout_name": handout_name or "unknown",
                "total_images": len(all_results),
            },
            "summary": {
                "passed": len(valid_results),
                "failed": len(failed_results),
                "pass_rate": (len(valid_results) / len(all_results) * 100) if all_results else 0.0,
                "average_overall_score": self._calculate_average_score(valid_results),
                "average_cartoon_confidence": (
                    sum(r.cartoon_confidence for r in valid_results) / len(valid_results)
                    if valid_results else 0.0
                ),
                "average_content_score": (
                    sum(r.content_score for r in valid_results) / len(valid_results)
                    if valid_results else 0.0
                ),
                "average_quality_score": (
                    sum(r.quality_score for r in valid_results) / len(valid_results)
                    if valid_results else 0.0
                ),
                "average_diversity_score": (
                    sum(r.diversity_score for r in valid_results) / len(valid_results)
                    if valid_results else 0.0
                ),
                "average_appropriateness_score": (
                    sum(r.appropriateness_score for r in valid_results) / len(valid_results)
                    if valid_results else 0.0
                ),
            },
            "passed_validations": [r.to_dict() for r in valid_results],
            "failed_validations": [r.to_dict() for r in failed_results],
            "recommendations": self._generate_recommendations(all_results),
        }
        
        # Save report if path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"📄 Report saved: {output_file}")
        
        return report
    
    def _generate_recommendations(self, all_results: List[MediaImage]) -> Dict[str, Any]:
        """Generate actionable recommendations from validation results"""
        recommendations = {
            "total_recommendations": 0,
            "items": []
        }
        
        # Analyze failure patterns
        failure_reasons = Counter()
        for result in all_results:
            if not result.is_valid and result.reason:
                failure_reasons[result.reason] += 1
        
        # Common failure patterns
        if failure_reasons:
            for reason, count in failure_reasons.most_common(3):
                recommendations["items"].append({
                    "type": "pattern",
                    "frequency": count,
                    "issue": reason,
                    "recommendation": self._get_recommendation_for_issue(reason)
                })
        
        # Quality improvement suggestions
        low_diversity = [r for r in all_results if r.diversity_score < 60.0]
        if low_diversity:
            recommendations["items"].append({
                "type": "improvement",
                "count": len(low_diversity),
                "issue": "Low diversity representation",
                "recommendation": "Consider sourcing more diverse images showing different age groups, ethnicities, abilities, and family structures"
            })
        
        # Manual review recommendations
        review_candidates = [r for r in all_results if "manual_review_recommended" in r.tags]
        if review_candidates:
            recommendations["items"].append({
                "type": "review",
                "count": len(review_candidates),
                "files": [r.file_name for r in review_candidates[:5]],
                "recommendation": "These images scored near the threshold and may benefit from manual review"
            })
        
        recommendations["total_recommendations"] = len(recommendations["items"])
        return recommendations
    
    def _get_recommendation_for_issue(self, issue: str) -> str:
        """Get recommendation for specific issue"""
        recommendations = {
            "resolution_too_low": "Source higher resolution images (at least 800x600, preferably 1280x720 or higher)",
            "style": "Ensure downloaded images are cartoons/illustrations, not photographs",
            "content": "Verify images are relevant to SLP, families, children, communication, or autism awareness",
            "quality": "Check for compression artifacts and ensure good clarity",
            "diversity": "Ensure diverse representation of ages, ethnicities, and abilities",
            "appropriateness": "Verify images are respectful and positive for autism awareness context",
        }
        
        for key, rec in recommendations.items():
            if key.lower() in issue.lower():
                return rec
        
        return "Review and resample this category of images"


# ============================================================================
# INTEGRATION WITH MEDIA GATHERING AGENT
# ============================================================================

def create_validation_filter(
    validator: MediaValidator,
    strict: bool = False
) -> Any:
    """
    Create a filter function for media gathering agent
    
    Usage:
        validator = MediaValidator()
        filter_fn = create_validation_filter(validator)
        
        # In media gathering agent:
        for result in media_results:
            if filter_fn(result):
                # Process validated media
    
    Args:
        validator: Initialized MediaValidator
        strict: If True, only pass PASS status. If False, allow REVIEW status
    
    Returns:
        Filter function for use with media agent
    """
    def validate_media_result(result: Dict[str, Any]) -> bool:
        """Filter function to validate media result"""
        local_path = result.get('local_path')
        if local_path and Path(local_path).exists():
            validation = validator.validate_image(local_path)
            result['validation'] = validation.to_dict()
            
            if strict:
                return validation.pass_status == "PASS"
            else:
                return validation.pass_status in ["PASS", "REVIEW"]
        return True  # Pass through if no local path
    
    return validate_media_result


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def main() -> None:
    """Example usage of media validator agent"""
    
    # Initialize validator with custom config
    config = ValidatorConfig(
        min_cartoon_confidence=0.6,
        min_content_score=60.0,
        min_quality_score=50.0,
        min_overall_score=65.0,
    )
    
    validator = MediaValidator(
        config=config,
        log_level=LogLevel.INFO
    )
    
    # Example 1: Validate images from each handout
    logger.info(f"\n{'='*70}")
    logger.info("EXAMPLE 1: Validating images from handout directories")
    logger.info(f"{'='*70}")
    
    media_dir = Path("media")
    if media_dir.exists():
        for handout_dir in sorted(media_dir.glob("handout_*")):
            if not handout_dir.is_dir():
                continue
            
            image_files = (
                list(handout_dir.glob("*.jpg")) +
                list(handout_dir.glob("*.png")) +
                list(handout_dir.glob("*.jpeg"))
            )
            
            if image_files:
                logger.info(f"\n📁 Processing: {handout_dir.name}")
                valid, failed = validator.validate_batch(
                    [str(f) for f in sorted(image_files)],
                    handout_name=handout_dir.name
                )
                
                # Generate report for this handout
                failed_results = []
                report = validator.generate_report(
                    valid,
                    failed_results,
                    handout_name=handout_dir.name,
                    output_path=f"validation_report_{handout_dir.name}.json"
                )
                
                logger.info(f"✅ Report generated with {len(valid)} valid images")
    else:
        logger.warning(f"Media directory not found: {media_dir}")
    
    # Example 2: Full validation workflow
    logger.info(f"\n{'='*70}")
    logger.info("EXAMPLE 2: Full validation workflow")
    logger.info(f"{'='*70}")
    
    all_media_dir = Path("media")
    if all_media_dir.exists():
        all_images = []
        for image_file in all_media_dir.glob("**/*.{jpg,png,jpeg}"):
            if image_file.is_file():
                all_images.append(str(image_file))
        
        if all_images:
            logger.info(f"\nValidating {len(all_images)} total images...")
            valid_results, failed_paths = validator.validate_batch(all_images)
            
            # Create failed MediaImage results for reporting
            failed_results = []
            for path in failed_paths:
                failed_results.append(validator.validate_image(path))
            
            # Generate comprehensive report
            report = validator.generate_report(
                valid_results,
                failed_results,
                handout_name="all_handouts",
                output_path="validation_report_comprehensive.json"
            )
            
            # Print recommendations
            logger.info(f"\n{'='*70}")
            logger.info("RECOMMENDATIONS")
            logger.info(f"{'='*70}")
            for rec in report["recommendations"]["items"]:
                logger.info(f"\n📌 {rec['type'].upper()}")
                logger.info(f"   Issue: {rec.get('issue', 'N/A')}")
                logger.info(f"   Recommendation: {rec['recommendation']}")
        else:
            logger.warning("No images found to validate")
    
    # Example 3: Integration with media gathering agent
    logger.info(f"\n{'='*70}")
    logger.info("EXAMPLE 3: Integration example")
    logger.info(f"{'='*70}")
    logger.info("\nTo integrate with media_gathering_agent.py:")
    logger.info("  1. Import: from media_validator import MediaValidator, create_validation_filter")
    logger.info("  2. Initialize: validator = MediaValidator()")
    logger.info("  3. Create filter: filter_fn = create_validation_filter(validator)")
    logger.info("  4. Apply to results: validated = filter(filter_fn, media_results)")


if __name__ == "__main__":
    main()
