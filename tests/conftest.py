"""Pytest fixtures for TikTok scraper tests."""

import pytest
from datetime import datetime, timedelta
from models.video import TikTokCreator, TikTokVideo, ViralCandidate


@pytest.fixture
def mock_micro_influencer():
    """Create a mock micro-influencer creator."""
    return TikTokCreator(
        user_id="creator_123",
        username="fashionista_micro",
        nickname="Fashion Micro",
        follower_count=75_000,
        following_count=500,
        video_count=150,
        heart_count=1_500_000,
        avg_views=50_000.0,
        avatar_url="https://example.com/avatar.jpg",
        bio="Fashion enthusiast | Style tips daily",
        verified=False
    )


@pytest.fixture
def mock_mega_influencer():
    """Create a mock mega-influencer creator."""
    return TikTokCreator(
        user_id="creator_456",
        username="fashion_mega",
        nickname="Fashion Mega",
        follower_count=2_000_000,
        following_count=100,
        video_count=500,
        heart_count=50_000_000,
        avg_views=500_000.0,
        avatar_url="https://example.com/avatar2.jpg",
        bio="Fashion Icon | Brand Ambassador",
        verified=True
    )


@pytest.fixture
def mock_small_creator():
    """Create a mock small creator (below micro-influencer threshold)."""
    return TikTokCreator(
        user_id="creator_789",
        username="fashion_newbie",
        nickname="Fashion Newbie",
        follower_count=10_000,
        following_count=300,
        video_count=50,
        heart_count=100_000,
        avg_views=5_000.0,
        avatar_url="https://example.com/avatar3.jpg",
        bio="Just starting out",
        verified=False
    )


@pytest.fixture
def mock_viral_video(mock_micro_influencer):
    """Create a mock viral video."""
    return TikTokVideo(
        video_id="video_001",
        url="https://tiktok.com/@fashionista_micro/video/video_001",
        description="Check out this amazing outfit! #OOTD #Fashion #StreetStyle #Viral",
        creator=mock_micro_influencer,
        view_count=750_000,  # 15x creator average
        like_count=45_000,
        comment_count=2_500,
        share_count=8_000,
        created_at=datetime.utcnow() - timedelta(hours=6),
        duration=30,
        hashtags=["OOTD", "Fashion", "StreetStyle", "Viral"],
        music_title="Trending Sound 2024",
        music_author="DJ Fashion",
        thumbnail_url="https://example.com/thumb1.jpg"
    )


@pytest.fixture
def mock_normal_video(mock_micro_influencer):
    """Create a mock normal (non-viral) video."""
    return TikTokVideo(
        video_id="video_002",
        url="https://tiktok.com/@fashionista_micro/video/video_002",
        description="Daily vlog #DailyLife",
        creator=mock_micro_influencer,
        view_count=55_000,  # Just above creator average
        like_count=2_500,
        comment_count=150,
        share_count=200,
        created_at=datetime.utcnow() - timedelta(hours=48),
        duration=60,
        hashtags=["DailyLife"],
        music_title="Chill Beat",
        music_author="Lofi Artist",
        thumbnail_url="https://example.com/thumb2.jpg"
    )


@pytest.fixture
def mock_recent_video(mock_small_creator):
    """Create a mock recently posted video."""
    return TikTokVideo(
        video_id="video_003",
        url="https://tiktok.com/@fashion_newbie/video/video_003",
        description="New drop! #Fashion #NewCollection #Sneakers",
        creator=mock_small_creator,
        view_count=100_000,  # 20x creator average
        like_count=8_000,
        comment_count=500,
        share_count=1_200,
        created_at=datetime.utcnow() - timedelta(hours=2),
        duration=20,
        hashtags=["Fashion", "NewCollection", "Sneakers"],
        music_title="Hype Track",
        music_author="Beat Maker",
        thumbnail_url="https://example.com/thumb3.jpg"
    )


@pytest.fixture
def mock_old_video(mock_mega_influencer):
    """Create a mock old video (48+ hours)."""
    return TikTokVideo(
        video_id="video_004",
        url="https://tiktok.com/@fashion_mega/video/video_004",
        description="Throwback Thursday #TBT #Fashion",
        creator=mock_mega_influencer,
        view_count=300_000,  # Below creator average
        like_count=15_000,
        comment_count=800,
        share_count=1_500,
        created_at=datetime.utcnow() - timedelta(hours=96),
        duration=45,
        hashtags=["TBT", "Fashion"],
        music_title="Classic Song",
        music_author="Vintage Artist",
        thumbnail_url="https://example.com/thumb4.jpg"
    )


@pytest.fixture
def mock_fashion_video(mock_micro_influencer):
    """Create a mock fashion-focused video with product mentions."""
    return TikTokVideo(
        video_id="video_005",
        url="https://tiktok.com/@fashionista_micro/video/video_005",
        description="Obsessed with this Zara dress and Nike Air Force 1! #Fashion #OOTD #Zara #Nike #Sneakers #Streetwear",
        creator=mock_micro_influencer,
        view_count=500_000,
        like_count=30_000,
        comment_count=1_500,
        share_count=5_000,
        created_at=datetime.utcnow() - timedelta(hours=12),
        duration=25,
        hashtags=["Fashion", "OOTD", "Zara", "Nike", "Sneakers", "Streetwear"],
        music_title="Fashion Beat",
        music_author="Style Sounds",
        thumbnail_url="https://example.com/thumb5.jpg"
    )


@pytest.fixture
def mock_video_list(mock_viral_video, mock_normal_video, mock_recent_video, mock_old_video, mock_fashion_video):
    """Create a list of mock videos for testing."""
    return [
        mock_viral_video,
        mock_normal_video,
        mock_recent_video,
        mock_old_video,
        mock_fashion_video
    ]


@pytest.fixture
def sample_hashtag_data():
    """Sample hashtag data for testing."""
    return {
        "fashion_hashtags": [
            "#Fashion", "#OOTD", "#Style", "#StreetStyle", "#Outfit",
            "#FashionTrends", "#Streetwear", "#FashionInspo", "#StyleInspo",
            "#FashionBlogger", "#FashionTok", "#FashionStyle"
        ],
        "product_brands": [
            "Zara", "H&M", "Nike", "Adidas", "Shein", "Forever21",
            "Urban Outfitters", "ASOS", "Uniqlo", "Supreme", "Gucci", "Prada"
        ],
        "product_categories": [
            "dress", "jeans", "sneakers", "boots", "jacket", "coat",
            "t-shirt", "hoodie", "skirt", "pants", "bag", "accessories"
        ],
        "trend_categories": [
            "Streetwear", "Vintage", "Y2K", "Minimalist", "Maximalist",
            "Athleisure", "Business Casual", "Cottagecore", "Dark Academia"
        ]
    }


@pytest.fixture
def mock_recent_videos_data():
    """Mock data for calculating average views."""
    return [
        {"view_count": 50_000},
        {"view_count": 75_000},
        {"view_count": 60_000},
        {"view_count": 45_000},
        {"view_count": 70_000}
    ]


@pytest.fixture
def mock_viral_candidate(mock_viral_video):
    """Create a mock viral candidate."""
    return ViralCandidate(
        video=mock_viral_video,
        viral_score=25.5,
        view_multiplier=15.0,
        detected_products=["Zara dress", "Nike sneakers"],
        fashion_keywords=["OOTD", "Fashion", "StreetStyle"],
        trend_category="Streetwear"
    )


@pytest.fixture
def mock_zero_view_video(mock_small_creator):
    """Create a mock video with zero views (edge case)."""
    return TikTokVideo(
        video_id="video_006",
        url="https://tiktok.com/@fashion_newbie/video/video_006",
        description="Just posted #Fashion",
        creator=mock_small_creator,
        view_count=0,
        like_count=0,
        comment_count=0,
        share_count=0,
        created_at=datetime.utcnow() - timedelta(minutes=5),
        duration=15,
        hashtags=["Fashion"],
        music_title="New Track",
        music_author="New Artist",
        thumbnail_url="https://example.com/thumb6.jpg"
    )
