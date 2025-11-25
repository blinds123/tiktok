"""
Advanced Viral Prediction Algorithm for TikTok Fashion Scraper.

This module implements world-class social media expertise for identifying
content that's about to go viral BEFORE it peaks. Uses velocity metrics,
engagement patterns, influencer analysis, and timing data to predict viral potential.

Author: Expert Social Media Analyst
"""

from datetime import datetime, time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from rich.console import Console
from rich.table import Table

from models.video import TikTokVideo, ViralCandidate

console = Console()


class ViralStage(Enum):
    """Enumeration of viral lifecycle stages."""
    EMERGING = "emerging"      # Just starting to gain traction
    RISING = "rising"          # Growing rapidly
    PEAKING = "peaking"        # At or near peak performance
    DECLINING = "declining"    # Past peak, losing momentum


@dataclass
class VelocityMetrics:
    """Container for velocity-based metrics."""
    views_per_hour: float
    engagement_per_hour: float
    likes_per_hour: float
    comments_per_hour: float
    shares_per_hour: float
    comment_to_like_ratio: float
    share_to_view_ratio: float

    def __repr__(self) -> str:
        return (
            f"VelocityMetrics(views/h={self.views_per_hour:.0f}, "
            f"engagement/h={self.engagement_per_hour:.0f}, "
            f"share_ratio={self.share_to_view_ratio:.4f})"
        )


@dataclass
class ViralPrediction:
    """Complete viral prediction analysis for a video."""
    video: TikTokVideo
    viral_score: float
    viral_stage: ViralStage
    velocity_metrics: VelocityMetrics
    follower_efficiency: float
    timing_score: float
    estimated_peak_views: int
    confidence: float
    reasons: List[str]

    def to_dict(self) -> Dict:
        """Convert prediction to dictionary format."""
        return {
            "video_id": self.video.video_id,
            "video_url": self.video.url,
            "creator": {
                "username": self.video.creator.username,
                "followers": self.video.creator.follower_count,
                "is_micro_influencer": self.video.creator.is_micro_influencer,
            },
            "current_metrics": {
                "views": self.video.view_count,
                "likes": self.video.like_count,
                "comments": self.video.comment_count,
                "shares": self.video.share_count,
                "engagement_rate": round(self.video.engagement_rate, 2),
                "hours_since_posted": round(self.video.hours_since_posted, 1),
            },
            "prediction": {
                "viral_score": round(self.viral_score, 2),
                "viral_stage": self.viral_stage.value,
                "confidence": round(self.confidence, 2),
                "estimated_peak_views": self.estimated_peak_views,
                "follower_efficiency": round(self.follower_efficiency, 2),
                "timing_score": round(self.timing_score, 2),
            },
            "velocity": {
                "views_per_hour": round(self.velocity_metrics.views_per_hour, 0),
                "engagement_per_hour": round(self.velocity_metrics.engagement_per_hour, 0),
                "share_to_view_ratio": round(self.velocity_metrics.share_to_view_ratio, 4),
                "comment_to_like_ratio": round(self.velocity_metrics.comment_to_like_ratio, 4),
            },
            "reasons": self.reasons,
        }


class ViralPredictor:
    """
    World-class viral prediction algorithm for TikTok fashion content.

    This predictor uses expert social media knowledge to identify content
    that's about to go viral BEFORE it peaks. It analyzes:

    - Velocity metrics (views/hour, engagement velocity)
    - Early viral signals (age vs performance thresholds)
    - Micro-influencer sweet spot (50k-150k followers)
    - Content timing patterns (posting time, day of week)
    - Engagement quality indicators

    The algorithm produces a 0-100 viral potential score using weighted
    factors optimized for early detection of trending content.
    """

    # Micro-influencer sweet spot range
    MICRO_INFLUENCER_MIN = 50_000
    MICRO_INFLUENCER_MAX = 150_000

    # Early viral signal thresholds (hours, min_views)
    EARLY_SIGNALS = [
        (6, 100_000, "extremely_hot"),   # Under 6h with 100k+ views
        (12, 500_000, "very_hot"),       # 6-12h with 500k+ views
        (24, 1_000_000, "hot"),          # 12-24h with 1M+ views
    ]

    # High engagement threshold
    HIGH_ENGAGEMENT_RATE = 10.0  # 10%+

    # Optimal posting windows for fashion content (UTC)
    OPTIMAL_POSTING_HOURS = [
        # Morning: 6-9 AM (when people get ready)
        (6, 9),
        # Lunch: 12-2 PM (lunch scroll time)
        (12, 14),
        # Evening: 6-9 PM (after work/school)
        (18, 21),
        # Night: 9-11 PM (before bed scroll)
        (21, 23),
    ]

    # Weekend multiplier (fashion content performs better on weekends)
    WEEKEND_MULTIPLIER = 1.2

    def __init__(self, timezone_offset: int = 0):
        """
        Initialize the viral predictor.

        Args:
            timezone_offset: Hours offset from UTC for timing analysis (default: 0)
        """
        self.timezone_offset = timezone_offset
        console.log(
            "[bold cyan]Initialized ViralPredictor with advanced prediction algorithms[/bold cyan]"
        )

    def calculate_velocity_metrics(self, video: TikTokVideo) -> VelocityMetrics:
        """
        Calculate velocity metrics for a video.

        Velocity metrics are the MOST IMPORTANT indicators for early viral detection.
        High velocity indicates content is gaining momentum rapidly.

        Args:
            video: TikTokVideo object to analyze

        Returns:
            VelocityMetrics object with calculated rates
        """
        hours = max(video.hours_since_posted, 0.1)  # Avoid division by zero

        # Calculate base velocity metrics
        views_per_hour = video.view_count / hours
        likes_per_hour = video.like_count / hours
        comments_per_hour = video.comment_count / hours
        shares_per_hour = video.share_count / hours

        # Total engagement velocity
        total_engagement = video.like_count + video.comment_count + video.share_count
        engagement_per_hour = total_engagement / hours

        # Quality ratios
        comment_to_like_ratio = (
            video.comment_count / video.like_count
            if video.like_count > 0 else 0
        )

        share_to_view_ratio = (
            video.share_count / video.view_count
            if video.view_count > 0 else 0
        )

        metrics = VelocityMetrics(
            views_per_hour=views_per_hour,
            engagement_per_hour=engagement_per_hour,
            likes_per_hour=likes_per_hour,
            comments_per_hour=comments_per_hour,
            shares_per_hour=shares_per_hour,
            comment_to_like_ratio=comment_to_like_ratio,
            share_to_view_ratio=share_to_view_ratio,
        )

        console.log(
            f"[dim]Velocity for {video.video_id[:8]}...: "
            f"{views_per_hour:.0f} views/h, "
            f"{engagement_per_hour:.0f} engagement/h[/dim]"
        )

        return metrics

    def calculate_follower_efficiency(self, video: TikTokVideo) -> float:
        """
        Calculate follower efficiency ratio.

        This measures how effectively a creator's content reaches beyond their
        follower base. Viral content has HIGH follower efficiency (views >> followers).

        The micro-influencer sweet spot (50k-150k) typically has the highest
        efficiency because the algorithm pushes their content more aggressively.

        Args:
            video: TikTokVideo object to analyze

        Returns:
            Follower efficiency ratio (views / followers)
        """
        if video.creator.follower_count == 0:
            return 0.0

        efficiency = video.view_count / video.creator.follower_count

        # Bonus for micro-influencers in the sweet spot
        if (self.MICRO_INFLUENCER_MIN <=
            video.creator.follower_count <=
            self.MICRO_INFLUENCER_MAX):
            efficiency *= 1.25  # 25% bonus
            console.log(
                f"[green]Micro-influencer bonus applied for "
                f"@{video.creator.username}[/green]"
            )

        return efficiency

    def calculate_timing_score(self, video: TikTokVideo) -> float:
        """
        Calculate timing score based on when video was posted.

        Fashion content performs better during specific hours and on weekends.
        This score reflects how optimal the posting time was.

        Args:
            video: TikTokVideo object to analyze

        Returns:
            Timing score (0.0 to 1.0, higher is better)
        """
        # Adjust for timezone
        posted_time = video.created_at
        adjusted_hour = (posted_time.hour + self.timezone_offset) % 24

        # Check if posted during optimal window
        in_optimal_window = False
        for start_hour, end_hour in self.OPTIMAL_POSTING_HOURS:
            if start_hour <= adjusted_hour < end_hour:
                in_optimal_window = True
                break

        # Base score
        timing_score = 0.8 if in_optimal_window else 0.4

        # Weekend bonus (Friday-Sunday)
        weekday = posted_time.weekday()
        if weekday >= 4:  # Friday = 4, Saturday = 5, Sunday = 6
            timing_score *= self.WEEKEND_MULTIPLIER
            console.log(
                f"[blue]Weekend bonus applied (posted on "
                f"{posted_time.strftime('%A')})[/blue]"
            )

        return min(timing_score, 1.0)  # Cap at 1.0

    def _calculate_velocity_score(
        self,
        velocity_metrics: VelocityMetrics,
        video: TikTokVideo
    ) -> Tuple[float, List[str]]:
        """
        Calculate velocity component of viral score.

        Returns:
            Tuple of (score, reasons)
        """
        score = 0.0
        reasons = []

        # Views per hour scoring (exponential scale)
        if velocity_metrics.views_per_hour >= 50_000:
            score += 35
            reasons.append(f"Extreme velocity: {velocity_metrics.views_per_hour:.0f} views/h")
        elif velocity_metrics.views_per_hour >= 20_000:
            score += 30
            reasons.append(f"Very high velocity: {velocity_metrics.views_per_hour:.0f} views/h")
        elif velocity_metrics.views_per_hour >= 10_000:
            score += 25
            reasons.append(f"High velocity: {velocity_metrics.views_per_hour:.0f} views/h")
        elif velocity_metrics.views_per_hour >= 5_000:
            score += 20
            reasons.append(f"Good velocity: {velocity_metrics.views_per_hour:.0f} views/h")
        elif velocity_metrics.views_per_hour >= 1_000:
            score += 15
            reasons.append(f"Moderate velocity: {velocity_metrics.views_per_hour:.0f} views/h")
        else:
            score += 5

        # Share ratio bonus (shares indicate viral potential)
        if velocity_metrics.share_to_view_ratio >= 0.05:
            score += 5
            reasons.append(
                f"Exceptional share ratio: {velocity_metrics.share_to_view_ratio:.2%}"
            )
        elif velocity_metrics.share_to_view_ratio >= 0.03:
            score += 3
            reasons.append(
                f"High share ratio: {velocity_metrics.share_to_view_ratio:.2%}"
            )

        # Comment ratio (high = engaging/controversial)
        if velocity_metrics.comment_to_like_ratio >= 0.15:
            score += 2
            reasons.append(
                f"High engagement: {velocity_metrics.comment_to_like_ratio:.2%} comment/like ratio"
            )

        return min(score, 35), reasons

    def _calculate_engagement_score(self, video: TikTokVideo) -> Tuple[float, List[str]]:
        """
        Calculate engagement component of viral score.

        Returns:
            Tuple of (score, reasons)
        """
        score = 0.0
        reasons = []

        engagement_rate = video.engagement_rate

        if engagement_rate >= 15:
            score = 25
            reasons.append(f"Exceptional engagement: {engagement_rate:.1f}%")
        elif engagement_rate >= self.HIGH_ENGAGEMENT_RATE:
            score = 20
            reasons.append(f"High engagement: {engagement_rate:.1f}%")
        elif engagement_rate >= 7:
            score = 15
            reasons.append(f"Good engagement: {engagement_rate:.1f}%")
        elif engagement_rate >= 5:
            score = 10
            reasons.append(f"Moderate engagement: {engagement_rate:.1f}%")
        else:
            score = 5

        return score, reasons

    def _calculate_follower_efficiency_score(
        self,
        follower_efficiency: float,
        video: TikTokVideo
    ) -> Tuple[float, List[str]]:
        """
        Calculate follower efficiency component of viral score.

        Returns:
            Tuple of (score, reasons)
        """
        score = 0.0
        reasons = []

        # High efficiency indicates algorithmic push
        if follower_efficiency >= 20:
            score = 20
            reasons.append(f"Massive reach: {follower_efficiency:.1f}x followers")
        elif follower_efficiency >= 10:
            score = 18
            reasons.append(f"Excellent reach: {follower_efficiency:.1f}x followers")
        elif follower_efficiency >= 5:
            score = 15
            reasons.append(f"Strong reach: {follower_efficiency:.1f}x followers")
        elif follower_efficiency >= 3:
            score = 12
            reasons.append(f"Good reach: {follower_efficiency:.1f}x followers")
        elif follower_efficiency >= 1:
            score = 8
            reasons.append(f"Moderate reach: {follower_efficiency:.1f}x followers")
        else:
            score = 3

        # Extra points for micro-influencers
        if video.creator.is_micro_influencer:
            score += 3
            reasons.append("Micro-influencer sweet spot (50k-150k followers)")

        return min(score, 20), reasons

    def _calculate_timing_score_component(
        self,
        timing_score: float
    ) -> Tuple[float, List[str]]:
        """
        Calculate timing component of viral score.

        Returns:
            Tuple of (score, reasons)
        """
        score = timing_score * 10  # Scale to 0-10 range
        reasons = []

        if timing_score >= 0.9:
            reasons.append("Optimal posting time + weekend")
        elif timing_score >= 0.7:
            reasons.append("Optimal posting time")

        return score, reasons

    def _calculate_share_ratio_score(
        self,
        velocity_metrics: VelocityMetrics
    ) -> Tuple[float, List[str]]:
        """
        Calculate share ratio component of viral score.

        Returns:
            Tuple of (score, reasons)
        """
        score = 0.0
        reasons = []

        share_ratio = velocity_metrics.share_to_view_ratio

        if share_ratio >= 0.05:
            score = 10
            reasons.append(f"Viral share pattern: {share_ratio:.2%}")
        elif share_ratio >= 0.03:
            score = 8
            reasons.append(f"High share rate: {share_ratio:.2%}")
        elif share_ratio >= 0.02:
            score = 6
            reasons.append(f"Good share rate: {share_ratio:.2%}")
        elif share_ratio >= 0.01:
            score = 4
            reasons.append(f"Moderate share rate: {share_ratio:.2%}")
        else:
            score = 2

        return score, reasons

    def _calculate_recency_multiplier(self, video: TikTokVideo) -> float:
        """
        Calculate recency multiplier for viral score.

        Newer videos get higher multipliers as they have more growth potential.
        """
        hours = video.hours_since_posted

        if hours < 6:
            return 1.5  # 50% boost for very fresh content
        elif hours < 12:
            return 1.3
        elif hours < 24:
            return 1.15
        elif hours < 48:
            return 1.0
        else:
            return 0.85  # Penalty for old content

    def predict_viral_potential(self, video: TikTokVideo) -> float:
        """
        Predict viral potential score (0-100).

        This is the core algorithm using a weighted formula:

        viral_score = (
            velocity_score * 0.35 +
            engagement_score * 0.25 +
            follower_efficiency_score * 0.20 +
            timing_score * 0.10 +
            share_ratio_score * 0.10
        ) * recency_multiplier

        Args:
            video: TikTokVideo object to analyze

        Returns:
            Viral potential score (0-100, higher = more viral potential)
        """
        # Calculate all components
        velocity_metrics = self.calculate_velocity_metrics(video)
        follower_efficiency = self.calculate_follower_efficiency(video)
        timing_score = self.calculate_timing_score(video)

        # Get weighted scores
        velocity_score, _ = self._calculate_velocity_score(velocity_metrics, video)
        engagement_score, _ = self._calculate_engagement_score(video)
        efficiency_score, _ = self._calculate_follower_efficiency_score(
            follower_efficiency, video
        )
        timing_component, _ = self._calculate_timing_score_component(timing_score)
        share_score, _ = self._calculate_share_ratio_score(velocity_metrics)

        # Calculate base score with weights
        base_score = (
            velocity_score * 0.35 +
            engagement_score * 0.25 +
            efficiency_score * 0.20 +
            timing_component * 0.10 +
            share_score * 0.10
        )

        # Apply recency multiplier
        recency_multiplier = self._calculate_recency_multiplier(video)
        final_score = base_score * recency_multiplier

        # Cap at 100
        return min(final_score, 100.0)

    def classify_viral_stage(self, video: TikTokVideo) -> ViralStage:
        """
        Classify the current viral stage of a video.

        Stages:
        - EMERGING: Early traction, under 6 hours with strong velocity
        - RISING: Growing rapidly, clear upward trend
        - PEAKING: At or near peak performance
        - DECLINING: Past peak, losing momentum

        Args:
            video: TikTokVideo object to analyze

        Returns:
            ViralStage enum value
        """
        hours = video.hours_since_posted
        velocity_metrics = self.calculate_velocity_metrics(video)

        # Check for early viral signals
        for max_hours, min_views, label in self.EARLY_SIGNALS:
            if hours <= max_hours and video.view_count >= min_views:
                if hours < 6:
                    return ViralStage.EMERGING
                elif hours < 12:
                    return ViralStage.RISING
                else:
                    return ViralStage.PEAKING

        # Check velocity for stage classification
        if velocity_metrics.views_per_hour >= 10_000:
            if hours < 12:
                return ViralStage.EMERGING
            elif hours < 24:
                return ViralStage.RISING
            else:
                return ViralStage.PEAKING

        elif velocity_metrics.views_per_hour >= 1_000:
            if hours < 24:
                return ViralStage.RISING
            else:
                return ViralStage.PEAKING

        else:
            # Low velocity - likely declining or never took off
            if hours > 48 or video.view_count < 10_000:
                return ViralStage.DECLINING
            else:
                return ViralStage.EMERGING

    def estimate_peak_views(self, video: TikTokVideo) -> int:
        """
        Estimate the final peak view count for a video.

        Uses current velocity, engagement patterns, and typical viral curves
        to project final performance.

        Args:
            video: TikTokVideo object to analyze

        Returns:
            Estimated peak view count
        """
        velocity_metrics = self.calculate_velocity_metrics(video)
        stage = self.classify_viral_stage(video)
        hours = video.hours_since_posted

        # Current views
        current_views = video.view_count

        # Estimate remaining growth based on stage
        if stage == ViralStage.EMERGING:
            # Very early, use velocity to project
            # Assume velocity will be maintained for 12h then decay
            remaining_hours = 12 - hours
            fast_growth = velocity_metrics.views_per_hour * remaining_hours

            # Then slower growth for next 36h
            slow_velocity = velocity_metrics.views_per_hour * 0.3
            slow_growth = slow_velocity * 36

            estimated_peak = current_views + fast_growth + slow_growth

        elif stage == ViralStage.RISING:
            # Strong growth phase, project with decay
            remaining_fast_hours = max(24 - hours, 0)
            fast_growth = velocity_metrics.views_per_hour * remaining_fast_hours * 0.8

            slow_growth = velocity_metrics.views_per_hour * 24 * 0.2

            estimated_peak = current_views + fast_growth + slow_growth

        elif stage == ViralStage.PEAKING:
            # Near peak, minimal additional growth
            additional_growth = velocity_metrics.views_per_hour * 12 * 0.3
            estimated_peak = current_views + additional_growth

        else:  # DECLINING
            # Past peak, minimal growth
            additional_growth = current_views * 0.1
            estimated_peak = current_views + additional_growth

        # Apply engagement multiplier (high engagement = better retention)
        engagement_multiplier = 1 + (video.engagement_rate / 100)
        estimated_peak *= engagement_multiplier

        # Apply follower efficiency factor
        follower_efficiency = self.calculate_follower_efficiency(video)
        if follower_efficiency >= 10:
            estimated_peak *= 1.2  # Strong algorithmic push

        return int(estimated_peak)

    def analyze_video(self, video: TikTokVideo) -> ViralPrediction:
        """
        Perform complete viral analysis on a video.

        Args:
            video: TikTokVideo object to analyze

        Returns:
            ViralPrediction object with complete analysis
        """
        # Calculate all metrics
        viral_score = self.predict_viral_potential(video)
        viral_stage = self.classify_viral_stage(video)
        velocity_metrics = self.calculate_velocity_metrics(video)
        follower_efficiency = self.calculate_follower_efficiency(video)
        timing_score = self.calculate_timing_score(video)
        estimated_peak = self.estimate_peak_views(video)

        # Gather reasons
        all_reasons = []

        _, velocity_reasons = self._calculate_velocity_score(velocity_metrics, video)
        all_reasons.extend(velocity_reasons)

        _, engagement_reasons = self._calculate_engagement_score(video)
        all_reasons.extend(engagement_reasons)

        _, efficiency_reasons = self._calculate_follower_efficiency_score(
            follower_efficiency, video
        )
        all_reasons.extend(efficiency_reasons)

        _, timing_reasons = self._calculate_timing_score_component(timing_score)
        all_reasons.extend(timing_reasons)

        _, share_reasons = self._calculate_share_ratio_score(velocity_metrics)
        all_reasons.extend(share_reasons)

        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(video, viral_score)

        return ViralPrediction(
            video=video,
            viral_score=viral_score,
            viral_stage=viral_stage,
            velocity_metrics=velocity_metrics,
            follower_efficiency=follower_efficiency,
            timing_score=timing_score,
            estimated_peak_views=estimated_peak,
            confidence=confidence,
            reasons=all_reasons,
        )

    def _calculate_confidence(self, video: TikTokVideo, viral_score: float) -> float:
        """Calculate confidence in prediction based on data quality."""
        confidence = 0.5  # Base confidence

        # More data = higher confidence
        if video.hours_since_posted >= 3:
            confidence += 0.1
        if video.hours_since_posted >= 6:
            confidence += 0.1

        # Higher view counts = more reliable
        if video.view_count >= 50_000:
            confidence += 0.1
        if video.view_count >= 100_000:
            confidence += 0.1

        # Strong signals = higher confidence
        if viral_score >= 80:
            confidence += 0.1

        return min(confidence, 1.0)

    def get_viral_candidates(
        self,
        videos: List[TikTokVideo],
        min_score: float = 70.0
    ) -> List[ViralPrediction]:
        """
        Filter videos to get high-potential viral candidates.

        Args:
            videos: List of TikTokVideo objects to analyze
            min_score: Minimum viral score threshold (default: 70)

        Returns:
            List of ViralPrediction objects for candidates above threshold
        """
        console.log(
            f"[cyan]Analyzing {len(videos)} videos for viral candidates "
            f"(min_score={min_score})[/cyan]"
        )

        candidates = []

        for video in videos:
            prediction = self.analyze_video(video)

            if prediction.viral_score >= min_score:
                candidates.append(prediction)
                console.log(
                    f"[green]  Candidate found: @{video.creator.username} - "
                    f"Score: {prediction.viral_score:.1f}, "
                    f"Stage: {prediction.viral_stage.value}[/green]"
                )

        console.log(
            f"[bold green]Found {len(candidates)} viral candidates "
            f"with score >= {min_score}[/bold green]"
        )

        return candidates

    def rank_by_viral_potential(
        self,
        candidates: List[ViralPrediction]
    ) -> List[ViralPrediction]:
        """
        Rank viral candidates by potential for maximum ROI.

        Prioritizes:
        1. High viral scores
        2. Early stage (more growth potential)
        3. High confidence
        4. Micro-influencers (better ROI)

        Args:
            candidates: List of ViralPrediction objects to rank

        Returns:
            Sorted list of ViralPrediction objects (best first)
        """
        def ranking_key(prediction: ViralPrediction) -> float:
            """Calculate composite ranking score."""
            score = prediction.viral_score

            # Stage bonus (earlier = better)
            stage_bonus = {
                ViralStage.EMERGING: 15,
                ViralStage.RISING: 10,
                ViralStage.PEAKING: 5,
                ViralStage.DECLINING: 0,
            }
            score += stage_bonus[prediction.viral_stage]

            # Confidence bonus
            score += prediction.confidence * 10

            # Micro-influencer bonus (better ROI)
            if prediction.video.creator.is_micro_influencer:
                score += 10

            return score

        ranked = sorted(candidates, key=ranking_key, reverse=True)

        console.log(
            f"[magenta]Ranked {len(ranked)} candidates by viral potential + ROI[/magenta]"
        )

        return ranked

    def print_prediction_report(
        self,
        predictions: List[ViralPrediction],
        top_n: int = 10
    ):
        """
        Print a rich console report of top viral predictions.

        Args:
            predictions: List of ViralPrediction objects
            top_n: Number of top predictions to display (default: 10)
        """
        if not predictions:
            console.log("[yellow]No predictions to display[/yellow]")
            return

        table = Table(title=f"Top {top_n} Viral Predictions")

        table.add_column("Rank", style="cyan", justify="right")
        table.add_column("Creator", style="green")
        table.add_column("Score", style="yellow", justify="right")
        table.add_column("Stage", style="magenta")
        table.add_column("Views", style="blue", justify="right")
        table.add_column("Est. Peak", style="blue", justify="right")
        table.add_column("Views/h", style="red", justify="right")
        table.add_column("Confidence", style="white", justify="right")

        for i, pred in enumerate(predictions[:top_n], 1):
            table.add_row(
                str(i),
                f"@{pred.video.creator.username}",
                f"{pred.viral_score:.1f}",
                pred.viral_stage.value.upper(),
                f"{pred.video.view_count:,}",
                f"{pred.estimated_peak_views:,}",
                f"{pred.velocity_metrics.views_per_hour:.0f}",
                f"{pred.confidence:.0%}",
            )

        console.print(table)

        # Print top prediction details
        if predictions:
            console.print("\n[bold]Top Prediction Details:[/bold]")
            top = predictions[0]
            console.print(f"  Creator: @{top.video.creator.username}")
            console.print(f"  Video: {top.video.url}")
            console.print(f"  Viral Score: {top.viral_score:.2f}/100")
            console.print(f"  Stage: {top.viral_stage.value.upper()}")
            console.print(f"  Current Views: {top.video.view_count:,}")
            console.print(f"  Estimated Peak: {top.estimated_peak_views:,}")
            console.print(f"  Growth Potential: {(top.estimated_peak_views / top.video.view_count):.1f}x")
            console.print("\n[bold]  Key Signals:[/bold]")
            for reason in top.reasons[:5]:
                console.print(f"    - {reason}")
