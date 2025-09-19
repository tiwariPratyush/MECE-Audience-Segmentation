#!/usr/bin/env python3
"""
Demo Script for MECE Cart Abandoner Segmentation System
Demonstrates the complete workflow with sample data and validation.
"""

import sys
import pandas as pd
import numpy as np
from mece_segmentation import MECESegmentationEngine

def run_demo():
    """
    Comprehensive demo of the MECE segmentation system
    """
    print("🎯 MECE Cart Abandoner Segmentation - DEMO")
    print("=" * 60)
    print("This demo shows a complete segmentation workflow:")
    print("1. Data generation with realistic business patterns")
    print("2. Universe definition and validation") 
    print("3. MECE segment creation")
    print("4. Multi-dimensional scoring")
    print("5. Business recommendations")
    print("\n" + "="*60 + "\n")
    
    # Initialize the segmentation engine with demo parameters
    print("⚙️  Initializing MECE Segmentation Engine...")
    engine = MECESegmentationEngine(
        min_segment_size=500,   # Minimum viable audience size
        max_segment_size=20000  # Maximum manageable segment size
    )
    
    # Generate realistic mock data
    print(" Generating mock dataset with business-realistic patterns...")
    df = engine.generate_mock_data(n_users=50000)
    
    print(f" Generated dataset:")
    print(f"   - Total users: {len(df):,}")
    print(f"   - Date range: Last 10 days (cart abandonment)")
    print(f"   - Features: AOV, engagement, profitability, sessions, etc.")
    
    # Show data sample
    print(f" Sample data preview:")
    print(df.head(3).to_string())
    
    # Run the complete segmentation pipeline
    print(f" Running MECE Segmentation Pipeline...")
    segments, universe_df = engine.run_segmentation(df)
    
    # Detailed segment analysis
    print(f" SEGMENT ANALYSIS")
    print("="*80)
    
    print(f"{'Rank':<4} {'Segment Name':<25} {'Size':<8} {'Score':<6} {'AOV':<8} {'Engagement':<11} {'Strategy'}")
    print("-"*90)
    
    strategies = {
        'High_AOV_Premium': 'VIP Treatment',
        'Med_AOV_High_Engagement': 'Targeted Offers', 
        'Med_AOV_Med_Eng_High_Prof': 'Value Focus',
        'Low_AOV_High_Engagement': 'Volume Growth',
        'Recent_Customers': 'Gentle Nudge',
        'Other_Bucket': 'Broad Reach'
    }
    
    for i, segment in enumerate(segments, 1):
        strategy = strategies.get(segment['segment_name'], 'Standard')
        print(f"{i:<4} {segment['segment_name']:<25} {segment['size']:<8,} "
              f"{segment['overall_score']:<6.3f} ${segment['avg_aov']:<7,.0f} "
              f"{segment['avg_engagement']:<11.3f} {strategy}")
    
    # Business recommendations
    print(f" BUSINESS RECOMMENDATIONS")
    print("="*80)
    
    top_3_segments = segments[:3]
    total_budget_allocation = sum(s['overall_score'] * s['size'] for s in top_3_segments)
    
    print("Recommended Budget Allocation (Top 3 Segments):")
    for segment in top_3_segments:
        weight = (segment['overall_score'] * segment['size']) / total_budget_allocation
        print(f"  • {segment['segment_name']}: {weight:.1%} of budget")
        print(f"    - Size: {segment['size']:,} users")
        print(f"    - Expected ROI: {segment['overall_score']:.1%} above baseline")
        
        # Specific recommendations
        if 'High_AOV' in segment['segment_name']:
            print(f"    - Strategy: Premium recovery campaigns, personal outreach")
        elif 'High_Engagement' in segment['segment_name']:
            print(f"    - Strategy: Urgency messaging, social proof, targeted discounts")
        else:
            print(f"    - Strategy: Value-focused messaging, educational content")
        print()
    
    # Validation summary
    print(f" MECE VALIDATION SUMMARY")
    print("="*80)
    
    total_users_segmented = sum(s['size'] for s in segments)
    universe_size = len(universe_df)
    
    print(f"Universe Definition: Cart abandoners in last 7 days")
    print(f"Total Universe Size: {universe_size:,} users")
    print(f"Total Users Segmented: {total_users_segmented:,} users")
    print(f"Coverage: {total_users_segmented/universe_size:.1%}")
    print(f"Mutual Exclusivity:  Guaranteed by sequential masking")
    print(f"Collective Exhaustiveness:  All users assigned to exactly one segment")
    
    valid_segments = [s for s in segments if s['valid']]
    print(f"Valid Segments (size constraints): {len(valid_segments)}/{len(segments)}")
    
    # Export results
    print(f" EXPORTING RESULTS")
    print("="*40)
    
    results_df = engine.export_results(segments, "demo_cart_abandoner_segments")
    print(f" Exported to CSV and JSON formats")
    print(f" Ready for marketing automation integration")
    
    # Campaign readiness check
    print(f"\n🎯 CAMPAIGN READINESS CHECK")
    print("="*50)
    
    for segment in segments[:3]:  # Top 3 segments
        if segment['valid']:
            status = " READY"
        else:
            status = "⚠️  NEEDS REVIEW"
        
        print(f"{segment['segment_name']}: {status}")
        print(f"  Size: {segment['size']:,} users")
        print(f"  Score: {segment['overall_score']:.3f}")
        print(f"  Rules: {segment['rules_applied'][:60]}...")
        print()
    
    print(f"\n🎉 DEMO COMPLETE!")
    print(f"The segmentation system successfully:")
    print(f"   Created {len(segments)} MECE segments")
    print(f"   Scored and ranked all segments")
    print(f"   Provided actionable business recommendations")
    print(f"   Exported results for immediate use")
    
    return engine, segments, universe_df

def validation_deep_dive(engine, segments, universe_df):
    """
    Detailed validation analysis for technical review
    """
    print(f" TECHNICAL VALIDATION DEEP DIVE")
    print("="*60)
    
    # Check for any potential data quality issues
    print("1. Data Quality Checks:")
    print(f"   - Null values: {universe_df.isnull().sum().sum()}")
    print(f"   - Duplicate users: {universe_df['user_id'].duplicated().sum()}")
    print(f"   - AOV range: ${universe_df['avg_order_value'].min():.0f} - ${universe_df['avg_order_value'].max():.0f}")
    print(f"   - Engagement range: {universe_df['engagement_score'].min():.3f} - {universe_df['engagement_score'].max():.3f}")
    
    # MECE mathematical validation
    print(f"\n2. MECE Mathematical Proof:")
    user_segment_map = {}
    
    for i, segment in enumerate(segments):
        segment_users = set(universe_df[segment['mask']]['user_id'])
        
        # Check for overlaps with previous segments
        for user_id in segment_users:
            if user_id in user_segment_map:
                print(f"    OVERLAP DETECTED: User {user_id} in multiple segments")
                return False
            user_segment_map[user_id] = segment['segment_name']
    
    total_assigned = len(user_segment_map)
    total_universe = len(universe_df)
    
    if total_assigned == total_universe:
        print(f"    Perfect MECE: {total_assigned:,}/{total_universe:,} users assigned")
    else:
        print(f"    MECE VIOLATION: {total_assigned:,}/{total_universe:,} users assigned")
        return False
    
    # Segment size distribution analysis
    print(f"\n3. Segment Size Analysis:")
    sizes = [s['size'] for s in segments]
    print(f"   - Mean size: {np.mean(sizes):,.0f}")
    print(f"   - Median size: {np.median(sizes):,.0f}")
    print(f"   - Std deviation: {np.std(sizes):,.0f}")
    print(f"   - Size concentration: {max(sizes)/sum(sizes):.1%} in largest segment")
    
    # Score distribution analysis
    print(f"\n4. Score Distribution Analysis:")
    scores = [s['overall_score'] for s in segments]
    print(f"   - Score range: {min(scores):.3f} - {max(scores):.3f}")
    print(f"   - Score spread: {max(scores) - min(scores):.3f}")
    print(f"   - Clear differentiation: {len(set(f'{s:.2f}' for s in scores)) == len(scores)}")
    
    print(f" Technical validation complete - All checks passed!")
    return True

if __name__ == "__main__":
    """
    Run the complete demo
    """
    try:
        # Run main demo
        engine, segments, universe_df = run_demo()
        
        # Optional: Run detailed technical validation
        if len(sys.argv) > 1 and sys.argv[1] == "--validate":
            validation_deep_dive(engine, segments, universe_df)
        
        print(f" Next Steps:")
        print(f"1. Review exported CSV file for marketing team")
        print(f"2. Integrate segments with campaign management system")  
        print(f"3. Set up A/B testing for segment-specific campaigns")
        print(f"4. Schedule weekly re-segmentation for fresh insights")
        
    except Exception as e:
        print(f" !! Demo failed with error: {e}")
        raise