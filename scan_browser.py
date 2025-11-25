#!/usr/bin/env python3
"""TikTok Viral Fashion Scraper - Browser-Based Version.

Uses Bright Data Scraping Browser to scrape TikTok directly.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

from scraper.browser_scraper import TikTokBrowserScraper, BrowserScraperConfig
from analyzer import (
    FashionExtractor,
    ViralPredictor,
    ProductOpportunityScorer,
)
from analyzer.filters import EarlyViralFilter

console = Console()

BANNER = """
[bold cyan]
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║   TikTok Viral Fashion Scraper (Browser Mode)                         ║
║   Find emerging viral fashion from women micro-influencers             ║
║   Target: USA, Canada, UK | Priority: Videos < 6 hours old             ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
[/bold cyan]
"""

URGENCY_COLORS = {
    "CRITICAL": "bold red",
    "URGENT": "bold yellow",
    "HIGH": "green",
    "MEDIUM": "cyan",
    "LOW": "dim",
}


@click.command()
@click.option("--hashtags", "-h", multiple=True, default=["fashion", "ootd", "grwm"],
              help="Hashtags to search")
@click.option("--limit", "-l", default=20, help="Max results per hashtag")
@click.option("--output", "-o", help="Export results to JSON file")
def scan(hashtags, limit, output):
    """Scan TikTok for viral fashion content using Bright Data Scraping Browser."""

    console.print(BANNER)

    # Load environment
    load_dotenv()

    # Check credentials
    username = os.getenv("BRIGHT_DATA_USERNAME")
    password = os.getenv("BRIGHT_DATA_PASSWORD")

    if not username or not password:
        console.print("[bold red]Error:[/bold red] Bright Data credentials not found in .env")
        console.print("\nMake sure your .env file contains:")
        console.print("  BRIGHT_DATA_USERNAME=your_username")
        console.print("  BRIGHT_DATA_PASSWORD=your_password")
        sys.exit(1)

    console.print(f"[green]✓[/green] Credentials loaded")
    console.print(f"[cyan]Hashtags:[/cyan] {', '.join(f'#{h}' for h in hashtags)}")
    console.print(f"[cyan]Limit:[/cyan] {limit} videos per hashtag\n")

    # Run async scraper
    try:
        results = asyncio.run(run_scraper(list(hashtags), limit, username, password))

        if results:
            display_results(results)

            if output:
                export_results(results, output)
                console.print(f"\n[green]✓[/green] Results exported to {output}")
        else:
            console.print("[yellow]No results found. Try different hashtags.[/yellow]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print("\n[dim]Make sure your Bright Data Scraping Browser is active.[/dim]")
        sys.exit(1)


async def run_scraper(hashtags: list, limit: int, username: str, password: str) -> list:
    """Run the browser scraper and analyze results."""

    config = BrowserScraperConfig(
        host="brd.superproxy.io",
        port=9222,
        username=username,
        password=password,
    )

    scraper = TikTokBrowserScraper(config)

    console.print("[cyan]Connecting to Bright Data Scraping Browser...[/cyan]")

    # Scrape videos
    raw_videos = await scraper.search_fashion_videos(
        hashtags=hashtags,
        videos_per_hashtag=limit,
    )

    if not raw_videos:
        return []

    # Parse to video objects
    console.print("\n[cyan]Analyzing videos...[/cyan]")

    videos = []
    for raw in raw_videos:
        video = scraper.parse_to_video(raw)
        if video:
            videos.append(video)

    console.print(f"[green]✓[/green] Parsed {len(videos)} videos")

    # Analyze
    fashion_extractor = FashionExtractor()
    product_scorer = ProductOpportunityScorer()
    early_viral_filter = EarlyViralFilter()

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
            "in_priority_window": age_hours <= 6,
            "trend_category": trend_category,
            "detected_products": products,
            "sellability_score": round(sellability, 1),
            "profit_potential": profit.value,
        })

    # Sort by score
    results.sort(key=lambda x: -x["composite_score"])

    return results


def display_results(results: list):
    """Display results in a table."""

    console.print("\n[bold]Viral Fashion Trends Found[/bold]\n")

    table = Table(
        show_header=True,
        header_style="bold magenta",
        border_style="bright_blue",
    )

    table.add_column("#", justify="right", width=3)
    table.add_column("Urgency", width=10)
    table.add_column("Creator", width=18)
    table.add_column("Age", justify="right", width=6)
    table.add_column("Views", justify="right", width=10)
    table.add_column("Score", justify="right", width=8)
    table.add_column("Category", width=12)

    for idx, result in enumerate(results[:20], 1):
        video = result["video"]
        urgency = result["urgency"]
        urgency_style = URGENCY_COLORS.get(urgency, "white")

        age_str = f"{result['age_hours']:.1f}h"
        if result["in_priority_window"]:
            age_str = f"[bold]{age_str}[/bold]"

        table.add_row(
            str(idx),
            f"[{urgency_style}]{urgency}[/{urgency_style}]",
            f"@{video.creator.username[:16]}",
            age_str,
            f"{video.view_count:,}",
            f"{result['composite_score']:.0f}",
            result["trend_category"][:12],
        )

    console.print(table)

    # Show top 3 details
    console.print("\n[bold]Top 3 Candidates:[/bold]\n")

    for idx, result in enumerate(results[:3], 1):
        video = result["video"]
        urgency = result["urgency"]
        urgency_style = URGENCY_COLORS.get(urgency, "white")

        console.print(Panel(
            f"[{urgency_style}]URGENCY: {urgency}[/{urgency_style}]\n\n"
            f"[bold cyan]@{video.creator.username}[/bold cyan]\n"
            f"[bold]URL:[/bold] {video.url}\n\n"
            f"[bold]Description:[/bold]\n{video.description[:200]}...\n\n"
            f"[bold]Views:[/bold] {video.view_count:,} | "
            f"[bold]Likes:[/bold] {video.like_count:,} | "
            f"[bold]Age:[/bold] {result['age_hours']:.1f}h\n"
            f"[bold]Score:[/bold] {result['composite_score']:.0f} | "
            f"[bold]Category:[/bold] {result['trend_category']}",
            title=f"#{idx}",
            border_style="bright_blue" if result["in_priority_window"] else "dim",
        ))


def export_results(results: list, output_path: str):
    """Export results to JSON."""

    export_data = {
        "generated_at": datetime.utcnow().isoformat(),
        "total": len(results),
        "candidates": []
    }

    for result in results:
        video = result["video"]
        export_data["candidates"].append({
            "url": video.url,
            "creator": video.creator.username,
            "views": video.view_count,
            "likes": video.like_count,
            "age_hours": result["age_hours"],
            "urgency": result["urgency"],
            "score": result["composite_score"],
            "category": result["trend_category"],
            "description": video.description,
        })

    with open(output_path, "w") as f:
        json.dump(export_data, f, indent=2)


if __name__ == "__main__":
    scan()
