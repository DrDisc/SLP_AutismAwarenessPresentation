#!/usr/bin/env python3
"""
Cartoon & Illustration Media Retrieval for Handout 1: What is a Speech-Language Pathologist?

This script demonstrates retrieving cartoon/illustration images for each section
of the SLP awareness handout with optimized cartoon detection and style constraints.

Sections covered:
1. Who Are We? (SLPs with children)
2. How SLPs Help Children with Autism (learning/communication)
3. What Makes SLP Services Unique (collaborative care)
4. What to Expect from SLP Services (assessment/therapy)

Features:
- Multiple cartoon-optimized queries per section
- High style confidence weighting for cartoon detection
- Organized output structure by section
- Comprehensive JSON reporting
- Error handling and retry logic
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Import media gathering agent
try:
    from media_gathering_agent import (
        MediaGatheringAgent,
        MediaRequest,
        AgentConfig,
        LogLevel
    )
except ImportError:
    print("❌ Error: media_gathering_agent.py not found in current directory")
    print("   Please ensure media_gathering_agent.py is in the same location")
    sys.exit(1)


# ============================================================================
# HANDOUT 1 MEDIA CONFIGURATION
# ============================================================================

@dataclass
class Section:
    """Structure for handout sections"""
    name: str
    description: str
    queries: List[str]
    target_quantity: int = 3
    quality: str = "professional"


# Define all sections for Handout 1
HANDOUT_1_SECTIONS = [
    Section(
        name="Who Are We?",
        description="SLPs with children - showing professional interaction",
        queries=[
            "speech pathologist working with children cartoon illustration",
            "therapist helping child communicate fun playful illustration",
            "professional women working with kids educational cartoon",
            "diverse children learning with adult support cartoon",
            "SLP speech therapy session cartoon illustration",
        ],
        target_quantity=3,
        quality="professional"
    ),
    Section(
        name="How SLPs Help Children with Autism",
        description="Learning and communication support",
        queries=[
            "child learning communication skills cartoon illustration",
            "autism communication therapy playful cartoon",
            "children developing language skills fun illustration",
            "social communication learning cartoon diverse",
            "speech development activities children cartoon",
        ],
        target_quantity=3,
        quality="professional"
    ),
    Section(
        name="What Makes SLP Services Unique?",
        description="Collaborative and family-centered care",
        queries=[
            "team collaboration healthcare professionals cartoon",
            "family centered care parents children illustration",
            "multidisciplinary team working together cartoon",
            "therapist explaining to parents illustration",
            "collaborative support network children cartoon",
        ],
        target_quantity=2,
        quality="professional"
    ),
    Section(
        name="What to Expect from SLP Services",
        description="Assessment and therapy process",
        queries=[
            "therapy assessment children cartoon illustration",
            "speech therapist assessing child communication",
            "progress monitoring therapy session cartoon",
            "play-based learning therapy illustration",
            "individualized treatment plan cartoon",
        ],
        target_quantity=2,
        quality="professional"
    ),
]


# ============================================================================
# AGENT CONFIGURATION - CARTOON OPTIMIZED
# ============================================================================

def create_cartoon_optimized_config() -> AgentConfig:
    """
    Create AgentConfig optimized for cartoon/illustration detection.
    
    Key optimizations:
    - Higher style_confidence_weight (0.3 instead of 0.2)
    - Lower min_final_score for acceptance (45.0 instead of 50.0)
    - Better cartoon keyword matching
    - Stricter negative keywords for photos
    
    Returns:
        AgentConfig tuned for cartoon detection
    """
    config = AgentConfig(
        max_search_queries=5,
        results_per_source=5,
        
        # Scoring thresholds - stricter for style
        min_final_score=45.0,  # Lower threshold, rely on style confidence
        style_confidence_weight=0.3,  # Higher weight for style (cartoon vs photo)
        quality_weight=0.3,
        relevance_weight=0.5,
        
        # Default scores
        base_quality_score=70.0,
        base_relevance_score=50.0,
        base_style_confidence=0.4,  # Assume 40% base for unknown styles
        
        # Quality bonuses
        quality_bonus_fhd=15.0,
        quality_bonus_hd=10.0,
        quality_bonus_cc0=10.0,
        quality_bonus_free=5.0,
        
        # Download/API
        download_timeout=10,
        api_timeout=5,
        
        # Retry
        max_retries=3,
        retry_delay_base=1.0,
        
        # Style keywords - enhanced for cartoons
        style_keywords={
            'cartoon': {
                'positive': [
                    'cartoon', 'illustration', 'illustrated', 'comic',
                    'animated', 'animation', 'drawing', 'drawn', 'hand-drawn',
                    'vector', 'art', 'artistic', 'sketch', 'sketchy',
                    'cute', 'playful', 'fun', 'whimsical', 'stylized',
                    'graphic', 'design', 'digital art', 'clip art',
                    'colorful', 'vibrant', 'expressive', 'caricature'
                ],
                'negative': [
                    'photo', 'photograph', 'photography', 'real', 'realistic',
                    'stock photo', 'people', 'person', 'portrait', 'candid',
                    'camera', 'photograph', 'professional photo', 'stock',
                    'portrait photography', 'close-up', 'detail'
                ]
            }
        }
    )
    return config


# ============================================================================
# RETRIEVAL PROCESS
# ============================================================================

def retrieve_handout_1_media(
    output_dir: str = "media/handout_1_slp_info",
    dry_run: bool = False,
    verbose: bool = False
) -> Dict:
    """
    Retrieve cartoon media for all Handout 1 sections.
    
    Args:
        output_dir: Base directory for media output
        dry_run: If True, show queries without downloading
        verbose: If True, show detailed logging
    
    Returns:
        Dictionary with complete retrieval report
    """
    
    # Setup
    log_level = LogLevel.DEBUG if verbose else LogLevel.INFO
    config = create_cartoon_optimized_config()
    agent = MediaGatheringAgent(
        output_dir=output_dir,
        config=config,
        log_level=log_level
    )
    
    print("\n" + "="*80)
    print("HANDOUT 1: What is a Speech-Language Pathologist?")
    print("Cartoon & Illustration Media Retrieval")
    print("="*80)
    
    # Process all sections
    all_results = {
        'handout': 'HANDOUT_1_What_Is_SLP',
        'total_sections': len(HANDOUT_1_SECTIONS),
        'sections': {},
        'summary': {
            'total_retrieved': 0,
            'total_requested': 0,
            'sections_completed': 0,
            'sections_partial': 0,
            'sections_failed': 0,
        }
    }
    
    for section in HANDOUT_1_SECTIONS:
        print(f"\n📚 Section: {section.name}")
        print(f"   Description: {section.description}")
        print(f"   Target: {section.target_quantity} cartoon images")
        
        section_results = {
            'name': section.name,
            'description': section.description,
            'target_quantity': section.target_quantity,
            'queries_used': [],
            'results': []
        }
        
        total_section_retrieved = 0
        
        # Process each query in the section
        for query in section.queries:
            print(f"   🔍 Query: {query}")
            
            if dry_run:
                section_results['queries_used'].append(query)
                print(f"      [DRY RUN] Would retrieve with this query")
                continue
            
            try:
                # Create request with cartoon style constraint
                request = MediaRequest(
                    query=query,
                    media_type="image",
                    quantity=section.target_quantity,
                    quality=section.quality,
                    licensing="free",
                    context={
                        "handout": "1_slp_info",
                        "section": section.name
                    },
                    constraints={"style": "cartoon"}  # Cartoon/illustration only
                )
                
                # Process request
                report = agent.process_request(request)
                
                # Track results
                retrieved = report['summary']['total_retrieved']
                total_section_retrieved += retrieved
                
                section_results['queries_used'].append(query)
                for result in report['results']:
                    section_results['results'].append({
                        'title': result['title'],
                        'source': result['source'],
                        'local_path': result['local_path'],
                        'quality_score': result['quality_score'],
                        'relevance_score': result['relevance_score'],
                        'style_confidence': result['style_confidence'],
                        'final_score': result['final_score'],
                    })
                
                # Stop if we have enough for this section
                if total_section_retrieved >= section.target_quantity:
                    print(f"      ✓ Retrieved {total_section_retrieved} images (target met)")
                    break
                    
            except Exception as e:
                print(f"      ❌ Error: {str(e)[:100]}")
                continue
        
        # Update all results
        all_results['sections'][section.name] = section_results
        
        # Update summary
        if total_section_retrieved >= section.target_quantity:
            all_results['summary']['sections_completed'] += 1
        elif total_section_retrieved > 0:
            all_results['summary']['sections_partial'] += 1
        else:
            all_results['summary']['sections_failed'] += 1
        
        all_results['summary']['total_retrieved'] += total_section_retrieved
        all_results['summary']['total_requested'] += section.target_quantity
        
        print(f"   ✅ Section complete: {total_section_retrieved}/{section.target_quantity} retrieved")
    
    # Calculate completion rate
    if all_results['summary']['total_requested'] > 0:
        completion_rate = (
            all_results['summary']['total_retrieved'] /
            all_results['summary']['total_requested'] * 100
        )
        all_results['summary']['completion_rate'] = f"{completion_rate:.0f}%"
    else:
        all_results['summary']['completion_rate'] = "0%"
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✅ Sections Completed: {all_results['summary']['sections_completed']}/{all_results['summary']['total_sections']}")
    print(f"⚠️  Sections Partial:  {all_results['summary']['sections_partial']}")
    print(f"❌ Sections Failed:   {all_results['summary']['sections_failed']}")
    print(f"\n📊 Total Retrieved: {all_results['summary']['total_retrieved']}/{all_results['summary']['total_requested']}")
    print(f"📈 Completion Rate: {all_results['summary']['completion_rate']}")
    
    return all_results


# ============================================================================
# EXPORT & REPORTING
# ============================================================================

def save_report(results: Dict, output_file: str = "handout_1_retrieval_report.json") -> str:
    """
    Save retrieval report to JSON file.
    
    Args:
        results: Dictionary with retrieval results
        output_file: Output filename
    
    Returns:
        Path to saved report file
    """
    output_path = Path(output_file)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Report saved: {output_path}")
    return str(output_path)


def print_usage_examples():
    """Print usage examples for this script."""
    print("""
USAGE EXAMPLES:

1. Basic retrieval (download media):
   python3 handout_1_cartoon_retrieval.py

2. Dry run (show queries without downloading):
   python3 handout_1_cartoon_retrieval.py --dry-run

3. Verbose output with debug info:
   python3 handout_1_cartoon_retrieval.py --verbose

4. Custom output directory:
   python3 handout_1_cartoon_retrieval.py --output custom_media_dir

5. Dry run with verbose output:
   python3 handout_1_cartoon_retrieval.py --dry-run --verbose

OUTPUT:
- Media files: media/handout_1_slp_info/[section_name]/
- Report: handout_1_retrieval_report.json

FEATURES:
✓ Cartoon/illustration style constraints
✓ Optimized keyword matching
✓ Error handling and retry logic
✓ Organized by section
✓ JSON reporting with quality metrics
""")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Retrieve cartoon media for Handout 1: What is a Speech-Language Pathologist?"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show queries without downloading'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed debug output'
    )
    parser.add_argument(
        '--output',
        default='media',
        help='Output directory for media (default: media)'
    )
    parser.add_argument(
        '--help-examples',
        action='store_true',
        help='Show usage examples'
    )
    
    args = parser.parse_args()
    
    if args.help_examples:
        print_usage_examples()
        return
    
    # Run retrieval
    results = retrieve_handout_1_media(
        output_dir=args.output,
        dry_run=args.dry_run,
        verbose=args.verbose
    )
    
    # Save report
    if not args.dry_run:
        save_report(results)
    
    print("\n" + "="*80)
    print("✨ Handout 1 media retrieval complete!")
    print("="*80)


if __name__ == "__main__":
    main()
