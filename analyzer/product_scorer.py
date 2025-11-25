"""Product Opportunity Scorer for TikTok Fashion Scraper.

Expert-driven product analysis based on $10M+ TikTok media buying experience.
Identifies high-potential products with strong purchase intent and sellability.
"""

import re
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from models.video import TikTokVideo, ViralCandidate

console = Console()


class ProfitPotential(Enum):
    """Profit potential categories for products."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ProductCategory(Enum):
    """High-performing product categories on TikTok (ranked by profitability)."""
    SHAPEWEAR = "shapewear"  # HIGHEST margin
    ACCESSORIES = "accessories"  # Impulse buys
    VIRAL_AESTHETIC = "viral_aesthetic"  # Coquette, Y2K
    PROBLEM_SOLVING = "problem_solving"  # Comfortable heels, etc.
    LUXURY_DUPES = "luxury_dupes"  # Designer alternatives
    SEASONAL = "seasonal"  # Trending seasonal items
    SIZE_INCLUSIVE = "size_inclusive"  # Plus size fashion
    SUSTAINABLE = "sustainable"  # Thrift, eco-friendly
    GENERAL_FASHION = "general_fashion"  # Default category


@dataclass
class ProductOpportunity:
    """Represents a product opportunity with scoring metrics."""

    video: TikTokVideo
    category: ProductCategory
    sellability_score: float  # 0-100
    profit_potential: ProfitPotential
    purchase_intent_signals: List[str] = field(default_factory=list)
    sourcing_platforms: List[str] = field(default_factory=list)
    price_indicators: List[str] = field(default_factory=list)
    competitive_advantage: str = ""
    ad_creative_score: float = 0.0  # 0-100

    def to_dict(self) -> Dict:
        """Convert to dictionary for output."""
        return {
            "video_url": self.video.url,
            "video_id": self.video.video_id,
            "creator": self.video.creator.username,
            "category": self.category.value,
            "sellability_score": round(self.sellability_score, 2),
            "profit_potential": self.profit_potential.value,
            "purchase_intent_signals": self.purchase_intent_signals,
            "sourcing_platforms": self.sourcing_platforms,
            "price_indicators": self.price_indicators,
            "ad_creative_score": round(self.ad_creative_score, 2),
            "competitive_advantage": self.competitive_advantage,
            "metrics": {
                "views": self.video.view_count,
                "engagement_rate": round(self.video.engagement_rate, 2),
            }
        }


class ProductOpportunityScorer:
    """World-class TikTok product opportunity analyzer.

    Based on $10M+ ad spend experience, this scorer identifies fashion products
    with high purchase intent, sellability, and profit potential on TikTok.
    """

    def __init__(self):
        """Initialize with expert-curated keyword dictionaries."""

        # HIGH-CONVERTING PRODUCT KEYWORDS by category
        self.product_keywords: Dict[ProductCategory, Set[str]] = {
            ProductCategory.SHAPEWEAR: {
                "shapewear", "body shaper", "waist trainer", "cincher",
                "compression", "sculpting", "smoothing", "tummy control",
                "body suit", "bodysuit", "sculpt", "contour", "lift",
                "enhance", "curve", "hourglass", "snatch", "slim",
                "skims", "spanx", "honeylove", "shapermint",
            },
            ProductCategory.ACCESSORIES: {
                "bag", "purse", "mini bag", "clutch", "crossbody",
                "tote bag", "shoulder bag", "belt bag", "fanny pack",
                "jewelry", "necklace", "earrings", "bracelet", "ring",
                "sunglasses", "sunnies", "shades", "hat", "beanie",
                "hair clip", "claw clip", "scrunchie", "bow", "headband",
                "belt", "scarf", "phone case", "wallet", "coin purse",
            },
            ProductCategory.VIRAL_AESTHETIC: {
                "coquette", "bow", "ribbon", "ballet", "balletcore",
                "y2k", "2000s", "early 2000s", "butterfly", "rhinestone",
                "baby tee", "juicy couture", "velour", "low rise",
                "cargo", "parachute pants", "mini skirt", "platform",
                "chunky", "fairy", "cottagecore", "cottage core",
                "aesthetic", "clean girl", "mob wife", "coastal grandmother",
            },
            ProductCategory.PROBLEM_SOLVING: {
                "comfortable", "all day", "no pain", "pain free",
                "cushioned", "supportive", "breathable", "stretchy",
                "flexible", "adjustable", "no show", "invisible",
                "seamless", "anti chafe", "non slip", "stay put",
                "wrinkle free", "crease resistant", "waterproof",
                "sweat proof", "stain resistant", "easy care",
                "travel friendly", "packable", "convertible",
            },
            ProductCategory.LUXURY_DUPES: {
                "dupe", "dupe for", "looks like", "similar to",
                "designer look", "luxury look", "expensive look",
                "affordable version", "budget friendly", "cheaper alternative",
                "hermes dupe", "chanel dupe", "lv dupe", "gucci dupe",
                "designer inspired", "high end look", "bougie on a budget",
                "target find", "amazon find", "dhgate", "aliexpress find",
            },
            ProductCategory.SEASONAL: {
                "fall fashion", "autumn style", "winter coat", "puffer",
                "cozy", "sweater weather", "boots", "layering",
                "spring style", "spring dress", "floral", "pastel",
                "summer outfit", "beach", "vacation", "resort",
                "swimsuit", "bikini", "shorts", "sandals",
                "holiday party", "holiday outfit", "christmas", "nye",
                "valentine", "valentines day", "date night",
            },
            ProductCategory.SIZE_INCLUSIVE: {
                "plus size", "curve", "curvy", "midsize", "mid size",
                "all sizes", "size inclusive", "extended sizes",
                "true to size", "runs big", "runs small", "fits like",
                "petite", "tall", "short", "long", "regular",
                "for every body", "everybody", "real bodies",
            },
            ProductCategory.SUSTAINABLE: {
                "thrift", "thrifted", "vintage", "secondhand",
                "preloved", "consignment", "resale", "depop",
                "poshmark", "vinted", "goodwill", "savers",
                "sustainable", "eco friendly", "ethical", "slow fashion",
                "upcycled", "recycled", "handmade", "small business",
            },
        }

        # PURCHASE INTENT PHRASES (high-signal keywords)
        self.purchase_intent_phrases: Set[str] = {
            # Direct call-to-action
            "link in bio", "link in my bio", "shop the look", "shop my look",
            "shop link", "link below", "check the link", "swipe up",
            "tap the link", "click the link", "find it at", "available at",

            # Urgency/scarcity
            "selling out", "almost sold out", "back in stock", "restock",
            "limited edition", "limited time", "hurry", "grab it now",
            "before it's gone", "only a few left", "low stock",

            # Price mentions (sweet spot indicators)
            "under $", "only $", "just $", "for $", "less than",
            "on sale", "sale alert", "discount", "off", "% off",
            "deal", "steal", "bargain", "affordable", "budget",

            # Social proof
            "everyone is buying", "viral", "trending", "tiktok made me",
            "tiktok made me buy", "saw this on tiktok", "everyone has",
            "everyone needs", "must have", "game changer", "obsessed",
            "can't stop wearing", "living in", "wear all the time",

            # Questions (high intent)
            "where did you get", "where is this from", "where to buy",
            "what is this", "need this", "i need", "where can i find",
            "link please", "drop the link", "what brand",

            # Comparison/Review signals
            "amazon find", "amazon must have", "target find", "target run",
            "is it worth it", "honest review", "try on", "tryon",
            "unboxing", "first impression", "testing", "does it work",

            # Discount codes
            "code", "discount code", "promo code", "use code",
            "coupon", "save money", "get it cheaper",
        }

        # BRAND/RETAILER MENTIONS (for sourcing detection)
        self.sourcing_retailers: Dict[str, List[str]] = {
            "amazon": ["amazon", "amazon find", "amazon fashion", "amazon prime"],
            "aliexpress": ["aliexpress", "ali express", "ae", "china"],
            "shein": ["shein", "she in"],
            "temu": ["temu"],
            "target": ["target", "target style", "target run"],
            "walmart": ["walmart", "wally world"],
            "zara": ["zara"],
            "h&m": ["h&m", "h and m", "hm"],
            "forever21": ["forever21", "forever 21", "f21"],
            "asos": ["asos"],
            "boohoo": ["boohoo"],
            "prettylittlething": ["prettylittlething", "plt"],
            "fashion_nova": ["fashion nova", "fashionnova"],
            "nordstrom": ["nordstrom", "nordstrom rack"],
            "revolve": ["revolve"],
            "dhgate": ["dhgate", "dh gate"],
            "etsy": ["etsy", "small business", "small shop"],
        }

        # PRICE SENSITIVITY KEYWORDS (for profit margin analysis)
        self.price_keywords: Dict[str, Set[str]] = {
            "impulse_buy": {  # $15-$50 sweet spot
                "under $20", "under $25", "under $30", "under $50",
                "less than $20", "only $15", "just $20", "$10", "$15",
                "cheap", "affordable", "budget", "inexpensive",
            },
            "premium_impulse": {  # $50-$100 - still high conversion
                "under $100", "under $75", "worth it", "investment piece",
                "splurge", "treat yourself", "save up", "worth the money",
            },
            "discount_hunters": {  # High intent segment
                "on sale", "clearance", "marked down", "discount",
                "% off", "percent off", "sale alert", "deal",
                "coupon", "promo", "code", "save",
            },
            "value_props": {  # Justification signals
                "worth every penny", "best purchase", "no regrets",
                "would buy again", "highly recommend", "changed my life",
                "game changer", "holy grail", "obsessed",
            },
        }

        # AD CREATIVE POTENTIAL INDICATORS
        self.ad_creative_signals: Set[str] = {
            # Transformation content (highly engaging)
            "before and after", "before after", "transformation",
            "glow up", "makeover", "changed my",

            # Try-on content (converts well)
            "try on", "tryon", "try-on", "fitting room",
            "haul", "unboxing", "first try", "first time",

            # Problem/solution format (FB/TikTok ad gold)
            "i used to", "i struggled with", "this fixed",
            "finally found", "solved my", "no more",

            # Hooks (scroll-stoppers)
            "you need", "stop scrolling", "hear me out",
            "trust me", "wait for it", "watch till the end",

            # Social proof hooks
            "everyone is talking about", "went viral", "blew up",
            "tiktok famous", "trending", "all over tiktok",
        }

        console.log("[green]ProductOpportunityScorer initialized with expert keyword dictionaries[/green]")

    def detect_purchase_intent(self, video: TikTokVideo) -> Tuple[float, List[str]]:
        """Detect purchase intent signals in video content.

        Args:
            video: TikTokVideo object to analyze

        Returns:
            Tuple of (intent_score, list of detected signals)
        """
        signals_found = []
        description_lower = video.description.lower()
        hashtags_lower = [tag.lower() for tag in video.hashtags]
        combined_text = f"{description_lower} {' '.join(hashtags_lower)}"

        # Detect purchase intent phrases
        for phrase in self.purchase_intent_phrases:
            if phrase in combined_text:
                signals_found.append(phrase)

        # Calculate intent score (0-100)
        # Base score from signal count
        signal_count = len(signals_found)
        base_score = min(signal_count * 15, 60)  # Cap at 60 from signals alone

        # Bonus points for high-value signals
        high_value_signals = ["link in bio", "shop", "on sale", "selling out", "must have"]
        bonus = sum(10 for signal in signals_found if any(hvs in signal for hvs in high_value_signals))

        # Engagement multiplier (higher engagement = higher real interest)
        engagement_multiplier = min(video.engagement_rate / 5, 1.5)  # Cap at 1.5x

        intent_score = min((base_score + bonus) * engagement_multiplier, 100)

        if signals_found:
            console.log(f"[cyan]Purchase intent detected: {len(signals_found)} signals, score: {intent_score:.1f}[/cyan]")

        return intent_score, signals_found

    def categorize_product_opportunity(self, video: TikTokVideo) -> ProductCategory:
        """Categorize the product opportunity type.

        Args:
            video: TikTokVideo object to analyze

        Returns:
            ProductCategory enum value
        """
        description_lower = video.description.lower()
        hashtags_lower = [tag.lower() for tag in video.hashtags]
        combined_text = f"{description_lower} {' '.join(hashtags_lower)}"

        # Score each category
        category_scores: Dict[ProductCategory, int] = {}

        for category, keywords in self.product_keywords.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                category_scores[category] = score

        # Return highest scoring category or default
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            console.log(f"[green]Product categorized as: {best_category[0].value} (score: {best_category[1]})[/green]")
            return best_category[0]

        return ProductCategory.GENERAL_FASHION

    def detect_sourcing_ease(self, video: TikTokVideo) -> List[str]:
        """Detect sourcing platform mentions for easy product acquisition.

        Args:
            video: TikTokVideo object to analyze

        Returns:
            List of detected sourcing platforms
        """
        platforms_found = []
        description_lower = video.description.lower()
        hashtags_lower = [tag.lower() for tag in video.hashtags]
        combined_text = f"{description_lower} {' '.join(hashtags_lower)}"

        for platform, keywords in self.sourcing_retailers.items():
            if any(keyword in combined_text for keyword in keywords):
                platforms_found.append(platform)

        if platforms_found:
            console.log(f"[blue]Sourcing platforms detected: {', '.join(platforms_found)}[/blue]")

        return platforms_found

    def analyze_price_indicators(self, video: TikTokVideo) -> Tuple[List[str], str]:
        """Analyze price mentions and value propositions.

        Args:
            video: TikTokVideo object to analyze

        Returns:
            Tuple of (price_indicators_found, price_tier)
        """
        indicators = []
        description_lower = video.description.lower()

        # Check all price keyword categories
        for category, keywords in self.price_keywords.items():
            for keyword in keywords:
                if keyword in description_lower:
                    indicators.append(f"{category}: {keyword}")

        # Determine price tier
        if any("impulse_buy" in ind for ind in indicators):
            price_tier = "impulse ($15-$50)"
        elif any("premium_impulse" in ind for ind in indicators):
            price_tier = "premium impulse ($50-$100)"
        elif any("discount_hunters" in ind for ind in indicators):
            price_tier = "discount-driven"
        else:
            price_tier = "unspecified"

        # Extract actual dollar amounts if present
        dollar_matches = re.findall(r'\$(\d+)', description_lower)
        if dollar_matches:
            prices = [int(m) for m in dollar_matches]
            price_tier = f"${min(prices)}-${max(prices)}"

        if indicators:
            console.log(f"[yellow]Price indicators found: {len(indicators)}, tier: {price_tier}[/yellow]")

        return indicators, price_tier

    def identify_ad_creative_potential(self, video: TikTokVideo) -> float:
        """Score the video's potential for repurposing as ad creative.

        Args:
            video: TikTokVideo object to analyze

        Returns:
            Ad creative score (0-100)
        """
        description_lower = video.description.lower()
        score = 0.0

        # Check for ad-friendly content signals
        signal_count = sum(1 for signal in self.ad_creative_signals
                          if signal in description_lower)
        score += min(signal_count * 15, 50)

        # Bonus for high engagement (proves content resonates)
        if video.engagement_rate > 5:
            score += 20
        elif video.engagement_rate > 3:
            score += 10

        # Bonus for viral metrics
        if hasattr(video, 'viral_score') and video.viral_score > 50:
            score += 15

        # Bonus for view count (social proof)
        if video.view_count > 1_000_000:
            score += 15
        elif video.view_count > 500_000:
            score += 10

        score = min(score, 100)

        console.log(f"[magenta]Ad creative potential score: {score:.1f}[/magenta]")
        return score

    def calculate_sellability_score(self, video: TikTokVideo) -> float:
        """Calculate comprehensive sellability score (0-100).

        Factors:
        - Purchase intent signals (30 points)
        - Product category profitability (20 points)
        - Sourcing ease (15 points)
        - Price point optimization (15 points)
        - Viral metrics (10 points)
        - Engagement quality (10 points)

        Args:
            video: TikTokVideo object to analyze

        Returns:
            Sellability score (0-100)
        """
        total_score = 0.0

        # 1. Purchase intent (30 points max)
        intent_score, signals = self.detect_purchase_intent(video)
        total_score += (intent_score / 100) * 30

        # 2. Product category profitability (20 points max)
        category = self.categorize_product_opportunity(video)
        category_points = {
            ProductCategory.SHAPEWEAR: 20,
            ProductCategory.ACCESSORIES: 18,
            ProductCategory.VIRAL_AESTHETIC: 16,
            ProductCategory.PROBLEM_SOLVING: 16,
            ProductCategory.LUXURY_DUPES: 15,
            ProductCategory.SEASONAL: 14,
            ProductCategory.SIZE_INCLUSIVE: 13,
            ProductCategory.SUSTAINABLE: 12,
            ProductCategory.GENERAL_FASHION: 10,
        }
        total_score += category_points.get(category, 10)

        # 3. Sourcing ease (15 points max)
        platforms = self.detect_sourcing_ease(video)
        if platforms:
            # Amazon/AliExpress = easiest sourcing
            if any(p in platforms for p in ["amazon", "aliexpress", "shein", "temu"]):
                total_score += 15
            else:
                total_score += 10

        # 4. Price point optimization (15 points max)
        price_indicators, price_tier = self.analyze_price_indicators(video)
        if "impulse" in price_tier.lower():
            total_score += 15  # Sweet spot
        elif price_indicators:
            total_score += 10

        # 5. Viral metrics (10 points max)
        if hasattr(video, 'viral_score'):
            viral_contribution = min((video.viral_score / 100) * 10, 10)
            total_score += viral_contribution

        # 6. Engagement quality (10 points max)
        engagement_contribution = min((video.engagement_rate / 10) * 10, 10)
        total_score += engagement_contribution

        total_score = min(total_score, 100)

        console.log(f"[bold green]Sellability score calculated: {total_score:.1f}/100[/bold green]")
        return total_score

    def estimate_profit_potential(self, video: TikTokVideo) -> ProfitPotential:
        """Estimate profit potential based on product characteristics.

        Args:
            video: TikTokVideo object to analyze

        Returns:
            ProfitPotential enum value
        """
        category = self.categorize_product_opportunity(video)
        intent_score, _ = self.detect_purchase_intent(video)
        platforms = self.detect_sourcing_ease(video)

        # High-margin categories with strong intent = VERY HIGH
        high_margin_cats = [ProductCategory.SHAPEWEAR, ProductCategory.ACCESSORIES]
        if category in high_margin_cats and intent_score > 60:
            return ProfitPotential.VERY_HIGH

        # Easy sourcing + viral potential = HIGH
        easy_source = any(p in platforms for p in ["aliexpress", "amazon", "shein"])
        if easy_source and video.engagement_rate > 5:
            return ProfitPotential.HIGH

        # Trending categories with good metrics = MEDIUM
        trending_cats = [ProductCategory.VIRAL_AESTHETIC, ProductCategory.LUXURY_DUPES]
        if category in trending_cats or intent_score > 40:
            return ProfitPotential.MEDIUM

        return ProfitPotential.LOW

    def analyze_competition(self, video: TikTokVideo, all_videos: List[TikTokVideo]) -> str:
        """Analyze competitive landscape for the product.

        Args:
            video: TikTokVideo to analyze
            all_videos: All videos in dataset for comparison

        Returns:
            Competitive advantage description
        """
        category = self.categorize_product_opportunity(video)

        # Count similar products in category
        similar_count = sum(1 for v in all_videos
                          if self.categorize_product_opportunity(v) == category)

        # Analyze market saturation
        if similar_count < 5:
            return "Low competition - first mover advantage"
        elif similar_count < 15:
            return "Moderate competition - good opportunity window"
        elif similar_count < 30:
            return "High competition - differentiation required"
        else:
            return "Saturated market - enter with caution"

    def score_product_opportunity(
        self,
        video: TikTokVideo,
        all_videos: Optional[List[TikTokVideo]] = None
    ) -> ProductOpportunity:
        """Score a complete product opportunity.

        Args:
            video: TikTokVideo to analyze
            all_videos: Optional list of all videos for competitive analysis

        Returns:
            ProductOpportunity object with complete analysis
        """
        console.log(f"[bold cyan]Scoring product opportunity for video: {video.video_id}[/bold cyan]")

        # Run all analyses
        category = self.categorize_product_opportunity(video)
        sellability_score = self.calculate_sellability_score(video)
        profit_potential = self.estimate_profit_potential(video)
        intent_score, signals = self.detect_purchase_intent(video)
        platforms = self.detect_sourcing_ease(video)
        price_indicators, price_tier = self.analyze_price_indicators(video)
        ad_score = self.identify_ad_creative_potential(video)

        competitive_advantage = ""
        if all_videos:
            competitive_advantage = self.analyze_competition(video, all_videos)

        opportunity = ProductOpportunity(
            video=video,
            category=category,
            sellability_score=sellability_score,
            profit_potential=profit_potential,
            purchase_intent_signals=signals,
            sourcing_platforms=platforms,
            price_indicators=price_indicators,
            competitive_advantage=competitive_advantage,
            ad_creative_score=ad_score,
        )

        console.log(f"[bold green]Product opportunity scored: {sellability_score:.1f}/100, "
                   f"profit: {profit_potential.value}[/bold green]")

        return opportunity

    def get_top_opportunities(
        self,
        videos: List[TikTokVideo],
        limit: int = 20
    ) -> List[ProductOpportunity]:
        """Get top product opportunities from a list of videos.

        Args:
            videos: List of TikTokVideo objects to analyze
            limit: Maximum number of opportunities to return

        Returns:
            List of top ProductOpportunity objects sorted by sellability score
        """
        console.log(f"[bold cyan]Analyzing {len(videos)} videos for product opportunities...[/bold cyan]")

        opportunities = []
        for video in videos:
            try:
                opportunity = self.score_product_opportunity(video, videos)
                opportunities.append(opportunity)
            except Exception as e:
                console.log(f"[red]Error scoring video {video.video_id}: {e}[/red]")
                continue

        # Sort by sellability score (descending)
        opportunities.sort(key=lambda x: x.sellability_score, reverse=True)

        top_opportunities = opportunities[:limit]

        console.log(f"[bold green]Found {len(top_opportunities)} top product opportunities![/bold green]")

        return top_opportunities

    def generate_product_report(self, opportunity: ProductOpportunity) -> str:
        """Generate detailed opportunity report for a product.

        Args:
            opportunity: ProductOpportunity object

        Returns:
            Formatted report string
        """
        video = opportunity.video

        # Create rich formatted report
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append(f"PRODUCT OPPORTUNITY REPORT - Score: {opportunity.sellability_score:.1f}/100")
        report_lines.append("=" * 80)
        report_lines.append("")

        # Video details
        report_lines.append("VIDEO DETAILS:")
        report_lines.append(f"  URL: {video.url}")
        report_lines.append(f"  Creator: @{video.creator.username} ({video.creator.follower_count:,} followers)")
        report_lines.append(f"  Views: {video.view_count:,}")
        report_lines.append(f"  Engagement Rate: {video.engagement_rate:.2f}%")
        report_lines.append(f"  Description: {video.description[:200]}...")
        report_lines.append("")

        # Opportunity analysis
        report_lines.append("OPPORTUNITY ANALYSIS:")
        report_lines.append(f"  Category: {opportunity.category.value.upper()}")
        report_lines.append(f"  Profit Potential: {opportunity.profit_potential.value.upper()}")
        report_lines.append(f"  Sellability Score: {opportunity.sellability_score:.1f}/100")
        report_lines.append(f"  Ad Creative Score: {opportunity.ad_creative_score:.1f}/100")
        report_lines.append("")

        # Purchase intent signals
        if opportunity.purchase_intent_signals:
            report_lines.append("PURCHASE INTENT SIGNALS:")
            for signal in opportunity.purchase_intent_signals[:10]:
                report_lines.append(f"  - {signal}")
            report_lines.append("")

        # Sourcing information
        if opportunity.sourcing_platforms:
            report_lines.append("SOURCING PLATFORMS:")
            for platform in opportunity.sourcing_platforms:
                report_lines.append(f"  - {platform.upper()}")
            report_lines.append("")

        # Price indicators
        if opportunity.price_indicators:
            report_lines.append("PRICE INDICATORS:")
            for indicator in opportunity.price_indicators[:5]:
                report_lines.append(f"  - {indicator}")
            report_lines.append("")

        # Competitive advantage
        if opportunity.competitive_advantage:
            report_lines.append("COMPETITIVE ANALYSIS:")
            report_lines.append(f"  {opportunity.competitive_advantage}")
            report_lines.append("")

        # Recommendations
        report_lines.append("RECOMMENDATIONS:")

        if opportunity.sellability_score >= 80:
            report_lines.append("  HIGH PRIORITY - Launch immediately!")
            report_lines.append("  - Set up product page within 48 hours")
            report_lines.append("  - Prepare ad creative using this video style")
            report_lines.append("  - Allocate $500+ test budget")
        elif opportunity.sellability_score >= 60:
            report_lines.append("  MEDIUM PRIORITY - Strong potential")
            report_lines.append("  - Research supplier options")
            report_lines.append("  - Create product listing")
            report_lines.append("  - Test with $200-300 budget")
        else:
            report_lines.append("  LOW PRIORITY - Consider if resources allow")
            report_lines.append("  - Monitor for trend growth")
            report_lines.append("  - Validate demand before sourcing")

        report_lines.append("")
        report_lines.append("=" * 80)

        report = "\n".join(report_lines)

        # Also create a rich console panel
        panel = Panel(
            report,
            title=f"[bold cyan]Product Opportunity Report[/bold cyan]",
            border_style="cyan",
        )
        console.print(panel)

        return report

    def export_opportunities_table(self, opportunities: List[ProductOpportunity]) -> Table:
        """Export opportunities as a rich formatted table.

        Args:
            opportunities: List of ProductOpportunity objects

        Returns:
            Rich Table object
        """
        table = Table(title="Top Product Opportunities", show_lines=True)

        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Creator", style="magenta", width=15)
        table.add_column("Category", style="green", width=15)
        table.add_column("Score", style="yellow", width=8)
        table.add_column("Profit", style="red", width=12)
        table.add_column("Intent Signals", style="blue", width=10)
        table.add_column("Sourcing", style="cyan", width=12)

        for i, opp in enumerate(opportunities, 1):
            table.add_row(
                f"#{i}",
                f"@{opp.video.creator.username}",
                opp.category.value,
                f"{opp.sellability_score:.1f}",
                opp.profit_potential.value,
                str(len(opp.purchase_intent_signals)),
                ", ".join(opp.sourcing_platforms[:2]) if opp.sourcing_platforms else "N/A",
            )

        return table

    def analyze_viral_candidates(
        self,
        candidates: List[ViralCandidate],
        limit: int = 20
    ) -> List[ProductOpportunity]:
        """Analyze viral candidates for product opportunities.

        Convenience method for working with ViralCandidate objects.

        Args:
            candidates: List of ViralCandidate objects
            limit: Maximum number of opportunities to return

        Returns:
            List of top ProductOpportunity objects
        """
        videos = [candidate.video for candidate in candidates]
        return self.get_top_opportunities(videos, limit)
