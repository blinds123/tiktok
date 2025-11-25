"""
TikTok Scraper using Bright Data Scraping Browser.
Connects via WebSocket to Bright Data's browser infrastructure.
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass
import os

from playwright.async_api import async_playwright, Browser, Page
from rich.console import Console
from dotenv import load_dotenv

from models.video import TikTokVideo, TikTokCreator

console = Console()
load_dotenv()


@dataclass
class BrowserScraperConfig:
    """Configuration for Bright Data Scraping Browser."""

    host: str = "brd.superproxy.io"
    port: int = 9222
    username: str = ""
    password: str = ""

    @property
    def ws_endpoint(self) -> str:
        """Get WebSocket endpoint URL."""
        return f"wss://{self.username}:{self.password}@{self.host}:{self.port}"

    @classmethod
    def from_env(cls) -> "BrowserScraperConfig":
        """Load configuration from environment variables."""
        return cls(
            host=os.getenv("BRIGHT_DATA_HOST", "brd.superproxy.io"),
            port=int(os.getenv("BRIGHT_DATA_PORT", "9222")),
            username=os.getenv("BRIGHT_DATA_USERNAME", ""),
            password=os.getenv("BRIGHT_DATA_PASSWORD", ""),
        )


class TikTokBrowserScraper:
    """Scrapes TikTok using Bright Data's Scraping Browser."""

    # Fashion hashtags to search
    FASHION_HASHTAGS = [
        "fashion", "ootd", "fashiontiktok", "outfitinspo", "grwm",
        "fashionhaul", "tryonhaul", "styleinspo", "y2k", "coquette",
        "aesthetic", "streetstyle", "outfitoftheday", "fashiontrends",
    ]

    def __init__(self, config: BrowserScraperConfig):
        self.config = config
        self.browser: Optional[Browser] = None
        self.playwright = None

    async def connect(self):
        """Connect to Bright Data Scraping Browser."""
        console.print("[cyan]Connecting to Bright Data Scraping Browser...[/cyan]")

        self.playwright = await async_playwright().start()

        try:
            self.browser = await self.playwright.chromium.connect_over_cdp(
                self.config.ws_endpoint
            )
            console.print("[green]✓ Connected to Bright Data browser[/green]")
        except Exception as e:
            console.print(f"[red]Failed to connect: {e}[/red]")
            raise

    async def disconnect(self):
        """Disconnect from browser."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        console.print("[dim]Disconnected from browser[/dim]")

    async def scrape_hashtag(self, hashtag: str, max_videos: int = 30) -> list[dict]:
        """
        Scrape videos from a TikTok hashtag page.

        Args:
            hashtag: Hashtag to search (without #)
            max_videos: Maximum videos to collect

        Returns:
            List of raw video data dictionaries
        """
        if not self.browser:
            await self.connect()

        context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = await context.new_page()

        videos = []

        try:
            url = f"https://www.tiktok.com/tag/{hashtag}"
            console.print(f"[cyan]Scraping #{hashtag}...[/cyan]")

            await page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(3)  # Let content load

            # Scroll to load more videos
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, 1000)")
                await asyncio.sleep(1)

            # Extract video data from the page
            video_elements = await page.query_selector_all('[data-e2e="challenge-item"]')

            if not video_elements:
                # Try alternative selector
                video_elements = await page.query_selector_all('div[class*="DivItemContainer"]')

            console.print(f"[dim]Found {len(video_elements)} video elements[/dim]")

            for element in video_elements[:max_videos]:
                try:
                    video_data = await self._extract_video_data(element, page)
                    if video_data:
                        videos.append(video_data)
                except Exception as e:
                    console.print(f"[yellow]Error extracting video: {e}[/yellow]")
                    continue

        except Exception as e:
            console.print(f"[red]Error scraping #{hashtag}: {e}[/red]")
        finally:
            await context.close()

        return videos

    async def _extract_video_data(self, element, page: Page) -> Optional[dict]:
        """Extract video data from a video element."""
        try:
            # Get video link
            link = await element.query_selector('a')
            if not link:
                return None

            href = await link.get_attribute('href')
            if not href or '/video/' not in href:
                return None

            # Extract video ID from URL
            video_id_match = re.search(r'/video/(\d+)', href)
            video_id = video_id_match.group(1) if video_id_match else None

            # Extract username
            username_match = re.search(r'@([^/]+)', href)
            username = username_match.group(1) if username_match else "unknown"

            # Try to get view count
            view_text = await element.inner_text()
            views = self._parse_count(view_text)

            # Get description if available
            desc_element = await element.query_selector('[class*="desc"], [class*="title"]')
            description = await desc_element.inner_text() if desc_element else ""

            return {
                "id": video_id,
                "url": f"https://www.tiktok.com{href}" if href.startswith('/') else href,
                "author": {"uniqueId": username},
                "desc": description,
                "playCount": views,
                "createTime": int(datetime.utcnow().timestamp()) - 3600 * 6,  # Estimate ~6 hours ago
            }

        except Exception as e:
            return None

    async def scrape_video_details(self, video_url: str) -> Optional[dict]:
        """
        Scrape detailed information from a specific video page.

        Args:
            video_url: Full TikTok video URL

        Returns:
            Detailed video data dictionary
        """
        if not self.browser:
            await self.connect()

        context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        try:
            await page.goto(video_url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(2)

            # Extract data from the page
            data = await page.evaluate("""
                () => {
                    const result = {};

                    // Try to get video stats
                    const statsElements = document.querySelectorAll('[data-e2e="like-count"], [data-e2e="comment-count"], [data-e2e="share-count"]');
                    statsElements.forEach(el => {
                        const key = el.getAttribute('data-e2e');
                        result[key] = el.innerText;
                    });

                    // Get description
                    const desc = document.querySelector('[data-e2e="browse-video-desc"]');
                    result.description = desc ? desc.innerText : '';

                    // Get author info
                    const author = document.querySelector('[data-e2e="browse-username"]');
                    result.author = author ? author.innerText : '';

                    // Get follower count if visible
                    const followers = document.querySelector('[data-e2e="followers-count"]');
                    result.followers = followers ? followers.innerText : '';

                    return result;
                }
            """)

            return data

        except Exception as e:
            console.print(f"[yellow]Error getting video details: {e}[/yellow]")
            return None
        finally:
            await context.close()

    async def search_fashion_videos(
        self,
        hashtags: list[str] = None,
        videos_per_hashtag: int = 20,
    ) -> list[dict]:
        """
        Search for fashion videos across multiple hashtags.

        Args:
            hashtags: List of hashtags to search
            videos_per_hashtag: Max videos per hashtag

        Returns:
            Combined list of video data
        """
        if hashtags is None:
            hashtags = self.FASHION_HASHTAGS[:5]  # Use top 5 by default

        all_videos = []

        await self.connect()

        try:
            for hashtag in hashtags:
                videos = await self.scrape_hashtag(hashtag, videos_per_hashtag)
                all_videos.extend(videos)
                console.print(f"[green]✓ #{hashtag}: {len(videos)} videos[/green]")
                await asyncio.sleep(2)  # Rate limiting
        finally:
            await self.disconnect()

        # Remove duplicates by video ID
        seen_ids = set()
        unique_videos = []
        for video in all_videos:
            vid = video.get("id")
            if vid and vid not in seen_ids:
                seen_ids.add(vid)
                unique_videos.append(video)

        console.print(f"[bold green]Total unique videos: {len(unique_videos)}[/bold green]")
        return unique_videos

    def _parse_count(self, text: str) -> int:
        """Parse view/like count from text like '1.2M' or '500K'."""
        if not text:
            return 0

        # Find numbers with K/M suffix
        match = re.search(r'([\d.]+)\s*([KkMm])?', text)
        if not match:
            return 0

        num = float(match.group(1))
        suffix = match.group(2)

        if suffix and suffix.upper() == 'K':
            return int(num * 1000)
        elif suffix and suffix.upper() == 'M':
            return int(num * 1000000)
        return int(num)

    def parse_to_video(self, raw_data: dict) -> Optional[TikTokVideo]:
        """
        Parse raw scraped data into TikTokVideo object.

        Args:
            raw_data: Raw data from scraping

        Returns:
            TikTokVideo object or None
        """
        try:
            author_data = raw_data.get("author", {})
            if isinstance(author_data, str):
                username = author_data
                author_data = {"uniqueId": username}

            creator = TikTokCreator(
                user_id=str(author_data.get("id", "")),
                username=author_data.get("uniqueId", "unknown"),
                nickname=author_data.get("nickname", author_data.get("uniqueId", "")),
                follower_count=int(author_data.get("followerCount", 0) or 0),
                following_count=int(author_data.get("followingCount", 0) or 0),
                video_count=int(author_data.get("videoCount", 0) or 0),
                verified=author_data.get("verified", False),
            )

            # Parse creation time
            create_time = raw_data.get("createTime")
            if isinstance(create_time, (int, float)):
                created_at = datetime.fromtimestamp(create_time)
            else:
                created_at = datetime.utcnow() - timedelta(hours=6)

            # Extract hashtags from description
            desc = raw_data.get("desc", "")
            hashtags = re.findall(r'#(\w+)', desc)

            video = TikTokVideo(
                video_id=str(raw_data.get("id", "")),
                url=raw_data.get("url", ""),
                description=desc,
                creator=creator,
                view_count=int(raw_data.get("playCount", 0) or 0),
                like_count=int(raw_data.get("diggCount", 0) or 0),
                comment_count=int(raw_data.get("commentCount", 0) or 0),
                share_count=int(raw_data.get("shareCount", 0) or 0),
                created_at=created_at,
                hashtags=hashtags,
            )

            return video

        except Exception as e:
            console.print(f"[yellow]Error parsing video: {e}[/yellow]")
            return None


async def run_scraper_test():
    """Test the browser scraper."""
    config = BrowserScraperConfig.from_env()
    scraper = TikTokBrowserScraper(config)

    videos = await scraper.search_fashion_videos(
        hashtags=["fashion", "ootd"],
        videos_per_hashtag=10
    )

    console.print(f"\n[bold]Scraped {len(videos)} videos[/bold]")
    for v in videos[:5]:
        console.print(f"  - {v.get('url', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(run_scraper_test())
