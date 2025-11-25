@echo off
REM TikTok Viral Fashion Scraper - Windows Setup Script
REM Run this script to set up everything automatically

echo ========================================================================
echo    TikTok Viral Fashion Scraper - Setup Script (Windows)
echo ========================================================================
echo.

REM Check Python
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed. Please install Python 3.9+ first.
    pause
    exit /b 1
)

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Install Playwright browser
echo.
echo Installing Playwright Chromium browser...
playwright install chromium

REM Create .env if it doesn't exist
if not exist .env (
    echo.
    echo Creating .env configuration file...
    (
        echo # Bright Data Scraping Browser Credentials
        echo BRIGHT_DATA_HOST=brd.superproxy.io
        echo BRIGHT_DATA_PORT=9222
        echo BRIGHT_DATA_USERNAME=brd-customer-hl_9d12e57c-zone-scraping_browser1
        echo BRIGHT_DATA_PASSWORD=u2ynaxqh9889
        echo BRIGHT_DATA_BROWSER_WS=wss://brd-customer-hl_9d12e57c-zone-scraping_browser1:u2ynaxqh9889@brd.superproxy.io:9222
        echo MIN_FOLLOWERS=50000
        echo MAX_FOLLOWERS=150000
        echo VIRAL_MULTIPLIER=10
        echo HOURS_LOOKBACK=24
        echo PRIORITY_WINDOW=6
        echo MAX_RESULTS=20
        echo TARGET_LOCATIONS=US,CA,GB
        echo TARGET_GENDER=female
        echo TARGET_NICHE=fashion
    ) > .env
    echo    Created .env with your Bright Data credentials
) else (
    echo    .env file already exists
)

echo.
echo ========================================================================
echo    Setup Complete!
echo ========================================================================
echo.
echo To activate the environment in future sessions:
echo    venv\Scripts\activate.bat
echo.
echo To run the scanner:
echo    python main.py scan --limit 20
echo.
echo To run with custom hashtags:
echo    python main.py scan -h fashion -h ootd -h coquette --limit 20
echo.
pause
