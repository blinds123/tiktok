#!/usr/bin/env python3
"""
Demo mode - Simulates real TikTok scraping results.
Shows exactly what the app output looks like with realistic data.
"""

import random
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from models.video import TikTokVideo, TikTokCreator
from analyzer import (
    ViralPredictor,
    FashionExtractor,
    ProductOpportunityScorer,
    ContentFilter,
    FilterConfig,
)
from analyzer.filters import EarlyViralFilter

console = Console()

# Realistic sample data based on actual TikTok fashion trends
SAMPLE_CREATORS = [
    {"username": "fashiongirl_emma", "nickname": "Emma | Fashion", "followers": 87000, "location": "US", "bio": "NYC fashion blogger | style inspo daily 🇺🇸"},
    {"username": "ootd.queen.sarah", "nickname": "Sarah Style", "followers": 124000, "location": "UK", "bio": "London girl | outfit ideas | she/her 🇬🇧"},
    {"username": "y2k.vibes.jen", "nickname": "Jen ✨", "followers": 65000, "location": "US", "bio": "y2k aesthetic | LA based | fashion hauls 💕"},
    {"username": "coquette.claire", "nickname": "Claire", "followers": 93000, "location": "CA", "bio": "Toronto | coquette style | girly fits 🎀"},
    {"username": "streetstyle.maya", "nickname": "Maya", "followers": 108000, "location": "UK", "bio": "Manchester | streetwear | outfit inspo"},
    {"username": "thrift.queen.lisa", "nickname": "Lisa Thrifts", "followers": 72000, "location": "US", "bio": "sustainable fashion | thrift hauls | Chicago girl"},
    {"username": "minimal.style.anna", "nickname": "Anna", "followers": 145000, "location": "CA", "bio": "Vancouver | minimalist wardrobe | capsule closet"},
    {"username": "aesthetic.fits.mia", "nickname": "Mia", "followers": 58000, "location": "US", "bio": "aesthetic outfits | grwm | Miami ☀️"},
    {"username": "fashionfinds.sophie", "nickname": "Sophie", "followers": 81000, "location": "UK", "bio": "Birmingham | amazon fashion finds | she/her"},
    {"username": "styletips.olivia", "nickname": "Olivia", "followers": 99000, "location": "US", "bio": "fashion tips | NYC | outfit ideas daily"},
    {"username": "grwm.with.bella", "nickname": "Bella", "followers": 112000, "location": "CA", "bio": "Montreal | get ready with me | style content"},
    {"username": "trendy.fits.zoe", "nickname": "Zoe", "followers": 76000, "location": "UK", "bio": "London fashion girl | trends | ootd"},
]

SAMPLE_VIDEOS = [
    {
        "desc": "This Amazon dress is going VIRAL 😍 under $30 and perfect for date night! Link in bio #fashion #amazonfinds #datenight #ootd #viral",
        "views": 1850000, "likes": 245000, "comments": 8900, "shares": 42000,
        "hours_ago": 4.2, "category": "viral_aesthetic",
        "products": ["dress", "amazon find"],
    },
    {
        "desc": "POV: you find the perfect coquette top 🎀 $15 on Shein and it's SO CUTE #coquette #shein #fashionhaul #grwm #pink",
        "views": 920000, "likes": 156000, "comments": 4200, "shares": 18000,
        "hours_ago": 2.8, "category": "coquette",
        "products": ["top", "coquette", "shein"],
    },
    {
        "desc": "STOP SCROLLING!! This shapewear changed my LIFE 🙌 amazon link in bio #shapewear #amazonfinds #fashion #viral #musthave",
        "views": 2100000, "likes": 312000, "comments": 15600, "shares": 67000,
        "hours_ago": 5.5, "category": "shapewear",
        "products": ["shapewear", "amazon find"],
    },
    {
        "desc": "y2k outfit inspo for fall 🍂✨ all from princess polly! #y2k #fall #outfitinspo #fashion #aesthetic",
        "views": 780000, "likes": 98000, "comments": 2800, "shares": 12000,
        "hours_ago": 3.1, "category": "y2k",
        "products": ["outfit", "y2k", "princess polly"],
    },
    {
        "desc": "The viral TikTok leggings are actually SO GOOD 😱 Amazon link in bio!! #leggings #amazon #viral #fashion #gym",
        "views": 1450000, "likes": 189000, "comments": 7800, "shares": 34000,
        "hours_ago": 6.2, "category": "athleisure",
        "products": ["leggings", "amazon find"],
    },
    {
        "desc": "Thrift flip transformation ✨ $5 jacket to designer dupe! #thrift #sustainable #fashion #diy #transformation",
        "views": 560000, "likes": 78000, "comments": 3400, "shares": 8900,
        "hours_ago": 1.5, "category": "sustainable",
        "products": ["jacket", "thrift"],
    },
    {
        "desc": "GRWM for girls night 💄 this dress is EVERYTHING #grwm #dress #girlsnight #fashion #ootd #style",
        "views": 890000, "likes": 123000, "comments": 5600, "shares": 21000,
        "hours_ago": 4.8, "category": "glamorous",
        "products": ["dress", "party wear"],
    },
    {
        "desc": "Zara haul!! Found the cutest fall pieces 🍁 #zara #haul #fall #fashion #tryonhaul",
        "views": 670000, "likes": 87000, "comments": 2100, "shares": 9500,
        "hours_ago": 3.7, "category": "minimalist",
        "products": ["zara", "fall fashion"],
    },
    {
        "desc": "These $20 heels look SO expensive 👠 Amazon find alert! #heels #amazon #fashion #affordable #dupe",
        "views": 1120000, "likes": 167000, "comments": 6700, "shares": 28000,
        "hours_ago": 5.1, "category": "accessories",
        "products": ["heels", "amazon find", "dupe"],
    },
    {
        "desc": "The prettiest bag for under $40!! Found on Amazon 🤍 #bag #amazon #fashion #accessories #viral",
        "views": 980000, "likes": 134000, "comments": 4900, "shares": 19000,
        "hours_ago": 2.2, "category": "accessories",
        "products": ["bag", "amazon find"],
    },
    {
        "desc": "Styling the viral Aritzia sweater 3 ways 🧥 #aritzia #sweater #styling #fall #fashion #ootd",
        "views": 720000, "likes": 95000, "comments": 3200, "shares": 11000,
        "hours_ago": 7.3, "category": "minimalist",
        "products": ["sweater", "aritzia"],
    },
    {
        "desc": "Unboxing my Shein haul 📦 everything under $25!! #shein #haul #fashion #affordable #tryonhaul",
        "views": 830000, "likes": 109000, "comments": 4500, "shares": 15000,
        "hours_ago": 4.0, "category": "streetwear",
        "products": ["shein", "haul"],
    },
]

URGENCY_COLORS = {
    "CRITICAL": "bold red",
    "URGENT": "bold yellow",
    "HIGH": "green",
    "MEDIUM": "cyan",
    "LOW": "dim",
}


def generate_sample_videos() -> list[TikTokVideo]:
    """Generate realistic sample TikTok videos."""
    videos = []

    for i, sample in enumerate(SAMPLE_VIDEOS):
        creator_data = SAMPLE_CREATORS[i % len(SAMPLE_CREATORS)]

        creator = TikTokCreator(
            user_id=str(1000000 + i),
            username=creator_data["username"],
            nickname=creator_data["nickname"],
            follower_count=creator_data["followers"],
            bio=creator_data["bio"],
            avg_views=creator_data["followers"] * 0.8,  # Estimate avg views
        )

        created_at = datetime.utcnow() - timedelta(hours=sample["hours_ago"])

        # Extract hashtags from description
        import re
        hashtags = re.findall(r'#(\w+)', sample["desc"])

        video = TikTokVideo(
            video_id=str(7000000000000000000 + i),
            url=f"https://www.tiktok.com/@{creator.username}/video/{7000000000000000000 + i}",
            description=sample["desc"],
            creator=creator,
            view_count=sample["views"],
            like_count=sample["likes"],
            comment_count=sample["comments"],
            share_count=sample["shares"],
            created_at=created_at,
            hashtags=hashtags,
        )

        # Set creator average based on follower count
        video.creator.avg_views = creator_data["followers"] * random.uniform(0.5, 1.0)

        videos.append(video)

    return videos


def run_demo():
    """Run the full demo showing what real results look like."""
    console.print("""
[bold cyan]
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║   TikTok Viral Fashion Scraper - DEMO MODE                            ║
║   Showing realistic results for women micro-influencers               ║
║   Target: USA, Canada, UK | Priority: Videos < 6 hours old            ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
[/bold cyan]
""")

    console.print(Panel.fit(
        "[bold]Demo Configuration[/bold]\n\n"
        "[cyan]Target Audience:[/cyan]\n"
        "  Locations: USA, Canada, UK\n"
        "  Gender: Women only\n"
        "  Followers: 50,000 - 150,000\n\n"
        "[cyan]Content Filters:[/cyan]\n"
        "  Hashtags: #fashion, #ootd, #grwm, #haul, #y2k, #coquette\n"
        "  Niche: Fashion\n\n"
        "[cyan]Viral Detection:[/cyan]\n"
        "  Time Window: 24 hours\n"
        "  [bold yellow]Priority Window: 6 hours (early detection)[/bold yellow]\n"
        "  Viral Multiplier: 10x average views\n"
        "  Max Results: 12",
        title="Configuration",
        border_style="cyan"
    ))

    console.print("\n[cyan]Generating sample TikTok data...[/cyan]")
    videos = generate_sample_videos()
    console.print(f"[green]✓[/green] Generated {len(videos)} sample videos")

    # Initialize analyzers
    console.print("\n[cyan]Analyzing viral potential...[/cyan]")
    predictor = ViralPredictor()
    fashion_extractor = FashionExtractor()
    product_scorer = ProductOpportunityScorer()
    early_viral_filter = EarlyViralFilter()

    # Process videos
    results = []
    for video in videos:
        age_hours = early_viral_filter.get_video_age_hours(video)
        early_viral_score = early_viral_filter.calculate_early_viral_score(video)
        urgency = early_viral_filter.classify_urgency(video)

        fashion_score = fashion_extractor.calculate_fashion_score(video)
        products = fashion_extractor.extract_products(video.description, video.hashtags)
        trend_category = fashion_extractor.categorize_trend(video.hashtags, video.description)

        sellability = product_scorer.calculate_sellability_score(video)
        profit = product_scorer.estimate_profit_potential(video)

        # Get location from creator bio
        location = "US"
        if "UK" in (video.creator.bio or "") or "London" in (video.creator.bio or ""):
            location = "UK"
        elif "CA" in (video.creator.bio or "") or "Toronto" in (video.creator.bio or "") or "Vancouver" in (video.creator.bio or ""):
            location = "CA"

        composite_score = (
            early_viral_score * 0.50 +
            fashion_score * 0.25 +
            video.engagement_rate * 2 +
            (20 if age_hours <= 6 else 10 if age_hours <= 12 else 0)
        )

        results.append({
            "video": video,
            "age_hours": round(age_hours, 1),
            "urgency": urgency,
            "early_viral_score": round(early_viral_score, 1),
            "composite_score": round(composite_score, 1),
            "fashion_relevance": round(fashion_score, 1),
            "location": location,
            "in_priority_window": age_hours <= 6,
            "trend_category": trend_category,
            "detected_products": products,
            "sellability_score": round(sellability, 1),
            "profit_potential": profit.value,
        })

    # Sort by composite score
    results.sort(key=lambda x: (-x["composite_score"], x["age_hours"]))

    console.print(f"[green]✓[/green] Analysis complete. Found {len(results)} viral candidates")

    # Display results table
    console.print("\n[bold]Viral Fashion Trends - Women Micro-Influencers (USA/CA/UK)[/bold]")

    table = Table(
        show_header=True,
        header_style="bold magenta",
        border_style="bright_blue",
        title=f"Top {len(results)} Emerging Viral Videos",
        title_style="bold cyan"
    )

    table.add_column("#", justify="right", style="cyan", width=3)
    table.add_column("Urgency", style="bold", width=10)
    table.add_column("Creator", style="green", width=18)
    table.add_column("Location", style="yellow", width=8)
    table.add_column("Age", justify="right", style="cyan", width=6)
    table.add_column("Views", justify="right", style="blue", width=10)
    table.add_column("Score", justify="right", style="magenta", width=8)
    table.add_column("Category", style="white", width=12)

    for idx, result in enumerate(results, 1):
        video = result["video"]
        urgency = result["urgency"]
        urgency_style = URGENCY_COLORS.get(urgency, "white")

        age_hours = result["age_hours"]
        age_str = f"{age_hours:.1f}h"
        if result["in_priority_window"]:
            age_str = f"[bold]{age_str}[/bold]"

        table.add_row(
            str(idx),
            f"[{urgency_style}]{urgency}[/{urgency_style}]",
            f"@{video.creator.username[:16]}",
            result["location"],
            age_str,
            f"{video.view_count:,}",
            f"{result['composite_score']:.0f}",
            result["trend_category"][:12],
        )

    console.print(table)

    # Show top 3 detailed
    console.print("\n[bold]Top 3 Priority Candidates (Early Viral Detection):[/bold]\n")

    priority_results = [r for r in results if r["in_priority_window"]][:3]
    if not priority_results:
        priority_results = results[:3]

    for idx, result in enumerate(priority_results, 1):
        video = result["video"]
        urgency = result["urgency"]
        urgency_style = URGENCY_COLORS.get(urgency, "white")

        # Handle products - may be list of strings or dicts
        products_list = result["detected_products"][:5]
        if products_list and isinstance(products_list[0], dict):
            products_str = ", ".join(p.get("item", str(p)) for p in products_list)
        else:
            products_str = ", ".join(str(p) for p in products_list) if products_list else "none detected"

        panel_content = (
            f"[{urgency_style}]URGENCY: {urgency}[/{urgency_style}] | "
            f"Age: {result['age_hours']:.1f}h | "
            f"Location: {result['location']}\n\n"
            f"[bold cyan]@{video.creator.username}[/bold cyan] "
            f"({video.creator.follower_count:,} followers)\n"
            f"[bold]Video:[/bold] {video.url}\n\n"
            f"[bold]Description:[/bold]\n{video.description[:150]}...\n\n"
            f"[bold]Metrics:[/bold]\n"
            f"  Views: {video.view_count:,} | Likes: {video.like_count:,} | "
            f"Comments: {video.comment_count:,} | Shares: {video.share_count:,}\n"
            f"  Engagement Rate: {video.engagement_rate:.2f}%\n\n"
            f"[bold]Scores:[/bold]\n"
            f"  Composite: {result['composite_score']:.0f} | "
            f"Early Viral: {result['early_viral_score']:.0f} | "
            f"Sellability: {result['sellability_score']:.0f}\n"
            f"  Profit Potential: [bold]{result['profit_potential'].upper()}[/bold]\n\n"
            f"[bold]Fashion:[/bold]\n"
            f"  Category: {result['trend_category']}\n"
            f"  Products: {products_str}\n\n"
            f"[bold]Hashtags:[/bold] {', '.join(f'#{tag}' for tag in video.hashtags[:8])}"
        )

        console.print(Panel(
            panel_content,
            title=f"#{idx} - {'🔥 PRIORITY WINDOW' if result['in_priority_window'] else 'Standard'}",
            border_style="bright_blue" if result["in_priority_window"] else "dim",
            padding=(1, 2)
        ))

    # Summary statistics
    console.print("\n[bold]Summary Statistics[/bold]\n")

    total = len(results)
    in_priority = sum(1 for r in results if r["in_priority_window"])
    avg_score = sum(r["composite_score"] for r in results) / total
    avg_views = sum(r["video"].view_count for r in results) / total

    stats_table = Table(show_header=False, box=None, padding=(0, 2))
    stats_table.add_column("Metric", style="cyan", justify="right")
    stats_table.add_column("Value", style="yellow")

    stats_table.add_row("Total Viral Candidates", str(total))
    stats_table.add_row("In 6hr Priority Window", f"[bold]{in_priority}[/bold]")
    stats_table.add_row("Average Composite Score", f"{avg_score:.1f}")
    stats_table.add_row("Average Views", f"{avg_views:,.0f}")

    console.print(stats_table)

    # Urgency breakdown
    urgency_counts = {}
    for r in results:
        u = r["urgency"]
        urgency_counts[u] = urgency_counts.get(u, 0) + 1

    console.print("\n[bold]Urgency Levels:[/bold]")
    urgency_table = Table(show_header=False, box=None, padding=(0, 2))
    urgency_table.add_column("Level")
    urgency_table.add_column("Count", justify="right")

    for level in ["CRITICAL", "URGENT", "HIGH", "MEDIUM", "LOW"]:
        if level in urgency_counts:
            style = URGENCY_COLORS.get(level, "white")
            urgency_table.add_row(f"[{style}]{level}[/{style}]", str(urgency_counts[level]))

    console.print(urgency_table)

    console.print("\n[bold green]Demo complete![/bold green]")
    console.print("\n[dim]To run with real data, execute this on your local machine with Bright Data credentials.[/dim]")


if __name__ == "__main__":
    run_demo()
