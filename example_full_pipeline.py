#!/usr/bin/env python3
"""Full Pipeline Example - Viral Detection + Fashion Extraction + Product Scoring.

This example shows how to integrate all three analyzers:
1. ViralTrendDetector - Find viral videos
2. FashionExtractor - Extract fashion information
3. ProductOpportunityScorer - Score product opportunities
"""

from datetime import datetime
from rich.console import Console
from rich.panel import Panel

from models.video import TikTokVideo, TikTokCreator
from analyzer.viral_detector import ViralTrendDetector
from analyzer.fashion_extractor import FashionExtractor
from analyzer.product_scorer import ProductOpportunityScorer

console = Console()


def create_sample_dataset():
    """Create a realistic dataset of TikTok videos."""
    videos = []

    # Mix of micro-influencers with various content types
    creators_data = [
        ("user1", "fashion_finds", 75_000, 50_000),
        ("user2", "thrift_queen", 85_000, 60_000),
        ("user3", "style_guru", 120_000, 80_000),
        ("user4", "outfit_inspo", 95_000, 70_000),
        ("user5", "budget_fashion", 65_000, 45_000),
    ]

    video_data = [
        # High-intent shapewear video
        {
            "desc": "OMG this SKIMS dupe from Amazon is INCREDIBLE! Under $25 and it snatches everything! Link in bio, use code SHAPE20 for 20% off. Selling out FAST! #shapewear #amazonfind #bodygoals",
            "views": 850_000,
            "likes": 85_000,
            "comments": 6_200,
            "shares": 4_100,
            "hashtags": ["shapewear", "amazonfind", "bodygoals", "fashion", "ootd"],
        },
        # Viral coquette accessories
        {
            "desc": "These claw clips are EVERYWHERE rn 🎀 so coquette! Just $10 on Amazon, comes in 12 colors. Everyone is asking where I got them! Shop link in bio #coquette #balletcore #bow #aesthetic",
            "views": 1_200_000,
            "likes": 120_000,
            "comments": 8_500,
            "shares": 5_800,
            "hashtags": ["coquette", "balletcore", "bow", "aesthetic", "fashion"],
        },
        # Luxury dupe bag
        {
            "desc": "STOP SCROLLING! This $30 bag looks EXACTLY like the $2500 Bottega dupe! Amazon find, link in bio. Trust me you need this! #dupe #luxurydupe #amazonfashion #bottegaveneta",
            "views": 950_000,
            "likes": 92_000,
            "comments": 7_100,
            "shares": 4_900,
            "hashtags": ["dupe", "luxurydupe", "amazonfashion", "bottegaveneta"],
        },
        # Lower intent thrift video
        {
            "desc": "Amazing thrift haul from Goodwill! Found this vintage 90s denim jacket for $8. Sustainable fashion FTW 🌱 #thrifted #vintage #sustainable #slowfashion",
            "views": 180_000,
            "likes": 15_000,
            "comments": 890,
            "shares": 450,
            "hashtags": ["thrifted", "vintage", "sustainable", "slowfashion"],
        },
        # Problem-solving fashion
        {
            "desc": "These no-show socks changed my LIFE! Finally socks that don't slip! Under $15 for 6 pairs on Amazon. Link in bio! Game changer for sneaker girls! #amazonfind #fashion #musthave",
            "views": 620_000,
            "likes": 58_000,
            "comments": 4_200,
            "shares": 2_800,
            "hashtags": ["amazonfind", "fashion", "musthave", "lifehack"],
        },
    ]

    for i, (uid, username, followers, avg_views) in enumerate(creators_data):
        if i < len(video_data):
            data = video_data[i]

            creator = TikTokCreator(
                user_id=uid,
                username=username,
                nickname=username.replace("_", " ").title(),
                follower_count=followers,
                avg_views=avg_views,
            )

            video = TikTokVideo(
                video_id=f"v{i+1:03d}",
                url=f"https://tiktok.com/@{username}/video/{i+1000}",
                description=data["desc"],
                creator=creator,
                view_count=data["views"],
                like_count=data["likes"],
                comment_count=data["comments"],
                share_count=data["shares"],
                created_at=datetime.utcnow(),
                hashtags=data["hashtags"],
            )

            videos.append(video)

    return videos


def main():
    """Run complete pipeline analysis."""

    console.print("\n[bold cyan]" + "=" * 80 + "[/bold cyan]")
    console.print("[bold cyan]  FULL PIPELINE: Fashion Extraction → Product Scoring[/bold cyan]")
    console.print("[bold cyan]" + "=" * 80 + "[/bold cyan]\n")

    # Step 1: Create dataset
    console.print("[yellow]Step 1: Creating sample TikTok dataset...[/yellow]")
    videos = create_sample_dataset()
    console.print(f"[green]Created {len(videos)} sample videos[/green]\n")

    # Step 2: Fashion Extraction
    console.print("[yellow]Step 2: Extracting Fashion Information...[/yellow]")
    extractor = FashionExtractor()

    fashion_videos = []
    for video in videos:
        if extractor.is_fashion_content(video):
            fashion_videos.append(video)

    console.print(f"[green]Identified {len(fashion_videos)} fashion videos[/green]\n")

    # Step 3: Product Opportunity Scoring
    console.print("[yellow]Step 3: Scoring Product Opportunities...[/yellow]")
    scorer = ProductOpportunityScorer()
    opportunities = scorer.get_top_opportunities(fashion_videos, limit=20)
    console.print(f"[green]Scored {len(opportunities)} product opportunities[/green]\n")

    # Step 5: Display Results
    console.print("\n[bold magenta]" + "=" * 80 + "[/bold magenta]")
    console.print("[bold magenta]  TOP PRODUCT OPPORTUNITIES[/bold magenta]")
    console.print("[bold magenta]" + "=" * 80 + "[/bold magenta]\n")

    # Show table
    if opportunities:
        table = scorer.export_opportunities_table(opportunities)
        console.print(table)
        console.print()

    # Step 6: Detailed Analysis of Top 3
    console.print("\n[bold magenta]" + "=" * 80 + "[/bold magenta]")
    console.print("[bold magenta]  DETAILED REPORTS FOR TOP 3 OPPORTUNITIES[/bold magenta]")
    console.print("[bold magenta]" + "=" * 80 + "[/bold magenta]\n")

    for i, opportunity in enumerate(opportunities[:3], 1):
        console.print(f"\n[bold cyan]═══ OPPORTUNITY #{i} ═══[/bold cyan]\n")
        scorer.generate_product_report(opportunity)

        # Additional insights
        video = opportunity.video
        console.print(f"\n[yellow]Fashion Category:[/yellow] {opportunity.video.creator.username}")

        if hasattr(video, 'viral_score'):
            console.print(f"[yellow]Viral Score:[/yellow] {video.viral_score:.2f}")

        console.print()

    # Step 7: Summary Statistics
    console.print("\n[bold magenta]" + "=" * 80 + "[/bold magenta]")
    console.print("[bold magenta]  PIPELINE SUMMARY[/bold magenta]")
    console.print("[bold magenta]" + "=" * 80 + "[/bold magenta]\n")

    top_opp = opportunities[0] if opportunities else None

    summary_panel = f"""
[cyan]Pipeline Results:[/cyan]
• Total Videos Analyzed: {len(videos)}
• Fashion Videos Identified: {len(fashion_videos)}
• Product Opportunities: {len(opportunities)}

[green]Top Opportunity:[/green]
• Product: {top_opp.category.value if top_opp else 'N/A'}
• Sellability Score: {f'{top_opp.sellability_score:.1f}/100' if top_opp else 'N/A'}
• Profit Potential: {top_opp.profit_potential.value if top_opp else 'N/A'}
• Creator: @{top_opp.video.creator.username if top_opp else 'N/A'}

[yellow]Recommendations:[/yellow]
• HIGH PRIORITY products (80+ score): {sum(1 for o in opportunities if o.sellability_score >= 80)}
• MEDIUM PRIORITY products (60-79 score): {sum(1 for o in opportunities if 60 <= o.sellability_score < 80)}
• LOW PRIORITY products (<60 score): {sum(1 for o in opportunities if o.sellability_score < 60)}

[red]Action Items:[/red]
• Launch top {min(3, len([o for o in opportunities if o.sellability_score >= 80]))} opportunities within 48 hours
• Allocate $500+ test budget for each HIGH PRIORITY product
• Repurpose viral videos as ad creative
"""

    panel = Panel(summary_panel, title="[bold green]Pipeline Complete![/bold green]", border_style="green")
    console.print(panel)

    console.print("\n[bold green]✓ Full pipeline analysis complete![/bold green]\n")


if __name__ == "__main__":
    main()
