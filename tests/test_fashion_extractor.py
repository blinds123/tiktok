"""Tests for fashion content extraction and analysis."""

import pytest
from datetime import datetime, timedelta
from models.video import TikTokCreator, TikTokVideo


class MockFashionExtractor:
    """
    Mock implementation of FashionExtractor for testing.
    This simulates the expected behavior of fashion content detection.
    """

    def __init__(self, fashion_hashtags=None, product_brands=None, product_categories=None, trend_categories=None):
        self.fashion_hashtags = fashion_hashtags or [
            "fashion", "ootd", "style", "streetstyle", "outfit",
            "fashiontrends", "streetwear", "fashioninspo", "styleinspo"
        ]
        self.product_brands = product_brands or [
            "zara", "h&m", "nike", "adidas", "shein", "forever21",
            "urbanoutfitters", "asos", "uniqlo", "supreme"
        ]
        self.product_categories = product_categories or [
            "dress", "jeans", "sneakers", "boots", "jacket", "coat",
            "t-shirt", "hoodie", "skirt", "pants", "bag"
        ]
        self.trend_categories = trend_categories or {
            "streetwear": ["streetwear", "streetstyle", "urban", "hypebeast"],
            "vintage": ["vintage", "thrift", "retro", "90s", "y2k"],
            "minimalist": ["minimalist", "minimal", "simple", "clean"],
            "athleisure": ["athleisure", "athletic", "sportswear", "activewear"]
        }

    def is_fashion_content(self, video):
        """Determine if a video contains fashion content."""
        # Check description
        description_lower = video.description.lower()
        has_fashion_words = any(word in description_lower for word in self.fashion_hashtags)

        # Check hashtags
        hashtags_lower = [h.lower() for h in video.hashtags]
        has_fashion_hashtags = any(tag in hashtags_lower for tag in self.fashion_hashtags)

        return has_fashion_words or has_fashion_hashtags

    def extract_products(self, video):
        """Extract product mentions from video description and hashtags."""
        products = []
        text = (video.description + " " + " ".join(video.hashtags)).lower()

        # Extract brand mentions
        for brand in self.product_brands:
            if brand.lower() in text:
                products.append(brand)

        # Extract product categories
        for category in self.product_categories:
            if category.lower() in text:
                products.append(category)

        return list(set(products))  # Remove duplicates

    def categorize_trend(self, video):
        """Categorize the fashion trend shown in the video."""
        text = (video.description + " " + " ".join(video.hashtags)).lower()

        # Check each trend category
        for category, keywords in self.trend_categories.items():
            if any(keyword in text for keyword in keywords):
                return category.capitalize()

        return "General"

    def calculate_fashion_score(self, video):
        """
        Calculate a fashion relevance score (0-100).
        Based on number of fashion keywords, products, and engagement.
        """
        score = 0.0

        # Fashion keyword presence (up to 30 points)
        text = (video.description + " " + " ".join(video.hashtags)).lower()
        fashion_keyword_count = sum(1 for word in self.fashion_hashtags if word in text)
        score += min(fashion_keyword_count * 5, 30)

        # Product mentions (up to 30 points)
        products = self.extract_products(video)
        score += min(len(products) * 10, 30)

        # Engagement rate (up to 40 points)
        engagement_component = min(video.engagement_rate * 4, 40)
        score += engagement_component

        return min(score, 100.0)

    def extract_fashion_keywords(self, video):
        """Extract fashion-related keywords from video."""
        text = (video.description + " " + " ".join(video.hashtags)).lower()
        keywords = []

        for hashtag in self.fashion_hashtags:
            if hashtag in text:
                keywords.append(hashtag)

        return keywords

    def analyze_fashion_content(self, video):
        """
        Complete fashion analysis of a video.
        Returns dict with fashion data or None if not fashion content.
        """
        if not self.is_fashion_content(video):
            return None

        return {
            "is_fashion": True,
            "products": self.extract_products(video),
            "keywords": self.extract_fashion_keywords(video),
            "category": self.categorize_trend(video),
            "fashion_score": self.calculate_fashion_score(video)
        }


@pytest.fixture
def extractor(sample_hashtag_data):
    """Create a default fashion extractor."""
    return MockFashionExtractor(
        fashion_hashtags=[h.lower().replace("#", "") for h in sample_hashtag_data["fashion_hashtags"]],
        product_brands=[b.lower() for b in sample_hashtag_data["product_brands"]],
        product_categories=[c.lower() for c in sample_hashtag_data["product_categories"]],
        trend_categories={
            "streetwear": ["streetwear", "streetstyle", "urban"],
            "vintage": ["vintage", "thrift", "y2k"],
            "minimalist": ["minimalist", "minimal"],
            "athleisure": ["athleisure", "athletic", "sportswear"]
        }
    )


class TestFashionContentDetection:
    """Tests for detecting fashion content in videos."""

    def test_is_fashion_content_with_hashtags(self, extractor, mock_fashion_video):
        """Test fashion detection with fashion hashtags."""
        assert extractor.is_fashion_content(mock_fashion_video) is True

    def test_is_fashion_content_with_description(self, extractor, mock_micro_influencer):
        """Test fashion detection with fashion keywords in description."""
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="Check out my outfit of the day! Love this style",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=[]
        )
        assert extractor.is_fashion_content(video) is True

    def test_is_fashion_content_non_fashion_video(self, extractor, mock_micro_influencer):
        """Test that non-fashion content is correctly identified."""
        video = TikTokVideo(
            video_id="non_fashion",
            url="https://test.com",
            description="Cooking dinner tonight! #Food #Recipes",
            creator=mock_micro_influencer,
            view_count=50_000,
            like_count=2_500,
            comment_count=150,
            share_count=200,
            created_at=datetime.utcnow(),
            hashtags=["Food", "Recipes", "Cooking"]
        )
        assert extractor.is_fashion_content(video) is False

    def test_is_fashion_content_case_insensitive(self, extractor, mock_micro_influencer):
        """Test that fashion detection is case insensitive."""
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="FASHION and STYLE tips",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=["OOTD", "Style"]
        )
        assert extractor.is_fashion_content(video) is True

    def test_is_fashion_content_empty_description(self, extractor, mock_micro_influencer):
        """Test fashion detection with empty description but fashion hashtags."""
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=["Fashion", "Style"]
        )
        assert extractor.is_fashion_content(video) is True

    def test_is_fashion_content_no_hashtags(self, extractor, mock_micro_influencer):
        """Test fashion detection with no hashtags but fashion description."""
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="Loving this streetwear outfit",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=[]
        )
        assert extractor.is_fashion_content(video) is True


class TestProductExtraction:
    """Tests for extracting product mentions from videos."""

    def test_extract_products_with_brands(self, extractor, mock_fashion_video):
        """Test extraction of brand names from video."""
        products = extractor.extract_products(mock_fashion_video)
        assert "zara" in products
        assert "nike" in products

    def test_extract_products_with_categories(self, extractor, mock_fashion_video):
        """Test extraction of product categories."""
        products = extractor.extract_products(mock_fashion_video)
        assert "sneakers" in products

    def test_extract_products_multiple_mentions(self, extractor, mock_micro_influencer):
        """Test extraction with multiple product mentions."""
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="Wearing my Nike sneakers with Zara jeans and an H&M jacket!",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=["Nike", "Zara", "HM"]
        )
        products = extractor.extract_products(video)
        assert "nike" in products
        assert "zara" in products
        assert "h&m" in products
        assert "sneakers" in products
        assert "jeans" in products
        assert "jacket" in products

    def test_extract_products_no_products(self, extractor, mock_micro_influencer):
        """Test extraction when no products are mentioned."""
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="Just a random video",
            creator=mock_micro_influencer,
            view_count=50_000,
            like_count=2_500,
            comment_count=150,
            share_count=200,
            created_at=datetime.utcnow(),
            hashtags=["Random"]
        )
        products = extractor.extract_products(video)
        assert len(products) == 0

    def test_extract_products_case_insensitive(self, extractor, mock_micro_influencer):
        """Test that product extraction is case insensitive."""
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="NIKE SNEAKERS and ZARA dress",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=[]
        )
        products = extractor.extract_products(video)
        assert "nike" in products
        assert "zara" in products
        assert "sneakers" in products
        assert "dress" in products

    def test_extract_products_no_duplicates(self, extractor, mock_micro_influencer):
        """Test that duplicate products are removed."""
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="Nike Nike Nike sneakers sneakers",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=["Nike", "Sneakers"]
        )
        products = extractor.extract_products(video)
        # Should only have unique entries
        assert products.count("nike") == 1
        assert products.count("sneakers") == 1

    def test_extract_products_from_hashtags_only(self, extractor, mock_micro_influencer):
        """Test product extraction from hashtags when description is empty."""
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=["Zara", "Sneakers", "Nike"]
        )
        products = extractor.extract_products(video)
        assert len(products) > 0
        assert "zara" in products
        assert "nike" in products


class TestTrendCategorization:
    """Tests for categorizing fashion trends."""

    def test_categorize_trend_streetwear(self, extractor, mock_fashion_video):
        """Test categorization of streetwear content."""
        category = extractor.categorize_trend(mock_fashion_video)
        assert category == "Streetwear"

    def test_categorize_trend_vintage(self, extractor, mock_micro_influencer):
        """Test categorization of vintage content."""
        video = TikTokVideo(
            video_id="vintage",
            url="https://test.com",
            description="Thrift store haul! Loving these vintage vibes",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=["Vintage", "Thrift", "Y2K"]
        )
        category = extractor.categorize_trend(video)
        assert category == "Vintage"

    def test_categorize_trend_minimalist(self, extractor, mock_micro_influencer):
        """Test categorization of minimalist content."""
        video = TikTokVideo(
            video_id="minimal",
            url="https://test.com",
            description="Minimalist fashion essentials",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=["Minimalist", "Minimal"]
        )
        category = extractor.categorize_trend(video)
        assert category == "Minimalist"

    def test_categorize_trend_athleisure(self, extractor, mock_micro_influencer):
        """Test categorization of athleisure content."""
        video = TikTokVideo(
            video_id="athleisure",
            url="https://test.com",
            description="Athleisure outfit for running errands",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=["Athleisure", "Sportswear"]
        )
        category = extractor.categorize_trend(video)
        assert category == "Athleisure"

    def test_categorize_trend_general(self, extractor, mock_micro_influencer):
        """Test categorization when no specific trend is detected."""
        video = TikTokVideo(
            video_id="general",
            url="https://test.com",
            description="Fashion tips and tricks",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=["Fashion"]
        )
        category = extractor.categorize_trend(video)
        assert category == "General"

    def test_categorize_trend_case_insensitive(self, extractor, mock_micro_influencer):
        """Test that trend categorization is case insensitive."""
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="STREETWEAR and URBAN style",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=[]
        )
        category = extractor.categorize_trend(video)
        assert category == "Streetwear"

    def test_categorize_trend_multiple_matches(self, extractor, mock_micro_influencer):
        """Test trend categorization when multiple categories match (returns first match)."""
        video = TikTokVideo(
            video_id="multi",
            url="https://test.com",
            description="Streetwear meets vintage style",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=["Streetwear", "Vintage"]
        )
        category = extractor.categorize_trend(video)
        # Should return one of the matching categories
        assert category in ["Streetwear", "Vintage"]


class TestFashionScoring:
    """Tests for calculating fashion relevance scores."""

    def test_calculate_fashion_score_high_score(self, extractor, mock_fashion_video):
        """Test score calculation for highly relevant fashion content."""
        score = extractor.calculate_fashion_score(mock_fashion_video)
        assert score > 50.0
        assert score <= 100.0

    def test_calculate_fashion_score_many_keywords(self, extractor, mock_micro_influencer):
        """Test that more fashion keywords increase the score."""
        video = TikTokVideo(
            video_id="many_keywords",
            url="https://test.com",
            description="Fashion style outfit ootd streetwear",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=["Fashion", "Style", "OOTD", "Streetwear", "Outfit"]
        )
        score = extractor.calculate_fashion_score(video)
        assert score >= 30.0  # Should get keyword points

    def test_calculate_fashion_score_many_products(self, extractor, mock_micro_influencer):
        """Test that more product mentions increase the score."""
        video = TikTokVideo(
            video_id="many_products",
            url="https://test.com",
            description="Nike sneakers, Zara dress, H&M jacket, Adidas pants",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=["Fashion"]
        )
        score = extractor.calculate_fashion_score(video)
        assert score >= 30.0  # Should get product points

    def test_calculate_fashion_score_high_engagement(self, extractor, mock_micro_influencer):
        """Test that high engagement increases the score."""
        video = TikTokVideo(
            video_id="high_engagement",
            url="https://test.com",
            description="Fashion",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=50_000,  # 50% engagement
            comment_count=10_000,
            share_count=5_000,
            created_at=datetime.utcnow(),
            hashtags=["Fashion"]
        )
        score = extractor.calculate_fashion_score(video)
        # High engagement should contribute significantly
        assert score >= 40.0

    def test_calculate_fashion_score_max_100(self, extractor, mock_micro_influencer):
        """Test that fashion score doesn't exceed 100."""
        video = TikTokVideo(
            video_id="max_score",
            url="https://test.com",
            description="Fashion style outfit ootd streetwear Nike Zara Adidas dress jeans sneakers",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=50_000,
            comment_count=10_000,
            share_count=5_000,
            created_at=datetime.utcnow(),
            hashtags=["Fashion", "Style", "OOTD", "Nike", "Zara"]
        )
        score = extractor.calculate_fashion_score(video)
        assert score <= 100.0

    def test_calculate_fashion_score_low_score(self, extractor, mock_micro_influencer):
        """Test score calculation for minimal fashion content."""
        video = TikTokVideo(
            video_id="low_score",
            url="https://test.com",
            description="fashion",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=100,
            comment_count=10,
            share_count=5,
            created_at=datetime.utcnow(),
            hashtags=[]
        )
        score = extractor.calculate_fashion_score(video)
        assert score >= 0.0
        assert score < 20.0

    def test_calculate_fashion_score_zero_engagement(self, extractor, mock_micro_influencer):
        """Test score with zero engagement."""
        video = TikTokVideo(
            video_id="zero_engagement",
            url="https://test.com",
            description="Fashion outfit style",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=0,
            comment_count=0,
            share_count=0,
            created_at=datetime.utcnow(),
            hashtags=["Fashion"]
        )
        score = extractor.calculate_fashion_score(video)
        # Should still have keyword/hashtag points
        assert score > 0.0


class TestFashionKeywordExtraction:
    """Tests for extracting fashion keywords."""

    def test_extract_fashion_keywords(self, extractor, mock_fashion_video):
        """Test extraction of fashion keywords."""
        keywords = extractor.extract_fashion_keywords(mock_fashion_video)
        assert "fashion" in keywords
        assert "ootd" in keywords
        assert len(keywords) > 0

    def test_extract_fashion_keywords_from_hashtags(self, extractor, mock_micro_influencer):
        """Test keyword extraction from hashtags."""
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=["Fashion", "Style", "OOTD"]
        )
        keywords = extractor.extract_fashion_keywords(video)
        assert "fashion" in keywords
        assert "style" in keywords
        assert "ootd" in keywords

    def test_extract_fashion_keywords_no_fashion_content(self, extractor, mock_micro_influencer):
        """Test keyword extraction when no fashion content exists."""
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="Cooking tutorial",
            creator=mock_micro_influencer,
            view_count=50_000,
            like_count=2_500,
            comment_count=150,
            share_count=200,
            created_at=datetime.utcnow(),
            hashtags=["Cooking", "Food"]
        )
        keywords = extractor.extract_fashion_keywords(video)
        assert len(keywords) == 0

    def test_extract_fashion_keywords_case_insensitive(self, extractor, mock_micro_influencer):
        """Test that keyword extraction is case insensitive."""
        video = TikTokVideo(
            video_id="test",
            url="https://test.com",
            description="FASHION and STYLE",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=["OOTD"]
        )
        keywords = extractor.extract_fashion_keywords(video)
        assert "fashion" in keywords
        assert "style" in keywords


class TestCompleteAnalysis:
    """Tests for complete fashion content analysis."""

    def test_analyze_fashion_content_fashion_video(self, extractor, mock_fashion_video):
        """Test complete analysis of fashion video."""
        result = extractor.analyze_fashion_content(mock_fashion_video)

        assert result is not None
        assert result["is_fashion"] is True
        assert "products" in result
        assert "keywords" in result
        assert "category" in result
        assert "fashion_score" in result

    def test_analyze_fashion_content_non_fashion_video(self, extractor, mock_micro_influencer):
        """Test analysis returns None for non-fashion content."""
        video = TikTokVideo(
            video_id="non_fashion",
            url="https://test.com",
            description="Cooking video #Food #Recipes",
            creator=mock_micro_influencer,
            view_count=50_000,
            like_count=2_500,
            comment_count=150,
            share_count=200,
            created_at=datetime.utcnow(),
            hashtags=["Food", "Recipes"]
        )
        result = extractor.analyze_fashion_content(video)
        assert result is None

    def test_analyze_fashion_content_all_fields_present(self, extractor, mock_fashion_video):
        """Test that analysis includes all expected fields."""
        result = extractor.analyze_fashion_content(mock_fashion_video)

        assert "is_fashion" in result
        assert "products" in result
        assert "keywords" in result
        assert "category" in result
        assert "fashion_score" in result

        # Verify data types
        assert isinstance(result["is_fashion"], bool)
        assert isinstance(result["products"], list)
        assert isinstance(result["keywords"], list)
        assert isinstance(result["category"], str)
        assert isinstance(result["fashion_score"], float)

    def test_analyze_fashion_content_products_extracted(self, extractor, mock_fashion_video):
        """Test that products are extracted in analysis."""
        result = extractor.analyze_fashion_content(mock_fashion_video)

        assert len(result["products"]) > 0
        # Mock fashion video mentions Zara and Nike
        assert any("zara" in p or "nike" in p for p in result["products"])

    def test_analyze_fashion_content_keywords_extracted(self, extractor, mock_fashion_video):
        """Test that keywords are extracted in analysis."""
        result = extractor.analyze_fashion_content(mock_fashion_video)

        assert len(result["keywords"]) > 0
        # Should include fashion-related keywords
        assert any(k in result["keywords"] for k in ["fashion", "ootd", "streetstyle"])

    def test_analyze_fashion_content_category_assigned(self, extractor, mock_fashion_video):
        """Test that trend category is assigned."""
        result = extractor.analyze_fashion_content(mock_fashion_video)

        assert result["category"] != ""
        # Mock fashion video has streetwear hashtags
        assert result["category"] in ["Streetwear", "General"]

    def test_analyze_fashion_content_score_calculated(self, extractor, mock_fashion_video):
        """Test that fashion score is calculated."""
        result = extractor.analyze_fashion_content(mock_fashion_video)

        assert result["fashion_score"] >= 0.0
        assert result["fashion_score"] <= 100.0


class TestEdgeCases:
    """Tests for edge cases in fashion extraction."""

    def test_empty_description_and_hashtags(self, extractor, mock_micro_influencer):
        """Test with video that has empty description and no hashtags."""
        video = TikTokVideo(
            video_id="empty",
            url="https://test.com",
            description="",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=[]
        )

        assert extractor.is_fashion_content(video) is False
        products = extractor.extract_products(video)
        assert len(products) == 0
        keywords = extractor.extract_fashion_keywords(video)
        assert len(keywords) == 0

    def test_special_characters_in_description(self, extractor, mock_micro_influencer):
        """Test handling of special characters."""
        video = TikTokVideo(
            video_id="special",
            url="https://test.com",
            description="Fashion!!! Style??? OOTD... #Fashion #Style",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=["Fashion", "Style"]
        )

        assert extractor.is_fashion_content(video) is True
        keywords = extractor.extract_fashion_keywords(video)
        assert len(keywords) > 0

    def test_very_long_description(self, extractor, mock_micro_influencer):
        """Test with very long description."""
        long_description = "Fashion " * 100 + "Nike Zara dress sneakers"
        video = TikTokVideo(
            video_id="long",
            url="https://test.com",
            description=long_description,
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=[]
        )

        assert extractor.is_fashion_content(video) is True
        products = extractor.extract_products(video)
        assert len(products) > 0

    def test_unicode_characters(self, extractor, mock_micro_influencer):
        """Test handling of unicode characters."""
        video = TikTokVideo(
            video_id="unicode",
            url="https://test.com",
            description="Fashion ✨ Style 💫 OOTD 🔥",
            creator=mock_micro_influencer,
            view_count=100_000,
            like_count=5_000,
            comment_count=500,
            share_count=1_000,
            created_at=datetime.utcnow(),
            hashtags=["Fashion", "Style"]
        )

        assert extractor.is_fashion_content(video) is True
        keywords = extractor.extract_fashion_keywords(video)
        assert "fashion" in keywords
