#!/bin/bash
# TikTok Viral Fashion Scraper - One-Command Setup Script
# Run this script to set up everything automatically

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║   TikTok Viral Fashion Scraper - Setup Script                         ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "   Found Python $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browser
echo ""
echo "🌐 Installing Playwright Chromium browser..."
playwright install chromium

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "⚙️  Creating .env configuration file..."
    cat > .env << 'EOF'
# Bright Data Scraping Browser Credentials
# Get these from: https://brightdata.com/cp/web_access
BRIGHT_DATA_HOST=brd.superproxy.io
BRIGHT_DATA_PORT=9222
BRIGHT_DATA_USERNAME=brd-customer-hl_9d12e57c-zone-scraping_browser1
BRIGHT_DATA_PASSWORD=u2ynaxqh9889

# WebSocket URL (auto-constructed from above)
BRIGHT_DATA_BROWSER_WS=wss://brd-customer-hl_9d12e57c-zone-scraping_browser1:u2ynaxqh9889@brd.superproxy.io:9222

# App Settings
MIN_FOLLOWERS=50000
MAX_FOLLOWERS=150000
VIRAL_MULTIPLIER=10
HOURS_LOOKBACK=24
PRIORITY_WINDOW=6
MAX_RESULTS=20

# Target Settings (hardcoded for fashion women micro-influencers)
TARGET_LOCATIONS=US,CA,GB
TARGET_GENDER=female
TARGET_NICHE=fashion
EOF
    echo "   ✓ Created .env with your Bright Data credentials"
else
    echo ""
    echo "   ✓ .env file already exists"
fi

# Run demo to verify installation
echo ""
echo "🧪 Running demo to verify installation..."
python demo_live.py 2>&1 | grep -E "(Generated|Analysis complete|Demo complete)" || true

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║   ✅ Setup Complete!                                                   ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "To activate the environment in future sessions:"
echo "   source venv/bin/activate"
echo ""
echo "To run the scanner:"
echo "   python main.py scan --limit 20"
echo ""
echo "To run with custom hashtags:"
echo "   python main.py scan -h fashion -h ootd -h coquette --limit 20"
echo ""
echo "To export results to JSON:"
echo "   python main.py scan --limit 20 --output results.json"
echo ""
