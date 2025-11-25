#!/usr/bin/env python3
"""TikTok Viral Fashion Scraper - Main CLI Application.

A powerful tool for discovering viral fashion trends from women micro-influencers
in USA, Canada, and UK. Optimized for early detection within 6 hours of posting.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from dotenv import load_dotenv, set_key

from config import Config
from scraper import BrightDataClient, TikTokScraper
from scraper.bright_data_client import BrightDataConfig
from analyzer import (
    ViralTrendDetector,
    FashionExtractor,
    ViralPredictor,
    ProductOpportunityScorer,
    ContentFilter,
    FilterConfig,
    EarlyViralFilter,
)
from models import TikTokVideo, ViralCandidate

# Initialize Rich console
console = Console()

# ASCII Art Banner
BANNER = """
[bold cyan]
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║   TikTok Viral Fashion Scraper                                         ║
║   Find emerging viral fashion from women micro-influencers             ║
║   Target: USA, Canada, UK | Priority: Videos < 6 hours old             ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
[/bold cyan]
"""

# Default target locations
TARGET_LOCATIONS = ["US", "CA", "GB"]

# Urgency color mapping
URGENCY_COLORS = {
    "CRITICAL": "bold red",
    "URGENT": "bold yellow",
    "HIGH": "green",
    "MEDIUM": "cyan",
    "LOW": "dim",
}


def print_banner():
    """Print application banner."""
    console.print(BANNER)


def load_config() -> Config:
    """Load configuration from environment variables."""
    load_dotenv()
    return Config.from_env()


def validate_config(config: Config) -> bool:
    """Validate configuration and display errors if any."""
    is_valid, error_msg = config.validate()
    if not is_valid:
        console.print(f"[bold red]Configuration Error:[/bold red] {error_msg}")
        console.print("\n[yellow]Tip:[/yellow] Run [cyan]python main.py configure[/cyan] to set up your configuration.")
        return False
    return True


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """TikTok Viral Fashion Scraper - Find emerging viral fashion trends.

    Discovers viral fashion content from women micro-influencers (50k-150k followers)
    in USA, Canada, and UK. Optimized for detecting videos within 6 hours of posting
    that are gaining massive traction (10x+ average views).
    """
    print_banner()


@cli.command()
@click.option(
    "--hashtags",
    "-h",
    multiple=True,
    help="Fashion hashtags to search (can specify multiple times)"
)
@click.option(
    "--min-followers",
    type=int,
    default=50000,
    help="Minimum follower count for creators (default: 50000)"
)
@click.option(
    "--max-followers",
    type=int,
    default=150000,
    help="Maximum follower count for creators (default: 150000)"
)
@click.option(
    "--viral-multiplier",
    type=float,
    default=10.0,
    help="Views multiplier threshold (default: 10 = 10x average)"
)
@click.option(
    "--hours",
    type=int,
    default=24,
    help="Only analyze videos from last N hours (default: 24)"
)
@click.option(
    "--priority-window",
    type=int,
    default=6,
    help="Priority window in hours for early detection (default: 6)"
)
@click.option(
    "--limit",
    "-l",
    type=int,
    default=20,
    help="Maximum number of results to return (default: 20)"
)
@click.option(
    "--locations",
    multiple=True,
    default=["US", "CA", "GB"],
    help="Target locations (default: US, CA, GB)"
)
@click.option(
    "--include-unverified-locations",
    is_flag=True,
    default=True,
    help="Include creators with unverified locations"
)
@click.option(
    "--strict-gender",
    is_flag=True,
    default=False,
    help="Only include confirmed female creators (stricter filter)"
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Export results to JSON file"
)
@click.option(
    "--include-products",
    is_flag=True,
    default=True,
    help="Include product opportunity scoring"
)
def scan(
    hashtags: tuple,
    min_followers: int,
    max_followers: int,
    viral_multiplier: float,
    hours: int,
    priority_window: int,
    limit: int,
    locations: tuple,
    include_unverified_locations: bool,
    strict_gender: bool,
    output: Optional[str],
    include_products: bool,
):
    """Scan TikTok for viral fashion content from women micro-influencers.

    This command searches TikTok fashion hashtags, filters for women creators
    in USA/Canada/UK, and identifies videos going viral within 6 hours of posting.

    Example:
        python main.py scan -h fashion -h ootd --limit 20

    The results are prioritized by:
    1. Videos in the 6-hour priority window (early viral detection)
    2. Viral score (views vs creator average)
    3. Fashion relevance
    """
    try:
        # Load configuration
        config = load_config()

        # Validate configuration
        if not validate_config(config):
            sys.exit(1)

        # Use provided hashtags or defaults
        search_hashtags = list(hashtags) if hashtags else [
            "fashion", "ootd", "fashiontiktok", "outfitinspo",
            "grwm", "fashionhaul", "tryonhaul", "styleinspo",
            "y2k", "coquette", "aesthetic", "streetstyle"
        ]

        # Create filter configuration
        filter_config = FilterConfig(
            allowed_locations=list(locations),
            target_gender="female",
            max_video_age_hours=hours,
            priority_window_hours=priority_window,
            min_followers=min_followers,
            max_followers=max_followers,
            required_niche="fashion",
            viral_multiplier=viral_multiplier,
        )

        # Display configuration
        console.print(Panel.fit(
            f"[bold]Scan Configuration[/bold]\n\n"
            f"[cyan]Target Audience:[/cyan]\n"
            f"  Locations: {', '.join(locations)}\n"
            f"  Gender: Women only {'(strict)' if strict_gender else '(inclusive)'}\n"
            f"  Followers: {min_followers:,} - {max_followers:,}\n\n"
            f"[cyan]Content Filters:[/cyan]\n"
            f"  Hashtags: {', '.join(f'#{h}' for h in search_hashtags[:6])}{'...' if len(search_hashtags) > 6 else ''}\n"
            f"  Niche: Fashion\n\n"
            f"[cyan]Viral Detection:[/cyan]\n"
            f"  Time Window: {hours} hours\n"
            f"  [bold yellow]Priority Window: {priority_window} hours (early detection)[/bold yellow]\n"
            f"  Viral Multiplier: {viral_multiplier}x average views\n"
            f"  Max Results: {limit}",
            title="Configuration",
            border_style="cyan"
        ))

        # Initialize clients and run scraping
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:

            # Step 1: Initialize clients
            task1 = progress.add_task("[cyan]Initializing Bright Data client...", total=1)
            bright_config = BrightDataConfig(
                api_token=config.bright_data_api_token,
                dataset_id=config.bright_data_dataset_id,
                proxy_host=config.bright_data_proxy_host,
                proxy_port=config.bright_data_proxy_port,
                proxy_username=config.bright_data_proxy_username,
                proxy_password=config.bright_data_proxy_password,
            )
            client = BrightDataClient(bright_config)
            scraper = TikTokScraper(client, config.bright_data_dataset_id)
            progress.update(task1, completed=1)

            # Step 2: Search hashtags
            task2 = progress.add_task(
                f"[cyan]Searching {len(search_hashtags)} fashion hashtags...",
                total=1
            )
            snapshot_id = scraper.search_by_hashtag(
                hashtags=search_hashtags,
                limit_per_hashtag=100  # Get more to filter down
            )
            progress.update(task2, completed=1)

            # Step 3: Wait for results
            task3 = progress.add_task("[cyan]Collecting data from TikTok...", total=100)

            def update_progress(state, status):
                progress.update(task3, description=f"[cyan]Status: {state}")

            raw_results = client.wait_for_snapshot(
                snapshot_id,
                timeout=600,
                poll_interval=15,
                progress_callback=update_progress
            )
            progress.update(task3, completed=100)

        console.print(f"\n[green]✓[/green] Collected {len(raw_results)} videos from TikTok")

        # Step 4: Parse videos
        console.print("\n[cyan]Parsing video data...[/cyan]")
        videos = []
        for raw_data in raw_results:
            video = scraper.parse_video_data(raw_data)
            if video:
                videos.append(video)

        console.print(f"[green]✓[/green] Successfully parsed {len(videos)} videos")

        if not videos:
            console.print("[yellow]No videos found. Try different hashtags or adjust your filters.[/yellow]")
            sys.exit(0)

        # Step 5: Apply content filters (location, gender, niche, timing)
        console.print("\n[cyan]Applying content filters...[/cyan]")
        content_filter = ContentFilter(filter_config)
        priority_candidates = content_filter.get_priority_candidates(videos, limit=limit * 2)

        if not priority_candidates:
            console.print("[yellow]No videos passed all filters.[/yellow]")
            console.print("\n[dim]Try adjusting these parameters:[/dim]")
            console.print("  • Increase follower range")
            console.print("  • Extend time window (--hours)")
            console.print("  • Add --include-unverified-locations")
            sys.exit(0)

        # Step 6: Analyze with ViralPredictor
        console.print("\n[cyan]Analyzing viral potential...[/cyan]")
        predictor = ViralPredictor()
        fashion_extractor = FashionExtractor()

        # Build final results
        final_results = []
        for candidate_data in priority_candidates[:limit]:
            video = candidate_data["video"]

            # Get viral prediction
            prediction = predictor.analyze_video(video)

            # Get fashion details
            fashion_score = fashion_extractor.calculate_fashion_score(video)
            products = fashion_extractor.extract_products(video.description, video.hashtags)
            trend_category = fashion_extractor.categorize_trend(video.hashtags, video.description)

            final_results.append({
                "video": video,
                "age_hours": candidate_data["age_hours"],
                "urgency": candidate_data["urgency"],
                "early_viral_score": candidate_data["early_viral_score"],
                "composite_score": candidate_data["composite_score"],
                "fashion_relevance": candidate_data["fashion_relevance"],
                "location": candidate_data["location"],
                "gender": candidate_data["gender"],
                "in_priority_window": candidate_data["in_priority_window"],
                "viral_prediction": prediction,
                "fashion_score": fashion_score,
                "detected_products": products,
                "trend_category": trend_category,
            })

        # Step 7: Add product opportunity scoring if requested
        if include_products:
            console.print("\n[cyan]Scoring product opportunities...[/cyan]")
            product_scorer = ProductOpportunityScorer()
            for result in final_results:
                sellability = product_scorer.calculate_sellability_score(result["video"])
                profit_potential = product_scorer.estimate_profit_potential(result["video"])
                result["sellability_score"] = sellability
                result["profit_potential"] = profit_potential.value

        console.print(f"[green]✓[/green] Analysis complete. Found {len(final_results)} viral candidates")

        # Step 8: Display results
        display_results_table(final_results, priority_window)

        # Step 9: Display summary
        display_summary_stats(final_results, priority_window)

        # Step 10: Export to JSON if requested
        if output:
            export_to_json(final_results, output)
            console.print(f"\n[green]✓[/green] Results exported to [cyan]{output}[/cyan]")

        console.print("\n[bold green]Scan complete![/bold green]")
        console.print(f"\n[dim]Videos in {priority_window}hr priority window: {sum(1 for r in final_results if r['in_priority_window'])}[/dim]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Scan cancelled by user.[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        console.print("\n[dim]For help, run: python main.py scan --help[/dim]")
        raise


@cli.command()
def configure():
    """Interactive configuration setup for Bright Data credentials.

    This command guides you through setting up your Bright Data API credentials
    and scraper preferences. Configuration is saved to a .env file.
    """
    console.print("\n[bold cyan]Configuration Setup[/bold cyan]\n")
    console.print("This wizard will help you configure the TikTok Viral Fashion Scraper.")
    console.print("Your settings will be saved to a [cyan].env[/cyan] file.\n")

    env_path = Path(".env")

    # API Token
    console.print("[bold]1. Bright Data API Token[/bold]")
    console.print("   Get your API token from: https://brightdata.com/cp/dashboard\n")

    current_token = ""
    if env_path.exists():
        load_dotenv()
        import os
        current_token = os.getenv("BRIGHT_DATA_API_TOKEN", "")

    if current_token:
        console.print(f"   Current: [dim]***{current_token[-4:]}[/dim]")
        if not Confirm.ask("   Update API token?", default=False):
            api_token = current_token
        else:
            api_token = Prompt.ask("   Enter new API token", password=True)
    else:
        api_token = Prompt.ask("   Enter API token", password=True)

    # Dataset ID
    console.print("\n[bold]2. TikTok Dataset ID (Optional)[/bold]")
    console.print("   Leave empty to use default Bright Data TikTok datasets\n")
    dataset_id = Prompt.ask("   Dataset ID", default="")

    # Scraping Parameters
    console.print("\n[bold]3. Default Scraping Parameters[/bold]\n")

    min_followers = Prompt.ask(
        "   Minimum follower count",
        default="50000"
    )

    max_followers = Prompt.ask(
        "   Maximum follower count",
        default="150000"
    )

    viral_multiplier = Prompt.ask(
        "   Viral multiplier (e.g., 10 = 10x average views)",
        default="10.0"
    )

    hours_lookback = Prompt.ask(
        "   Hours lookback (only recent videos)",
        default="24"
    )

    priority_window = Prompt.ask(
        "   Priority window hours (early viral detection)",
        default="6"
    )

    max_results = Prompt.ask(
        "   Maximum results to return",
        default="20"
    )

    # Create/update .env file
    console.print("\n[cyan]Saving configuration...[/cyan]")

    if not env_path.exists():
        env_path.write_text("")

    set_key(env_path, "BRIGHT_DATA_API_TOKEN", api_token)
    if dataset_id:
        set_key(env_path, "BRIGHT_DATA_DATASET_ID", dataset_id)
    set_key(env_path, "MIN_FOLLOWERS", min_followers)
    set_key(env_path, "MAX_FOLLOWERS", max_followers)
    set_key(env_path, "VIRAL_MULTIPLIER", viral_multiplier)
    set_key(env_path, "HOURS_LOOKBACK", hours_lookback)
    set_key(env_path, "PRIORITY_WINDOW", priority_window)
    set_key(env_path, "MAX_RESULTS", max_results)

    # Target settings (hardcoded for this use case)
    set_key(env_path, "TARGET_LOCATIONS", "US,CA,GB")
    set_key(env_path, "TARGET_GENDER", "female")
    set_key(env_path, "TARGET_NICHE", "fashion")

    console.print("\n[bold green]✓ Configuration saved successfully![/bold green]")
    console.print(f"\nYour settings are stored in [cyan]{env_path.absolute()}[/cyan]")
    console.print("\n[bold]Default Targeting:[/bold]")
    console.print("  • Locations: USA, Canada, UK")
    console.print("  • Gender: Women only")
    console.print("  • Niche: Fashion")
    console.print(f"  • Priority Window: {priority_window} hours (early viral detection)")
    console.print("\n[dim]You can now run:[/dim] [cyan]python main.py scan[/cyan]")


@cli.command()
def test_connection():
    """Test connection to Bright Data API.

    Verifies that your API credentials are valid and you can connect
    to the Bright Data service.
    """
    try:
        console.print("\n[bold cyan]Testing Bright Data Connection[/bold cyan]\n")

        # Load config
        config = load_config()

        if not config.bright_data_api_token:
            console.print("[bold red]Error:[/bold red] BRIGHT_DATA_API_TOKEN not set")
            console.print("\n[yellow]Run[/yellow] [cyan]python main.py configure[/cyan] [yellow]to set up your credentials[/yellow]")
            sys.exit(1)

        console.print(f"API Token: [dim]***{config.bright_data_api_token[-4:]}[/dim]")

        # Initialize client
        with console.status("[cyan]Connecting to Bright Data API...", spinner="dots"):
            bright_config = BrightDataConfig(
                api_token=config.bright_data_api_token,
                dataset_id=config.bright_data_dataset_id,
            )
            client = BrightDataClient(bright_config)

            # Try to get available datasets
            try:
                datasets = client.get_available_datasets()
                console.print("\n[bold green]✓ Connection successful![/bold green]")
                console.print(f"\nFound {len(datasets)} available datasets")

                if datasets:
                    console.print("\n[bold]Your Datasets:[/bold]")
                    for ds in datasets[:5]:
                        console.print(f"  • {ds.get('id', 'N/A')}: {ds.get('name', 'Unknown')}")
                    if len(datasets) > 5:
                        console.print(f"  ... and {len(datasets) - 5} more")

            except Exception as e:
                console.print(f"\n[bold yellow]⚠ Connection established but error fetching datasets:[/bold yellow]")
                console.print(f"[dim]{str(e)}[/dim]")
                console.print("\n[green]Your API token appears to be valid.[/green]")

        # Display configuration
        console.print("\n[bold]Current Configuration:[/bold]")
        config_table = Table(show_header=False, box=None, padding=(0, 2))
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="white")

        for key, value in config.to_dict().items():
            config_table.add_row(key, str(value))

        console.print(config_table)

        console.print("\n[bold]Target Filters (Hardcoded):[/bold]")
        console.print("  • Locations: USA, Canada, UK")
        console.print("  • Gender: Women only")
        console.print("  • Niche: Fashion")

        console.print("\n[dim]Ready to scan! Run:[/dim] [cyan]python main.py scan[/cyan]")

    except Exception as e:
        console.print(f"\n[bold red]✗ Connection failed:[/bold red] {str(e)}")
        console.print("\n[yellow]Please check:[/yellow]")
        console.print("  • Your API token is correct")
        console.print("  • You have internet connectivity")
        console.print("  • Your Bright Data account is active")
        sys.exit(1)


def display_results_table(results: list[dict], priority_window: int):
    """Display viral candidates in a beautiful Rich table."""
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
    table.add_column("Creator", style="green", width=15)
    table.add_column("Location", style="yellow", width=8)
    table.add_column("Age", justify="right", style="cyan", width=6)
    table.add_column("Views", justify="right", style="blue", width=10)
    table.add_column("Score", justify="right", style="magenta", width=8)
    table.add_column("Category", style="white", width=12)

    for idx, result in enumerate(results, 1):
        video = result["video"]
        creator = video.creator
        urgency = result["urgency"]
        urgency_style = URGENCY_COLORS.get(urgency, "white")

        # Format age
        age_hours = result["age_hours"]
        if age_hours < 1:
            age_str = f"{int(age_hours * 60)}m"
        else:
            age_str = f"{age_hours:.1f}h"

        # Priority window indicator
        if result["in_priority_window"]:
            age_str = f"[bold]{age_str}[/bold]"

        table.add_row(
            str(idx),
            f"[{urgency_style}]{urgency}[/{urgency_style}]",
            f"@{creator.username[:13]}",
            result["location"],
            age_str,
            f"{video.view_count:,}",
            f"{result['composite_score']:.0f}",
            result.get("trend_category", "fashion")[:12],
        )

    console.print(table)

    # Display detailed info for top candidates
    console.print(f"\n[bold]Top Candidates in {priority_window}-Hour Priority Window:[/bold]\n")

    priority_results = [r for r in results if r["in_priority_window"]][:5]

    if not priority_results:
        console.print("[yellow]No videos currently in the priority window. Showing top overall:[/yellow]\n")
        priority_results = results[:5]

    for idx, result in enumerate(priority_results, 1):
        video = result["video"]
        urgency = result["urgency"]
        urgency_style = URGENCY_COLORS.get(urgency, "white")

        # Products display
        products_str = ", ".join(result.get("detected_products", [])[:5])
        if not products_str:
            products_str = "[dim]none detected[/dim]"

        panel_content = (
            f"[{urgency_style}]URGENCY: {urgency}[/{urgency_style}] | "
            f"Age: {result['age_hours']:.1f} hours | "
            f"Location: {result['location']}\n\n"
            f"[bold cyan]@{video.creator.username}[/bold cyan] "
            f"({video.creator.follower_count:,} followers)\n"
            f"[bold]Video:[/bold] {video.url}\n\n"
            f"[bold]Description:[/bold]\n{video.description[:150]}{'...' if len(video.description) > 150 else ''}\n\n"
            f"[bold]Metrics:[/bold]\n"
            f"  Views: {video.view_count:,} | Likes: {video.like_count:,} | "
            f"Comments: {video.comment_count:,} | Shares: {video.share_count:,}\n"
            f"  Engagement Rate: {video.engagement_rate:.2f}%\n\n"
            f"[bold]Scores:[/bold]\n"
            f"  Composite: {result['composite_score']:.0f} | "
            f"Early Viral: {result['early_viral_score']:.0f} | "
            f"Fashion: {result['fashion_relevance']:.0f}\n"
        )

        if "sellability_score" in result:
            panel_content += f"  Sellability: {result['sellability_score']:.0f} | Profit: {result['profit_potential']}\n"

        panel_content += (
            f"\n[bold]Fashion:[/bold]\n"
            f"  Category: {result.get('trend_category', 'fashion')}\n"
            f"  Products: {products_str}\n\n"
            f"[bold]Hashtags:[/bold] {', '.join(f'#{tag}' for tag in video.hashtags[:8])}"
        )

        console.print(Panel(
            panel_content,
            title=f"#{idx} - {'PRIORITY' if result['in_priority_window'] else 'Standard'}",
            border_style="bright_blue" if result["in_priority_window"] else "dim",
            padding=(1, 2)
        ))


def display_summary_stats(results: list[dict], priority_window: int):
    """Display summary statistics."""
    console.print("\n[bold]Summary Statistics[/bold]\n")

    # Calculate stats
    total = len(results)
    in_priority = sum(1 for r in results if r["in_priority_window"])
    avg_score = sum(r["composite_score"] for r in results) / total if total else 0
    avg_views = sum(r["video"].view_count for r in results) / total if total else 0

    # Urgency breakdown
    urgency_counts = {}
    for r in results:
        u = r["urgency"]
        urgency_counts[u] = urgency_counts.get(u, 0) + 1

    # Location breakdown
    location_counts = {}
    for r in results:
        loc = r["location"]
        location_counts[loc] = location_counts.get(loc, 0) + 1

    # Category breakdown
    category_counts = {}
    for r in results:
        cat = r.get("trend_category", "unknown")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    stats_table = Table(show_header=False, box=None, padding=(0, 2))
    stats_table.add_column("Metric", style="cyan", justify="right")
    stats_table.add_column("Value", style="yellow")

    stats_table.add_row("Total Viral Candidates", str(total))
    stats_table.add_row(f"In {priority_window}hr Priority Window", f"[bold]{in_priority}[/bold]")
    stats_table.add_row("Average Composite Score", f"{avg_score:.1f}")
    stats_table.add_row("Average Views", f"{avg_views:,.0f}")

    console.print(stats_table)

    # Urgency breakdown
    if urgency_counts:
        console.print("\n[bold]Urgency Levels:[/bold]")
        urgency_table = Table(show_header=False, box=None, padding=(0, 2))
        urgency_table.add_column("Level", style="cyan")
        urgency_table.add_column("Count", style="yellow", justify="right")

        for level in ["CRITICAL", "URGENT", "HIGH", "MEDIUM", "LOW"]:
            if level in urgency_counts:
                style = URGENCY_COLORS.get(level, "white")
                urgency_table.add_row(f"[{style}]{level}[/{style}]", str(urgency_counts[level]))

        console.print(urgency_table)

    # Location breakdown
    if location_counts:
        console.print("\n[bold]Locations:[/bold]")
        loc_table = Table(show_header=False, box=None, padding=(0, 2))
        loc_table.add_column("Location", style="cyan")
        loc_table.add_column("Count", style="yellow", justify="right")

        for loc, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True):
            loc_table.add_row(loc, str(count))

        console.print(loc_table)

    # Category breakdown
    if category_counts:
        console.print("\n[bold]Fashion Categories:[/bold]")
        cat_table = Table(show_header=False, box=None, padding=(0, 2))
        cat_table.add_column("Category", style="cyan")
        cat_table.add_column("Count", style="yellow", justify="right")

        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:8]:
            cat_table.add_row(cat.title(), str(count))

        console.print(cat_table)


def export_to_json(results: list[dict], output_path: str):
    """Export results to JSON file."""
    export_data = {
        "generated_at": datetime.utcnow().isoformat(),
        "total_candidates": len(results),
        "filters": {
            "locations": ["US", "CA", "GB"],
            "gender": "female",
            "niche": "fashion",
        },
        "candidates": []
    }

    for result in results:
        video = result["video"]
        candidate_data = {
            "video_url": video.url,
            "video_id": video.video_id,
            "description": video.description,
            "creator": {
                "username": video.creator.username,
                "followers": video.creator.follower_count,
                "location": result["location"],
                "gender": result["gender"],
            },
            "metrics": {
                "views": video.view_count,
                "likes": video.like_count,
                "comments": video.comment_count,
                "shares": video.share_count,
                "engagement_rate": round(video.engagement_rate, 2),
            },
            "timing": {
                "age_hours": result["age_hours"],
                "urgency": result["urgency"],
                "in_priority_window": result["in_priority_window"],
                "posted_at": video.created_at.isoformat(),
            },
            "scores": {
                "composite": round(result["composite_score"], 1),
                "early_viral": round(result["early_viral_score"], 1),
                "fashion_relevance": round(result["fashion_relevance"], 1),
            },
            "fashion": {
                "category": result.get("trend_category", ""),
                "detected_products": result.get("detected_products", []),
            },
            "hashtags": video.hashtags,
        }

        if "sellability_score" in result:
            candidate_data["product_opportunity"] = {
                "sellability_score": round(result["sellability_score"], 1),
                "profit_potential": result["profit_potential"],
            }

        export_data["candidates"].append(candidate_data)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    cli()
