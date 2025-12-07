#!/usr/bin/env python3
"""
Integration Example: Using Media Validator with Media Gathering Agent

This example demonstrates how to:
1. Gather media using MediaGatheringAgent
2. Validate gathered media using MediaValidator
3. Generate validation reports
4. Select high-quality images for presentation
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from media_validator import (
    MediaValidator,
    ValidatorConfig,
    LogLevel,
    create_validation_filter,
)


def example_1_validate_existing_media() -> None:
    """Example 1: Validate media that's already been downloaded"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Validate Existing Media")
    print("="*70)
    
    # Initialize validator with custom config for presentation
    config = ValidatorConfig(
        min_cartoon_confidence=0.65,
        min_content_score=65.0,
        min_quality_score=60.0,
        min_overall_score=70.0,
    )
    
    validator = MediaValidator(
        config=config,
        log_level=LogLevel.INFO
    )
    
    # Find all media files
    media_dir = Path("media")
    if not media_dir.exists():
        print("⚠️  Media directory not found")
        return
    
    image_files = []
    for ext in ["*.jpg", "*.png", "*.jpeg"]:
        image_files.extend(media_dir.glob(f"**/{ext}"))
    
    if not image_files:
        print("⚠️  No images found")
        return
    
    print(f"\n📁 Found {len(image_files)} images")
    
    # Validate all images
    valid_results, failed_paths = validator.validate_batch(
        [str(f) for f in sorted(image_files)]
    )
    
    # Generate report
    failed_results = []
    for path in failed_paths:
        failed_results.append(validator.validate_image(path))
    
    report = validator.generate_report(
        valid_results=valid_results,
        failed_results=failed_results,
        handout_name="all_media",
        output_path="validation_report_comprehensive.json"
    )
    
    # Print summary
    print(f"\n📊 VALIDATION SUMMARY")
    print(f"   Total: {report['metadata']['total_images']}")
    print(f"   Valid: {report['summary']['passed']}")
    print(f"   Failed: {report['summary']['failed']}")
    print(f"   Pass Rate: {report['summary']['pass_rate']:.1f}%")
    print(f"   Avg Score: {report['summary']['average_overall_score']:.0f}/100")


def example_2_quality_selection() -> None:
    """Example 2: Select images based on quality tier"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Quality Tier Selection")
    print("="*70)
    
    validator = MediaValidator(log_level=LogLevel.WARNING)
    
    media_dir = Path("media")
    if not media_dir.exists():
        return
    
    image_files = []
    for ext in ["*.jpg", "*.png", "*.jpeg"]:
        image_files.extend(media_dir.glob(f"**/{ext}"))
    
    if not image_files:
        return
    
    # Validate
    valid_results, _ = validator.validate_batch(
        [str(f) for f in sorted(image_files)]
    )
    
    # Organize by quality tier
    high_quality = [r for r in valid_results if r.overall_score >= 80.0]
    medium_quality = [r for r in valid_results 
                      if 70.0 <= r.overall_score < 80.0]
    low_quality = [r for r in valid_results 
                   if r.overall_score < 70.0]
    
    print(f"\n🏆 HIGH QUALITY (≥80): {len(high_quality)} images")
    for img in high_quality[:3]:
        print(f"   ✅ {img.file_name}: {img.overall_score:.0f}")
    
    print(f"\n⚡ MEDIUM QUALITY (70-80): {len(medium_quality)} images")
    for img in medium_quality[:3]:
        print(f"   ⚠️  {img.file_name}: {img.overall_score:.0f}")
    
    print(f"\n📌 LOW QUALITY (<70): {len(low_quality)} images")
    for img in low_quality[:3]:
        print(f"   ❌ {img.file_name}: {img.overall_score:.0f}")
    
    print(f"\n💡 Recommendation: Use high quality tier for primary content")


def example_3_content_analysis() -> None:
    """Example 3: Analyze content distribution"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Content Analysis")
    print("="*70)
    
    validator = MediaValidator(log_level=LogLevel.WARNING)
    
    media_dir = Path("media")
    if not media_dir.exists():
        return
    
    image_files = []
    for ext in ["*.jpg", "*.png", "*.jpeg"]:
        image_files.extend(media_dir.glob(f"**/{ext}"))
    
    if not image_files:
        return
    
    # Validate
    results = []
    for image_path in sorted(image_files):
        result = validator.validate_image(str(image_path))
        results.append(result)
    
    # Analyze content
    content_distribution = {}
    for result in results:
        keywords = result.content_keywords_matched
        for keyword in keywords:
            if keyword not in content_distribution:
                content_distribution[keyword] = 0
            content_distribution[keyword] += 1
    
    # Print distribution
    print(f"\n📊 CONTENT KEYWORD DISTRIBUTION")
    if content_distribution:
        sorted_keywords = sorted(
            content_distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )
        for keyword, count in sorted_keywords:
            print(f"   {keyword}: {count} images")
    else:
        print("   No content keywords matched (consider renaming files)")
    
    # Diversity analysis
    high_diversity = [r for r in results if r.diversity_score >= 80.0]
    flagged_diversity = [r for r in results if r.diversity_flags]
    
    print(f"\n🌍 DIVERSITY ANALYSIS")
    print(f"   High diversity: {len(high_diversity)}")
    print(f"   Flagged for review: {len(flagged_diversity)}")
    
    if flagged_diversity:
        print(f"   Examples: {', '.join([r.file_name for r in flagged_diversity[:3]])}")


def example_4_batch_handout_validation() -> None:
    """Example 4: Validate media for each handout separately"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Per-Handout Validation")
    print("="*70)
    
    validator = MediaValidator(log_level=LogLevel.WARNING)
    
    media_dir = Path("media")
    if not media_dir.exists():
        return
    
    # Find all handout directories
    handout_dirs = sorted([d for d in media_dir.glob("handout_*") 
                          if d.is_dir()])
    
    if not handout_dirs:
        print("⚠️  No handout directories found")
        return
    
    # Validate each handout
    all_results = {}
    for handout_dir in handout_dirs:
        image_files = []
        for ext in ["*.jpg", "*.png", "*.jpeg"]:
            image_files.extend(handout_dir.glob(ext))
        
        if image_files:
            valid, failed = validator.validate_batch(
                [str(f) for f in sorted(image_files)],
                handout_name=handout_dir.name
            )
            
            all_results[handout_dir.name] = {
                'valid': valid,
                'failed': failed,
                'pass_rate': len(valid) / (len(valid) + len(failed)) * 100
                             if (len(valid) + len(failed)) > 0 else 0,
            }
    
    # Summary table
    print(f"\n📋 HANDOUT SUMMARY")
    print(f"{'Handout':<35} {'Valid':>6} {'Failed':>6} {'Pass Rate':>10}")
    print("-" * 60)
    
    for handout_name, stats in all_results.items():
        total = len(stats['valid']) + len(stats['failed'])
        print(f"{handout_name:<35} {len(stats['valid']):>6} "
              f"{len(stats['failed']):>6} {stats['pass_rate']:>9.0f}%")


def example_5_strict_vs_lenient() -> None:
    """Example 5: Comparing strict vs lenient validation"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Strict vs Lenient Validation")
    print("="*70)
    
    media_dir = Path("media")
    if not media_dir.exists():
        return
    
    image_files = []
    for ext in ["*.jpg", "*.png", "*.jpeg"]:
        image_files.extend(media_dir.glob(f"**/{ext}"))
    
    if not image_files:
        return
    
    # Strict validation (high standards)
    strict_config = ValidatorConfig(
        min_overall_score=80.0,
        min_cartoon_confidence=0.75,
        min_content_score=75.0,
        min_quality_score=75.0,
    )
    strict_validator = MediaValidator(config=strict_config, log_level=LogLevel.WARNING)
    
    # Lenient validation (lower standards)
    lenient_config = ValidatorConfig(
        min_overall_score=60.0,
        min_cartoon_confidence=0.5,
        min_content_score=50.0,
        min_quality_score=40.0,
    )
    lenient_validator = MediaValidator(config=lenient_config, log_level=LogLevel.WARNING)
    
    # Run both validations
    print(f"\n🔍 Running strict validation...")
    strict_valid, _ = strict_validator.validate_batch(
        [str(f) for f in sorted(image_files)]
    )
    
    print(f"🔍 Running lenient validation...")
    lenient_valid, _ = lenient_validator.validate_batch(
        [str(f) for f in sorted(image_files)]
    )
    
    # Compare results
    print(f"\n📊 VALIDATION COMPARISON")
    print(f"   Strict mode:   {len(strict_valid)} images approved")
    print(f"   Lenient mode:  {len(lenient_valid)} images approved")
    
    strict_names = {r.file_name for r in strict_valid}
    lenient_names = {r.file_name for r in lenient_valid}
    
    only_lenient = lenient_names - strict_names
    if only_lenient:
        print(f"\n   Images approved only in lenient mode: {len(only_lenient)}")
        for name in list(only_lenient)[:3]:
            print(f"      • {name}")


def main() -> None:
    """Run all integration examples"""
    print("\n" + "="*70)
    print("MEDIA VALIDATOR INTEGRATION EXAMPLES")
    print("="*70)
    
    try:
        example_1_validate_existing_media()
        example_2_quality_selection()
        example_3_content_analysis()
        example_4_batch_handout_validation()
        example_5_strict_vs_lenient()
        
        print("\n" + "="*70)
        print("✅ ALL EXAMPLES COMPLETED")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
