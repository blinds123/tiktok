"""
Advanced filtering module for TikTok fashion scraper.
Filters by location, gender, niche, and timing for optimal viral detection.
"""

import re
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum
from rich.console import Console

from models.video import TikTokVideo, TikTokCreator

console = Console()


class TargetLocation(Enum):
    """Supported target locations."""
    USA = "US"
    CANADA = "CA"
    UK = "GB"


class CreatorGender(Enum):
    """Creator gender classification."""
    FEMALE = "female"
    MALE = "male"
    UNKNOWN = "unknown"


@dataclass
class FilterConfig:
    """Configuration for content filtering."""
    # Location settings
    allowed_locations: list = field(default_factory=lambda: ["US", "CA", "GB"])

    # Gender settings
    target_gender: str = "female"

    # Timing settings (hours)
    max_video_age_hours: int = 24
    priority_window_hours: int = 6  # Videos in this window get priority

    # Follower settings
    min_followers: int = 50_000
    max_followers: int = 150_000

    # Niche settings
    required_niche: str = "fashion"

    # Viral thresholds
    viral_multiplier: float = 10.0
    early_viral_view_threshold: int = 50_000  # Min views for 6hr window


class LocationFilter:
    """Filter creators by geographic location."""

    # Location indicators in bio/username
    LOCATION_KEYWORDS = {
        "US": [
            "usa", "united states", "america", "american",
            "new york", "nyc", "la", "los angeles", "california", "cali",
            "texas", "tx", "florida", "miami", "chicago", "atlanta", "atl",
            "seattle", "boston", "denver", "phoenix", "houston", "dallas",
            "san francisco", "sf", "bay area", "philly", "philadelphia",
            "dc", "washington", "vegas", "portland", "nashville",
            "🇺🇸", "based in us", "us based", "american girl"
        ],
        "CA": [
            "canada", "canadian", "toronto", "vancouver", "montreal",
            "calgary", "ottawa", "edmonton", "winnipeg", "quebec",
            "ontario", "british columbia", "bc", "alberta",
            "🇨🇦", "based in canada", "canadian girl"
        ],
        "GB": [
            "uk", "united kingdom", "britain", "british", "england",
            "english", "london", "manchester", "birmingham", "liverpool",
            "leeds", "bristol", "glasgow", "edinburgh", "scotland",
            "scottish", "wales", "welsh", "belfast", "northern ireland",
            "🇬🇧", "based in uk", "british girl", "london girl"
        ]
    }

    @classmethod
    def detect_location(cls, creator: TikTokCreator) -> Optional[str]:
        """
        Detect creator's location from bio and username.

        Args:
            creator: TikTokCreator object

        Returns:
            Location code (US, CA, GB) or None if not detected
        """
        # Combine searchable text
        search_text = f"{creator.bio} {creator.username} {creator.nickname}".lower()

        for location_code, keywords in cls.LOCATION_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in search_text:
                    return location_code

        return None

    @classmethod
    def is_target_location(cls, creator: TikTokCreator, allowed_locations: list) -> bool:
        """Check if creator is in one of the target locations."""
        location = cls.detect_location(creator)
        return location in allowed_locations if location else False


class GenderFilter:
    """Filter creators by gender (targeting women fashion influencers)."""

    # Female indicators
    FEMALE_INDICATORS = [
        # Common female names in usernames
        "girl", "queen", "princess", "babe", "goddess", "diva", "lady",
        "mama", "mom", "mum", "sister", "sis", "her", "she", "woman",
        "fem", "feminine", "girly", "wifey", "wife", "daughter",

        # Female fashion terms
        "fashionista", "stylist", "beauty", "glam", "glamour",
        "makeup", "skincare", "nails", "lashes", "hair",

        # Female-specific content indicators
        "grwm", "get ready with me", "outfit of the day", "ootd",
        "closet", "wardrobe", "dress", "heels", "purse", "handbag",

        # Pronouns and self-references
        "she/her", "(she)", "♀", "👸", "💅", "💄", "👗", "👠", "👛",
        "💋", "🎀", "🌸", "💖", "👩",

        # Common female name patterns
        "jessica", "ashley", "emma", "olivia", "sophia", "mia",
        "isabella", "charlotte", "amelia", "harper", "evelyn",
        "abigail", "emily", "elizabeth", "sofia", "avery",
        "ella", "scarlett", "grace", "chloe", "victoria",
        "madison", "luna", "penelope", "layla", "riley",
        "zoey", "nora", "lily", "eleanor", "hannah",
        "lillian", "addison", "aubrey", "ellie", "stella",
        "natalie", "zoe", "leah", "hazel", "violet",
        "aurora", "savannah", "audrey", "brooklyn", "bella",
        "claire", "skylar", "lucy", "paisley", "everly",
        "anna", "caroline", "nova", "genesis", "emilia",
        "kennedy", "samantha", "maya", "willow", "kinsley",
        "naomi", "aaliyah", "elena", "sarah", "ariana",
        "allison", "gabriella", "alice", "madelyn", "cora",
        "ruby", "eva", "serenity", "autumn", "adeline",
        "hailey", "gianna", "valentina", "isla", "eliana",
        "quinn", "nevaeh", "ivy", "sadie", "piper",
    ]

    # Male indicators (to exclude)
    MALE_INDICATORS = [
        "guy", "boy", "man", "men", "king", "prince", "bro", "brother",
        "dad", "father", "son", "husband", "boyfriend", "mr", "sir",
        "dude", "he/him", "(he)", "♂", "🤴", "👨", "🧔",
        "mens fashion", "men's style", "menswear",
    ]

    @classmethod
    def detect_gender(cls, creator: TikTokCreator, video_hashtags: list = None) -> CreatorGender:
        """
        Detect creator's gender from bio, username, and content.

        Args:
            creator: TikTokCreator object
            video_hashtags: Optional list of hashtags from their videos

        Returns:
            CreatorGender enum value
        """
        search_text = f"{creator.bio} {creator.username} {creator.nickname}".lower()

        if video_hashtags:
            search_text += " " + " ".join(video_hashtags).lower()

        female_score = 0
        male_score = 0

        for indicator in cls.FEMALE_INDICATORS:
            if indicator.lower() in search_text:
                female_score += 1

        for indicator in cls.MALE_INDICATORS:
            if indicator.lower() in search_text:
                male_score += 1

        # Require clear female signals
        if female_score > male_score and female_score >= 1:
            return CreatorGender.FEMALE
        elif male_score > female_score:
            return CreatorGender.MALE
        else:
            return CreatorGender.UNKNOWN

    @classmethod
    def is_female(cls, creator: TikTokCreator, video_hashtags: list = None) -> bool:
        """Check if creator is identified as female."""
        gender = cls.detect_gender(creator, video_hashtags)
        # Include UNKNOWN to not exclude potentially female creators
        return gender in [CreatorGender.FEMALE, CreatorGender.UNKNOWN]

    @classmethod
    def is_confirmed_female(cls, creator: TikTokCreator, video_hashtags: list = None) -> bool:
        """Check if creator is confirmed female (stricter filter)."""
        return cls.detect_gender(creator, video_hashtags) == CreatorGender.FEMALE


class FashionNicheFilter:
    """Filter for fashion-specific content."""

    FASHION_HASHTAGS = {
        # Core fashion hashtags
        "fashion", "fashiontiktok", "fashiontrends", "fashioninspo",
        "ootd", "outfitoftheday", "outfitinspo", "outfitideas",
        "style", "styleinspo", "styletips", "streetstyle",

        # Content types
        "grwm", "getreadywithme", "haul", "tryonhaul", "fashionhaul",
        "clothinghaul", "shopwithme", "whatiwore", "lookbook",
        "fitcheck", "outfitcheck",

        # Aesthetic styles
        "aesthetic", "aestheticoutfit", "y2k", "y2kfashion",
        "coquette", "coquetteaesthetic", "oldmoney", "quietluxury",
        "minimalist", "streetwear", "vintage", "thrift",

        # Women's specific
        "womensfashion", "girlsfashion", "womenstyle",
        "dress", "dresses", "skirt", "heels", "handbag",
    }

    FASHION_KEYWORDS = [
        "outfit", "dress", "wearing", "styled", "fashion",
        "clothes", "clothing", "wardrobe", "closet", "look",
        "fit", "drip", "slay", "serve", "aesthetic",
        "try on", "haul", "shopping", "bought", "purchased",
    ]

    @classmethod
    def is_fashion_content(cls, video: TikTokVideo) -> bool:
        """
        Check if video is fashion-related content.

        Args:
            video: TikTokVideo object

        Returns:
            True if fashion content, False otherwise
        """
        # Check hashtags
        video_hashtags = [h.lower().replace("#", "") for h in video.hashtags]
        if any(tag in cls.FASHION_HASHTAGS for tag in video_hashtags):
            return True

        # Check description
        description_lower = video.description.lower()
        if any(keyword in description_lower for keyword in cls.FASHION_KEYWORDS):
            return True

        return False

    @classmethod
    def calculate_fashion_relevance(cls, video: TikTokVideo) -> float:
        """
        Calculate how relevant the video is to fashion (0-100).

        Args:
            video: TikTokVideo object

        Returns:
            Fashion relevance score (0-100)
        """
        score = 0.0

        video_hashtags = [h.lower().replace("#", "") for h in video.hashtags]
        description_lower = video.description.lower()

        # Hashtag matches (up to 50 points)
        hashtag_matches = sum(1 for tag in video_hashtags if tag in cls.FASHION_HASHTAGS)
        score += min(hashtag_matches * 10, 50)

        # Keyword matches (up to 30 points)
        keyword_matches = sum(1 for kw in cls.FASHION_KEYWORDS if kw in description_lower)
        score += min(keyword_matches * 6, 30)

        # Creator bio fashion indicators (up to 20 points)
        if video.creator.bio:
            bio_lower = video.creator.bio.lower()
            bio_fashion_terms = ["fashion", "style", "outfit", "beauty", "model", "influencer"]
            bio_matches = sum(1 for term in bio_fashion_terms if term in bio_lower)
            score += min(bio_matches * 5, 20)

        return min(score, 100)


class EarlyViralFilter:
    """
    Filter optimized for catching videos within 6 hours of posting.
    This is the PRIORITY window for viral detection.
    """

    @classmethod
    def get_video_age_hours(cls, video: TikTokVideo) -> float:
        """Get video age in hours."""
        delta = datetime.utcnow() - video.created_at
        return delta.total_seconds() / 3600

    @classmethod
    def is_in_priority_window(cls, video: TikTokVideo, window_hours: int = 6) -> bool:
        """
        Check if video is within the priority detection window.

        Args:
            video: TikTokVideo object
            window_hours: Priority window in hours (default 6)

        Returns:
            True if video is within priority window
        """
        return cls.get_video_age_hours(video) <= window_hours

    @classmethod
    def calculate_early_viral_score(cls, video: TikTokVideo) -> float:
        """
        Calculate early viral potential score for videos under 6 hours.

        This uses aggressive thresholds because we want to catch
        viral content BEFORE it peaks.

        Args:
            video: TikTokVideo object

        Returns:
            Early viral score (0-100)
        """
        age_hours = cls.get_video_age_hours(video)

        if age_hours <= 0:
            return 0

        # Views per hour (velocity)
        views_per_hour = video.view_count / age_hours

        # Engagement per hour
        total_engagement = video.like_count + video.comment_count + video.share_count
        engagement_per_hour = total_engagement / age_hours

        score = 0.0

        # Ultra early (0-2 hours) - HIGHEST PRIORITY
        if age_hours <= 2:
            if views_per_hour >= 50_000:  # 100k views in 2 hours
                score = 100
            elif views_per_hour >= 25_000:  # 50k views in 2 hours
                score = 90
            elif views_per_hour >= 10_000:  # 20k views in 2 hours
                score = 80
            elif views_per_hour >= 5_000:  # 10k views in 2 hours
                score = 70
            else:
                score = min(views_per_hour / 500, 60)

        # Early (2-6 hours) - HIGH PRIORITY
        elif age_hours <= 6:
            if views_per_hour >= 30_000:  # 180k+ views in 6 hours
                score = 95
            elif views_per_hour >= 15_000:  # 90k+ views in 6 hours
                score = 85
            elif views_per_hour >= 8_000:  # 48k+ views in 6 hours
                score = 75
            elif views_per_hour >= 4_000:  # 24k+ views in 6 hours
                score = 65
            else:
                score = min(views_per_hour / 400, 55)

        # Standard window (6-24 hours)
        elif age_hours <= 24:
            if views_per_hour >= 20_000:
                score = 85
            elif views_per_hour >= 10_000:
                score = 75
            elif views_per_hour >= 5_000:
                score = 65
            else:
                score = min(views_per_hour / 500, 50)

        else:
            # Older than 24 hours - lower scores
            score = min(views_per_hour / 1000, 40)

        # Engagement bonus (up to 15 points)
        if engagement_per_hour >= 5_000:
            score += 15
        elif engagement_per_hour >= 2_000:
            score += 10
        elif engagement_per_hour >= 500:
            score += 5

        return min(score, 100)

    @classmethod
    def classify_urgency(cls, video: TikTokVideo) -> str:
        """
        Classify the urgency level for acting on this video.

        Returns:
            "CRITICAL" - Act within minutes (0-2 hours, high velocity)
            "URGENT" - Act within hours (2-6 hours, high velocity)
            "HIGH" - Act today (6-12 hours, good velocity)
            "MEDIUM" - Monitor closely (12-24 hours)
            "LOW" - May have peaked (>24 hours)
        """
        age_hours = cls.get_video_age_hours(video)
        score = cls.calculate_early_viral_score(video)

        if age_hours <= 2 and score >= 70:
            return "CRITICAL"
        elif age_hours <= 6 and score >= 65:
            return "URGENT"
        elif age_hours <= 12 and score >= 60:
            return "HIGH"
        elif age_hours <= 24 and score >= 50:
            return "MEDIUM"
        else:
            return "LOW"


class ContentFilter:
    """
    Master filter combining all filtering criteria.
    Optimized for finding viral fashion content from women micro-influencers
    in USA, Canada, and UK within 6 hours of posting.
    """

    def __init__(self, config: FilterConfig = None):
        self.config = config or FilterConfig()
        self.location_filter = LocationFilter()
        self.gender_filter = GenderFilter()
        self.niche_filter = FashionNicheFilter()
        self.early_viral_filter = EarlyViralFilter()

    def apply_all_filters(self, videos: list[TikTokVideo]) -> list[TikTokVideo]:
        """
        Apply all filters to a list of videos.

        Args:
            videos: List of TikTokVideo objects

        Returns:
            Filtered list of videos matching all criteria
        """
        console.print(f"[blue]Starting filter pipeline with {len(videos)} videos...[/blue]")

        filtered = videos.copy()

        # 1. Filter by recency (24 hours max, prioritize 6 hours)
        filtered = [v for v in filtered
                   if self.early_viral_filter.get_video_age_hours(v) <= self.config.max_video_age_hours]
        console.print(f"  [dim]After recency filter: {len(filtered)} videos[/dim]")

        # 2. Filter by fashion niche
        filtered = [v for v in filtered if self.niche_filter.is_fashion_content(v)]
        console.print(f"  [dim]After fashion filter: {len(filtered)} videos[/dim]")

        # 3. Filter by follower count (micro-influencers)
        filtered = [v for v in filtered
                   if self.config.min_followers <= v.creator.follower_count <= self.config.max_followers]
        console.print(f"  [dim]After follower filter: {len(filtered)} videos[/dim]")

        # 4. Filter by gender (women only)
        if self.config.target_gender == "female":
            filtered = [v for v in filtered
                       if self.gender_filter.is_female(v.creator, v.hashtags)]
            console.print(f"  [dim]After gender filter: {len(filtered)} videos[/dim]")

        # 5. Filter by location (USA, Canada, UK)
        # Note: Location detection is best-effort based on bio
        location_filtered = [v for v in filtered
                           if self.location_filter.is_target_location(v.creator, self.config.allowed_locations)]

        # If location filtering removes too many, include unknowns
        if len(location_filtered) < len(filtered) * 0.3:
            console.print(f"  [yellow]Location data sparse, including unverified locations[/yellow]")
        else:
            filtered = location_filtered
            console.print(f"  [dim]After location filter: {len(filtered)} videos[/dim]")

        console.print(f"[green]Filter pipeline complete: {len(filtered)} videos passed[/green]")

        return filtered

    def score_and_rank(self, videos: list[TikTokVideo]) -> list[dict]:
        """
        Score and rank filtered videos by viral potential.
        Prioritizes videos in the 6-hour window.

        Args:
            videos: List of filtered TikTokVideo objects

        Returns:
            List of dicts with video, scores, and rankings
        """
        scored_videos = []

        for video in videos:
            age_hours = self.early_viral_filter.get_video_age_hours(video)
            early_viral_score = self.early_viral_filter.calculate_early_viral_score(video)
            fashion_relevance = self.niche_filter.calculate_fashion_relevance(video)
            urgency = self.early_viral_filter.classify_urgency(video)

            # Detect location
            location = self.location_filter.detect_location(video.creator)

            # Detect gender
            gender = self.gender_filter.detect_gender(video.creator, video.hashtags)

            # Calculate composite score
            # Heavily weight early viral score and fashion relevance
            composite_score = (
                early_viral_score * 0.50 +  # Early viral potential
                fashion_relevance * 0.25 +   # Fashion relevance
                video.engagement_rate * 2 +  # Engagement (scaled)
                (20 if age_hours <= 6 else 10 if age_hours <= 12 else 0)  # Recency bonus
            )

            scored_videos.append({
                "video": video,
                "age_hours": round(age_hours, 1),
                "early_viral_score": round(early_viral_score, 1),
                "fashion_relevance": round(fashion_relevance, 1),
                "composite_score": round(composite_score, 1),
                "urgency": urgency,
                "location": location or "Unknown",
                "gender": gender.value,
                "in_priority_window": age_hours <= 6,
            })

        # Sort by composite score (descending), then by age (ascending for newer first)
        scored_videos.sort(key=lambda x: (-x["composite_score"], x["age_hours"]))

        return scored_videos

    def get_priority_candidates(self, videos: list[TikTokVideo], limit: int = 20) -> list[dict]:
        """
        Get top priority viral candidates.

        This is the main method to use - it filters, scores, and returns
        the best candidates prioritizing the 6-hour window.

        Args:
            videos: List of TikTokVideo objects
            limit: Maximum number of results

        Returns:
            Top candidates with full scoring data
        """
        # Apply all filters
        filtered = self.apply_all_filters(videos)

        if not filtered:
            console.print("[yellow]No videos passed all filters[/yellow]")
            return []

        # Score and rank
        ranked = self.score_and_rank(filtered)

        # Separate priority window videos
        priority_window = [v for v in ranked if v["in_priority_window"]]
        outside_window = [v for v in ranked if not v["in_priority_window"]]

        console.print(f"\n[cyan]Found {len(priority_window)} videos in 6-hour priority window[/cyan]")
        console.print(f"[dim]Found {len(outside_window)} videos outside priority window[/dim]")

        # Prioritize 6-hour window videos, then fill with others
        results = priority_window[:limit]
        remaining_slots = limit - len(results)
        if remaining_slots > 0:
            results.extend(outside_window[:remaining_slots])

        return results[:limit]
