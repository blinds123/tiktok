"""Utility helper functions for TikTok viral fashion scraper."""

import json
import csv
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
from functools import wraps


# =============================================================================
# Date/Time Helpers
# =============================================================================

def format_timestamp(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object to string.

    Args:
        dt: Datetime object to format
        format_str: Format string (default: ISO-like format)

    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def parse_tiktok_timestamp(timestamp: Union[int, float, str]) -> Optional[datetime]:
    """
    Parse various TikTok timestamp formats to datetime.

    Args:
        timestamp: Unix timestamp (int/float) or ISO string

    Returns:
        Datetime object or None if parsing fails
    """
    try:
        if isinstance(timestamp, (int, float)):
            # Unix timestamp (seconds or milliseconds)
            if timestamp > 1e10:  # Likely milliseconds
                timestamp = timestamp / 1000
            return datetime.fromtimestamp(timestamp)
        elif isinstance(timestamp, str):
            # Try ISO format
            timestamp = timestamp.replace("Z", "+00:00")
            return datetime.fromisoformat(timestamp)
    except (ValueError, OSError):
        pass
    return None


def get_time_ago_string(dt: datetime) -> str:
    """
    Get human-readable time ago string (e.g., "2 hours ago", "3 days ago").

    Args:
        dt: Datetime to compare against now

    Returns:
        Human-readable time string
    """
    now = datetime.utcnow()
    delta = now - dt

    if delta.days > 365:
        years = delta.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    elif delta.days > 30:
        months = delta.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif delta.days > 0:
        return f"{delta.days} day{'s' if delta.days != 1 else ''} ago"
    elif delta.seconds >= 3600:
        hours = delta.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif delta.seconds >= 60:
        minutes = delta.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "just now"


def is_recent_video(created_at: datetime, hours: int = 24) -> bool:
    """
    Check if a video was posted within the last N hours.

    Args:
        created_at: Video creation datetime
        hours: Number of hours to check (default: 24)

    Returns:
        True if video is recent, False otherwise
    """
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    return created_at >= cutoff


def get_date_range(days_back: int = 7) -> tuple[datetime, datetime]:
    """
    Get a date range from days_back until now.

    Args:
        days_back: Number of days to go back

    Returns:
        Tuple of (start_date, end_date)
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days_back)
    return start_date, end_date


# =============================================================================
# Rate Limiting Helpers
# =============================================================================

class RateLimiter:
    """
    Simple rate limiter to control API request frequency.

    Example:
        limiter = RateLimiter(max_calls=10, time_window=60)
        with limiter:
            make_api_call()
    """

    def __init__(self, max_calls: int, time_window: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: List[float] = []

    def __enter__(self):
        """Context manager entry - wait if needed before allowing call."""
        self.wait_if_needed()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - record the call time."""
        self.calls.append(time.time())

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()

        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls
                     if now - call_time < self.time_window]

        # If at limit, wait until oldest call expires
        if len(self.calls) >= self.max_calls:
            sleep_time = self.time_window - (now - self.calls[0]) + 0.1
            if sleep_time > 0:
                time.sleep(sleep_time)
                # Clean up again after sleeping
                now = time.time()
                self.calls = [call_time for call_time in self.calls
                            if now - call_time < self.time_window]

    def reset(self):
        """Reset the rate limiter."""
        self.calls = []


def exponential_backoff(
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for exponential backoff retry logic.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exceptions: Tuple of exceptions to catch

    Example:
        @exponential_backoff(max_retries=3)
        def fetch_data():
            return api.get_data()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = base_delay

            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        raise

                    sleep_time = min(delay * (2 ** (retries - 1)), max_delay)
                    print(f"Retry {retries}/{max_retries} after {sleep_time:.1f}s due to: {e}")
                    time.sleep(sleep_time)

            return None
        return wrapper
    return decorator


# =============================================================================
# Data Validation Helpers
# =============================================================================

def validate_video_data(data: Dict[str, Any]) -> bool:
    """
    Validate that video data has required fields.

    Args:
        data: Raw video data dictionary

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["id", "author"]
    return all(field in data for field in required_fields)


def validate_creator_data(data: Dict[str, Any]) -> bool:
    """
    Validate that creator data has required fields.

    Args:
        data: Raw creator data dictionary

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["uniqueId", "id"]
    return all(field in data for field in required_fields)


def sanitize_hashtag(hashtag: str) -> str:
    """
    Sanitize a hashtag by removing # and special characters.

    Args:
        hashtag: Raw hashtag string

    Returns:
        Cleaned hashtag
    """
    # Remove # prefix
    clean = hashtag.lstrip("#")
    # Remove special characters, keep only alphanumeric and underscores
    clean = re.sub(r"[^\w]", "", clean)
    return clean.lower()


def extract_video_id_from_url(url: str) -> Optional[str]:
    """
    Extract video ID from a TikTok URL.

    Args:
        url: TikTok video URL

    Returns:
        Video ID or None if not found

    Examples:
        https://www.tiktok.com/@user/video/1234567890 -> 1234567890
        https://vm.tiktok.com/ABC123/ -> ABC123
    """
    patterns = [
        r"/video/(\d+)",
        r"vm\.tiktok\.com/([A-Za-z0-9]+)",
        r"vt\.tiktok\.com/([A-Za-z0-9]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def is_valid_tiktok_url(url: str) -> bool:
    """
    Check if a URL is a valid TikTok URL.

    Args:
        url: URL to validate

    Returns:
        True if valid TikTok URL, False otherwise
    """
    tiktok_domains = [
        "tiktok.com",
        "vm.tiktok.com",
        "vt.tiktok.com",
    ]
    return any(domain in url for domain in tiktok_domains)


# =============================================================================
# JSON/CSV Export Helpers
# =============================================================================

def export_to_json(
    data: Union[List, Dict],
    filepath: Union[str, Path],
    indent: int = 2,
    ensure_ascii: bool = False
) -> Path:
    """
    Export data to JSON file.

    Args:
        data: Data to export
        filepath: Output file path
        indent: JSON indentation (default: 2)
        ensure_ascii: Whether to escape non-ASCII characters

    Returns:
        Path to created file
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii, default=str)

    return filepath


def export_to_csv(
    data: List[Dict],
    filepath: Union[str, Path],
    fieldnames: Optional[List[str]] = None
) -> Path:
    """
    Export list of dictionaries to CSV file.

    Args:
        data: List of dictionaries to export
        filepath: Output file path
        fieldnames: Optional list of field names (uses keys from first dict if None)

    Returns:
        Path to created file
    """
    if not data:
        raise ValueError("Cannot export empty data to CSV")

    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if fieldnames is None:
        fieldnames = list(data[0].keys())

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)

    return filepath


def load_from_json(filepath: Union[str, Path]) -> Union[List, Dict]:
    """
    Load data from JSON file.

    Args:
        filepath: Path to JSON file

    Returns:
        Loaded data (list or dict)
    """
    filepath = Path(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_viral_candidates(
    candidates: List,
    output_dir: Union[str, Path] = "output",
    filename_prefix: str = "viral_candidates"
) -> Dict[str, Path]:
    """
    Save viral candidates to both JSON and CSV formats with timestamp.

    Args:
        candidates: List of ViralCandidate objects
        output_dir: Output directory path
        filename_prefix: Prefix for output filenames

    Returns:
        Dictionary with paths to created files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Convert candidates to dictionaries
    data = [c.to_dict() if hasattr(c, "to_dict") else c for c in candidates]

    # Save JSON
    json_path = output_dir / f"{filename_prefix}_{timestamp}.json"
    export_to_json(data, json_path)

    # Flatten data for CSV
    csv_data = []
    for item in data:
        flat = {
            "video_url": item["video_url"],
            "video_id": item["video_id"],
            "description": item["description"],
            "username": item["creator"]["username"],
            "followers": item["creator"]["followers"],
            "avg_views": item["creator"]["avg_views"],
            "views": item["metrics"]["views"],
            "likes": item["metrics"]["likes"],
            "comments": item["metrics"]["comments"],
            "shares": item["metrics"]["shares"],
            "engagement_rate": item["metrics"]["engagement_rate"],
            "viral_score": item["viral_analysis"]["viral_score"],
            "view_multiplier": item["viral_analysis"]["view_multiplier"],
            "hours_since_posted": item["viral_analysis"]["hours_since_posted"],
            "fashion_category": item["fashion"]["category"],
            "keywords": ", ".join(item["fashion"]["keywords"]),
            "hashtags": ", ".join(item["hashtags"]),
            "posted_at": item["posted_at"],
        }
        csv_data.append(flat)

    # Save CSV
    csv_path = output_dir / f"{filename_prefix}_{timestamp}.csv"
    export_to_csv(csv_data, csv_path)

    return {
        "json": json_path,
        "csv": csv_path,
    }


# =============================================================================
# Formatting Helpers
# =============================================================================

def format_number(num: Union[int, float], precision: int = 1) -> str:
    """
    Format large numbers with K, M, B suffixes.

    Args:
        num: Number to format
        precision: Decimal precision

    Returns:
        Formatted string (e.g., "1.2M", "500K")
    """
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.{precision}f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.{precision}f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.{precision}f}K"
    else:
        return str(int(num))


def format_engagement_rate(rate: float) -> str:
    """
    Format engagement rate as percentage string.

    Args:
        rate: Engagement rate (0-100)

    Returns:
        Formatted percentage string
    """
    return f"{rate:.2f}%"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
