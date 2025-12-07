#!/usr/bin/env python3
"""
Cartoon & Illustration Media Retrieval for Handout 2: 10 Ways to Encourage Communication

This script retrieves playful, family-friendly cartoon images for communication strategies
with optimized detection for child-friendly illustration styles.

Sections covered:
1. Get Down to Their Level (eye-level interaction)
2. Follow Your Child's Lead (play-based learning)
3. Celebrate ALL Communication (positive reinforcement)
4. Create Routines and Rituals (family activities)

Features:
- Child-friendly cartoon queries
- Playful illustration detection
- Family interaction focus
- Organized by strategy section
- Comprehensive JSON reporting
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
# HANDOUT 2 MEDIA CONFIGURATION
# ============================================================================

@dataclass
class Strategy:
    """Structure for communication strategies"""
    name: str
    description: str
    queries: List[str]
    target_quantity: int = 3
    quality: str = "professional"


# Define all strategies for Handout 2
HANDOUT_2_STRATEGIES = [
    Strategy(
        name="Get Down to Their Level",
        description="Eye-level interaction with children",
        queries=[
            "parent sitting on floor with child playing illustration",
            "adult child eye level communication cartoon",
            "family play interaction same level illustration",
            "parent kneeling with child fun playful cartoon",
            "caregiver engaged at child height illustration",
        ],
        target_quantity=3,
        quality="professional"
    ),
    Strategy(
        name="Follow Your Child's Lead",
        description="Play-based learning following interests",
        queries=[
            "child playing toys interested parent watching cartoon",
            "parent following child play preferences illustration",
            "kids engaged in favorite activity family cartoon",
            "child-led play exploration illustration",
            "interest-based learning playful cartoon",
        ],
        target_quantity=3,
        quality="professional"
    ),
    Strategy(
        name="Celebrate ALL Communication",
        description="Positive reinforcement for communication attempts",
        queries=[
            "celebrating child achievement happy family illustration",
            "positive reinforcement praise child cartoon",
            "parent encouraging child communication smile illustration",
            "celebration success communication attempt cartoon",
            "joy happiness family interaction illustration",
        ],
        target_quantity=3,
        quality="professional"
    ),
    Strategy(
        name="Create Routines and Rituals",
        description="Predictable family activities and routines",
        queries=[
            "family routine bedtime bath time illustration",
            "predictable family ritual morning routine cartoon",
            "daily family routine togetherness illustration",
            "family tradition repeated activity cartoon",
            "structured routine children comfort illustration",
        ],
        target_quantity=2,
        quality="professional"
    ),
]


# ============================================================================
# AGENT CONFIGURATION - CHILD-FRIENDLY CARTOON OPTIMIZED
# ============================================================================

def create_family_cartoon_optimized_config() -> AgentConfig:
    """
    Create AgentConfig optimized for family-friendly cartoon/illustration detection.
    
    Key optimizations:
    - Higher style_confidence_weight for cartoon detection
    - Keywords emphasizing playful, family-friendly content
    - Color and emotion-oriented positive keywords
    - Rejection of formal/clinical imagery
    
    Returns:
        AgentConfig tuned for family cartoon detection
    """
    config = AgentConfig(
        max_search_queries=5,
        results_per_source=5,
        
        # Scoring thresholds
        min_final_score=45.0,
        style_confidence_weight=0.3,
        quality_weight=0.3,
        relevance_weight=0.5,
        
        # Default scores
        base_quality_score=70.0,
        base_relevance_score=50.0,
        base_style_confidence=0.4,
        
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
        
        # Enhanced style keywords for family/playful cartoons
        style_keywords={
            'cartoon': {
                'positive': [
                    'cartoon', 'illustration', 'illustrated', 'comic',
                    'animated', 'animation', 'drawing', 'drawn', 'hand-drawn',
                    'vector', 'art', 'artistic', 'sketch', 'cute',
                    'playful', 'fun', 'whimsical', 'stylized', 'graphic',
                    'design', 'digital art', 'colorful', 'vibrant', 'expressive',
                    'happy', 'smile', 'joy', 'family', 'children', 'kids',
                    'playful interaction', 'friendly', 'warm', 'inviting'
                ],
                'negative': [
                    'photo', 'photograph', 'photography', 'real', 'realistic',
                    'stock photo', 'portrait', 'candid', 'camera',
                    'professional photo', 'close-up', 'clinical',
                    'medical', 'therapy session', 'formal', 'serious'
                ]
            }
        }
    )
    return config


# ============================================================================
# RETRIEVAL PROCESS
# ============================================================================

def retrieve_handout_2_media(
    output_dir: str = "media/handout_2_communication_strategies",
    dry_run: bool = False,
    verbose: bool = False
) -> Dict:
    """
    Retrieve family-friendly cartoon media for all Handout 2 strategies.
    
    Args:
        output_dir: Base directory for media output
        dry_run: If True, show queries without downloading
        verbose: If True, show detailed logging
    
    Returns:
        Dictionary with complete retrieval report
    """
    
    # Setup
    log_level = LogLevel.DEBUG if verbose else LogLevel.INFO
    config = create_family_cartoon_optimized_config()
    agent = MediaGatheringAgent(
        output_dir=output_dir,
        config=config,
        log_level=log_level
    )
    
    print("\n" + "="*80)
    print("HANDOUT 2: 10 Ways to Encourage Communication at Home")
    print("Family-Friendly Cartoon Media Retrieval")
    print("="*80)
    
    # Process all strategies
    all_results = {
        'handout': 'HANDOUT_2_10_Ways_Encourage_Communication',
        'total_strategies': len(HANDOUT_2_STRATEGIES),
        'strategies': {},
        'summary': {
            'total_retrieved': 0,
            'total_requested': 0,
            'strategies_completed': 0,
            'strategies_partial': 0,
            'strategies_failed': 0,
        }
    }
    
    for strategy in HANDOUT_2_STRATEGIES:
        print(f"\n👨‍👧‍👦 Strategy: {strategy.name}")
        print(f"   Description: {strategy.description}")
        print(f"   Target: {strategy.target_quantity} family cartoon images")
        
        strategy_results = {
            'name': strategy.name,
            'description': strategy.description,
            'target_quantity': strategy.target_quantity,
            'queries_used': [],
            'results': []
        }
        
        total_strategy_retrieved = 0
        
        # Process each query in the strategy
        for query in strategy.queries:
            print(f"   🔍 Query: {query}")
            
            if dry_run:
                strategy_results['queries_used'].append(query)
                print(f"      [DRY RUN] Would retrieve with this query")
                continue
            
            try:
                # Create request with cartoon style constraint
                request = MediaRequest(
                    query=query,
                    media_type="image",
                    quantity=strategy.target_quantity,
                    quality=strategy.quality,
                    licensing="free",
                    context={
                        "handout": "2_communication_strategies",
                        "strategy": strategy.name
                    },
                    constraints={"style": "cartoon"}  # Family-friendly cartoon
                )
                
                # Process request
                report = agent.process_request(request)
                
                # Track results
                retrieved = report['summary']['total_retrieved']
                total_strategy_retrieved += retrieved
                
                strategy_results['queries_used'].append(query)
                for result in report['results']:
                    strategy_results['results'].append({
                        'title': result['title'],
                        'source': result['source'],
                        'local_path': result['local_path'],
                        'quality_score': result['quality_score'],
                        'relevance_score': result['relevance_score'],
                        'style_confidence': result['style_confidence'],
                        'final_score': result['final_score'],
                    })
                
                # Stop if we have enough for this strategy
                if total_strategy_retrieved >= strategy.target_quantity:
                    print(f"      ✓ Retrieved {total_strategy_retrieved} images (target met)")
                    break
                    
            except Exception as e:
                print(f"      ❌ Error: {str(e)[:100]}")
                continue
        
        # Update all results
        all_results['strategies'][strategy.name] = strategy_results
        
        # Update summary
        if total_strategy_retrieved >= strategy.target_quantity:
            all_results['summary']['strategies_completed'] += 1
        elif total_strategy_retrieved > 0:
            all_results['summary']['strategies_partial'] += 1
        else:
            all_results['summary']['strategies_failed'] += 1
        
        all_results['summary']['total_retrieved'] += total_strategy_retrieved
        all_results['summary']['total_requested'] += strategy.target_quantity
        
        print(f"   ✅ Strategy complete: {total_strategy_retrieved}/{strategy.target_quantity} retrieved")
    
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
    print(f"✅ Strategies Completed: {all_results['summary']['strategies_completed']}/{all_results['summary']['total_strategies']}")
    print(f"⚠️  Strategies Partial:  {all_results['summary']['strategies_partial']}")
    print(f"❌ Strategies Failed:   {all_results['summary']['strategies_failed']}")
    print(f"\n📊 Total Retrieved: {all_results['summary']['total_retrieved']}/{all_results['summary']['total_requested']}")
    print(f"📈 Completion Rate: {all_results['summary']['completion_rate']}")
    
    return all_results


# ============================================================================
# EXPORT & REPORTING
# ============================================================================

def save_report(results: Dict, output_file: str = "handout_2_retrieval_report.json") -> str:
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
   python3 handout_2_cartoon_retrieval.py

2. Dry run (show queries without downloading):
   python3 handout_2_cartoon_retrieval.py --dry-run

3. Verbose output with debug info:
   python3 handout_2_cartoon_retrieval.py --verbose

4. Custom output directory:
   python3 handout_2_cartoon_retrieval.py --output custom_media_dir

5. Dry run with verbose output:
   python3 handout_2_cartoon_retrieval.py --dry-run --verbose

OUTPUT:
- Media files: media/handout_2_communication_strategies/[strategy_name]/
- Report: handout_2_retrieval_report.json

FEATURES:
✓ Family-friendly cartoon/illustration style
✓ Playful interaction focus
✓ Optimized keyword matching
✓ Error handling and retry logic
✓ Organized by strategy section
✓ JSON reporting with quality metrics
""")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Retrieve cartoon media for Handout 2: 10 Ways to Encourage Communication"
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
    results = retrieve_handout_2_media(
        output_dir=args.output,
        dry_run=args.dry_run,
        verbose=args.verbose
    )
    
    # Save report
    if not args.dry_run:
        save_report(results)
    
    print("\n" + "="*80)
    print("✨ Handout 2 media retrieval complete!")
    print("="*80)


if __name__ == "__main__":
    main()
