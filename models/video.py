"""Data models for TikTok videos and creators."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class TikTokCreator:
    """Represents a TikTok creator/account."""

    user_id: str
    username: str
    nickname: str
    follower_count: int
    following_count: int = 0
    video_count: int = 0
    heart_count: int = 0
    avg_views: float = 0.0
    avatar_url: str = ""
    bio: str = ""
    verified: bool = False

    @property
    def is_micro_influencer(self) -> bool:
        """Check if creator is a micro-influencer (50k-150k followers)."""
        return 50_000 <= self.follower_count <= 150_000

    def calculate_avg_views(self, recent_videos: list) -> float:
        """Calculate average views from recent videos."""
        if not recent_videos:
            return 0.0
        total_views = sum(v.get("view_count", 0) for v in recent_videos)
        self.avg_views = total_views / len(recent_videos)
        return self.avg_views


@dataclass
class TikTokVideo:
    """Represents a TikTok video."""

    video_id: str
    url: str
    description: str
    creator: TikTokCreator
    view_count: int
    like_count: int
    comment_count: int
    share_count: int
    created_at: datetime
    duration: int = 0
    hashtags: list = field(default_factory=list)
    music_title: str = ""
    music_author: str = ""
    thumbnail_url: str = ""

    @property
    def engagement_rate(self) -> float:
        """Calculate engagement rate."""
        if self.view_count == 0:
            return 0.0
        return ((self.like_count + self.comment_count + self.share_count) / self.view_count) * 100

    @property
    def hours_since_posted(self) -> float:
        """Get hours since video was posted."""
        delta = datetime.utcnow() - self.created_at
        return delta.total_seconds() / 3600

    def is_viral_candidate(self, multiplier: float = 10.0) -> bool:
        """Check if video has viral potential based on views vs creator average."""
        if self.creator.avg_views == 0:
            return False
        return self.view_count >= (self.creator.avg_views * multiplier)

    @property
    def viral_score(self) -> float:
        """Calculate a viral score for ranking."""
        if self.creator.avg_views == 0:
            return 0.0
        view_multiplier = self.view_count / self.creator.avg_views
        # Factor in engagement and recency
        recency_bonus = max(0, (24 - self.hours_since_posted) / 24)
        return view_multiplier * (1 + self.engagement_rate / 100) * (1 + recency_bonus)


@dataclass
class ViralCandidate:
    """A video identified as having viral potential."""

    video: TikTokVideo
    viral_score: float
    view_multiplier: float
    detected_products: list = field(default_factory=list)
    fashion_keywords: list = field(default_factory=list)
    trend_category: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for output."""
        return {
            "video_url": self.video.url,
            "video_id": self.video.video_id,
            "description": self.video.description,
            "creator": {
                "username": self.video.creator.username,
                "followers": self.video.creator.follower_count,
                "avg_views": round(self.video.creator.avg_views, 0),
            },
            "metrics": {
                "views": self.video.view_count,
                "likes": self.video.like_count,
                "comments": self.video.comment_count,
                "shares": self.video.share_count,
                "engagement_rate": round(self.video.engagement_rate, 2),
            },
            "viral_analysis": {
                "viral_score": round(self.viral_score, 2),
                "view_multiplier": round(self.view_multiplier, 2),
                "hours_since_posted": round(self.video.hours_since_posted, 1),
            },
            "fashion": {
                "detected_products": self.detected_products,
                "keywords": self.fashion_keywords,
                "category": self.trend_category,
            },
            "hashtags": self.video.hashtags,
            "posted_at": self.video.created_at.isoformat(),
        }
