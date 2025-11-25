# 🔥 TikTok Viral Fashion Scraper

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Coverage](https://img.shields.io/badge/coverage-85%25-yellowgreen)

A powerful CLI tool for discovering viral fashion trends from **women micro-influencers** in **USA, Canada, and UK** using Bright Data's web scraping infrastructure. Optimized for **early viral detection within 6 hours** of posting.

### 🎯 Key Targeting

| Feature | Setting |
|---------|---------|
| **Locations** | USA, Canada, UK only |
| **Gender** | Women influencers only |
| **Niche** | Fashion content |
| **Priority Window** | Videos < 6 hours old |
| **Followers** | 50k-150k (micro-influencers) |
| **Viral Threshold** | 10x average views |

---

## 📖 Overview

The **TikTok Viral Fashion Scraper** is an intelligent tool designed to help fashion brands, marketers, and trend researchers identify emerging fashion trends before they go mainstream. By analyzing content from micro-influencers (creators with 50k-150k followers), this tool identifies videos experiencing exceptional viral growth and extracts actionable fashion insights.

### Why This Tool?

- **Early Trend Detection**: Catch trends as they emerge from micro-influencers before they saturate the market
- **Data-Driven Insights**: Algorithmic viral detection based on engagement multipliers and growth patterns
- **Fashion-Specific Analysis**: Comprehensive product extraction, brand detection, and trend categorization
- **Professional Infrastructure**: Built on Bright Data's enterprise-grade TikTok scraping platform
- **Beautiful CLI**: Rich terminal output with progress tracking, tables, and detailed reports

---

## ✨ Features

### 🎯 Core Capabilities

- **Bright Data Integration**: Enterprise-grade TikTok scraping using Bright Data's Web Scraper API
- **Early Viral Detection**: Priority 6-hour window to catch videos BEFORE they peak
- **Location Filtering**: Targets USA, Canada, and UK creators only
- **Gender Filtering**: Women influencers only (fashion niche)
- **Viral Trend Detection**: Sophisticated algorithm that identifies videos with exceptional performance (10x+ average views)
- **Micro-Influencer Targeting**: Focuses on creators with 50k-150k followers where trends originate
- **Urgency Classification**: CRITICAL/URGENT/HIGH/MEDIUM/LOW based on viral velocity
- **Fashion Product Extraction**: AI-powered detection of clothing items, accessories, and brands
- **Product Opportunity Scoring**: Sellability scores and profit potential analysis
- **Trend Categorization**: Automatic classification into 12+ fashion categories (streetwear, Y2K, minimalist, etc.)
- **CLI with Rich Output**: Beautiful terminal interface with progress bars, tables, and colored output
- **JSON Export**: Export results for integration with other tools and workflows

### 📊 Fashion Intelligence

The tool maintains comprehensive keyword dictionaries for:
- **200+ Clothing Items**: From crop tops to cargo pants
- **150+ Accessories**: Shoes, bags, jewelry, and more
- **100+ Fashion Brands**: Fast fashion to luxury labels
- **12 Style Categories**: Streetwear, Y2K, minimalist, coquette, cottagecore, dark academia, coastal, boho, athleisure, glamorous, edgy, preppy
- **80+ Fashion Actions**: Hauls, try-ons, styling, lookbooks, thrift flips

---

## 🚀 Quick Start

Get up and running in 5 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/tiktok-viral-fashion-scraper.git
cd tiktok-viral-fashion-scraper

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up configuration (interactive wizard)
python main.py configure

# 4. Run your first scan
python main.py scan -h fashion -h ootd --limit 10
```

That's it! You'll see viral fashion trends from TikTok micro-influencers.

---

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- Bright Data account with API access
- pip package manager

### Step-by-Step Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/tiktok-viral-fashion-scraper.git
   cd tiktok-viral-fashion-scraper
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**:
   ```bash
   python main.py --version
   ```

### Dependencies

The tool requires the following Python packages:
- `requests>=2.31.0` - HTTP client for API calls
- `python-dotenv>=1.0.0` - Environment variable management
- `pydantic>=2.5.0` - Data validation and parsing
- `rich>=13.7.0` - Beautiful terminal output
- `aiohttp>=3.9.0` - Async HTTP client
- `asyncio>=3.4.3` - Asynchronous programming
- `pandas>=2.1.0` - Data analysis and manipulation
- `schedule>=1.2.0` - Job scheduling
- `click>=8.1.0` - CLI framework
- `pytest>=7.4.0` - Testing framework
- `pytest-cov>=4.1.0` - Test coverage
- `pytest-asyncio>=0.21.0` - Async testing

---

## ⚙️ Configuration

### Getting Bright Data Credentials

1. **Sign up for Bright Data**:
   - Visit [brightdata.com](https://brightdata.com)
   - Create an account (free trial available)

2. **Get your API Token**:
   - Navigate to the [Dashboard](https://brightdata.com/cp/dashboard)
   - Click on "API Tokens" in the sidebar
   - Generate a new token and copy it

3. **Set up TikTok Scraper** (optional):
   - Go to [Web Scraper](https://brightdata.com/products/web-scraper)
   - Create a new TikTok scraper or use default datasets
   - Copy the Dataset ID if using custom scraper

### Environment Variables

The tool uses the following environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BRIGHT_DATA_API_TOKEN` | ✅ Yes | - | Your Bright Data API token |
| `BRIGHT_DATA_DATASET_ID` | ❌ No | Auto | Custom dataset ID (uses default TikTok datasets if not set) |
| `BRIGHT_DATA_PROXY_HOST` | ❌ No | `brd.superproxy.io` | Proxy host for web scraping |
| `BRIGHT_DATA_PROXY_PORT` | ❌ No | `22225` | Proxy port |
| `BRIGHT_DATA_PROXY_USERNAME` | ❌ No | - | Proxy username (if using proxies) |
| `BRIGHT_DATA_PROXY_PASSWORD` | ❌ No | - | Proxy password (if using proxies) |
| `MIN_FOLLOWERS` | ❌ No | `50000` | Minimum follower count for creators |
| `MAX_FOLLOWERS` | ❌ No | `150000` | Maximum follower count for creators |
| `VIRAL_MULTIPLIER` | ❌ No | `10.0` | Views multiplier threshold (10 = 10x average) |
| `HOURS_LOOKBACK` | ❌ No | `24` | Only analyze videos from last N hours |
| `MAX_RESULTS` | ❌ No | `20` | Maximum number of results to return |

### .env File Setup

#### Option 1: Interactive Configuration (Recommended)

Run the configuration wizard:

```bash
python main.py configure
```

This interactive wizard will:
- Prompt you for your Bright Data credentials
- Guide you through setting up scraping parameters
- Save everything to a `.env` file automatically

#### Option 2: Manual Setup

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your favorite editor:
   ```bash
   nano .env  # or vim, code, etc.
   ```

3. Add your credentials:
   ```env
   BRIGHT_DATA_API_TOKEN=your_actual_token_here
   BRIGHT_DATA_DATASET_ID=gd_lyclj2e041hb8cxmz7

   MIN_FOLLOWERS=50000
   MAX_FOLLOWERS=150000
   VIRAL_MULTIPLIER=10
   HOURS_LOOKBACK=24
   MAX_RESULTS=20
   ```

### Test Your Configuration

Verify your setup is working:

```bash
python main.py test-connection
```

This command will:
- ✅ Validate your API token
- ✅ Check connectivity to Bright Data
- ✅ List available datasets
- ✅ Display your current configuration

---

## 💻 Usage Examples

### Basic Scan

Search for viral fashion content using default hashtags:

```bash
python main.py scan
```

This uses default hashtags: `#fashion`, `#ootd`, `#streetwear`

### Custom Hashtags

Specify your own hashtags to search:

```bash
python main.py scan -h fashion -h ootd -h streetwear -h y2k -h grwm
```

You can specify multiple `-h` flags for different hashtags.

### Custom Parameters

Override default configuration with command-line options:

```bash
python main.py scan \
  -h fashion \
  -h ootd \
  --min-followers 30000 \
  --max-followers 100000 \
  --viral-multiplier 15 \
  --hours 48 \
  --limit 50
```

**Parameters explained**:
- `--min-followers`: Minimum follower count (default: 50,000)
- `--max-followers`: Maximum follower count (default: 150,000)
- `--viral-multiplier`: How many times above average views (default: 10x)
- `--hours`: Time window in hours (default: 24)
- `--limit`: Maximum results to return (default: 20)

### JSON Export

Export results to a JSON file for further analysis:

```bash
python main.py scan -h fashion -h ootd --output results.json
```

The JSON file contains:
- Video metadata (URL, description, metrics)
- Creator information (username, followers, engagement)
- Fashion analysis (products, categories, keywords)
- Viral scores and multipliers

Example output structure:

```json
{
  "total_candidates": 15,
  "candidates": [
    {
      "video_id": "7234567890123456789",
      "url": "https://www.tiktok.com/@fashionista/video/7234567890123456789",
      "creator": {
        "username": "fashionista",
        "follower_count": 87000,
        "verified": false
      },
      "viral_score": 245.8,
      "view_multiplier": 23.4,
      "detected_products": ["crop top", "jeans", "nike", "sunglasses"],
      "trend_category": "streetwear",
      "fashion_keywords": ["ootd", "outfit", "style", "fashion"]
    }
  ]
}
```

### Testing Connection

Before running a full scan, test your Bright Data connection:

```bash
python main.py test-connection
```

### Help and Documentation

Get help on any command:

```bash
python main.py --help
python main.py scan --help
python main.py configure --help
```

---

## 🏗️ Architecture Overview

### Module Structure

```
tiktok-viral-fashion-scraper/
├── main.py                 # CLI application entry point
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
│
├── scraper/              # Data collection layer
│   ├── __init__.py
│   ├── bright_data_client.py    # Bright Data API client
│   └── tiktok_scraper.py        # TikTok-specific scraping logic
│
├── analyzer/             # Data analysis layer
│   ├── __init__.py
│   ├── viral_detector.py        # Viral trend detection algorithm
│   └── fashion_extractor.py     # Fashion content analysis
│
├── models/               # Data models
│   ├── __init__.py
│   └── video.py                 # TikTokVideo, Creator, ViralCandidate
│
└── tests/                # Test suite
    ├── test_viral_detector.py
    └── test_fashion_extractor.py
```

### Data Flow

```
┌─────────────────┐
│   User Input    │
│  (Hashtags)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│   TikTok Scraper        │
│   (Bright Data API)     │
│  • Search by hashtags   │
│  • Collect video data   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Data Parser           │
│  • Parse JSON responses │
│  • Create TikTokVideo   │
│  • Extract metadata     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Viral Detector        │
│  • Filter by followers  │
│  • Calculate averages   │
│  • Detect viral videos  │
│  • Calculate scores     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Fashion Extractor     │
│  • Detect products      │
│  • Categorize trends    │
│  • Extract keywords     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Results Display       │
│  • Rich table output    │
│  • Summary statistics   │
│  • JSON export          │
└─────────────────────────┘
```

### Key Design Decisions

1. **Bright Data Integration**: Uses enterprise-grade scraping infrastructure for reliability and scale
2. **Modular Architecture**: Separation of concerns between scraping, detection, and analysis
3. **Rich CLI**: Beautiful terminal output makes the tool pleasant to use
4. **Type Safety**: Pydantic models ensure data validation and type checking
5. **Configurable Parameters**: All thresholds can be adjusted via CLI or environment variables

---

## 📚 API Reference

### Core Classes

#### `TikTokScraper`

Handles all TikTok data collection using Bright Data.

```python
from scraper import TikTokScraper, BrightDataClient
from scraper.bright_data_client import BrightDataConfig

# Initialize
config = BrightDataConfig(api_token="your_token")
client = BrightDataClient(config)
scraper = TikTokScraper(client)

# Search by hashtags
snapshot_id = scraper.search_by_hashtag(
    hashtags=["fashion", "ootd"],
    limit_per_hashtag=50
)

# Wait for results
results = scraper.wait_and_get_results(snapshot_id, timeout=600)

# Parse video data
videos = [scraper.parse_video_data(raw) for raw in results]
```

**Methods**:
- `search_by_hashtag(hashtags, limit_per_hashtag)` - Search TikTok by hashtags
- `search_by_keyword(keywords, limit_per_keyword)` - Search by keywords
- `get_user_profile(usernames)` - Fetch user profiles
- `get_user_posts(usernames, posts_per_user)` - Get posts from specific users
- `wait_and_get_results(snapshot_id, timeout)` - Wait for data collection
- `parse_video_data(raw_data)` - Parse API response into TikTokVideo object

#### `ViralTrendDetector`

Analyzes videos to identify viral trends among micro-influencers.

```python
from analyzer import ViralTrendDetector

# Initialize with video data
detector = ViralTrendDetector(videos)

# Run complete analysis
viral_candidates = detector.analyze(
    min_followers=50000,
    max_followers=150000,
    recency_hours=24,
    viral_multiplier=10.0,
    top_n=20
)

# Get summary statistics
stats = detector.get_summary_stats()
```

**Methods**:
- `filter_by_follower_range(min_followers, max_followers)` - Filter by creator size
- `filter_by_recency(hours)` - Filter by video age
- `calculate_creator_averages()` - Calculate average views per creator
- `detect_viral_candidates(multiplier)` - Identify viral videos
- `rank_candidates()` - Sort by viral score
- `get_top_candidates(n)` - Get top N results
- `analyze(...)` - Run complete pipeline
- `get_summary_stats()` - Get analysis statistics

#### `FashionExtractor`

Extracts fashion-specific information from video content.

```python
from analyzer import FashionExtractor

# Initialize
extractor = FashionExtractor()

# Check if video contains fashion content
is_fashion = extractor.is_fashion_content(video)

# Extract products
products = extractor.extract_products(
    description=video.description,
    hashtags=video.hashtags
)

# Categorize trend
category = extractor.categorize_trend(
    hashtags=video.hashtags,
    description=video.description
)

# Calculate fashion relevance score
score = extractor.calculate_fashion_score(video)

# Enrich viral candidate with fashion data
enriched = extractor.enrich_viral_candidate(candidate)
```

**Methods**:
- `is_fashion_content(video)` - Detect if video is fashion-related
- `extract_products(description, hashtags)` - Extract product mentions
- `categorize_trend(hashtags, description)` - Classify fashion trend
- `calculate_fashion_score(video)` - Calculate relevance score (0-100)
- `enrich_viral_candidate(candidate)` - Add fashion metadata to candidate

### Data Models

#### `TikTokVideo`

Represents a TikTok video with all metadata.

**Attributes**:
- `video_id`: Unique video identifier
- `url`: Direct link to video
- `description`: Video caption/description
- `creator`: TikTokCreator object
- `view_count`: Number of views
- `like_count`: Number of likes
- `comment_count`: Number of comments
- `share_count`: Number of shares
- `created_at`: Timestamp when posted
- `hashtags`: List of hashtags
- `music_title`: Background music title
- `engagement_rate`: Calculated engagement percentage

#### `TikTokCreator`

Represents a TikTok content creator.

**Attributes**:
- `user_id`: Unique user identifier
- `username`: @username handle
- `nickname`: Display name
- `follower_count`: Number of followers
- `following_count`: Number of accounts followed
- `video_count`: Total videos posted
- `verified`: Verification status
- `avg_views`: Average views per video (calculated)

#### `ViralCandidate`

Represents a video identified as having viral potential.

**Attributes**:
- `video`: TikTokVideo object
- `viral_score`: Composite viral score
- `view_multiplier`: How many times above creator's average
- `detected_products`: List of fashion products found
- `fashion_keywords`: Relevant fashion keywords
- `trend_category`: Fashion trend classification

---

## 📤 Output Format

### Terminal Output

The tool provides rich terminal output including:

1. **Configuration Panel**: Shows scan parameters
2. **Progress Tracking**: Real-time progress with spinners
3. **Results Table**: Beautiful table with viral candidates
4. **Detailed Info**: Top 3 candidates with full details
5. **Summary Statistics**: Analysis metrics and category distribution

Example terminal output:

```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   TikTok Viral Fashion Scraper                                ║
║   Discover trending fashion from micro-influencers            ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

┌─────────── Configuration ───────────┐
│                                     │
│  Hashtags: #fashion, #ootd         │
│  Follower Range: 50,000 - 150,000 │
│  Viral Multiplier: 10.0x           │
│  Time Window: 24 hours             │
│  Max Results: 20                   │
│                                     │
└─────────────────────────────────────┘

✓ Collected 847 videos from TikTok
✓ Successfully parsed 842 videos
✓ Found 23 viral candidates
✓ Enriched 23 candidates with fashion data

🔥 Top Viral Candidates
┌───┬─────────────────┬────────────┬────────────┬────────────┬────────┬──────────────┬─────────────────┐
│ # │ Creator         │ Followers  │ Views      │ Multiplier │ Score  │ Category     │ Products        │
├───┼─────────────────┼────────────┼────────────┼────────────┼────────┼──────────────┼─────────────────┤
│ 1 │ @fashionista123 │     87,245 │  2,145,678 │      24.6x │  289.4 │ streetwear   │ crop top, je... │
│ 2 │ @stylemaster    │     92,103 │  1,876,234 │      20.3x │  267.8 │ y2k          │ mini skirt, ... │
│ 3 │ @trendyvibes    │     65,432 │  1,543,210 │      18.9x │  245.2 │ minimalist   │ blazer, trou... │
└───┴─────────────────┴────────────┴────────────┴────────────┴────────┴──────────────┴─────────────────┘
```

### JSON Export Format

When using `--output`, results are exported in this structure:

```json
{
  "total_candidates": 23,
  "candidates": [
    {
      "video": {
        "video_id": "7234567890123456789",
        "url": "https://www.tiktok.com/@fashionista123/video/7234567890123456789",
        "description": "Summer outfit inspo! 🌞 #fashion #ootd #streetwear",
        "creator": {
          "user_id": "123456789",
          "username": "fashionista123",
          "nickname": "Fashion Ista",
          "follower_count": 87245,
          "following_count": 432,
          "video_count": 234,
          "verified": false,
          "avg_views": 87234.5
        },
        "view_count": 2145678,
        "like_count": 345678,
        "comment_count": 12345,
        "share_count": 8765,
        "created_at": "2025-11-24T14:30:00",
        "hashtags": ["fashion", "ootd", "streetwear", "summer"],
        "music_title": "Summer Vibes",
        "engagement_rate": 17.23
      },
      "viral_score": 289.4,
      "view_multiplier": 24.6,
      "detected_products": ["crop top", "jeans", "nike", "sunglasses", "crossbody bag"],
      "fashion_keywords": ["outfit", "ootd", "style", "summer", "streetwear"],
      "trend_category": "streetwear"
    }
  ]
}
```

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version)

### Suggesting Features

Have an idea? Open an issue with:
- Feature description
- Use case and benefits
- Proposed implementation (optional)

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Ensure tests pass: `pytest`
6. Commit with clear messages: `git commit -m "Add amazing feature"`
7. Push to your fork: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/tiktok-viral-fashion-scraper.git
cd tiktok-viral-fashion-scraper

# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Check code style
flake8 .
black --check .
```

### Code Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions and classes
- Write unit tests for new features
- Keep functions focused and modular
- Use type hints where possible

---

## 📄 License

MIT License

Copyright (c) 2025 TikTok Viral Fashion Scraper

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🙏 Acknowledgments

- **Bright Data** - For providing enterprise-grade web scraping infrastructure
- **Rich** - For beautiful terminal output
- **Click** - For elegant CLI framework
- **Pydantic** - For robust data validation

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/tiktok-viral-fashion-scraper/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/tiktok-viral-fashion-scraper/discussions)
- **Email**: support@example.com

---

## 🔗 Links

- [Documentation](https://github.com/yourusername/tiktok-viral-fashion-scraper/wiki)
- [Bright Data Platform](https://brightdata.com)
- [TikTok API Documentation](https://developers.tiktok.com)

---

**Made with ❤️ for the fashion and tech community**
