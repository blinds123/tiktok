"""Tests for TikTok data models."""

import pytest
from datetime import datetime, timedelta
from models.video import TikTokCreator, TikTokVideo, ViralCandidate


class TestTikTokCreator:
    """Tests for TikTokCreator class."""

    def test_is_micro_influencer_true(self, mock_micro_influencer):
        """Test that a creator with 50k-150k followers is identified as micro-influencer."""
        assert mock_micro_influencer.is_micro_influencer is True
        assert mock_micro_influencer.follower_count == 75_000

    def test_is_micro_influencer_false_too_small(self, mock_small_creator):
        """Test that a creator with <50k followers is not a micro-influencer."""
        assert mock_small_creator.is_micro_influencer is False
        assert mock_small_creator.follower_count == 10_000

    def test_is_micro_influencer_false_too_large(self, mock_mega_influencer):
        """Test that a creator with >150k followers is not a micro-influencer."""
        assert mock_mega_influencer.is_micro_influencer is False
        assert mock_mega_influencer.follower_count == 2_000_000

    def test_is_micro_influencer_lower_boundary(self):
        """Test micro-influencer detection at lower boundary (50k)."""
        creator = TikTokCreator(
            user_id="test_1",
            username="test_user_1",
            nickname="Test User 1",
            follower_count=50_000
        )
        assert creator.is_micro_influencer is True

    def test_is_micro_influencer_upper_boundary(self):
        """Test micro-influencer detection at upper boundary (150k)."""
        creator = TikTokCreator(
            user_id="test_2",
            username="test_user_2",
            nickname="Test User 2",
            follower_count=150_000
        )
        assert creator.is_micro_influencer is True

    def test_is_micro_influencer_just_below_lower_boundary(self):
        """Test micro-influencer detection just below lower boundary (49,999)."""
        creator = TikTokCreator(
            user_id="test_3",
            username="test_user_3",
            nickname="Test User 3",
            follower_count=49_999
        )
        assert creator.is_micro_influencer is False

    def test_is_micro_influencer_just_above_upper_boundary(self):
        """Test micro-influencer detection just above upper boundary (150,001)."""
        creator = TikTokCreator(
            user_id="test_4",
            username="test_user_4",
            nickname="Test User 4",
            follower_count=150_001
        )
        assert creator.is_micro_influencer is False

    def test_calculate_avg_views_with_videos(self, mock_micro_influencer, mock_recent_videos_data):
        """Test average views calculation with valid video data."""
        avg = mock_micro_influencer.calculate_avg_views(mock_recent_videos_data)
        expected_avg = (50_000 + 75_000 + 60_000 + 45_000 + 70_000) / 5
        assert avg == expected_avg
        assert mock_micro_influencer.avg_views == expected_avg

    def test_calculate_avg_views_empty_list(self, mock_small_creator):
        """Test average views calculation with empty video list."""
        # Store original avg_views
        original_avg = mock_small_creator.avg_views
        avg = mock_small_creator.calculate_avg_views([])
        assert avg == 0.0
        # When list is empty, avg_views property should remain unchanged
        assert mock_small_creator.avg_views == original_avg

    def test_calculate_avg_views_single_video(self, mock_small_creator):
        """Test average views calculation with a single video."""
        videos = [{"view_count": 100_000}]
        avg = mock_small_creator.calculate_avg_views(videos)
        assert avg == 100_000.0
        assert mock_small_creator.avg_views == 100_000.0

    def test_calculate_avg_views_with_zero_views(self, mock_small_creator):
        """Test average views calculation with videos that have zero views."""
        videos = [{"view_count": 0}, {"view_count": 0}, {"view_count": 0}]
        avg = mock_small_creator.calculate_avg_views(videos)
        assert avg == 0.0

    def test_calculate_avg_views_mixed_counts(self, mock_small_creator):
        """Test average views calculation with mixed view counts."""
        videos = [
            {"view_count": 0},
            {"view_count": 100_000},
            {"view_count": 50_000}
        ]
        avg = mock_small_creator.calculate_avg_views(videos)
        assert avg == 50_000.0

    def test_creator_defaults(self):
        """Test that TikTokCreator has correct default values."""
        creator = TikTokCreator(
            user_id="test_id",
            username="test_user",
            nickname="Test",
            follower_count=1000
        )
        assert creator.following_count == 0
        assert creator.video_count == 0
        assert creator.heart_count == 0
        assert creator.avg_views == 0.0
        assert creator.avatar_url == ""
        assert creator.bio == ""
        assert creator.verified is False


class TestTikTokVideo:
    """Tests for TikTokVideo class."""

    def test_engagement_rate_calculation(self, mock_viral_video):
        """Test engagement rate calculation for a viral video."""
        # Engagement = (likes + comments + shares) / views * 100
        # (45,000 + 2,500 + 8,000) / 750,000 * 100 = 7.4%
        expected_rate = ((45_000 + 2_500 + 8_000) / 750_000) * 100
        assert abs(mock_viral_video.engagement_rate - expected_rate) < 0.01

    def test_engagement_rate_zero_views(self, mock_zero_view_video):
        """Test engagement rate calculation with zero views."""
        assert mock_zero_view_video.engagement_rate == 0.0

    def test_engagement_rate_high_engagement(self):
        """Test engagement rate with very high engagement."""
        creator = TikTokCreator(
            user_id="test",
            username="test",
            nickname="Test",
            follower_count=1000,
            avg_views=10_000.0
        )
        video = TikTokVideo(
            video_id="test_video",
            url="https://test.com",
            description="Test",
            creator=creator,
            view_count=100_000,
            like_count=50_000,  # 50% like rate
            comment_count=10_000,  # 10% comment rate
            share_count=5_000,  # 5% share rate
            created_at=datetime.utcnow()
        )
        # Total engagement: 65%
        expected_rate = ((50_000 + 10_000 + 5_000) / 100_000) * 100
        assert video.engagement_rate == expected_rate
        assert video.engagement_rate == 65.0

    def test_hours_since_posted_recent(self, mock_recent_video):
        """Test hours since posted for a recent video (2 hours old)."""
        hours = mock_recent_video.hours_since_posted
        assert 1.5 <= hours <= 2.5  # Allow some variance due to test execution time

    def test_hours_since_posted_old(self, mock_old_video):
        """Test hours since posted for an old video (96 hours old)."""
        hours = mock_old_video.hours_since_posted
        assert 95.5 <= hours <= 96.5  # Allow some variance

    def test_hours_since_posted_just_posted(self):
        """Test hours since posted for a video posted right now."""
        creator = TikTokCreator(
            user_id="test",
            username="test",
            nickname="Test",
            follower_count=1000
        )
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="Test",
            creator=creator,
            view_count=1000,
            like_count=100,
            comment_count=10,
            share_count=5,
            created_at=datetime.utcnow()
        )
        hours = video.hours_since_posted
        assert hours < 0.1  # Less than 6 minutes

    def test_is_viral_candidate_true(self, mock_viral_video):
        """Test viral candidate detection for a truly viral video."""
        # Video has 750k views, creator avg is 50k, ratio is 15x
        assert mock_viral_video.is_viral_candidate(multiplier=10.0) is True

    def test_is_viral_candidate_false(self, mock_normal_video):
        """Test viral candidate detection for a normal video."""
        # Video has 55k views, creator avg is 50k, ratio is 1.1x
        assert mock_normal_video.is_viral_candidate(multiplier=10.0) is False

    def test_is_viral_candidate_boundary(self, mock_micro_influencer):
        """Test viral candidate detection at exact boundary."""
        # Creator avg is 50k, video with exactly 500k views (10x)
        video = TikTokVideo(
            video_id="boundary_test",
            url="https://test.com",
            description="Test",
            creator=mock_micro_influencer,
            view_count=500_000,  # Exactly 10x
            like_count=10_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow()
        )
        assert video.is_viral_candidate(multiplier=10.0) is True

    def test_is_viral_candidate_just_below_boundary(self, mock_micro_influencer):
        """Test viral candidate detection just below boundary."""
        video = TikTokVideo(
            video_id="below_boundary",
            url="https://test.com",
            description="Test",
            creator=mock_micro_influencer,
            view_count=499_999,  # Just below 10x
            like_count=10_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow()
        )
        assert video.is_viral_candidate(multiplier=10.0) is False

    def test_is_viral_candidate_zero_avg_views(self):
        """Test viral candidate detection when creator has zero avg views."""
        creator = TikTokCreator(
            user_id="test",
            username="test",
            nickname="Test",
            follower_count=1000,
            avg_views=0.0
        )
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="Test",
            creator=creator,
            view_count=1_000_000,
            like_count=50_000,
            comment_count=1_000,
            share_count=500,
            created_at=datetime.utcnow()
        )
        assert video.is_viral_candidate(multiplier=10.0) is False

    def test_is_viral_candidate_custom_multiplier(self, mock_recent_video):
        """Test viral candidate detection with custom multiplier."""
        # Video has 100k views, creator avg is 5k, ratio is 20x
        assert mock_recent_video.is_viral_candidate(multiplier=15.0) is True
        assert mock_recent_video.is_viral_candidate(multiplier=25.0) is False

    def test_viral_score_calculation(self, mock_viral_video):
        """Test viral score calculation."""
        score = mock_viral_video.viral_score
        # Should be > 0 for a viral video
        assert score > 0
        # Video is 6 hours old, so should have recency bonus
        assert score > 15.0  # Base multiplier alone is 15x

    def test_viral_score_zero_avg_views(self, mock_zero_view_video):
        """Test viral score when creator has zero avg views."""
        mock_zero_view_video.creator.avg_views = 0.0
        assert mock_zero_view_video.viral_score == 0.0

    def test_viral_score_recent_vs_old(self, mock_micro_influencer):
        """Test that recent videos get higher viral scores than old ones."""
        recent_video = TikTokVideo(
            video_id="recent",
            url="https://test.com/recent",
            description="Recent",
            creator=mock_micro_influencer,
            view_count=500_000,
            like_count=25_000,
            comment_count=1_000,
            share_count=3_000,
            created_at=datetime.utcnow() - timedelta(hours=2)
        )

        old_video = TikTokVideo(
            video_id="old",
            url="https://test.com/old",
            description="Old",
            creator=mock_micro_influencer,
            view_count=500_000,
            like_count=25_000,
            comment_count=1_000,
            share_count=3_000,
            created_at=datetime.utcnow() - timedelta(hours=48)
        )

        assert recent_video.viral_score > old_video.viral_score

    def test_viral_score_components(self, mock_micro_influencer):
        """Test that viral score factors in views, engagement, and recency."""
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="Test",
            creator=mock_micro_influencer,
            view_count=500_000,  # 10x multiplier
            like_count=25_000,
            comment_count=1_000,
            share_count=3_000,
            created_at=datetime.utcnow() - timedelta(hours=12)
        )

        view_multiplier = video.view_count / video.creator.avg_views
        engagement_factor = 1 + video.engagement_rate / 100
        recency_bonus = max(0, (24 - video.hours_since_posted) / 24)
        expected_score = view_multiplier * engagement_factor * (1 + recency_bonus)

        assert abs(video.viral_score - expected_score) < 0.1

    def test_video_defaults(self):
        """Test that TikTokVideo has correct default values."""
        creator = TikTokCreator(
            user_id="test",
            username="test",
            nickname="Test",
            follower_count=1000
        )
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="Test",
            creator=creator,
            view_count=1000,
            like_count=100,
            comment_count=10,
            share_count=5,
            created_at=datetime.utcnow()
        )
        assert video.duration == 0
        assert video.hashtags == []
        assert video.music_title == ""
        assert video.music_author == ""
        assert video.thumbnail_url == ""


class TestViralCandidate:
    """Tests for ViralCandidate class."""

    def test_to_dict_structure(self, mock_viral_candidate):
        """Test that to_dict returns correct structure."""
        result = mock_viral_candidate.to_dict()

        # Check top-level keys
        assert "video_url" in result
        assert "video_id" in result
        assert "description" in result
        assert "creator" in result
        assert "metrics" in result
        assert "viral_analysis" in result
        assert "fashion" in result
        assert "hashtags" in result
        assert "posted_at" in result

    def test_to_dict_creator_info(self, mock_viral_candidate):
        """Test that creator information is correctly formatted."""
        result = mock_viral_candidate.to_dict()
        creator = result["creator"]

        assert creator["username"] == "fashionista_micro"
        assert creator["followers"] == 75_000
        assert creator["avg_views"] == 50_000.0

    def test_to_dict_metrics(self, mock_viral_candidate):
        """Test that video metrics are correctly formatted."""
        result = mock_viral_candidate.to_dict()
        metrics = result["metrics"]

        assert metrics["views"] == 750_000
        assert metrics["likes"] == 45_000
        assert metrics["comments"] == 2_500
        assert metrics["shares"] == 8_000
        assert "engagement_rate" in metrics

    def test_to_dict_viral_analysis(self, mock_viral_candidate):
        """Test that viral analysis data is correctly formatted."""
        result = mock_viral_candidate.to_dict()
        analysis = result["viral_analysis"]

        assert analysis["viral_score"] == 25.5
        assert analysis["view_multiplier"] == 15.0
        assert "hours_since_posted" in analysis

    def test_to_dict_fashion_data(self, mock_viral_candidate):
        """Test that fashion data is correctly formatted."""
        result = mock_viral_candidate.to_dict()
        fashion = result["fashion"]

        assert fashion["detected_products"] == ["Zara dress", "Nike sneakers"]
        assert fashion["keywords"] == ["OOTD", "Fashion", "StreetStyle"]
        assert fashion["category"] == "Streetwear"

    def test_to_dict_hashtags(self, mock_viral_candidate):
        """Test that hashtags are included."""
        result = mock_viral_candidate.to_dict()
        assert "OOTD" in result["hashtags"]
        assert "Fashion" in result["hashtags"]
        assert len(result["hashtags"]) == 4

    def test_to_dict_empty_fashion_data(self, mock_viral_video):
        """Test to_dict with no fashion data."""
        candidate = ViralCandidate(
            video=mock_viral_video,
            viral_score=20.0,
            view_multiplier=15.0,
            detected_products=[],
            fashion_keywords=[],
            trend_category=""
        )
        result = candidate.to_dict()

        assert result["fashion"]["detected_products"] == []
        assert result["fashion"]["keywords"] == []
        assert result["fashion"]["category"] == ""

    def test_to_dict_rounding(self, mock_viral_video):
        """Test that numeric values are properly rounded."""
        candidate = ViralCandidate(
            video=mock_viral_video,
            viral_score=23.456789,
            view_multiplier=15.987654,
            detected_products=[],
            fashion_keywords=[],
            trend_category=""
        )
        result = candidate.to_dict()

        # Check rounding
        assert result["viral_analysis"]["viral_score"] == 23.46
        assert result["viral_analysis"]["view_multiplier"] == 15.99
        assert isinstance(result["creator"]["avg_views"], (int, float))
        assert isinstance(result["metrics"]["engagement_rate"], (int, float))

    def test_to_dict_datetime_format(self, mock_viral_candidate):
        """Test that datetime is converted to ISO format."""
        result = mock_viral_candidate.to_dict()
        posted_at = result["posted_at"]

        # Should be ISO format string
        assert isinstance(posted_at, str)
        # Should be parseable back to datetime
        parsed_dt = datetime.fromisoformat(posted_at.replace('Z', '+00:00'))
        assert isinstance(parsed_dt, datetime)

    def test_viral_candidate_defaults(self, mock_viral_video):
        """Test ViralCandidate default values."""
        candidate = ViralCandidate(
            video=mock_viral_video,
            viral_score=20.0,
            view_multiplier=10.0
        )

        assert candidate.detected_products == []
        assert candidate.fashion_keywords == []
        assert candidate.trend_category == ""
