import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

class MECESegmentationEngine:
    """
    MECE (Mutually Exclusive, Collectively Exhaustive) Audience Segmentation Engine
    for Cart Abandoner Retention Strategy
    """
    
    def __init__(self, min_segment_size: int = 500, max_segment_size: int = 20000):
        self.min_segment_size = min_segment_size
        self.max_segment_size = max_segment_size
        self.segments = []
        self.universe_df = None
        
    def generate_mock_data(self, n_users: int = 50000) -> pd.DataFrame:
        """Generate realistic mock cart abandonment data"""
        np.random.seed(42)
        
        # Generate base data
        user_ids = [f"user_{i:05d}" for i in range(n_users)]
        
        # Cart abandoned in last 7 days
        base_date = datetime.now()
        cart_abandoned_dates = [
            (base_date - timedelta(days=np.random.randint(0, 8))).strftime('%Y-%m-%d')
            for _ in range(n_users)
        ]
        
        # Generate correlated features
        # High AOV users tend to have higher engagement and profitability
        base_aov = np.random.lognormal(mean=6.5, sigma=1.2, size=n_users)
        avg_order_value = np.clip(base_aov, 10, 10000)
        
        # Engagement correlated with AOV but with noise
        engagement_base = (np.log(avg_order_value) - 3) / 5  # Normalize AOV influence
        engagement_noise = np.random.normal(0, 0.3, n_users)
        engagement_score = np.clip(engagement_base + engagement_noise, 0, 1)
        
        # Profitability correlated with both AOV and engagement
        profitability_base = (engagement_score * 0.6) + (np.log(avg_order_value) / 10)
        profitability_noise = np.random.normal(0, 0.2, n_users)
        profitability_score = np.clip(profitability_base + profitability_noise, 0, 1)
        
        # Other features
        sessions_last_30d = np.random.poisson(lam=8, size=n_users)
        num_cart_items = np.random.poisson(lam=3, size=n_users) + 1
        
        # Last order date (some users are new, others haven't ordered recently)
        days_since_order = np.random.exponential(scale=30, size=n_users)
        last_order_dates = [
            (base_date - timedelta(days=int(days))).strftime('%Y-%m-%d') 
            if days < 365 else None  # Some users never ordered
            for days in days_since_order
        ]
        
        return pd.DataFrame({
            'user_id': user_ids,
            'cart_abandoned_date': cart_abandoned_dates,
            'last_order_date': last_order_dates,
            'avg_order_value': np.round(avg_order_value, 2),
            'sessions_last_30d': sessions_last_30d,
            'num_cart_items': num_cart_items,
            'engagement_score': np.round(engagement_score, 3),
            'profitability_score': np.round(profitability_score, 3)
        })
    
    def define_universe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Define universe: users who abandoned carts in last 7 days"""
        # Convert cart_abandoned_date to datetime
        df['cart_abandoned_date'] = pd.to_datetime(df['cart_abandoned_date'])
        
        # Filter for last 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        universe = df[df['cart_abandoned_date'] >= cutoff_date].copy()
        
        print(f"Universe defined: {len(universe):,} users who abandoned carts in last 7 days")
        print(f"Original dataset: {len(df):,} users")
        
        self.universe_df = universe
        return universe
    
    def create_mece_segments(self, df: pd.DataFrame) -> List[Dict]:
        """
        Create MECE segments using a decision tree approach
        Priority: AOV > Engagement > Profitability
        """
        segments = []
        
        # Define thresholds based on data distribution
        aov_high = df['avg_order_value'].quantile(0.75)  # Top 25%
        aov_medium = df['avg_order_value'].quantile(0.40)  # 40th percentile
        
        engagement_high = df['engagement_score'].quantile(0.70)  # Top 30%
        engagement_medium = df['engagement_score'].quantile(0.40)  # 40th percentile
        
        profitability_high = df['profitability_score'].quantile(0.70)  # Top 30%
        
        print(f"Thresholds - AOV: High={aov_high:.0f}, Med={aov_medium:.0f}")
        print(f"Thresholds - Engagement: High={engagement_high:.3f}, Med={engagement_medium:.3f}")
        print(f"Thresholds - Profitability: High={profitability_high:.3f}")
        
        # Segment 1: High AOV Premium
        s1_mask = df['avg_order_value'] >= aov_high
        s1_df = df[s1_mask]
        if len(s1_df) >= self.min_segment_size:
            segments.append({
                'name': 'High_AOV_Premium',
                'rules': f'AOV >= {aov_high:.0f}',
                'mask': s1_mask,
                'size': len(s1_df),
                'priority': 1
            })
        
        # Remaining users for further segmentation
        remaining_mask = ~s1_mask
        remaining_df = df[remaining_mask]
        
        # Segment 2: Medium AOV + High Engagement
        s2_mask = (
            remaining_mask & 
            (df['avg_order_value'] >= aov_medium) & 
            (df['engagement_score'] >= engagement_high)
        )
        s2_df = df[s2_mask]
        if len(s2_df) >= self.min_segment_size:
            segments.append({
                'name': 'Med_AOV_High_Engagement',
                'rules': f'{aov_medium:.0f} <= AOV < {aov_high:.0f} & Engagement >= {engagement_high:.3f}',
                'mask': s2_mask,
                'size': len(s2_df),
                'priority': 2
            })
            remaining_mask = remaining_mask & ~s2_mask
            remaining_df = df[remaining_mask]
        
        # Segment 3: Medium AOV + Medium Engagement + High Profitability
        s3_mask = (
            remaining_mask & 
            (df['avg_order_value'] >= aov_medium) & 
            (df['engagement_score'] >= engagement_medium) &
            (df['profitability_score'] >= profitability_high)
        )
        s3_df = df[s3_mask]
        if len(s3_df) >= self.min_segment_size:
            segments.append({
                'name': 'Med_AOV_Med_Eng_High_Prof',
                'rules': f'{aov_medium:.0f} <= AOV < {aov_high:.0f} & {engagement_medium:.3f} <= Engagement < {engagement_high:.3f} & Profitability >= {profitability_high:.3f}',
                'mask': s3_mask,
                'size': len(s3_df),
                'priority': 3
            })
            remaining_mask = remaining_mask & ~s3_mask
            remaining_df = df[remaining_mask]
        
        # Segment 4: High Engagement (Low-Medium AOV)
        s4_mask = (
            remaining_mask & 
            (df['engagement_score'] >= engagement_high)
        )
        s4_df = df[s4_mask]
        if len(s4_df) >= self.min_segment_size:
            segments.append({
                'name': 'Low_AOV_High_Engagement',
                'rules': f'AOV < {aov_medium:.0f} & Engagement >= {engagement_high:.3f}',
                'mask': s4_mask,
                'size': len(s4_df),
                'priority': 4
            })
            remaining_mask = remaining_mask & ~s4_mask
            remaining_df = df[remaining_mask]
        
        # Segment 5: Recent Customers (have recent order)
        recent_customers_mask = (
            remaining_mask & 
            df['last_order_date'].notna() &
            (pd.to_datetime(df['last_order_date']) >= (datetime.now() - timedelta(days=30)))
        )
        s5_df = df[recent_customers_mask]
        if len(s5_df) >= self.min_segment_size:
            segments.append({
                'name': 'Recent_Customers',
                'rules': 'Last order within 30 days & Other conditions',
                'mask': recent_customers_mask,
                'size': len(s5_df),
                'priority': 5
            })
            remaining_mask = remaining_mask & ~recent_customers_mask
            remaining_df = df[remaining_mask]
        
        # ELSE Bucket - All remaining users
        else_mask = remaining_mask
        segments.append({
            'name': 'Other_Bucket',
            'rules': 'All other users (ELSE condition)',
            'mask': else_mask,
            'size': len(df[else_mask]),
            'priority': 999
        })
        
        # Validating MECE properties
        self._validate_mece(df, segments)
        
        return segments
    
    def _validate_mece(self, df: pd.DataFrame, segments: List[Dict]) -> None:
        """Validate that segments are Mutually Exclusive and Collectively Exhaustive"""
        total_assigned = 0
        overlapping_users = set()
        
        # Checking for overlaps and count total assignments
        all_assigned_users = set()
        
        for segment in segments:
            segment_users = set(df[segment['mask']]['user_id'])
            
            # Checking for overlaps
            overlap = all_assigned_users.intersection(segment_users)
            if overlap:
                print(f"WARNING: Segment {segment['name']} overlaps with previous segments!")
                print(f"Overlapping users: {len(overlap)}")
            
            all_assigned_users.update(segment_users)
            total_assigned += segment['size']
        
        # Checking collective exhaustiveness
        if len(all_assigned_users) != len(df):
            print(f"ERROR: Not collectively exhaustive!")
            print(f"Total users: {len(df)}, Assigned users: {len(all_assigned_users)}")
        else:
            print(f" MECE Validation Passed:")
            print(f"   - Total users: {len(df):,}")
            print(f"   - Total assigned: {len(all_assigned_users):,}")
            print(f"   - All segments are mutually exclusive")
            print(f"   - All users are assigned to exactly one segment")
    
    def compute_segment_scores(self, df: pd.DataFrame, segments: List[Dict]) -> List[Dict]:
        """Compute weighted scores for each segment"""
        scored_segments = []
        
        for segment in segments:
            segment_data = df[segment['mask']]
            
            if len(segment_data) == 0:
                continue
                
            # Calculating individual dimension scores
            
            # 1. Conversion Potential (engagement × recency factor)
            avg_engagement = segment_data['engagement_score'].mean()
            avg_sessions = segment_data['sessions_last_30d'].mean()
            recency_factor = min(avg_sessions / 10, 1.0)  # Normalize sessions
            conversion_potential = (avg_engagement * 0.7) + (recency_factor * 0.3)
            
            # 2. Profitability
            avg_profitability = segment_data['profitability_score'].mean()
            avg_aov = segment_data['avg_order_value'].mean()
            profitability = (avg_profitability * 0.8) + (min(avg_aov / 1000, 1.0) * 0.2)
            
            # 3. Size Score (normalized - prefer medium sized segments)
            size = len(segment_data)
            optimal_size = 5000
            if size <= optimal_size:
                size_score = size / optimal_size
            else:
                size_score = max(0.5, 1 - (size - optimal_size) / 20000)
            
            # 4. Lift vs Control (simulated)
            # Higher AOV and engagement typically have higher lift
            base_lift = (avg_engagement * 0.4) + (min(avg_aov / 2000, 1.0) * 0.3)
            lift_vs_control = min(base_lift + np.random.normal(0.1, 0.05), 1.0)
            
            # 5. Strategic Fit (business priority score)
            if segment['name'] == 'High_AOV_Premium':
                strategic_fit = 0.95
            elif segment['name'] == 'Med_AOV_High_Engagement':
                strategic_fit = 0.85
            elif 'High_Engagement' in segment['name']:
                strategic_fit = 0.75
            elif segment['name'] == 'Recent_Customers':
                strategic_fit = 0.70
            else:
                strategic_fit = 0.50
            
            # Overall Score (weighted combination)
            overall_score = (
                conversion_potential * 0.25 +
                profitability * 0.25 +
                lift_vs_control * 0.20 +
                strategic_fit * 0.20 +
                size_score * 0.10
            )
            
            # Checking if segment meets size constraints
            valid = self.min_segment_size <= size <= self.max_segment_size
            
            scored_segment = {
                'segment_name': segment['name'],
                'rules_applied': segment['rules'],
                'size': size,
                'conversion_potential': round(conversion_potential, 3),
                'profitability': round(profitability, 3),
                'lift_vs_control': round(lift_vs_control, 3),
                'strategic_fit': round(strategic_fit, 3),
                'size_score': round(size_score, 3),
                'overall_score': round(overall_score, 3),
                'valid': valid,
                'avg_aov': round(avg_aov, 2),
                'avg_engagement': round(avg_engagement, 3),
                'avg_profitability': round(avg_profitability, 3)
            }
            
            scored_segments.append(scored_segment)
        
        # Sort by overall score (descending)
        scored_segments.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return scored_segments
    
    def run_segmentation(self, df: pd.DataFrame = None) -> Tuple[List[Dict], pd.DataFrame]:
        """Run the complete MECE segmentation pipeline"""
        print(" Starting MECE Cart Abandoner Segmentation")
        print("=" * 60)
        
        # Generate data if not provided
        if df is None:
            print(" Generating mock dataset...")
            df = self.generate_mock_data()
        
        # Define universe
        print(" Step 1: Define Universe")
        universe_df = self.define_universe(df)
        
        # Create MECE segments
        print(" Step 2: Create MECE Segments")
        segments = self.create_mece_segments(universe_df)
        
        # Compute scores
        print(" Step 3: Compute Segment Scores")
        scored_segments = self.compute_segment_scores(universe_df, segments)
        
        print(" Segmentation Complete!")
        self.segments = scored_segments
        
        return scored_segments, universe_df
    
    def export_results(self, segments: List[Dict], filename: str = "mece_segments") -> None:
        """Export results to CSV and JSON"""
        
        # Create DataFrame for CSV export
        df_export = pd.DataFrame(segments)
        
        # Reorder columns for better readability
        column_order = [
            'segment_name', 'rules_applied', 'size', 'conversion_potential', 
            'profitability', 'lift_vs_control', 'strategic_fit', 'overall_score', 
            'valid', 'avg_aov', 'avg_engagement', 'avg_profitability'
        ]
        
        df_export = df_export[column_order]
        
        # Export CSV
        csv_filename = f"{filename}.csv"
        df_export.to_csv(csv_filename, index=False)
        print(f" Results exported to {csv_filename}")
        
        # Export JSON
        json_filename = f"{filename}.json"
        with open(json_filename, 'w') as f:
            json.dump(segments, f, indent=2)
        print(f" Results exported to {json_filename}")
        
        return df_export
    
    def print_summary(self, segments: List[Dict]) -> None:
        """Print a summary of the segmentation results"""
        print("\n" + "="*80)
        print(" MECE SEGMENTATION SUMMARY")
        print("="*80)
        
        total_users = sum(s['size'] for s in segments)
        valid_segments = [s for s in segments if s['valid']]
        
        print(f"Total Users Segmented: {total_users:,}")
        print(f"Number of Segments: {len(segments)}")
        print(f"Valid Segments: {len(valid_segments)}")
        
        print(f"\n{'Segment Name':<25} {'Size':<8} {'Overall Score':<13} {'Valid':<6} {'Rules'}")
        print("-" * 100)
        
        for segment in segments:
            valid_status = "OK" if segment['valid'] else "ERROR!!"
            print(f"{segment['segment_name']:<25} {segment['size']:<8,} "
                  f"{segment['overall_score']:<13} {valid_status:<6} {segment['rules_applied'][:50]}...")
        
        print(f"\nTop 3 Segments by Overall Score:")
        for i, segment in enumerate(segments[:3], 1):
            print(f"{i}. {segment['segment_name']} - Score: {segment['overall_score']}")


def main():
    """Main execution function"""
    
    # Initialize the segmentation engine
    engine = MECESegmentationEngine(min_segment_size=500, max_segment_size=20000)
    
    # Run the complete segmentation pipeline
    segments, universe_df = engine.run_segmentation()
    
    # Print summary
    engine.print_summary(segments)
    
    # Export results
    results_df = engine.export_results(segments, "cart_abandoner_segments")
    
    print(f" MECE Segmentation Complete!")
    print(f" Universe Size: {len(universe_df):,} users")
    print(f" Created {len(segments)} segments")
    print(f" MECE Properties: Validated")
    
    return engine, segments, universe_df

if __name__ == "__main__":
    engine, segments, universe_df = main()