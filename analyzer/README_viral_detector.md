# Viral Trend Detector Module

## Overview

The `ViralTrendDetector` is a comprehensive module for analyzing TikTok videos to identify emerging viral trends among micro-influencers (50k-150k followers).

## Files Created

- **`/home/user/tiktok/analyzer/viral_detector.py`** - Main detector class (295 lines)
- **`/home/user/tiktok/analyzer/__init__.py`** - Module exports
- **`/home/user/tiktok/test_viral_detector.py`** - Demo script with sample data

## Features

### ViralTrendDetector Class

The main class that orchestrates the entire viral detection pipeline.

#### Constructor
```python
detector = ViralTrendDetector(videos: List[TikTokVideo])
```

#### Core Methods

1. **`filter_by_follower_range(min_followers=50_000, max_followers=150_000)`**
   - Filters videos from creators within specified follower range
   - Default targets micro-influencers (50k-150k followers)
   - Returns filtered list of TikTokVideo objects

2. **`filter_by_recency(hours=24)`**
   - Filters videos posted within specified time window
   - Default: last 24 hours
   - Returns recent TikTokVideo objects

3. **`calculate_creator_averages(videos=None)`**
   - Groups videos by creator
   - Calculates average view counts for each creator
   - Updates creator.avg_views attribute
   - Returns dict mapping user_id to average views

4. **`detect_viral_candidates(multiplier=10.0)`**
   - Identifies videos exceeding multiplier × creator average
   - Default: 10x performance threshold
   - Returns list of ViralCandidate objects

5. **`rank_candidates()`**
   - Sorts viral candidates by viral_score (descending)
   - Viral score factors in: view multiplier, engagement rate, recency
   - Returns sorted list of ViralCandidate objects

6. **`get_top_candidates(n=20)`**
   - Returns top N viral candidates
   - Logs summary to console with rich formatting
   - Default: top 20 candidates

#### Helper Methods

7. **`analyze(min_followers, max_followers, recency_hours, viral_multiplier, top_n)`**
   - Convenience method running complete pipeline
   - Executes all steps in sequence
   - Returns top N viral candidates

8. **`get_summary_stats()`**
   - Returns dictionary with analysis statistics
   - Includes: total videos, filtered count, viral candidates, scores, multipliers

9. **`export_results()`**
   - Exports viral candidates as JSON-ready dictionaries
   - Uses ViralCandidate.to_dict() method
   - Returns list of dictionaries

## Usage Example

### Basic Usage

```python
from analyzer import ViralTrendDetector
from models.video import TikTokVideo

# Load your TikTok videos
videos = load_tiktok_videos()

# Initialize detector
detector = ViralTrendDetector(videos)

# Run complete analysis
viral_trends = detector.analyze(
    min_followers=50_000,
    max_followers=150_000,
    recency_hours=24,
    viral_multiplier=10.0,
    top_n=20
)

# Get results
for candidate in viral_trends:
    print(f"@{candidate.video.creator.username}")
    print(f"  Score: {candidate.viral_score:.2f}")
    print(f"  Views: {candidate.video.view_count:,}")
    print(f"  Multiplier: {candidate.view_multiplier:.1f}x")
```

### Step-by-Step Usage

```python
# Initialize
detector = ViralTrendDetector(videos)

# Filter micro-influencers
detector.filter_by_follower_range(50_000, 150_000)

# Filter recent videos
detector.filter_by_recency(hours=24)

# Calculate averages
detector.calculate_creator_averages()

# Detect viral candidates
detector.detect_viral_candidates(multiplier=10.0)

# Rank by viral score
detector.rank_candidates()

# Get top results
top_20 = detector.get_top_candidates(n=20)

# Export to JSON
json_data = detector.export_results()
```

## Viral Score Calculation

The viral score combines multiple factors:

```python
view_multiplier = views / creator_avg_views
recency_bonus = max(0, (24 - hours_since_posted) / 24)
viral_score = view_multiplier × (1 + engagement_rate/100) × (1 + recency_bonus)
```

**Factors:**
- **View Multiplier**: How many times more views than creator's average
- **Engagement Rate**: (likes + comments + shares) / views × 100
- **Recency Bonus**: Rewards videos posted recently (within 24 hours)

## Output Format

### ViralCandidate Object

Each candidate includes:
- `video`: Full TikTokVideo object
- `viral_score`: Calculated viral score
- `view_multiplier`: Views relative to creator average
- `detected_products`: List of detected fashion products (empty by default)
- `fashion_keywords`: List of fashion keywords (empty by default)
- `trend_category`: Trend category (empty by default)

### JSON Export Format

```json
{
  "video_url": "https://tiktok.com/@username/video/id",
  "video_id": "vid123",
  "description": "Video description",
  "creator": {
    "username": "fashionista",
    "followers": 75000,
    "avg_views": 50000.0
  },
  "metrics": {
    "views": 500000,
    "likes": 50000,
    "comments": 2000,
    "shares": 5000,
    "engagement_rate": 11.4
  },
  "viral_analysis": {
    "viral_score": 15.2,
    "view_multiplier": 10.0,
    "hours_since_posted": 12.5
  },
  "fashion": {
    "detected_products": [],
    "keywords": [],
    "category": ""
  },
  "hashtags": ["fashion", "viral", "trending"],
  "posted_at": "2025-11-25T01:23:37.200897"
}
```

## Console Output

The detector uses `rich.console` for beautiful, informative logging:

- **Cyan**: Initialization messages
- **Green**: Filter results
- **Blue**: Calculation progress
- **Yellow**: Detection results
- **Magenta**: Ranking progress
- **Bold Green**: Final results

## Testing

Run the demo script:

```bash
python3 test_viral_detector.py
```

This demonstrates:
- Sample data generation
- Complete analysis pipeline
- Results display
- JSON export
- Summary statistics

## Dependencies

- `rich>=13.7.0` - Console logging with colors
- `models.video` - TikTokVideo, TikTokCreator, ViralCandidate data models
- Python 3.7+ (uses dataclasses, type hints)

## Notes

- **Creator Averages**: Calculated from ALL videos in the dataset (including viral ones), which may inflate averages. Consider using historical data or adjusting the multiplier accordingly.
- **Micro-Influencers**: Default range is 50k-150k followers, but this is customizable.
- **Multiplier Tuning**: The default 10x multiplier may need adjustment based on your dataset. Start with 3-5x if including viral videos in the average calculation.
- **Recency**: Default 24-hour window ensures trending content is fresh.

## Integration

Import and use in your TikTok scraper:

```python
from analyzer import ViralTrendDetector
from scraper import TikTokScraper

# Scrape videos
scraper = TikTokScraper()
videos = scraper.scrape_hashtag("#fashion", limit=1000)

# Detect viral trends
detector = ViralTrendDetector(videos)
viral_trends = detector.analyze()

# Process results
for trend in viral_trends:
    print(f"Found viral trend: {trend.video.url}")
```
