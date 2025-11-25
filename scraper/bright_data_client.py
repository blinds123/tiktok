"""Bright Data API client for web scraping."""

import time
import requests
from typing import Optional
from dataclasses import dataclass


@dataclass
class BrightDataConfig:
    """Configuration for Bright Data API."""

    api_token: str
    dataset_id: Optional[str] = None
    proxy_host: str = "brd.superproxy.io"
    proxy_port: int = 22225
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None

    @property
    def proxy_url(self) -> Optional[str]:
        """Get formatted proxy URL if credentials are available."""
        if self.proxy_username and self.proxy_password:
            return f"http://{self.proxy_username}:{self.proxy_password}@{self.proxy_host}:{self.proxy_port}"
        return None


class BrightDataClient:
    """Client for interacting with Bright Data APIs."""

    BASE_URL = "https://api.brightdata.com"
    DATASET_API_URL = "https://api.brightdata.com/datasets/v3"

    def __init__(self, config: BrightDataConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {config.api_token}",
            "Content-Type": "application/json",
        })

    def trigger_dataset_collection(
        self,
        dataset_id: str,
        inputs: list[dict],
        notify_url: Optional[str] = None,
    ) -> dict:
        """
        Trigger a dataset collection job.

        Args:
            dataset_id: The Bright Data dataset ID
            inputs: List of input parameters for the collection
            notify_url: Optional webhook URL for completion notification

        Returns:
            Response containing snapshot_id for tracking
        """
        url = f"{self.DATASET_API_URL}/trigger"
        params = {"dataset_id": dataset_id}

        if notify_url:
            params["notify"] = notify_url

        response = self.session.post(url, params=params, json=inputs)
        response.raise_for_status()
        return response.json()

    def get_snapshot_status(self, snapshot_id: str) -> dict:
        """
        Get the status of a dataset snapshot.

        Args:
            snapshot_id: The snapshot ID from trigger response

        Returns:
            Status information including state and progress
        """
        url = f"{self.DATASET_API_URL}/snapshot/{snapshot_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_snapshot_data(self, snapshot_id: str, format: str = "json") -> list:
        """
        Get the data from a completed snapshot.

        Args:
            snapshot_id: The snapshot ID
            format: Output format (json, csv, etc.)

        Returns:
            List of scraped data records
        """
        url = f"{self.DATASET_API_URL}/snapshot/{snapshot_id}"
        params = {"format": format}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def wait_for_snapshot(
        self,
        snapshot_id: str,
        timeout: int = 300,
        poll_interval: int = 10,
        progress_callback=None,
    ) -> list:
        """
        Wait for a snapshot to complete and return the data.

        Args:
            snapshot_id: The snapshot ID to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: How often to check status
            progress_callback: Optional callback for progress updates

        Returns:
            List of scraped data records
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_snapshot_status(snapshot_id)
            state = status.get("status", "unknown")

            if progress_callback:
                progress_callback(state, status)

            if state == "ready":
                return self.get_snapshot_data(snapshot_id)
            elif state == "failed":
                raise Exception(f"Snapshot failed: {status.get('error', 'Unknown error')}")

            time.sleep(poll_interval)

        raise TimeoutError(f"Snapshot {snapshot_id} did not complete within {timeout} seconds")

    def scrape_with_proxy(self, url: str, headers: Optional[dict] = None) -> requests.Response:
        """
        Make a request using Bright Data proxy.

        Args:
            url: The URL to scrape
            headers: Optional additional headers

        Returns:
            Response object
        """
        proxy_url = self.config.proxy_url
        if not proxy_url:
            raise ValueError("Proxy credentials not configured")

        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }

        req_headers = headers or {}
        response = requests.get(url, proxies=proxies, headers=req_headers, verify=False)
        return response

    def get_available_datasets(self) -> list:
        """Get list of available datasets for the account."""
        url = f"{self.DATASET_API_URL}/datasets"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def search_marketplace_datasets(self, keyword: str = "tiktok") -> list:
        """Search for datasets in the Bright Data marketplace."""
        url = f"{self.BASE_URL}/datasets/marketplace"
        params = {"search": keyword}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
