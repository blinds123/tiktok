"""Configuration management for TikTok viral fashion scraper."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    # Bright Data API credentials
    bright_data_api_token: str
    bright_data_dataset_id: Optional[str] = None
    bright_data_proxy_host: str = "brd.superproxy.io"
    bright_data_proxy_port: int = 22225
    bright_data_proxy_username: Optional[str] = None
    bright_data_proxy_password: Optional[str] = None

    # Scraping settings
    min_followers: int = 50000
    max_followers: int = 150000
    viral_multiplier: float = 10.0
    hours_lookback: int = 24
    max_results: int = 20

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables with defaults."""
        return cls(
            bright_data_api_token=os.getenv("BRIGHT_DATA_API_TOKEN", ""),
            bright_data_dataset_id=os.getenv("BRIGHT_DATA_DATASET_ID"),
            bright_data_proxy_host=os.getenv("BRIGHT_DATA_PROXY_HOST", "brd.superproxy.io"),
            bright_data_proxy_port=int(os.getenv("BRIGHT_DATA_PROXY_PORT", "22225")),
            bright_data_proxy_username=os.getenv("BRIGHT_DATA_PROXY_USERNAME"),
            bright_data_proxy_password=os.getenv("BRIGHT_DATA_PROXY_PASSWORD"),
            min_followers=int(os.getenv("MIN_FOLLOWERS", "50000")),
            max_followers=int(os.getenv("MAX_FOLLOWERS", "150000")),
            viral_multiplier=float(os.getenv("VIRAL_MULTIPLIER", "10.0")),
            hours_lookback=int(os.getenv("HOURS_LOOKBACK", "24")),
            max_results=int(os.getenv("MAX_RESULTS", "20")),
        )

    def validate(self) -> tuple[bool, str]:
        """
        Validate configuration.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.bright_data_api_token:
            return False, "BRIGHT_DATA_API_TOKEN is required"

        if self.min_followers < 0:
            return False, "MIN_FOLLOWERS must be positive"

        if self.max_followers < self.min_followers:
            return False, "MAX_FOLLOWERS must be greater than MIN_FOLLOWERS"

        if self.viral_multiplier <= 0:
            return False, "VIRAL_MULTIPLIER must be positive"

        if self.hours_lookback <= 0:
            return False, "HOURS_LOOKBACK must be positive"

        return True, ""

    def to_dict(self) -> dict:
        """Convert config to dictionary for display."""
        return {
            "Bright Data API Token": "***" + self.bright_data_api_token[-4:] if self.bright_data_api_token else "Not set",
            "Dataset ID": self.bright_data_dataset_id or "Using default",
            "Proxy Host": self.bright_data_proxy_host,
            "Proxy Port": self.bright_data_proxy_port,
            "Proxy Username": self.bright_data_proxy_username or "Not set",
            "Min Followers": f"{self.min_followers:,}",
            "Max Followers": f"{self.max_followers:,}",
            "Viral Multiplier": f"{self.viral_multiplier}x",
            "Hours Lookback": f"{self.hours_lookback}h",
            "Max Results": self.max_results,
        }
