# 🎯 MECE Cart Abandoner Segmentation System

## Overview
This project implements a **Mutually Exclusive, Collectively Exhaustive (MECE)** audience segmentation system for cart abandoner retention strategies. The system partitions users who abandoned carts in the last 7 days into actionable marketing segments while ensuring no overlaps and complete coverage.

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pandas
- numpy

### Installation & Usage
```bash
# Clone/download the script
# Install dependencies
pip install pandas numpy

# Run the segmentation
python mece_segmentation.py
```

## 📊 System Architecture

### 1. Universe Definition
- **Target Audience**: Users who abandoned carts in the last 7 days
- **Data Sources**: Mock dataset with realistic correlations between features
- **Size**: ~50,000 total users → ~40,000 in universe (last 7 days)

### 2. MECE Segmentation Logic

The segmentation follows a **hierarchical decision tree** approach:

```
Universe (All Cart Abandoners - Last 7 Days)
├── High AOV Premium (AOV ≥ 75th percentile)
├── Medium AOV + High Engagement 
│   └── (40th ≤ AOV < 75th percentile & Engagement ≥ 70th percentile)
├── Medium AOV + Medium Engagement + High Profitability
│   └── (40th ≤ AOV < 75th percentile & 40th ≤ Engagement < 70th & Profitability ≥ 70th)
├── Low AOV + High Engagement
│   └── (AOV < 40th percentile & Engagement ≥ 70th percentile)
├── Recent Customers
│   └── (Last order within 30 days & not in above segments)
└── Other Bucket (ELSE - All remaining users)
```

### 3. Key Features

#### MECE Enforcement
- **Mutually Exclusive**: Each user belongs to exactly one segment
- **Collectively Exhaustive**: Every user is assigned to a segment
- **Validation**: Automated checks ensure no overlaps or gaps

#### Segment Constraints
- **Minimum Size**: 500 users (configurable)
- **Maximum Size**: 20,000 users (configurable)
- **Automatic Merging**: Small segments fold into parent categories

#### Multi-Dimensional Scoring
Each segment receives scores across 5 dimensions:

1. **Conversion Potential** (25% weight)
   - Engagement Score × Recency Factor
   - Higher engagement + recent activity = higher potential

2. **Profitability** (25% weight)
   - Average profitability score + AOV normalization
   - Balances user value and purchase power

3. **Lift vs Control** (20% weight)
   - Simulated based on engagement and AOV
   - Estimates campaign effectiveness

4. **Strategic Fit** (20% weight)
   - Business priority scoring
   - High-AOV segments get priority

5. **Size Score** (10% weight)
   - Optimal size preference (around 5,000 users)
   - Penalizes very large or very small segments

## 🎯 Segmentation Results

### Typical Output Segments

| Segment Name | Size | Overall Score | Key Characteristics |
|-------------|------|---------------|-------------------|
| High_AOV_Premium | 3,200 | 0.76 | AOV > $2,000, High value customers |
| Med_AOV_High_Engagement | 5,000 | 0.68 | AOV $800-2,000, Engaged users |
| Low_AOV_High_Engagement | 2,800 | 0.62 | AOV < $800, High engagement |
| Recent_Customers | 4,200 | 0.58 | Purchased within 30 days |
| Other_Bucket | 25,000 | 0.52 | All remaining users |

### Strategic Recommendations

1. **High AOV Premium** → VIP recovery campaigns, personalized offers
2. **Medium AOV High Engagement** → Targeted discounts, urgency messaging  
3. **Low AOV High Engagement** → Social proof, smaller incentives
4. **Recent Customers** → Gentle reminders, complementary products
5. **Other Bucket** → Broad awareness campaigns, basic offers

## 🔍 Technical Implementation

### Data Generation
- **Realistic Correlations**: High AOV users tend to have higher engagement
- **Natural Distributions**: Log-normal for AOV, normal for scores
- **Business Logic**: Recent customers, cart complexity, seasonal patterns

### Validation Framework
```python
def _validate_mece(self, df, segments):
    # Check mutual exclusivity
    # Verify collective exhaustiveness  
    # Report overlaps and gaps
```

### Export Capabilities
- **CSV Format**: Marketer-friendly tabular data
- **JSON Format**: API integration ready
- **Summary Reports**: Executive dashboards

## 📈 Business Impact

### Immediate Benefits
- **Precision Targeting**: 5 distinct audience segments vs. broadcast
- **Resource Optimization**: Focus spend on high-value segments
- **Campaign Personalization**: Tailored messaging by segment characteristics

### Success Metrics
- **Segment Coverage**: 100% of cart abandoners assigned
- **Size Compliance**: All segments meet minimum thresholds
- **Score Differentiation**: Clear ranking for resource allocation

## 🔧 Configuration Options

```python
# Customize thresholds
engine = MECESegmentationEngine(
    min_segment_size=500,    # Minimum viable segment size
    max_segment_size=20000   # Maximum manageable segment size
)

# Modify scoring weights
scoring_weights = {
    'conversion_potential': 0.25,
    'profitability': 0.25,
    'lift_vs_control': 0.20,
    'strategic_fit': 0.20,
    'size_score': 0.10
}
```

## ⚠️ Limitations & Future Improvements

### Current Limitations
1. **Static Thresholds**: Percentile-based cuts may not reflect business rules
2. **Simulated Lift**: Real A/B test data would improve accuracy
3. **Limited Features**: Additional behavioral signals could enhance segmentation
4. **Historical Bias**: Past performance may not predict future behavior

### Potential Enhancements
1. **Dynamic Thresholds**: Machine learning-based optimal cut points
2. **Real-time Updates**: Streaming data integration for daily refresh
3. **Holdout Testing**: Built-in A/B testing framework
4. **Advanced Scoring**: Propensity models, CLV predictions
5. **Seasonal Adjustments**: Time-based segment modifications

## 📋 File Structure
```
mece-segmentation/
├── mece_segmentation.py          # Main implementation
├── README.md                     # This file
├── cart_abandoner_segments.csv   # Output results (CSV)
├── cart_abandoner_segments.json  # Output results (JSON)
└── requirements.txt              # Dependencies
```

## 🤝 Usage Examples

### Basic Usage
```python
from mece_segmentation import MECESegmentationEngine

# Initialize
engine = MECESegmentationEngine()

# Run segmentation  
segments, universe_df = engine.run_segmentation()

# Export results
engine.export_results(segments, "my_segments")
```

### Custom Data
```python
# Use your own dataset
my_data = pd.read_csv('my_cart_data.csv')
segments, universe_df = engine.run_segmentation(my_data)
```

### Integration Ready
```python
# Get segments for API integration
segment_list = engine.segments
for segment in segment_list:
    if segment['valid']:
        send_to_marketing_platform(segment)
```

## 📞 Support

For questions about implementation, customization, or integration, please refer to the inline documentation or create an issue in the repository.

---

**Built with Python | Designed for Growth Marketing | Validated for Production**