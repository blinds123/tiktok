"""Tests for viral trend detection functionality."""

import pytest
from datetime import datetime, timedelta
from models.video import TikTokCreator, TikTokVideo, ViralCandidate


class MockViralTrendDetector:
    """
    Mock implementation of ViralTrendDetector for testing.
    This simulates the expected behavior of the actual detector.
    """

    def __init__(self, min_followers=50_000, max_followers=150_000,
                 max_hours_old=24, viral_multiplier=10.0):
        self.min_followers = min_followers
        self.max_followers = max_followers
        self.max_hours_old = max_hours_old
        self.viral_multiplier = viral_multiplier

    def filter_by_follower_range(self, videos):
        """Filter videos by creator follower count."""
        return [
            v for v in videos
            if self.min_followers <= v.creator.follower_count <= self.max_followers
        ]

    def filter_by_recency(self, videos):
        """Filter videos by how recently they were posted."""
        return [
            v for v in videos
            if v.hours_since_posted <= self.max_hours_old
        ]

    def detect_viral_videos(self, videos):
        """Detect videos with viral potential."""
        viral_videos = []
        for video in videos:
            if video.is_viral_candidate(self.viral_multiplier):
                viral_videos.append(video)
        return viral_videos

    def rank_by_viral_score(self, videos):
        """Rank videos by their viral score (descending)."""
        return sorted(videos, key=lambda v: v.viral_score, reverse=True)

    def analyze_videos(self, videos):
        """
        Full analysis pipeline: filter, detect, and rank viral videos.
        Returns list of ViralCandidate objects.
        """
        # Apply filters
        filtered = self.filter_by_follower_range(videos)
        filtered = self.filter_by_recency(filtered)

        # Detect viral potential
        viral = self.detect_viral_videos(filtered)

        # Rank by score
        ranked = self.rank_by_viral_score(viral)

        # Convert to ViralCandidate objects
        candidates = []
        for video in ranked:
            view_multiplier = video.view_count / video.creator.avg_views if video.creator.avg_views > 0 else 0
            candidate = ViralCandidate(
                video=video,
                viral_score=video.viral_score,
                view_multiplier=view_multiplier
            )
            candidates.append(candidate)

        return candidates


@pytest.fixture
def detector():
    """Create a default viral trend detector."""
    return MockViralTrendDetector()


@pytest.fixture
def custom_detector():
    """Create a detector with custom parameters."""
    return MockViralTrendDetector(
        min_followers=10_000,
        max_followers=500_000,
        max_hours_old=48,
        viral_multiplier=5.0
    )


class TestViralTrendDetectorFiltering:
    """Tests for video filtering functionality."""

    def test_filter_by_follower_range_default(self, detector, mock_video_list):
        """Test filtering by default follower range (50k-150k)."""
        filtered = detector.filter_by_follower_range(mock_video_list)

        # Should only include micro-influencer videos
        for video in filtered:
            assert 50_000 <= video.creator.follower_count <= 150_000

    def test_filter_by_follower_range_excludes_small_creators(self, detector, mock_small_creator):
        """Test that small creators are filtered out."""
        video = TikTokVideo(
            video_id="small",
            url="https://test.com",
            description="Test",
            creator=mock_small_creator,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow()
        )

        filtered = detector.filter_by_follower_range([video])
        assert len(filtered) == 0

    def test_filter_by_follower_range_excludes_mega_influencers(self, detector, mock_mega_influencer):
        """Test that mega influencers are filtered out."""
        video = TikTokVideo(
            video_id="mega",
            url="https://test.com",
            description="Test",
            creator=mock_mega_influencer,
            view_count=1_000_000,
            like_count=50_000,
            comment_count=5_000,
            share_count=10_000,
            created_at=datetime.utcnow()
        )

        filtered = detector.filter_by_follower_range([video])
        assert len(filtered) == 0

    def test_filter_by_follower_range_custom(self, custom_detector, mock_video_list):
        """Test filtering with custom follower range."""
        filtered = custom_detector.filter_by_follower_range(mock_video_list)

        # Custom range is 10k-500k, should include more videos
        for video in filtered:
            assert 10_000 <= video.creator.follower_count <= 500_000

        # Should include both micro and small creators
        assert len(filtered) >= 2

    def test_filter_by_follower_range_empty_list(self, detector):
        """Test filtering with empty video list."""
        filtered = detector.filter_by_follower_range([])
        assert filtered == []

    def test_filter_by_follower_range_boundary_cases(self, detector):
        """Test filtering at exact follower count boundaries."""
        # Create creators at boundaries
        creator_at_min = TikTokCreator(
            user_id="min",
            username="min_user",
            nickname="Min",
            follower_count=50_000,
            avg_views=25_000.0
        )

        creator_at_max = TikTokCreator(
            user_id="max",
            username="max_user",
            nickname="Max",
            follower_count=150_000,
            avg_views=75_000.0
        )

        video_min = TikTokVideo(
            video_id="min_video",
            url="https://test.com/min",
            description="Min",
            creator=creator_at_min,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow()
        )

        video_max = TikTokVideo(
            video_id="max_video",
            url="https://test.com/max",
            description="Max",
            creator=creator_at_max,
            view_count=500_000,
            like_count=25_000,
            comment_count=2_500,
            share_count=5_000,
            created_at=datetime.utcnow()
        )

        filtered = detector.filter_by_follower_range([video_min, video_max])
        assert len(filtered) == 2

    def test_filter_by_recency_includes_recent(self, detector, mock_recent_video):
        """Test that recent videos (within 24 hours) are included."""
        filtered = detector.filter_by_recency([mock_recent_video])
        assert len(filtered) == 1
        assert filtered[0].video_id == mock_recent_video.video_id

    def test_filter_by_recency_excludes_old(self, detector, mock_old_video):
        """Test that old videos (>24 hours) are excluded."""
        filtered = detector.filter_by_recency([mock_old_video])
        assert len(filtered) == 0

    def test_filter_by_recency_mixed_ages(self, detector, mock_video_list):
        """Test filtering with videos of various ages."""
        filtered = detector.filter_by_recency(mock_video_list)

        # All filtered videos should be within 24 hours
        for video in filtered:
            assert video.hours_since_posted <= 24

    def test_filter_by_recency_custom_window(self, custom_detector, mock_old_video):
        """Test filtering with custom time window (48 hours)."""
        # Old video is 96 hours old, should still be excluded
        filtered = custom_detector.filter_by_recency([mock_old_video])
        assert len(filtered) == 0

        # But a 30-hour old video should be included
        creator = TikTokCreator(
            user_id="test",
            username="test",
            nickname="Test",
            follower_count=75_000,
            avg_views=50_000.0
        )
        video_30h = TikTokVideo(
            video_id="30h",
            url="https://test.com",
            description="Test",
            creator=creator,
            view_count=200_000,
            like_count=10_000,
            comment_count=1_000,
            share_count=2_000,
            created_at=datetime.utcnow() - timedelta(hours=30)
        )

        filtered = custom_detector.filter_by_recency([video_30h])
        assert len(filtered) == 1

    def test_filter_by_recency_just_posted(self, detector):
        """Test that newly posted videos are included."""
        creator = TikTokCreator(
            user_id="test",
            username="test",
            nickname="Test",
            follower_count=75_000,
            avg_views=50_000.0
        )
        video = TikTokVideo(
            video_id="new",
            url="https://test.com",
            description="Just posted!",
            creator=creator,
            view_count=1_000,
            like_count=100,
            comment_count=10,
            share_count=5,
            created_at=datetime.utcnow()
        )

        filtered = detector.filter_by_recency([video])
        assert len(filtered) == 1


class TestViralDetectionLogic:
    """Tests for viral video detection logic."""

    def test_detect_viral_videos_identifies_viral(self, detector, mock_viral_video):
        """Test that truly viral videos are detected."""
        viral = detector.detect_viral_videos([mock_viral_video])
        assert len(viral) == 1
        assert viral[0].video_id == mock_viral_video.video_id

    def test_detect_viral_videos_excludes_normal(self, detector, mock_normal_video):
        """Test that normal videos are not detected as viral."""
        viral = detector.detect_viral_videos([mock_normal_video])
        assert len(viral) == 0

    def test_detect_viral_videos_mixed_list(self, detector, mock_video_list):
        """Test detection with mixed viral and normal videos."""
        viral = detector.detect_viral_videos(mock_video_list)

        # All detected videos should have high view multipliers
        for video in viral:
            multiplier = video.view_count / video.creator.avg_views
            assert multiplier >= 10.0

    def test_detect_viral_videos_custom_multiplier(self, custom_detector, mock_video_list):
        """Test detection with custom viral multiplier (5x)."""
        viral = custom_detector.detect_viral_videos(mock_video_list)

        # With lower threshold, should detect more videos
        for video in viral:
            multiplier = video.view_count / video.creator.avg_views
            assert multiplier >= 5.0

    def test_detect_viral_videos_zero_avg_views(self, detector):
        """Test that videos from creators with 0 avg views are not detected."""
        creator = TikTokCreator(
            user_id="new",
            username="new_creator",
            nickname="New",
            follower_count=75_000,
            avg_views=0.0
        )
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="First video!",
            creator=creator,
            view_count=1_000_000,
            like_count=50_000,
            comment_count=5_000,
            share_count=10_000,
            created_at=datetime.utcnow()
        )

        viral = detector.detect_viral_videos([video])
        assert len(viral) == 0

    def test_detect_viral_videos_empty_list(self, detector):
        """Test detection with empty video list."""
        viral = detector.detect_viral_videos([])
        assert viral == []


class TestRankingAlgorithm:
    """Tests for video ranking functionality."""

    def test_rank_by_viral_score_descending(self, detector, mock_video_list):
        """Test that videos are ranked by viral score in descending order."""
        ranked = detector.rank_by_viral_score(mock_video_list)

        # Check that scores are in descending order
        for i in range(len(ranked) - 1):
            assert ranked[i].viral_score >= ranked[i + 1].viral_score

    def test_rank_by_viral_score_single_video(self, detector, mock_viral_video):
        """Test ranking with a single video."""
        ranked = detector.rank_by_viral_score([mock_viral_video])
        assert len(ranked) == 1
        assert ranked[0].video_id == mock_viral_video.video_id

    def test_rank_by_viral_score_empty_list(self, detector):
        """Test ranking with empty list."""
        ranked = detector.rank_by_viral_score([])
        assert ranked == []

    def test_rank_by_viral_score_highest_first(self, detector):
        """Test that highest scoring video is ranked first."""
        creator = TikTokCreator(
            user_id="test",
            username="test",
            nickname="Test",
            follower_count=75_000,
            avg_views=50_000.0
        )

        # Create videos with different viral scores
        low_score_video = TikTokVideo(
            video_id="low",
            url="https://test.com/low",
            description="Low",
            creator=creator,
            view_count=60_000,  # 1.2x
            like_count=3_000,
            comment_count=150,
            share_count=200,
            created_at=datetime.utcnow() - timedelta(hours=48)
        )

        high_score_video = TikTokVideo(
            video_id="high",
            url="https://test.com/high",
            description="High",
            creator=creator,
            view_count=1_000_000,  # 20x
            like_count=60_000,
            comment_count=5_000,
            share_count=15_000,
            created_at=datetime.utcnow() - timedelta(hours=3)
        )

        ranked = detector.rank_by_viral_score([low_score_video, high_score_video])
        assert ranked[0].video_id == "high"
        assert ranked[1].video_id == "low"


class TestFullAnalysisPipeline:
    """Tests for the complete analysis pipeline."""

    def test_analyze_videos_returns_viral_candidates(self, detector, mock_video_list):
        """Test that analysis returns ViralCandidate objects."""
        candidates = detector.analyze_videos(mock_video_list)

        for candidate in candidates:
            assert isinstance(candidate, ViralCandidate)
            assert candidate.viral_score > 0
            assert candidate.view_multiplier > 0

    def test_analyze_videos_filters_and_detects(self, detector, mock_video_list):
        """Test that analysis applies filters before detection."""
        candidates = detector.analyze_videos(mock_video_list)

        # All candidates should meet filtering criteria
        for candidate in candidates:
            video = candidate.video
            # Should be from micro-influencers
            assert 50_000 <= video.creator.follower_count <= 150_000
            # Should be recent
            assert video.hours_since_posted <= 24
            # Should be viral
            assert video.is_viral_candidate(10.0)

    def test_analyze_videos_sorted_by_score(self, detector, mock_video_list):
        """Test that results are sorted by viral score."""
        candidates = detector.analyze_videos(mock_video_list)

        if len(candidates) > 1:
            for i in range(len(candidates) - 1):
                assert candidates[i].viral_score >= candidates[i + 1].viral_score

    def test_analyze_videos_empty_list(self, detector):
        """Test analysis with empty video list."""
        candidates = detector.analyze_videos([])
        assert candidates == []

    def test_analyze_videos_no_matches(self, detector, mock_mega_influencer):
        """Test analysis when no videos meet criteria."""
        # Create a mega-influencer video (will be filtered out)
        video = TikTokVideo(
            video_id="mega",
            url="https://test.com",
            description="Test",
            creator=mock_mega_influencer,
            view_count=5_000_000,
            like_count=250_000,
            comment_count=25_000,
            share_count=50_000,
            created_at=datetime.utcnow()
        )

        candidates = detector.analyze_videos([video])
        assert len(candidates) == 0

    def test_analyze_videos_calculates_multiplier(self, detector, mock_viral_video):
        """Test that view multiplier is correctly calculated."""
        candidates = detector.analyze_videos([mock_viral_video])

        if candidates:
            candidate = candidates[0]
            expected_multiplier = mock_viral_video.view_count / mock_viral_video.creator.avg_views
            assert abs(candidate.view_multiplier - expected_multiplier) < 0.1

    def test_analyze_videos_preserves_video_data(self, detector, mock_viral_video):
        """Test that original video data is preserved in candidates."""
        candidates = detector.analyze_videos([mock_viral_video])

        if candidates:
            candidate = candidates[0]
            assert candidate.video.video_id == mock_viral_video.video_id
            assert candidate.video.url == mock_viral_video.url
            assert candidate.video.creator.username == mock_viral_video.creator.username

    def test_analyze_videos_with_custom_parameters(self, custom_detector, mock_video_list):
        """Test analysis with custom detector parameters."""
        candidates = custom_detector.analyze_videos(mock_video_list)

        # Custom detector has more lenient criteria
        for candidate in candidates:
            video = candidate.video
            # Wider follower range
            assert 10_000 <= video.creator.follower_count <= 500_000
            # Longer time window
            assert video.hours_since_posted <= 48
            # Lower viral threshold
            multiplier = video.view_count / video.creator.avg_views
            assert multiplier >= 5.0


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_detector_with_zero_videos(self, detector):
        """Test detector behavior with zero videos."""
        candidates = detector.analyze_videos([])
        assert isinstance(candidates, list)
        assert len(candidates) == 0

    def test_detector_with_invalid_time_range(self):
        """Test detector with negative time range."""
        detector = MockViralTrendDetector(max_hours_old=-1)
        creator = TikTokCreator(
            user_id="test",
            username="test",
            nickname="Test",
            follower_count=75_000,
            avg_views=50_000.0
        )
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="Test",
            creator=creator,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow()
        )

        # Should filter out all videos (none can be negative hours old)
        filtered = detector.filter_by_recency([video])
        assert len(filtered) == 0

    def test_detector_with_inverted_follower_range(self):
        """Test detector with min > max followers."""
        detector = MockViralTrendDetector(min_followers=150_000, max_followers=50_000)
        creator = TikTokCreator(
            user_id="test",
            username="test",
            nickname="Test",
            follower_count=75_000,
            avg_views=50_000.0
        )
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="Test",
            creator=creator,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow()
        )

        # Should filter out all videos
        filtered = detector.filter_by_follower_range([video])
        assert len(filtered) == 0

    def test_detector_with_zero_multiplier(self):
        """Test detector with zero viral multiplier."""
        detector = MockViralTrendDetector(viral_multiplier=0.0)
        creator = TikTokCreator(
            user_id="test",
            username="test",
            nickname="Test",
            follower_count=75_000,
            avg_views=50_000.0
        )
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="Test",
            creator=creator,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow()
        )

        # Any video should be considered viral with 0 multiplier
        viral = detector.detect_viral_videos([video])
        assert len(viral) == 1
