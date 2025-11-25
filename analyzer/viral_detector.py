"""Viral trend detection module for TikTok fashion scraper."""

from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Optional

from rich.console import Console

from models.video import TikTokVideo, TikTokCreator, ViralCandidate

console = Console()


class ViralTrendDetector:
    """
    Analyzes TikTok videos to identify viral trends among micro-influencers.

    This detector filters videos from micro-influencers (50k-150k followers),
    calculates creator averages, and identifies videos with exceptional
    performance that could indicate emerging viral trends.
    """

    def __init__(self, videos: List[TikTokVideo]):
        """
        Initialize the viral trend detector with a list of TikTok videos.

        Args:
            videos: List of TikTokVideo objects to analyze
        """
        self.videos = videos
        self.filtered_videos: List[TikTokVideo] = []
        self.viral_candidates: List[ViralCandidate] = []

        console.log(f"[cyan]Initialized ViralTrendDetector with {len(videos)} videos[/cyan]")

    def filter_by_follower_range(
        self,
        min_followers: int = 50_000,
        max_followers: int = 150_000
    ) -> List[TikTokVideo]:
        """
        Filter videos by creator follower count range.

        Args:
            min_followers: Minimum follower count (default: 50,000)
            max_followers: Maximum follower count (default: 150,000)

        Returns:
            List of filtered TikTokVideo objects
        """
        self.filtered_videos = [
            video for video in self.videos
            if min_followers <= video.creator.follower_count <= max_followers
        ]

        console.log(
            f"[green]Filtered to {len(self.filtered_videos)} videos from micro-influencers "
            f"({min_followers:,}-{max_followers:,} followers)[/green]"
        )

        return self.filtered_videos

    def filter_by_recency(self, hours: int = 24) -> List[TikTokVideo]:
        """
        Filter videos posted within the specified time window.

        Args:
            hours: Maximum hours since posting (default: 24)

        Returns:
            List of recent TikTokVideo objects
        """
        self.filtered_videos = [
            video for video in self.filtered_videos
            if video.hours_since_posted <= hours
        ]

        console.log(
            f"[green]Filtered to {len(self.filtered_videos)} videos posted "
            f"within last {hours} hours[/green]"
        )

        return self.filtered_videos

    def calculate_creator_averages(
        self,
        videos: Optional[List[TikTokVideo]] = None
    ) -> Dict[str, float]:
        """
        Calculate average view counts for each creator.

        Groups videos by creator and calculates their average view count,
        updating the creator's avg_views attribute.

        Args:
            videos: List of videos to analyze (defaults to filtered_videos)

        Returns:
            Dictionary mapping creator user_id to average view count
        """
        if videos is None:
            videos = self.filtered_videos

        # Group videos by creator
        creator_videos: Dict[str, List[TikTokVideo]] = defaultdict(list)
        for video in videos:
            creator_videos[video.creator.user_id].append(video)

        # Calculate averages for each creator
        creator_averages: Dict[str, float] = {}
        for user_id, creator_vids in creator_videos.items():
            total_views = sum(v.view_count for v in creator_vids)
            avg_views = total_views / len(creator_vids)
            creator_averages[user_id] = avg_views

            # Update the creator's avg_views attribute
            for video in creator_vids:
                video.creator.avg_views = avg_views

        console.log(
            f"[blue]Calculated averages for {len(creator_averages)} creators[/blue]"
        )

        return creator_averages

    def detect_viral_candidates(
        self,
        multiplier: float = 10.0
    ) -> List[ViralCandidate]:
        """
        Identify videos exceeding their creator's average views by the multiplier.

        Args:
            multiplier: View count multiplier threshold (default: 10.0)

        Returns:
            List of ViralCandidate objects
        """
        self.viral_candidates = []

        for video in self.filtered_videos:
            if video.is_viral_candidate(multiplier=multiplier):
                # Calculate view multiplier
                view_multiplier = (
                    video.view_count / video.creator.avg_views
                    if video.creator.avg_views > 0
                    else 0
                )

                # Create viral candidate
                candidate = ViralCandidate(
                    video=video,
                    viral_score=video.viral_score,
                    view_multiplier=view_multiplier
                )

                self.viral_candidates.append(candidate)

        console.log(
            f"[yellow]Detected {len(self.viral_candidates)} viral candidates "
            f"(>{multiplier}x average views)[/yellow]"
        )

        return self.viral_candidates

    def rank_candidates(self) -> List[ViralCandidate]:
        """
        Rank viral candidates by their viral score in descending order.

        Returns:
            Sorted list of ViralCandidate objects
        """
        self.viral_candidates.sort(key=lambda c: c.viral_score, reverse=True)

        console.log(
            f"[magenta]Ranked {len(self.viral_candidates)} candidates by viral score[/magenta]"
        )

        return self.viral_candidates

    def get_top_candidates(self, n: int = 20) -> List[ViralCandidate]:
        """
        Get the top N viral candidates.

        Args:
            n: Number of top candidates to return (default: 20)

        Returns:
            List of top N ViralCandidate objects
        """
        top_candidates = self.viral_candidates[:n]

        console.log(
            f"[bold green]Returning top {len(top_candidates)} viral candidates[/bold green]"
        )

        # Log top candidates summary
        if top_candidates:
            console.log("[bold]Top Viral Candidates:[/bold]")
            for i, candidate in enumerate(top_candidates[:5], 1):
                console.log(
                    f"  {i}. @{candidate.video.creator.username} - "
                    f"Score: {candidate.viral_score:.2f}, "
                    f"Views: {candidate.video.view_count:,} "
                    f"({candidate.view_multiplier:.1f}x avg)"
                )
            if len(top_candidates) > 5:
                console.log(f"  ... and {len(top_candidates) - 5} more")

        return top_candidates

    def analyze(
        self,
        min_followers: int = 50_000,
        max_followers: int = 150_000,
        recency_hours: int = 24,
        viral_multiplier: float = 10.0,
        top_n: int = 20
    ) -> List[ViralCandidate]:
        """
        Run complete viral trend analysis pipeline.

        This is a convenience method that executes all steps in sequence:
        1. Filter by follower range
        2. Filter by recency
        3. Calculate creator averages
        4. Detect viral candidates
        5. Rank candidates
        6. Return top N results

        Args:
            min_followers: Minimum follower count (default: 50,000)
            max_followers: Maximum follower count (default: 150,000)
            recency_hours: Maximum hours since posting (default: 24)
            viral_multiplier: View count multiplier threshold (default: 10.0)
            top_n: Number of top candidates to return (default: 20)

        Returns:
            List of top N ViralCandidate objects
        """
        console.log("[bold cyan]Starting viral trend analysis pipeline...[/bold cyan]")

        # Execute pipeline
        self.filter_by_follower_range(min_followers, max_followers)
        self.filter_by_recency(recency_hours)
        self.calculate_creator_averages()
        self.detect_viral_candidates(viral_multiplier)
        self.rank_candidates()
        results = self.get_top_candidates(top_n)

        console.log(
            f"[bold green]Analysis complete! Found {len(results)} viral candidates.[/bold green]"
        )

        return results

    def get_summary_stats(self) -> Dict[str, any]:
        """
        Get summary statistics about the analysis.

        Returns:
            Dictionary containing summary statistics
        """
        if not self.viral_candidates:
            return {
                "total_videos": len(self.videos),
                "filtered_videos": len(self.filtered_videos),
                "viral_candidates": 0,
                "avg_viral_score": 0,
                "top_viral_score": 0,
                "avg_view_multiplier": 0,
                "top_view_multiplier": 0,
            }

        viral_scores = [c.viral_score for c in self.viral_candidates]
        view_multipliers = [c.view_multiplier for c in self.viral_candidates]

        return {
            "total_videos": len(self.videos),
            "filtered_videos": len(self.filtered_videos),
            "viral_candidates": len(self.viral_candidates),
            "avg_viral_score": sum(viral_scores) / len(viral_scores),
            "top_viral_score": max(viral_scores),
            "avg_view_multiplier": sum(view_multipliers) / len(view_multipliers),
            "top_view_multiplier": max(view_multipliers),
        }

    def export_results(self) -> List[Dict]:
        """
        Export viral candidates as a list of dictionaries.

        Returns:
            List of dictionaries containing candidate data
        """
        return [candidate.to_dict() for candidate in self.viral_candidates]
