#!/usr/bin/env python3
"""
Cartoon & Illustration Media Retrieval for Handout 3: Ontario Resources for Families

This script retrieves informative yet engaging cartoon images for community resources
and support services with a focus on accessibility and resource discovery themes.

Sections covered:
1. Government-Funded Programs (community resources)
2. Autism Organizations (support groups)
3. Parent Training Programs (workshops)
4. Support Groups & Community (family connections)

Features:
- Community-focused cartoon queries
- Resource discovery and support themes
- Accessible, family-friendly imagery
- Organized by resource type
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
# HANDOUT 3 MEDIA CONFIGURATION
# ============================================================================

@dataclass
class Resource:
    """Structure for resource categories"""
    name: str
    description: str
    queries: List[str]
    target_quantity: int = 2
    quality: str = "professional"


# Define all resource categories for Handout 3
HANDOUT_3_RESOURCES = [
    Resource(
        name="Government-Funded Programs",
        description="Community services and public programs",
        queries=[
            "community resources support services illustration",
            "government health program family support cartoon",
            "healthcare access children services illustration",
            "public program accessibility diverse families cartoon",
            "community care support system illustration",
        ],
        target_quantity=2,
        quality="professional"
    ),
    Resource(
        name="Autism Organizations",
        description="Support groups and advocacy organizations",
        queries=[
            "autism support community network illustration",
            "advocacy organization helping families cartoon",
            "support group people coming together illustration",
            "community organization connection cartoon",
            "autism awareness group illustration",
        ],
        target_quantity=2,
        quality="professional"
    ),
    Resource(
        name="Parent Training Programs",
        description="Workshops and educational programs",
        queries=[
            "parent training workshop education illustration",
            "family learning program teaching cartoon",
            "educational workshop participants illustration",
            "learning opportunity parent child illustration",
            "professional training parent support cartoon",
        ],
        target_quantity=2,
        quality="professional"
    ),
    Resource(
        name="Support Groups & Community",
        description="Family connections and community support",
        queries=[
            "support group community connection illustration",
            "family together supportive community cartoon",
            "people supporting each other illustration",
            "community care network family illustration",
            "friends supporting friends cartoon",
        ],
        target_quantity=2,
        quality="professional"
    ),
]


# ============================================================================
# AGENT CONFIGURATION - RESOURCE-FOCUSED CARTOON OPTIMIZED
# ============================================================================

def create_resource_cartoon_optimized_config() -> AgentConfig:
    """
    Create AgentConfig optimized for resource/community-focused cartoon detection.
    
    Key optimizations:
    - Keywords emphasizing community, support, and accessibility
    - Inclusive and diverse representation emphasis
    - Professional yet accessible cartoon style
    - Rejection of clinical/formal imagery
    
    Returns:
        AgentConfig tuned for resource-focused cartoon detection
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
        
        # Community and resource-focused keywords
        style_keywords={
            'cartoon': {
                'positive': [
                    'cartoon', 'illustration', 'illustrated', 'comic',
                    'animated', 'animation', 'drawing', 'drawn', 'hand-drawn',
                    'vector', 'art', 'artistic', 'sketch', 'stylized',
                    'graphic', 'design', 'digital art', 'colorful', 'vibrant',
                    'community', 'support', 'connection', 'together', 'network',
                    'inclusive', 'diverse', 'accessible', 'helping', 'caring',
                    'friendly', 'warm', 'welcoming', 'group', 'team'
                ],
                'negative': [
                    'photo', 'photograph', 'photography', 'real', 'realistic',
                    'stock photo', 'portrait', 'candid', 'camera',
                    'professional photo', 'clinical', 'medical', 'formal',
                    'serious business', 'corporate', 'stock image'
                ]
            }
        }
    )
    return config


# ============================================================================
# RETRIEVAL PROCESS
# ============================================================================

def retrieve_handout_3_media(
    output_dir: str = "media/handout_3_ontario_resources",
    dry_run: bool = False,
    verbose: bool = False
) -> Dict:
    """
    Retrieve community-focused cartoon media for all Handout 3 resources.
    
    Args:
        output_dir: Base directory for media output
        dry_run: If True, show queries without downloading
        verbose: If True, show detailed logging
    
    Returns:
        Dictionary with complete retrieval report
    """
    
    # Setup
    log_level = LogLevel.DEBUG if verbose else LogLevel.INFO
    config = create_resource_cartoon_optimized_config()
    agent = MediaGatheringAgent(
        output_dir=output_dir,
        config=config,
        log_level=log_level
    )
    
    print("\n" + "="*80)
    print("HANDOUT 3: Ontario Resources for Families")
    print("Community-Focused Cartoon Media Retrieval")
    print("="*80)
    
    # Process all resources
    all_results = {
        'handout': 'HANDOUT_3_Ontario_Resources',
        'total_resources': len(HANDOUT_3_RESOURCES),
        'resources': {},
        'summary': {
            'total_retrieved': 0,
            'total_requested': 0,
            'resources_completed': 0,
            'resources_partial': 0,
            'resources_failed': 0,
        }
    }
    
    for resource in HANDOUT_3_RESOURCES:
        print(f"\n🏘️  Resource: {resource.name}")
        print(f"   Description: {resource.description}")
        print(f"   Target: {resource.target_quantity} cartoon images")
        
        resource_results = {
            'name': resource.name,
            'description': resource.description,
            'target_quantity': resource.target_quantity,
            'queries_used': [],
            'results': []
        }
        
        total_resource_retrieved = 0
        
        # Process each query in the resource category
        for query in resource.queries:
            print(f"   🔍 Query: {query}")
            
            if dry_run:
                resource_results['queries_used'].append(query)
                print(f"      [DRY RUN] Would retrieve with this query")
                continue
            
            try:
                # Create request with cartoon style constraint
                request = MediaRequest(
                    query=query,
                    media_type="image",
                    quantity=resource.target_quantity,
                    quality=resource.quality,
                    licensing="free",
                    context={
                        "handout": "3_ontario_resources",
                        "resource": resource.name
                    },
                    constraints={"style": "cartoon"}  # Community-focused cartoon
                )
                
                # Process request
                report = agent.process_request(request)
                
                # Track results
                retrieved = report['summary']['total_retrieved']
                total_resource_retrieved += retrieved
                
                resource_results['queries_used'].append(query)
                for result in report['results']:
                    resource_results['results'].append({
                        'title': result['title'],
                        'source': result['source'],
                        'local_path': result['local_path'],
                        'quality_score': result['quality_score'],
                        'relevance_score': result['relevance_score'],
                        'style_confidence': result['style_confidence'],
                        'final_score': result['final_score'],
                    })
                
                # Stop if we have enough for this resource
                if total_resource_retrieved >= resource.target_quantity:
                    print(f"      ✓ Retrieved {total_resource_retrieved} images (target met)")
                    break
                    
            except Exception as e:
                print(f"      ❌ Error: {str(e)[:100]}")
                continue
        
        # Update all results
        all_results['resources'][resource.name] = resource_results
        
        # Update summary
        if total_resource_retrieved >= resource.target_quantity:
            all_results['summary']['resources_completed'] += 1
        elif total_resource_retrieved > 0:
            all_results['summary']['resources_partial'] += 1
        else:
            all_results['summary']['resources_failed'] += 1
        
        all_results['summary']['total_retrieved'] += total_resource_retrieved
        all_results['summary']['total_requested'] += resource.target_quantity
        
        print(f"   ✅ Resource complete: {total_resource_retrieved}/{resource.target_quantity} retrieved")
    
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
    print(f"✅ Resources Completed: {all_results['summary']['resources_completed']}/{all_results['summary']['total_resources']}")
    print(f"⚠️  Resources Partial:  {all_results['summary']['resources_partial']}")
    print(f"❌ Resources Failed:   {all_results['summary']['resources_failed']}")
    print(f"\n📊 Total Retrieved: {all_results['summary']['total_retrieved']}/{all_results['summary']['total_requested']}")
    print(f"📈 Completion Rate: {all_results['summary']['completion_rate']}")
    
    return all_results


# ============================================================================
# EXPORT & REPORTING
# ============================================================================

def save_report(results: Dict, output_file: str = "handout_3_retrieval_report.json") -> str:
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
   python3 handout_3_cartoon_retrieval.py

2. Dry run (show queries without downloading):
   python3 handout_3_cartoon_retrieval.py --dry-run

3. Verbose output with debug info:
   python3 handout_3_cartoon_retrieval.py --verbose

4. Custom output directory:
   python3 handout_3_cartoon_retrieval.py --output custom_media_dir

5. Dry run with verbose output:
   python3 handout_3_cartoon_retrieval.py --dry-run --verbose

OUTPUT:
- Media files: media/handout_3_ontario_resources/[resource_name]/
- Report: handout_3_retrieval_report.json

FEATURES:
✓ Community and support-focused cartoon/illustration style
✓ Inclusive and diverse imagery emphasis
✓ Accessibility-conscious design
✓ Optimized keyword matching
✓ Error handling and retry logic
✓ Organized by resource category
✓ JSON reporting with quality metrics
""")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Retrieve cartoon media for Handout 3: Ontario Resources for Families"
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
    results = retrieve_handout_3_media(
        output_dir=args.output,
        dry_run=args.dry_run,
        verbose=args.verbose
    )
    
    # Save report
    if not args.dry_run:
        save_report(results)
    
    print("\n" + "="*80)
    print("✨ Handout 3 media retrieval complete!")
    print("="*80)


if __name__ == "__main__":
    main()
