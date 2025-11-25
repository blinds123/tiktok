# Fashion Extractor Module

## Overview
The `fashion_extractor.py` module provides comprehensive fashion content detection, product extraction, trend categorization, and relevance scoring for TikTok videos.

## File Location
`/home/user/tiktok/analyzer/fashion_extractor.py`

## Features

### Comprehensive Keyword Dictionaries
- **104 clothing items**: tops, bottoms, dresses, outerwear, activewear, etc.
- **91 accessories**: bags, shoes, jewelry, hats, etc.
- **130 fashion brands**: fast fashion, luxury, streetwear, athletic brands
- **12 style categories** with 167 keywords:
  - Streetwear, Y2K, Minimalist, Coquette
  - Cottage Core, Dark Academia, Coastal, Boho
  - Athleisure, Glamorous, Edgy, Preppy
- **59 fashion actions**: haul, try-on, styling, GRWM, etc.
- **37 fashion hashtags**: #fashion, #ootd, #fashionhaul, etc.

## Class: FashionExtractor

### Methods

#### `is_fashion_content(video: TikTokVideo) -> bool`
Determines if a video contains fashion-related content.

**Returns:** `True` if fashion content detected, `False` otherwise

**Detection criteria:**
- Fashion-related hashtags
- Fashion action keywords
- Clothing items (2+ mentions)
- Brand mentions
- Accessories (2+ mentions)
- Style category keywords

#### `extract_products(description: str, hashtags: List[str]) -> List[Dict[str, str]]`
Extracts fashion product mentions from video description and hashtags.

**Returns:** List of product dictionaries with:
- `type`: "clothing", "accessory", or "brand"
- `name`: Product name
- `source`: "description" or "hashtag"

#### `categorize_trend(hashtags: List[str], description: str) -> str`
Categorizes the fashion trend/style of the content.

**Returns:** Trend category name (e.g., "y2k", "streetwear", "coquette") or "general"

**Scoring:** Based on keyword matches in combined hashtags and description

#### `calculate_fashion_score(video: TikTokVideo) -> float`
Calculates a fashion relevance score (0-100).

**Scoring breakdown:**
- Fashion hashtags: 0-30 points
- Fashion actions: 0-20 points
- Product mentions: 0-30 points
- Brand mentions: 0-10 points
- Style category: 0-10 points

#### `enrich_viral_candidate(candidate: ViralCandidate) -> ViralCandidate`
Enriches a ViralCandidate with fashion-specific data.

**Populates:**
- `detected_products`: List of product names
- `fashion_keywords`: Top 10 relevant keywords
- `trend_category`: Fashion trend/style category

**Returns:** The enriched ViralCandidate object

#### `get_all_keywords() -> Dict[str, int]`
Returns summary statistics of all keyword dictionaries.

#### `search_keywords(query: str) -> Dict[str, List[str]]`
Searches for keywords matching a query across all dictionaries.

## Usage Example

```python
from analyzer.fashion_extractor import FashionExtractor
from models.video import TikTokVideo, ViralCandidate

# Initialize extractor
extractor = FashionExtractor()

# Check if video is fashion content
if extractor.is_fashion_content(video):
    # Extract products
    products = extractor.extract_products(
        video.description,
        video.hashtags
    )

    # Categorize trend
    trend = extractor.categorize_trend(
        video.hashtags,
        video.description
    )

    # Calculate fashion score
    score = extractor.calculate_fashion_score(video)

    # Enrich viral candidate
    candidate = ViralCandidate(
        video=video,
        viral_score=video.viral_score,
        view_multiplier=view_multiplier
    )
    enriched = extractor.enrich_viral_candidate(candidate)
```

## Logging

Uses `rich.console` for colored console logging:
- Green: Success messages
- Cyan: Detection notifications
- Yellow: Warnings
- Dim: Debug information

## Dependencies

- `re`: Regular expression matching
- `typing`: Type hints
- `rich.console`: Console logging
- `models.video`: TikTokVideo and ViralCandidate classes

## Testing

Run the test script to verify functionality:
```bash
python3 test_fashion_extractor.py
```

## Module Statistics

- Total lines of code: 549
- File size: 24KB
- Public methods: 8
- Total keywords: 588+

## Notes

- Uses word boundary matching to avoid partial matches
- Case-insensitive keyword matching
- Removes duplicate product detections
- Scores categories based on keyword frequency
- Provides detailed logging for debugging
