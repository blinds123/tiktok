"""TikTok-specific scraping logic using Bright Data."""

import re
from datetime import datetime, timedelta
from typing import Optional
from rich.console import Console

from .bright_data_client import BrightDataClient, BrightDataConfig
from models.video import TikTokVideo, TikTokCreator

console = Console()


# Fashion-related hashtags to search for
FASHION_HASHTAGS = [
    "fashion", "fashiontiktok", "ootd", "outfit", "outfitinspo",
    "outfitoftheday", "fashiontrend", "trending", "style", "streetstyle",
    "streetwear", "grwm", "getreadywithme", "haul", "clothinghaul",
    "fashionhaul", "tryonhaul", "styleinspo", "lookbook", "fits",
    "fitcheck", "whatiwore", "fashionfinds", "thrifthaul", "thriftflip",
    "y2k", "y2kfashion", "aesthetic", "aestheticoutfit", "coquette",
    "oldmoney", "quietluxury", "capsulewardrobe", "minimalstyle",
    "maximalist", "vintagefashion", "sustainablefashion", "plussize",
    "plussizefashion", "mensfashion", "womensfashion", "teenfashion",
    "summerfashion", "winterfashion", "fallfashion", "springfashion",
    "workwear", "officestyle", "casualstyle", "partywear", "datenight",
    "vacationoutfit", "festivalfashion", "concertoutfit", "wedding",
    "weddingguest", "bridesmaid", "prom", "promoutfit", "graduation",
    "amazonfinds", "amazonfashion", "zarahaul", "sheinghaul", "shein",
    "zara", "hm", "uniqlo", "aritzia", "nordstrom", "princess polly",
]


class TikTokScraper:
    """Scraper for TikTok content using Bright Data."""

    # Bright Data TikTok dataset IDs (from their marketplace)
    DATASETS = {
        "hashtag_posts": "gd_lyclj2e041hb8cxmz7",  # TikTok Hashtag Posts
        "user_posts": "gd_lv5lz1cm28spcq1xx5",      # TikTok User Posts
        "user_profile": "gd_l1vikfnt1wgvvqz95w",    # TikTok User Profile
        "post_info": "gd_lyclj20il4r5helnj",        # TikTok Post Info
        "search": "gd_lwxkxvnf1cynvib9co",          # TikTok Search Results
        "comments": "gd_lyclj2el25pvs3x845",        # TikTok Post Comments
    }

    def __init__(self, client: BrightDataClient, custom_dataset_id: Optional[str] = None):
        self.client = client
        self.custom_dataset_id = custom_dataset_id

    def search_by_hashtag(
        self,
        hashtags: list[str],
        limit_per_hashtag: int = 50,
    ) -> str:
        """
        Search TikTok posts by hashtags.

        Args:
            hashtags: List of hashtags to search
            limit_per_hashtag: Max results per hashtag

        Returns:
            Snapshot ID for tracking the collection job
        """
        dataset_id = self.custom_dataset_id or self.DATASETS["hashtag_posts"]

        inputs = []
        for tag in hashtags:
            # Remove # if present
            clean_tag = tag.lstrip("#")
            inputs.append({
                "hashtag": clean_tag,
                "num_of_posts": limit_per_hashtag,
            })

        console.print(f"[blue]Triggering hashtag search for {len(hashtags)} hashtags...[/blue]")
        result = self.client.trigger_dataset_collection(dataset_id, inputs)
        return result.get("snapshot_id")

    def search_by_keyword(
        self,
        keywords: list[str],
        limit_per_keyword: int = 50,
    ) -> str:
        """
        Search TikTok by keywords.

        Args:
            keywords: List of search keywords
            limit_per_keyword: Max results per keyword

        Returns:
            Snapshot ID for tracking
        """
        dataset_id = self.custom_dataset_id or self.DATASETS["search"]

        inputs = []
        for keyword in keywords:
            inputs.append({
                "keyword": keyword,
                "num_of_posts": limit_per_keyword,
            })

        console.print(f"[blue]Triggering keyword search for {len(keywords)} keywords...[/blue]")
        result = self.client.trigger_dataset_collection(dataset_id, inputs)
        return result.get("snapshot_id")

    def get_user_profile(self, usernames: list[str]) -> str:
        """
        Get profile information for users.

        Args:
            usernames: List of TikTok usernames

        Returns:
            Snapshot ID for tracking
        """
        dataset_id = self.custom_dataset_id or self.DATASETS["user_profile"]

        inputs = [{"url": f"https://www.tiktok.com/@{u}"} for u in usernames]

        console.print(f"[blue]Fetching profiles for {len(usernames)} users...[/blue]")
        result = self.client.trigger_dataset_collection(dataset_id, inputs)
        return result.get("snapshot_id")

    def get_user_posts(
        self,
        usernames: list[str],
        posts_per_user: int = 30,
    ) -> str:
        """
        Get recent posts from specific users.

        Args:
            usernames: List of TikTok usernames
            posts_per_user: Number of posts to fetch per user

        Returns:
            Snapshot ID for tracking
        """
        dataset_id = self.custom_dataset_id or self.DATASETS["user_posts"]

        inputs = []
        for username in usernames:
            inputs.append({
                "url": f"https://www.tiktok.com/@{username}",
                "num_of_posts": posts_per_user,
            })

        console.print(f"[blue]Fetching posts for {len(usernames)} users...[/blue]")
        result = self.client.trigger_dataset_collection(dataset_id, inputs)
        return result.get("snapshot_id")

    def get_post_details(self, video_urls: list[str]) -> str:
        """
        Get detailed information for specific posts.

        Args:
            video_urls: List of TikTok video URLs

        Returns:
            Snapshot ID for tracking
        """
        dataset_id = self.custom_dataset_id or self.DATASETS["post_info"]

        inputs = [{"url": url} for url in video_urls]

        console.print(f"[blue]Fetching details for {len(video_urls)} videos...[/blue]")
        result = self.client.trigger_dataset_collection(dataset_id, inputs)
        return result.get("snapshot_id")

    def wait_and_get_results(
        self,
        snapshot_id: str,
        timeout: int = 600,
    ) -> list[dict]:
        """
        Wait for a snapshot to complete and return results.

        Args:
            snapshot_id: The snapshot ID to wait for
            timeout: Maximum wait time in seconds

        Returns:
            List of result records
        """
        def progress_callback(state, status):
            console.print(f"[yellow]Collection status: {state}[/yellow]")

        return self.client.wait_for_snapshot(
            snapshot_id,
            timeout=timeout,
            poll_interval=15,
            progress_callback=progress_callback,
        )

    def parse_video_data(self, raw_data: dict) -> Optional[TikTokVideo]:
        """
        Parse raw API response into TikTokVideo object.

        Args:
            raw_data: Raw data from Bright Data API

        Returns:
            TikTokVideo object or None if parsing fails
        """
        try:
            # Handle different response formats from various datasets
            author_data = raw_data.get("author", {}) or {}

            # Extract creator info
            creator = TikTokCreator(
                user_id=str(author_data.get("id", raw_data.get("author_id", ""))),
                username=author_data.get("uniqueId", raw_data.get("author_name", "")),
                nickname=author_data.get("nickname", author_data.get("uniqueId", "")),
                follower_count=int(author_data.get("followerCount", raw_data.get("author_followers", 0)) or 0),
                following_count=int(author_data.get("followingCount", 0) or 0),
                video_count=int(author_data.get("videoCount", 0) or 0),
                heart_count=int(author_data.get("heartCount", 0) or 0),
                avatar_url=author_data.get("avatarLarger", ""),
                bio=author_data.get("signature", ""),
                verified=author_data.get("verified", False),
            )

            # Parse creation time
            create_time = raw_data.get("createTime", raw_data.get("create_time"))
            if isinstance(create_time, (int, float)):
                created_at = datetime.fromtimestamp(create_time)
            elif isinstance(create_time, str):
                try:
                    created_at = datetime.fromisoformat(create_time.replace("Z", "+00:00"))
                except:
                    created_at = datetime.utcnow()
            else:
                created_at = datetime.utcnow()

            # Extract hashtags
            hashtags = []
            challenges = raw_data.get("challenges", []) or []
            for challenge in challenges:
                if isinstance(challenge, dict):
                    hashtags.append(challenge.get("title", ""))
                elif isinstance(challenge, str):
                    hashtags.append(challenge)

            # Also extract from description
            desc = raw_data.get("desc", raw_data.get("description", ""))
            desc_hashtags = re.findall(r"#(\w+)", desc)
            hashtags.extend(desc_hashtags)
            hashtags = list(set(hashtags))  # Remove duplicates

            # Build video URL
            video_id = str(raw_data.get("id", raw_data.get("video_id", "")))
            username = creator.username
            video_url = raw_data.get("url", f"https://www.tiktok.com/@{username}/video/{video_id}")

            video = TikTokVideo(
                video_id=video_id,
                url=video_url,
                description=desc,
                creator=creator,
                view_count=int(raw_data.get("playCount", raw_data.get("play_count", raw_data.get("views", 0))) or 0),
                like_count=int(raw_data.get("diggCount", raw_data.get("like_count", raw_data.get("likes", 0))) or 0),
                comment_count=int(raw_data.get("commentCount", raw_data.get("comment_count", raw_data.get("comments", 0))) or 0),
                share_count=int(raw_data.get("shareCount", raw_data.get("share_count", raw_data.get("shares", 0))) or 0),
                created_at=created_at,
                duration=int(raw_data.get("duration", raw_data.get("video_duration", 0)) or 0),
                hashtags=hashtags,
                music_title=raw_data.get("music", {}).get("title", "") if isinstance(raw_data.get("music"), dict) else "",
                music_author=raw_data.get("music", {}).get("authorName", "") if isinstance(raw_data.get("music"), dict) else "",
                thumbnail_url=raw_data.get("cover", raw_data.get("thumbnail", "")),
            )

            return video

        except Exception as e:
            console.print(f"[red]Error parsing video data: {e}[/red]")
            return None

    def get_fashion_hashtags(self, include_custom: list[str] = None) -> list[str]:
        """Get list of fashion-related hashtags to search."""
        hashtags = FASHION_HASHTAGS.copy()
        if include_custom:
            hashtags.extend(include_custom)
        return list(set(hashtags))
