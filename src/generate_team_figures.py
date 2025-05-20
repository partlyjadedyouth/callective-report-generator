#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import scipy.stats as stats
from pathlib import Path
import matplotlib.font_manager as fm
import matplotlib as mpl
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle
import datetime  # For date formatting and day of week calculation

# 절단점 값을 가져오기 위한 임포트
from cutoff_values import (
    CUTOFF_BURNOUT_PRIMARY,
    CUTOFF_BURNOUT_EXHAUSTION,
    CUTOFF_BURNOUT_DEPERSONALIZATION,
    CUTOFF_BURNOUT_COGNITIVE_REGULATION,
    CUTOFF_BURNOUT_EMOTIONAL_REGULATION,
    CUTOFF_STRESS,
    CUTOFF_JOB_DEMAND,
    CUTOFF_INSUFFICIENT_JOB_CONTROL,
    CUTOFF_INTERPERSONAL_CONFLICT,
    CUTOFF_JOB_INSECURITY,
    CUTOFF_ORGANIZATIONAL_SYSTEM,
    CUTOFF_LACK_OF_REWARD,
    CUTOFF_OCCUPATIONAL_CLIMATE,
    CUTOFF_EMOTIONAL_LABOR,
)


def generate_bat_primary_distribution_graph(week_number=0, team_number=None):
    """
    Generate a distribution graph for BAT_primary scores for a specific week

    Parameters:
    - week_number (int): Week number (0, 2, 4, etc.)
    - team_number (int or None): Team number to highlight (1, 2, 3, etc.)
    """
    # Create figures directory if it doesn't exist
    output_dir = f"data/figures/상담 {team_number}팀"
    os.makedirs(output_dir, exist_ok=True)

    # Load analysis data
    with open("data/analysis/analysis.json", "r", encoding="utf-8") as f:
        analysis_data = json.load(f)

    # 외부 모듈에서 가져온 절단점 사용
    cutoff_burnout_primary = CUTOFF_BURNOUT_PRIMARY

    # Collect BAT_primary scores for the specified week
    all_scores = []  # List to store scores from all participants
    team_scores = []  # List to store scores from the specified team
    week_key = f"{week_number}주차"

    for participant in analysis_data["participants"]:
        # Check if participant has data for the specified week
        if week_key in participant["analysis"]:
            # Get the BAT_primary score for this participant
            score = participant["analysis"][week_key]["category_averages"].get(
                "BAT_primary"
            )

            if score is not None:
                # Add to all scores list
                all_scores.append(score)

                # If team is specified, collect scores for that team
                if (
                    team_number is not None
                    and participant["team"] == f"상담 {team_number}팀"
                ):
                    team_scores.append(score)

    # Create the plot with a clean, modern style
    plt.figure(figsize=(10, 6))
    plt.style.use("seaborn-v0_8-whitegrid")

    # Create x values for the distributions (범위를 1에서 5까지로 설정)
    x = np.linspace(1, 5, 1000)  # Adjusted to focus on the valid score range (1-5)

    # Plot normal distribution for all participants (black dotted line)
    if all_scores:
        # Calculate mean and standard deviation for all participants
        mu_all = np.mean(all_scores)
        std_all = np.std(all_scores)
        # Plot normal distribution curve (black dotted line)
        plt.plot(
            x,
            stats.norm.pdf(x, mu_all, std_all),
            "k--",
            label="Overall",
            linewidth=1.5,
        )

    # Plot normal distribution for team participants (blue solid line)
    if team_scores:
        # Calculate mean and standard deviation for team participants
        mu_team = np.mean(team_scores)
        std_team = np.std(team_scores)
        # Plot normal distribution curve (blue solid line)
        plt.plot(
            x,
            stats.norm.pdf(x, mu_team, std_team),
            "b-",
            label=f"Team {team_number}",
            linewidth=2,
        )

    # Standardize y-axis limits to be between 0 and 1.0 for all team graphs
    plt.ylim(0, 1.0)

    # Set consistent y-axis ticks
    plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])

    # Get the maximum y value for filling background colors (use fixed value now)
    ymax = 1.0

    # Draw vertical lines at cutoff values
    plt.axvline(x=cutoff_burnout_primary[0], color="gray", linestyle="--", alpha=0.5)
    plt.axvline(x=cutoff_burnout_primary[1], color="gray", linestyle="--", alpha=0.5)

    # Fill background regions with colors (green, yellow, pink)
    # Normal range (light green)
    plt.fill_between(
        x, 0, ymax, where=(x < cutoff_burnout_primary[0]), color="lightgreen", alpha=0.3
    )
    # Warning range (light yellow)
    plt.fill_between(
        x,
        0,
        ymax,
        where=(x >= cutoff_burnout_primary[0]) & (x < cutoff_burnout_primary[1]),
        color="lightyellow",
        alpha=0.3,
    )
    # Risk range (light pink)
    plt.fill_between(
        x, 0, ymax, where=(x >= cutoff_burnout_primary[1]), color="lightpink", alpha=0.3
    )

    # Set labels and title
    plt.xlabel("Burnout Score", fontsize=12)
    plt.ylabel("Density", fontsize=12)
    plt.title(f"Team {team_number} Burnout Score Distribution", fontsize=14)

    # Add legend with proper placement
    plt.legend(loc="upper right")

    # Calculate statistics for display box
    if team_scores:
        # Count participants in each category
        normal_count = sum(
            1 for score in team_scores if score <= cutoff_burnout_primary[0]
        )
        warning_count = sum(
            1
            for score in team_scores
            if score > cutoff_burnout_primary[0] and score <= cutoff_burnout_primary[1]
        )
        risk_count = sum(
            1 for score in team_scores if score > cutoff_burnout_primary[1]
        )

    # Set x-axis limits to show only the valid range (1-5)
    plt.xlim(1, 5)  # Fixed range for BAT_primary scores that only exist from 1 to 5

    # Add tick marks at each integer score
    plt.xticks(range(1, 6))

    # Adjust layout
    plt.tight_layout()
    # Save the figure with high resolution (300 DPI)
    plt.savefig(
        f"{output_dir}/{week_number}주차_번아웃_상담 {team_number}팀.png", dpi=300
    )
    plt.close()

    print(
        f"Graph saved to {output_dir}/{week_number}주차_번아웃_상담 {team_number}팀.png"
    )


def generate_exhaustion_distribution_graph(week_number=0, team_number=None):
    """
    Generate a distribution graph for exhaustion (탈진) scores for a specific week

    Parameters:
    - week_number (int): Week number (0, 2, 4, etc.)
    - team_number (int or None): Team number to highlight (1, 2, 3, etc.)
    """
    # Create figures directory if it doesn't exist
    output_dir = f"data/figures/상담 {team_number}팀"
    os.makedirs(output_dir, exist_ok=True)

    # Load analysis data
    with open("data/analysis/analysis.json", "r", encoding="utf-8") as f:
        analysis_data = json.load(f)

    # 외부 모듈에서 가져온 절단점 사용
    cutoff_burnout_exhaustion = CUTOFF_BURNOUT_EXHAUSTION

    # Collect exhaustion scores for the specified week
    all_scores = []  # List to store scores from all participants
    team_scores = []  # List to store scores from the specified team
    week_key = f"{week_number}주차"

    for participant in analysis_data["participants"]:
        # Check if participant has data for the specified week
        if week_key in participant["analysis"]:
            # Get the exhaustion score for this participant
            try:
                # Access the "탈진" (exhaustion) score from type_averages
                score = participant["analysis"][week_key]["type_averages"][
                    "BAT_primary"
                ].get("탈진")

                if score is not None:
                    # Add to all scores list
                    all_scores.append(score)

                    # If team is specified, collect scores for that team
                    if (
                        team_number is not None
                        and participant["team"] == f"상담 {team_number}팀"
                    ):
                        team_scores.append(score)
            except (KeyError, TypeError):
                # Skip if the score is not available
                continue

    # Create the plot with a clean, modern style
    plt.figure(figsize=(10, 6))
    plt.style.use("seaborn-v0_8-whitegrid")

    # Create x values for the distributions (범위를 1에서 5까지로 설정)
    x = np.linspace(1, 5, 1000)  # Adjusted to focus on the valid score range (1-5)

    # Plot normal distribution for all participants (black dotted line)
    if all_scores:
        # Calculate mean and standard deviation for all participants
        mu_all = np.mean(all_scores)
        std_all = np.std(all_scores)
        # Plot normal distribution curve (black dotted line)
        plt.plot(
            x,
            stats.norm.pdf(x, mu_all, std_all),
            "k--",
            label="Overall",
            linewidth=1.5,
        )

    # Plot normal distribution for team participants (blue solid line)
    if team_scores:
        # Calculate mean and standard deviation for team participants
        mu_team = np.mean(team_scores)
        std_team = np.std(team_scores)
        # Plot normal distribution curve (blue solid line)
        plt.plot(
            x,
            stats.norm.pdf(x, mu_team, std_team),
            "b-",
            label=f"Team {team_number}",
            linewidth=2,
        )

    # Get the maximum y value for filling background colors
    ax = plt.gca()
    ymax = ax.get_ylim()[1]

    # Draw vertical lines at cutoff values
    plt.axvline(x=cutoff_burnout_exhaustion[0], color="gray", linestyle="--", alpha=0.5)
    plt.axvline(x=cutoff_burnout_exhaustion[1], color="gray", linestyle="--", alpha=0.5)

    # Fill background regions with colors (green, yellow, pink)
    # Normal range (light green)
    plt.fill_between(
        x,
        0,
        ymax,
        where=(x < cutoff_burnout_exhaustion[0]),
        color="lightgreen",
        alpha=0.3,
    )
    # Warning range (light yellow)
    plt.fill_between(
        x,
        0,
        ymax,
        where=(x >= cutoff_burnout_exhaustion[0]) & (x < cutoff_burnout_exhaustion[1]),
        color="lightyellow",
        alpha=0.3,
    )
    # Risk range (light pink)
    plt.fill_between(
        x,
        0,
        ymax,
        where=(x >= cutoff_burnout_exhaustion[1]),
        color="lightpink",
        alpha=0.3,
    )

    # Set labels and title
    plt.xlabel("Exhaustion Score", fontsize=12)
    plt.ylabel("Density", fontsize=12)
    plt.title(f"Team {team_number} Exhaustion Score Distribution", fontsize=14)

    # Add legend with proper placement
    plt.legend(loc="upper right")

    # Calculate statistics for display box
    if team_scores:
        # Count participants in each category
        normal_count = sum(
            1 for score in team_scores if score <= cutoff_burnout_exhaustion[0]
        )
        warning_count = sum(
            1
            for score in team_scores
            if score > cutoff_burnout_exhaustion[0]
            and score <= cutoff_burnout_exhaustion[1]
        )
        risk_count = sum(
            1 for score in team_scores if score > cutoff_burnout_exhaustion[1]
        )

    # Set x-axis limits to show only the valid range (1-5)
    plt.xlim(1, 5)  # Fixed range for exhaustion scores that only exist from 1 to 5

    # Add tick marks at each integer score
    plt.xticks(range(1, 6))

    # Adjust layout
    plt.tight_layout()
    # Save the figure with high resolution (300 DPI)
    plt.savefig(
        f"{output_dir}/{week_number}주차_탈진_상담 {team_number}팀.png", dpi=300
    )
    plt.close()

    print(
        f"Graph saved to {output_dir}/{week_number}주차_탈진_상담 {team_number}팀.png"
    )


def generate_cognitive_regulation_distribution_graph(week_number=0, team_number=None):
    """
    Generate a distribution graph for cognitive regulation (인지적 조절) scores for a specific week

    Parameters:
    - week_number (int): Week number (0, 2, 4, etc.)
    - team_number (int or None): Team number to highlight (1, 2, 3, etc.)
    """
    # Create figures directory if it doesn't exist
    output_dir = f"data/figures/상담 {team_number}팀"
    os.makedirs(output_dir, exist_ok=True)

    # Load analysis data
    with open("data/analysis/analysis.json", "r", encoding="utf-8") as f:
        analysis_data = json.load(f)

    # 외부 모듈에서 가져온 절단점 사용
    cutoff_burnout_cognitive_regulation = CUTOFF_BURNOUT_COGNITIVE_REGULATION

    # Collect cognitive regulation scores for the specified week
    all_scores = []  # List to store scores from all participants
    team_scores = []  # List to store scores from the specified team
    week_key = f"{week_number}주차"

    for participant in analysis_data["participants"]:
        # Check if participant has data for the specified week
        if week_key in participant["analysis"]:
            # Get the cognitive regulation score for this participant
            try:
                # Access the "인지적 조절" (cognitive regulation) score from type_averages
                score = participant["analysis"][week_key]["type_averages"][
                    "BAT_primary"
                ].get("인지적 조절")

                if score is not None:
                    # Add to all scores list
                    all_scores.append(score)

                    # If team is specified, collect scores for that team
                    if (
                        team_number is not None
                        and participant["team"] == f"상담 {team_number}팀"
                    ):
                        team_scores.append(score)
            except (KeyError, TypeError):
                # Skip if the score is not available
                continue

    # Create the plot with a clean, modern style
    plt.figure(figsize=(10, 6))
    plt.style.use("seaborn-v0_8-whitegrid")

    # Create x values for the distributions (범위를 1에서 5까지로 설정)
    x = np.linspace(1, 5, 1000)  # Adjusted to focus on the valid score range (1-5)

    # Plot normal distribution for all participants (black dotted line)
    if all_scores:
        # Calculate mean and standard deviation for all participants
        mu_all = np.mean(all_scores)
        std_all = np.std(all_scores)
        # Plot normal distribution curve (black dotted line)
        plt.plot(
            x,
            stats.norm.pdf(x, mu_all, std_all),
            "k--",
            label="Overall",
            linewidth=1.5,
        )

    # Plot normal distribution for team participants (blue solid line)
    if team_scores:
        # Calculate mean and standard deviation for team participants
        mu_team = np.mean(team_scores)
        std_team = np.std(team_scores)
        # Plot normal distribution curve (blue solid line)
        plt.plot(
            x,
            stats.norm.pdf(x, mu_team, std_team),
            "b-",
            label=f"Team {team_number}",
            linewidth=2,
        )

    # Get the maximum y value for filling background colors
    ax = plt.gca()
    ymax = ax.get_ylim()[1]

    # Draw vertical lines at cutoff values
    plt.axvline(
        x=cutoff_burnout_cognitive_regulation[0],
        color="gray",
        linestyle="--",
        alpha=0.5,
    )
    plt.axvline(
        x=cutoff_burnout_cognitive_regulation[1],
        color="gray",
        linestyle="--",
        alpha=0.5,
    )

    # Fill background regions with colors (green, yellow, pink)
    # Normal range (light green)
    plt.fill_between(
        x,
        0,
        ymax,
        where=(x < cutoff_burnout_cognitive_regulation[0]),
        color="lightgreen",
        alpha=0.3,
    )
    # Warning range (light yellow)
    plt.fill_between(
        x,
        0,
        ymax,
        where=(x >= cutoff_burnout_cognitive_regulation[0])
        & (x < cutoff_burnout_cognitive_regulation[1]),
        color="lightyellow",
        alpha=0.3,
    )
    # Risk range (light pink)
    plt.fill_between(
        x,
        0,
        ymax,
        where=(x >= cutoff_burnout_cognitive_regulation[1]),
        color="lightpink",
        alpha=0.3,
    )

    # Set labels and title
    plt.xlabel("Cognitive Regulation Score", fontsize=12)
    plt.ylabel("Density", fontsize=12)
    plt.title(
        f"Team {team_number} Cognitive Regulation Score Distribution", fontsize=14
    )

    # Add legend with proper placement
    plt.legend(loc="upper right")

    # Calculate statistics for display box
    if team_scores:
        # Count participants in each category
        normal_count = sum(
            1
            for score in team_scores
            if score <= cutoff_burnout_cognitive_regulation[0]
        )
        warning_count = sum(
            1
            for score in team_scores
            if score > cutoff_burnout_cognitive_regulation[0]
            and score <= cutoff_burnout_cognitive_regulation[1]
        )
        risk_count = sum(
            1 for score in team_scores if score > cutoff_burnout_cognitive_regulation[1]
        )

    # Set x-axis limits to show only the valid range (1-5)
    plt.xlim(
        1, 5
    )  # Fixed range for cognitive regulation scores that only exist from 1 to 5

    # Add tick marks at each integer score
    plt.xticks(range(1, 6))

    # Adjust layout
    plt.tight_layout()
    # Save the figure with high resolution (300 DPI)
    plt.savefig(
        f"{output_dir}/{week_number}주차_인지적조절_상담 {team_number}팀.png", dpi=300
    )
    plt.close()

    print(
        f"Graph saved to {output_dir}/{week_number}주차_인지적조절_상담 {team_number}팀.png"
    )


def generate_emotional_regulation_distribution_graph(week_number=0, team_number=None):
    """
    Generate a distribution graph for emotional regulation (정서적 조절) scores for a specific week

    Parameters:
    - week_number (int): Week number (0, 2, 4, etc.)
    - team_number (int or None): Team number to highlight (1, 2, 3, etc.)
    """
    # Create figures directory if it doesn't exist
    output_dir = f"data/figures/상담 {team_number}팀"
    os.makedirs(output_dir, exist_ok=True)

    # Load analysis data
    with open("data/analysis/analysis.json", "r", encoding="utf-8") as f:
        analysis_data = json.load(f)

    # 외부 모듈에서 가져온 절단점 사용
    cutoff_burnout_emotional_regulation = CUTOFF_BURNOUT_EMOTIONAL_REGULATION

    # Collect emotional regulation scores for the specified week
    all_scores = []  # List to store scores from all participants
    team_scores = []  # List to store scores from the specified team
    week_key = f"{week_number}주차"

    for participant in analysis_data["participants"]:
        # Check if participant has data for the specified week
        if week_key in participant["analysis"]:
            # Get the emotional regulation score for this participant
            try:
                # Access the "정서적 조절" (emotional regulation) score from type_averages
                score = participant["analysis"][week_key]["type_averages"][
                    "BAT_primary"
                ].get("정서적 조절")

                if score is not None:
                    # Add to all scores list
                    all_scores.append(score)

                    # If team is specified, collect scores for that team
                    if (
                        team_number is not None
                        and participant["team"] == f"상담 {team_number}팀"
                    ):
                        team_scores.append(score)
            except (KeyError, TypeError):
                # Skip if the score is not available
                continue

    # Create the plot with a clean, modern style
    plt.figure(figsize=(10, 6))
    plt.style.use("seaborn-v0_8-whitegrid")

    # Create x values for the distributions (범위를 1에서 5까지로 설정)
    x = np.linspace(1, 5, 1000)  # Adjusted to focus on the valid score range (1-5)

    # Plot normal distribution for all participants (black dotted line)
    if all_scores:
        # Calculate mean and standard deviation for all participants
        mu_all = np.mean(all_scores)
        std_all = np.std(all_scores)
        # Plot normal distribution curve (black dotted line)
        plt.plot(
            x,
            stats.norm.pdf(x, mu_all, std_all),
            "k--",
            label="Overall",
            linewidth=1.5,
        )

    # Plot normal distribution for team participants (blue solid line)
    if team_scores:
        # Calculate mean and standard deviation for team participants
        mu_team = np.mean(team_scores)
        std_team = np.std(team_scores)
        # Plot normal distribution curve (blue solid line)
        plt.plot(
            x,
            stats.norm.pdf(x, mu_team, std_team),
            "b-",
            label=f"Team {team_number}",
            linewidth=2,
        )

    # Get the maximum y value for filling background colors
    ax = plt.gca()
    ymax = ax.get_ylim()[1]

    # Draw vertical lines at cutoff values
    plt.axvline(
        x=cutoff_burnout_emotional_regulation[0],
        color="gray",
        linestyle="--",
        alpha=0.5,
    )
    plt.axvline(
        x=cutoff_burnout_emotional_regulation[1],
        color="gray",
        linestyle="--",
        alpha=0.5,
    )

    # Fill background regions with colors (green, yellow, pink)
    # Normal range (light green)
    plt.fill_between(
        x,
        0,
        ymax,
        where=(x < cutoff_burnout_emotional_regulation[0]),
        color="lightgreen",
        alpha=0.3,
    )
    # Warning range (light yellow)
    plt.fill_between(
        x,
        0,
        ymax,
        where=(x >= cutoff_burnout_emotional_regulation[0])
        & (x < cutoff_burnout_emotional_regulation[1]),
        color="lightyellow",
        alpha=0.3,
    )
    # Risk range (light pink)
    plt.fill_between(
        x,
        0,
        ymax,
        where=(x >= cutoff_burnout_emotional_regulation[1]),
        color="lightpink",
        alpha=0.3,
    )

    # Set labels and title
    plt.xlabel("Emotional Regulation Score", fontsize=12)
    plt.ylabel("Density", fontsize=12)
    plt.title(
        f"Team {team_number} Emotional Regulation Score Distribution", fontsize=14
    )

    # Add legend with proper placement
    plt.legend(loc="upper right")

    # Calculate statistics for display box
    if team_scores:
        # Count participants in each category
        normal_count = sum(
            1
            for score in team_scores
            if score <= cutoff_burnout_emotional_regulation[0]
        )
        warning_count = sum(
            1
            for score in team_scores
            if score > cutoff_burnout_emotional_regulation[0]
            and score <= cutoff_burnout_emotional_regulation[1]
        )
        risk_count = sum(
            1 for score in team_scores if score > cutoff_burnout_emotional_regulation[1]
        )

    # Set x-axis limits to show only the valid range (1-5)
    plt.xlim(
        1, 5
    )  # Fixed range for emotional regulation scores that only exist from 1 to 5

    # Add tick marks at each integer score
    plt.xticks(range(1, 6))

    # Adjust layout
    plt.tight_layout()
    # Save the figure with high resolution (300 DPI)
    plt.savefig(
        f"{output_dir}/{week_number}주차_정서적조절_상담 {team_number}팀.png", dpi=300
    )
    plt.close()

    print(
        f"Graph saved to {output_dir}/{week_number}주차_정서적조절_상담 {team_number}팀.png"
    )


def generate_depersonalization_distribution_graph(week_number=0, team_number=None):
    """
    Generate a distribution graph for depersonalization (정서적 거리감) scores for a specific week

    Parameters:
    - week_number (int): Week number (0, 2, 4, etc.)
    - team_number (int or None): Team number to highlight (1, 2, 3, etc.)
    """
    # Create figures directory if it doesn't exist
    output_dir = f"data/figures/상담 {team_number}팀"
    os.makedirs(output_dir, exist_ok=True)

    # Load analysis data
    with open("data/analysis/analysis.json", "r", encoding="utf-8") as f:
        analysis_data = json.load(f)

    # 외부 모듈에서 가져온 절단점 사용
    cutoff_burnout_depersonalization = CUTOFF_BURNOUT_DEPERSONALIZATION

    # Collect depersonalization scores for the specified week
    all_scores = []  # List to store scores from all participants
    team_scores = []  # List to store scores from the specified team
    week_key = f"{week_number}주차"

    for participant in analysis_data["participants"]:
        # Check if participant has data for the specified week
        if week_key in participant["analysis"]:
            # Get the depersonalization score for this participant
            try:
                # Access the "심적 거리" (depersonalization) score from type_averages
                score = participant["analysis"][week_key]["type_averages"][
                    "BAT_primary"
                ].get("심적 거리")

                if score is not None:
                    # Add to all scores list
                    all_scores.append(score)

                    # If team is specified, collect scores for that team
                    if (
                        team_number is not None
                        and participant["team"] == f"상담 {team_number}팀"
                    ):
                        team_scores.append(score)
            except (KeyError, TypeError):
                # Skip if the score is not available
                continue

    # Create the plot with a clean, modern style
    plt.figure(figsize=(10, 6))
    plt.style.use("seaborn-v0_8-whitegrid")

    # Create x values for the distributions (범위를 1에서 5까지로 설정)
    x = np.linspace(1, 5, 1000)  # Adjusted to focus on the valid score range (1-5)

    # Plot normal distribution for all participants (black dotted line)
    if all_scores:
        # Calculate mean and standard deviation for all participants
        mu_all = np.mean(all_scores)
        std_all = np.std(all_scores)
        # Plot normal distribution curve (black dotted line)
        plt.plot(
            x,
            stats.norm.pdf(x, mu_all, std_all),
            "k--",
            label="Overall",
            linewidth=1.5,
        )

    # Plot normal distribution for team participants (blue solid line)
    if team_scores:
        # Calculate mean and standard deviation for team participants
        mu_team = np.mean(team_scores)
        std_team = np.std(team_scores)
        # Plot normal distribution curve (blue solid line)
        plt.plot(
            x,
            stats.norm.pdf(x, mu_team, std_team),
            "b-",
            label=f"Team {team_number}",
            linewidth=2,
        )

    # Get the maximum y value for filling background colors
    ax = plt.gca()
    ymax = ax.get_ylim()[1]

    # Draw vertical lines at cutoff values
    plt.axvline(
        x=cutoff_burnout_depersonalization[0], color="gray", linestyle="--", alpha=0.5
    )
    plt.axvline(
        x=cutoff_burnout_depersonalization[1], color="gray", linestyle="--", alpha=0.5
    )

    # Fill background regions with colors (green, yellow, pink)
    # Normal range (light green)
    plt.fill_between(
        x,
        0,
        ymax,
        where=(x < cutoff_burnout_depersonalization[0]),
        color="lightgreen",
        alpha=0.3,
    )
    # Warning range (light yellow)
    plt.fill_between(
        x,
        0,
        ymax,
        where=(x >= cutoff_burnout_depersonalization[0])
        & (x < cutoff_burnout_depersonalization[1]),
        color="lightyellow",
        alpha=0.3,
    )
    # Risk range (light pink)
    plt.fill_between(
        x,
        0,
        ymax,
        where=(x >= cutoff_burnout_depersonalization[1]),
        color="lightpink",
        alpha=0.3,
    )

    # Set labels and title
    plt.xlabel("Depersonalization Score", fontsize=12)
    plt.ylabel("Density", fontsize=12)
    plt.title(f"Team {team_number} Depersonalization Score Distribution", fontsize=14)

    # Add legend with proper placement
    plt.legend(loc="upper right")

    # Calculate statistics for display box
    if team_scores:
        # Count participants in each category
        normal_count = sum(
            1 for score in team_scores if score <= cutoff_burnout_depersonalization[0]
        )
        warning_count = sum(
            1
            for score in team_scores
            if score > cutoff_burnout_depersonalization[0]
            and score <= cutoff_burnout_depersonalization[1]
        )
        risk_count = sum(
            1 for score in team_scores if score > cutoff_burnout_depersonalization[1]
        )

    # Set x-axis limits to show only the valid range (1-5)
    plt.xlim(
        1, 5
    )  # Fixed range for depersonalization scores that only exist from 1 to 5

    # Add tick marks at each integer score
    plt.xticks(range(1, 6))

    # Adjust layout
    plt.tight_layout()
    # Save the figure with high resolution (300 DPI)
    plt.savefig(
        f"{output_dir}/{week_number}주차_심적거리_상담 {team_number}팀.png", dpi=300
    )
    plt.close()

    print(
        f"Graph saved to {output_dir}/{week_number}주차_심적거리_상담 {team_number}팀.png"
    )


def generate_stress_distribution_graph(week_number=0, team_number=None):
    """
    Generate a distribution graph for stress scores for a specific week

    Parameters:
    - week_number (int): Week number (0, 2, 4, etc.)
    - team_number (int or None): Team number to highlight (1, 2, 3, etc.)
    """
    # Create figures directory if it doesn't exist
    output_dir = f"data/figures/상담 {team_number}팀"
    os.makedirs(output_dir, exist_ok=True)

    # Load analysis data
    with open("data/analysis/analysis.json", "r", encoding="utf-8") as f:
        analysis_data = json.load(f)

    # 외부 모듈에서 가져온 절단점 사용
    cutoff_stress = CUTOFF_STRESS

    # Collect stress scores for the specified week
    all_scores = []  # List to store scores from all participants
    team_scores = []  # List to store scores from the specified team
    week_key = f"{week_number}주차"

    for participant in analysis_data["participants"]:
        # Check if participant has data for the specified week
        if week_key in participant["analysis"]:
            # Get the stress score for this participant
            try:
                # Access the stress score from category_averages (correct field name is "stress")
                score = participant["analysis"][week_key]["category_averages"].get(
                    "stress"
                )

                if score is not None:
                    # Add to all scores list
                    all_scores.append(score)

                    # If team is specified, collect scores for that team
                    if (
                        team_number is not None
                        and participant["team"] == f"상담 {team_number}팀"
                    ):
                        team_scores.append(score)
            except (KeyError, TypeError):
                # Skip if the score is not available
                continue

    # Create the plot with a clean, modern style
    plt.figure(figsize=(10, 6))
    plt.style.use("seaborn-v0_8-whitegrid")

    # Create x values for the distributions (범위를 0에서 100까지로 설정 - 직무 스트레스는 0-100 범위임)
    x = np.linspace(0, 100, 1000)  # Adjusted to focus on the valid score range (0-100)

    # Plot normal distribution for all participants (black dotted line)
    if all_scores:
        # Calculate mean and standard deviation for all participants
        mu_all = np.mean(all_scores)
        std_all = np.std(all_scores)
        # Plot normal distribution curve (black dotted line)
        plt.plot(
            x,
            stats.norm.pdf(x, mu_all, std_all),
            "k--",
            label="Overall",
            linewidth=1.5,
        )

    # Plot normal distribution for team participants (blue solid line)
    if team_scores:
        # Calculate mean and standard deviation for team participants
        mu_team = np.mean(team_scores)
        std_team = np.std(team_scores)
        # Plot normal distribution curve (blue solid line)
        plt.plot(
            x,
            stats.norm.pdf(x, mu_team, std_team),
            "b-",
            label=f"Team {team_number}",
            linewidth=2,
        )

    # Get the maximum y value for filling background colors
    ax = plt.gca()
    ymax = ax.get_ylim()[1]

    # Draw vertical lines at cutoff values
    plt.axvline(x=cutoff_stress[0], color="gray", linestyle="--", alpha=0.5)
    plt.axvline(x=cutoff_stress[1], color="gray", linestyle="--", alpha=0.5)

    # Fill background regions with colors (green, yellow, pink)
    # Normal range (light green)
    plt.fill_between(
        x, 0, ymax, where=(x < cutoff_stress[0]), color="lightgreen", alpha=0.3
    )
    # Warning range (light yellow)
    plt.fill_between(
        x,
        0,
        ymax,
        where=(x >= cutoff_stress[0]) & (x < cutoff_stress[1]),
        color="lightyellow",
        alpha=0.3,
    )
    # Risk range (light pink)
    plt.fill_between(
        x, 0, ymax, where=(x >= cutoff_stress[1]), color="lightpink", alpha=0.3
    )

    # Set labels and title
    plt.xlabel("Stress Score", fontsize=12)
    plt.ylabel("Density", fontsize=12)
    plt.title(f"Team {team_number} Stress Score Distribution", fontsize=14)

    # Add legend with proper placement
    plt.legend(loc="upper right")

    # Calculate statistics for display box
    if team_scores:
        # Count participants in each category
        normal_count = sum(1 for score in team_scores if score <= cutoff_stress[0])
        warning_count = sum(
            1
            for score in team_scores
            if score > cutoff_stress[0] and score <= cutoff_stress[1]
        )
        risk_count = sum(1 for score in team_scores if score > cutoff_stress[1])

    # Set x-axis limits to show only the valid range (0-100)
    plt.xlim(0, 100)  # Fixed range for stress scores that exist from 0 to 100

    # Add tick marks at each 10 points
    plt.xticks(range(0, 101, 10))

    # Adjust layout
    plt.tight_layout()
    # Save the figure with high resolution (300 DPI)
    plt.savefig(
        f"{output_dir}/{week_number}주차_스트레스_상담 {team_number}팀.png", dpi=300
    )
    plt.close()

    print(
        f"Graph saved to {output_dir}/{week_number}주차_스트레스_상담 {team_number}팀.png"
    )


def generate_stress_subcategories_boxplot(week_number=0, team_number=None):
    """
    Generate horizontal box plots for stress subcategories for a specific team

    Parameters:
    - week_number (int): Week number (0, 2, 4, etc.)
    - team_number (int or None): Team number to highlight (1, 2, 3, etc.)
    """

    # Create figures directory if it doesn't exist
    output_dir = f"data/figures/상담 {team_number}팀"
    os.makedirs(output_dir, exist_ok=True)

    # Load analysis data
    with open("data/analysis/analysis.json", "r", encoding="utf-8") as f:
        analysis_data = json.load(f)

    # English subcategory names (this order will be maintained in the plot)
    subcategories_english = [
        "Job Demand",
        "Job Control",
        "Interpersonal Conflict",
        "Job Insecurity",
        "Organizational System",
        "Inadequate Compensation",
        "Workplace Culture",
    ]

    # Korean subcategories (matching the order of English subcategories)
    subcategories = [
        "직무 요구",
        "직무 자율",
        "관계 갈등",
        "직무 불안",
        "조직 체계",
        "보상 부적절",
        "직장 문화",
    ]

    # Map of Korean to English for reference
    korean_to_english = {k: v for k, v in zip(subcategories, subcategories_english)}

    # Map subcategories to their cutoff values
    cutoff_map = {
        "직무 요구": CUTOFF_JOB_DEMAND,
        "직무 자율": CUTOFF_INSUFFICIENT_JOB_CONTROL,
        "관계 갈등": CUTOFF_INTERPERSONAL_CONFLICT,
        "직무 불안": CUTOFF_JOB_INSECURITY,
        "조직 체계": CUTOFF_ORGANIZATIONAL_SYSTEM,
        "보상 부적절": CUTOFF_LACK_OF_REWARD,
        "직장 문화": CUTOFF_OCCUPATIONAL_CLIMATE,
    }

    # Data structure to hold values for each subcategory
    subcategory_data = {subcat: [] for subcat in subcategories}

    # Team name
    team_name = f"상담 {team_number}팀"
    week_key = f"{week_number}주차"

    # Collect stress subcategory scores for the specified week and team
    for participant in analysis_data["participants"]:
        if participant["team"] == team_name and week_key in participant["analysis"]:
            try:
                # Get stress subcategories data for this participant
                stress_data = participant["analysis"][week_key]["type_averages"][
                    "stress"
                ]

                # Add each subcategory value to the corresponding list
                for subcat in subcategories:
                    if subcat in stress_data:
                        subcategory_data[subcat].append(stress_data[subcat])
            except (KeyError, TypeError) as e:
                # Skip if data is missing or invalid
                continue

    # Create figure for box plot
    plt.figure(figsize=(12, 8))
    plt.style.use("seaborn-v0_8-whitegrid")

    # Create box plot (horizontal)
    # Convert dictionary to list of values for box plot, maintaining the order
    box_data = [subcategory_data[subcat] for subcat in subcategories]

    # Reverse both box_data and subcategories_english to make the first item appear at the top
    box_data = box_data[::-1]
    reversed_subcategories_english = subcategories_english[::-1]
    # Also reverse the subcategories to maintain alignment with the data
    reversed_subcategories = subcategories[::-1]

    # Create horizontal box plot with English labels
    box = plt.boxplot(
        box_data,
        vert=False,  # Horizontal orientation
        patch_artist=True,  # Fill boxes with color
        labels=reversed_subcategories_english,  # Use reversed English subcategory names as labels
    )

    # Calculate means and medians for each subcategory
    means = [np.mean(data) if len(data) > 0 else 0 for data in box_data]
    medians = [np.median(data) if len(data) > 0 else 0 for data in box_data]

    # Choose colors based on mean values and cutoff values
    box_colors = []
    for i, subcat in enumerate(reversed_subcategories):  # Use reversed subcategories
        mean_val = means[i]  # Use mean instead of median for color determination
        cutoff = cutoff_map[subcat]

        # Determine color based on mean value compared to cutoffs
        if mean_val < cutoff[0]:
            # Normal range (green)
            box_colors.append("lightgreen")
        elif mean_val < cutoff[1]:
            # Warning range (orange)
            box_colors.append("orange")
        else:
            # High risk range (red)
            box_colors.append("lightcoral")

    # Apply colors to boxes
    for patch, color in zip(box["boxes"], box_colors):
        patch.set_facecolor(color)

    # Add grid for better readability
    plt.grid(True, axis="x", linestyle="--", alpha=0.7)

    # Set labels and title
    plt.xlabel("Score (0-100)", fontsize=12)
    plt.title(
        f"Team {team_number} Stress Subcategories - Week {week_number}", fontsize=14
    )

    # Set x-axis limits to 0-100 for stress scores
    plt.xlim(0, 100)

    # Add text with mean, median values and cutoffs
    for i, subcat in enumerate(reversed_subcategories):  # Use reversed subcategories
        cutoff = cutoff_map[subcat]
        plt.text(
            95,
            i + 1,
            f"Mean: {means[i]:.1f}, Median: {medians[i]:.1f}\nCutoffs: {cutoff[0]}/{cutoff[1]}",
            verticalalignment="center",
            fontsize=9,
        )

        # Add cutoff vertical lines for each category
        y_pos = i + 1
        plt.plot([cutoff[0], cutoff[0]], [y_pos - 0.4, y_pos + 0.4], "k--", alpha=0.5)
        plt.plot([cutoff[1], cutoff[1]], [y_pos - 0.4, y_pos + 0.4], "k--", alpha=0.5)

    # Adjust layout
    plt.tight_layout()

    # Save the figure
    plt.savefig(
        f"{output_dir}/{week_number}주차_스트레스요인_상담 {team_number}팀.png", dpi=300
    )
    plt.close()

    print(
        f"Stress subcategories box plot saved to {output_dir}/{week_number}주차_스트레스요인_상담 {team_number}팀.png"
    )


def generate_emotional_labor_subcategories_boxplot(week_number=0, team_number=None):
    """
    Generate horizontal box plots for emotional labor subcategories for a specific team

    Parameters:
    - week_number (int): Week number (0, 2, 4, etc.)
    - team_number (int or None): Team number to highlight (1, 2, 3, etc.)
    """
    # Create figures directory if it doesn't exist
    output_dir = f"data/figures/상담 {team_number}팀"
    os.makedirs(output_dir, exist_ok=True)

    # Load analysis data
    with open("data/analysis/analysis.json", "r", encoding="utf-8") as f:
        analysis_data = json.load(f)

    # Korean emotional labor subcategories
    subcategories = [
        "감정조절의 노력 및 다양성",
        "고객응대의 과부하 및 갈등",
        "감정부조화 및 손상",
        "조직의 감시 및 모니터링",
        "조직의 지지 및 보호체계",
    ]

    # English translations for display
    subcategories_english = [
        "Emotional Control Effort & Diversity",
        "Customer Response Overload & Conflict",
        "Emotional Dissonance & Damage",
        "Organizational Monitoring",
        "Organizational Support & Protection",
    ]

    # Map of Korean to English for reference
    korean_to_english = {k: v for k, v in zip(subcategories, subcategories_english)}

    # Cutoff values for emotional labor (only normal and high risk levels)
    cutoff_values = CUTOFF_EMOTIONAL_LABOR

    # Create a map of subcategories to their cutoff values
    cutoff_map = {
        subcat: cutoff for subcat, cutoff in zip(subcategories, cutoff_values)
    }

    # Data structure to hold values for each subcategory
    subcategory_data = {subcat: [] for subcat in subcategories}

    # Team name
    team_name = f"상담 {team_number}팀"
    week_key = f"{week_number}주차"

    # Collect emotional labor subcategory scores for the specified week and team
    for participant in analysis_data["participants"]:
        if participant["team"] == team_name and week_key in participant["analysis"]:
            try:
                # Get emotional labor subcategories data for this participant
                emotional_labor_data = participant["analysis"][week_key][
                    "type_averages"
                ]["emotional_labor"]

                # Add each subcategory value to the corresponding list
                for subcat in subcategories:
                    if subcat in emotional_labor_data:
                        subcategory_data[subcat].append(emotional_labor_data[subcat])
            except (KeyError, TypeError) as e:
                # Skip if data is missing or invalid
                continue

    # Create figure for box plot
    plt.figure(figsize=(12, 8))
    plt.style.use("seaborn-v0_8-whitegrid")

    # Create box plot (horizontal)
    # Convert dictionary to list of values for box plot
    box_data = [subcategory_data[subcat] for subcat in subcategories]

    # Reverse both box_data and subcategories_english to make the first item appear at the top
    box_data = box_data[::-1]
    reversed_subcategories_english = subcategories_english[::-1]
    # Also reverse the subcategories to maintain alignment with the data
    reversed_subcategories = subcategories[::-1]

    # Create horizontal box plot with English labels
    box = plt.boxplot(
        box_data,
        vert=False,  # Horizontal orientation
        patch_artist=True,  # Fill boxes with color
        labels=reversed_subcategories_english,  # Use reversed English subcategory names as labels
    )

    # Calculate means and medians for each subcategory
    means = [np.mean(data) if len(data) > 0 else 0 for data in box_data]
    medians = [np.median(data) if len(data) > 0 else 0 for data in box_data]

    # Choose colors based on mean values and cutoff values
    box_colors = []
    for i, subcat in enumerate(reversed_subcategories):  # Use reversed subcategories
        mean_val = means[i]  # Use mean instead of median for color determination
        cutoff = cutoff_map[subcat]

        # Determine color based on mean value compared to cutoff
        # Only two levels: normal and high risk
        if mean_val < cutoff:
            # Normal range (green)
            box_colors.append("lightgreen")
        else:
            # High risk range (red)
            box_colors.append("lightcoral")

    # Apply colors to boxes
    for patch, color in zip(box["boxes"], box_colors):
        patch.set_facecolor(color)

    # Add grid for better readability
    plt.grid(True, axis="x", linestyle="--", alpha=0.7)

    # Set labels and title
    plt.xlabel("Score (0-100)", fontsize=12)
    plt.title(
        f"Team {team_number} Emotional Labor Subcategories - Week {week_number}",
        fontsize=14,
    )

    # Set x-axis limits to 0-100 for emotional labor scores
    plt.xlim(0, 100)

    # Add text with mean, median values and cutoffs
    for i, subcat in enumerate(reversed_subcategories):  # Use reversed subcategories
        cutoff = cutoff_map[subcat]
        plt.text(
            95,
            i + 1,
            f"Mean: {means[i]:.1f}, Median: {medians[i]:.1f}\nCutoff: {cutoff}",
            verticalalignment="center",
            fontsize=9,
        )

        # Add cutoff vertical lines for each category
        y_pos = i + 1
        plt.plot([cutoff, cutoff], [y_pos - 0.4, y_pos + 0.4], "k--", alpha=0.5)

    # Adjust layout
    plt.tight_layout()

    # Save the figure
    plt.savefig(
        f"{output_dir}/{week_number}주차_감정노동정도_상담 {team_number}팀.png", dpi=300
    )
    plt.close()

    print(
        f"Emotional labor subcategories box plot saved to {output_dir}/{week_number}주차_감정노동정도_상담 {team_number}팀.png"
    )


def generate_burnout_summary_table(week_number=0):
    """
    Generate a summary table visualizing BAT_primary (burnout) scores for the company and teams.

    Parameters:
    - week_number (int): Week number (0, 2, 4, etc.)
    """
    # Define the output directory for company-wide figures
    output_dir = "data/figures/회사/번아웃"  # Updated output directory
    # Create the directory if it doesn't exist, with error handling
    os.makedirs(output_dir, exist_ok=True)

    # Load analysis data from the JSON file
    try:
        # Open and read the JSON file with UTF-8 encoding
        with open("data/analysis/analysis.json", "r", encoding="utf-8") as f:
            # Load the JSON content into a Python dictionary
            analysis_data = json.load(f)
    except FileNotFoundError:  # Handle case where the JSON file is not found
        print(f"Error: analysis.json not found at data/analysis/analysis.json")
        return  # Exit the function if file not found
    except json.JSONDecodeError:  # Handle case where JSON is invalid
        print(f"Error: Could not decode JSON from data/analysis/analysis.json")
        return  # Exit the function if JSON is invalid

    # Define the week key to access data in the JSON structure
    week_key = f"{week_number}주차"

    # --- Define Burnout Categories & Data Structure ---
    # List of burnout dimensions to display, their keys in JSON, and cutoff variables
    burnout_categories_config = [
        {
            "name_en": "Exhaustion",
            "is_primary_bat": False,
            "json_key": "탈진",
            "cutoff_var": CUTOFF_BURNOUT_EXHAUSTION,
            "company_score": 0.0,
            "team_scores": {},
        },
        {
            "name_en": "Mental Distance",
            "is_primary_bat": False,
            "json_key": "심적 거리",
            "cutoff_var": CUTOFF_BURNOUT_DEPERSONALIZATION,
            "company_score": 0.0,
            "team_scores": {},
        },
        {
            "name_en": "Cognitive Reg.",
            "is_primary_bat": False,
            "json_key": "인지적 조절",
            "cutoff_var": CUTOFF_BURNOUT_COGNITIVE_REGULATION,
            "company_score": 0.0,
            "team_scores": {},
        },
        {
            "name_en": "Emotional Reg.",
            "is_primary_bat": False,
            "json_key": "정서적 조절",
            "cutoff_var": CUTOFF_BURNOUT_EMOTIONAL_REGULATION,
            "company_score": 0.0,
            "team_scores": {},
        },
    ]

    # List of team names to process (actual keys in JSON)
    team_names_actual = ["상담 1팀", "상담 2팀", "상담 3팀", "상담 4팀"]
    # Short display names for team headers in the table (English)
    team_display_names_header = ["Team1", "Team2", "Team3", "Team4"]
    # Default score if data is missing
    default_score = 0.0

    # --- Data Extraction ---
    for category_info in burnout_categories_config:
        # Extract company-wide average score for the current category
        try:
            if category_info["is_primary_bat"]:
                # Access score from category_averages for overall BAT_primary
                score = analysis_data["groups"]["회사"]["analysis"][week_key][
                    "category_averages"
                ][category_info["json_key"]]
            else:
                # Access score from type_averages.BAT_primary for sub-dimensions
                score = analysis_data["groups"]["회사"]["analysis"][week_key][
                    "type_averages"
                ]["BAT_primary"][category_info["json_key"]]
            category_info["company_score"] = score
        except KeyError:
            print(
                f"Warning: Company average for {category_info['name_en']} for {week_key} not found. Using {default_score}."
            )
            category_info["company_score"] = default_score

        # Extract average score for each team for the current category
        for team_name in team_names_actual:
            try:
                if category_info["is_primary_bat"]:
                    score = analysis_data["groups"][team_name]["analysis"][week_key][
                        "category_averages"
                    ][category_info["json_key"]]
                else:
                    score = analysis_data["groups"][team_name]["analysis"][week_key][
                        "type_averages"
                    ]["BAT_primary"][category_info["json_key"]]
                category_info["team_scores"][team_name] = score
            except KeyError:
                print(
                    f"Warning: {team_name} score for {category_info['name_en']} for {week_key} not found. Using {default_score}."
                )
                category_info["team_scores"][team_name] = default_score

    # --- Plotting ---
    # Number of data rows (one for each burnout category)
    num_data_rows = len(burnout_categories_config)
    # Total rows in grid (data rows + 1 header row)
    total_grid_rows = num_data_rows + 1

    # Create the figure and GridSpec
    fig = plt.figure(figsize=(12, total_grid_rows * 0.9))
    gs = GridSpec(
        nrows=total_grid_rows,
        ncols=7,
        height_ratios=[0.6] + [1] * num_data_rows,
        width_ratios=[2.5, 2.5, 1.2, 0.7, 0.7, 0.7, 0.7],
        wspace=0.4,
        hspace=0.6,
    )

    fig.suptitle(f"Week {week_number} Burnout Indicators Summary", fontsize=16, y=0.98)

    # Helper function to determine status and color based on score and cutoffs
    def get_status_and_color(score, co):
        if score <= co[0]:
            return "Normal", "green"
        elif score <= co[1]:
            return "Warning", "orange"
        else:
            return "High Risk", "red"

    # --- Populate Header Row ---
    ax_header_cat = fig.add_subplot(gs[0, 0])
    ax_header_cat.text(
        0.5,
        0.5,
        "Burnout Indicator",
        ha="center",
        va="center",
        fontweight="bold",
        fontsize=10,
    )
    ax_header_cat.axis("off")

    ax_header_bar = fig.add_subplot(gs[0, 1])
    ax_header_bar.text(
        0.5,
        0.5,
        "Company Average Score",
        ha="center",
        va="center",
        fontweight="bold",
        fontsize=10,
    )
    ax_header_bar.axis("off")

    ax_header_status = fig.add_subplot(gs[0, 2])
    ax_header_status.text(
        0.5,
        0.5,
        "Company Status",
        ha="center",
        va="center",
        fontweight="bold",
        fontsize=10,
    )
    ax_header_status.axis("off")

    for j, team_dn_header in enumerate(team_display_names_header):
        ax_team_header = fig.add_subplot(gs[0, 3 + j])
        ax_team_header.text(
            0.5,
            0.5,
            team_dn_header,
            ha="center",
            va="center",
            fontweight="bold",
            fontsize=10,
        )
        ax_team_header.axis("off")

    # --- Populate Data Rows ---
    for i, cat_info in enumerate(burnout_categories_config):
        row_idx_in_grid = i + 1

        # 1) Burnout Category Name Column
        ax0 = fig.add_subplot(gs[row_idx_in_grid, 0])
        ax0.text(0.05, 0.5, cat_info["name_en"], ha="left", va="center", fontsize=9)
        ax0.axis("off")

        # 2) Bar Graph Column (Company Average for this category)
        ax1 = fig.add_subplot(gs[row_idx_in_grid, 1])
        company_bar_score = cat_info["company_score"]
        current_cutoffs = cat_info["cutoff_var"]
        _bar_status, bar_color = get_status_and_color(
            company_bar_score, current_cutoffs
        )

        ax1.barh([0], [company_bar_score], color=bar_color, height=0.6)
        ax1.axvline(current_cutoffs[1], color="grey", linestyle="--", linewidth=0.8)
        ax1.set_xlim(1, 5)
        ax1.set_ylim(-0.3, 0.3)
        ax1.set_yticks([])
        ax1.set_xticks([])
        ax1.tick_params(axis="x", labelsize=8)

        # --- Save Individual Company Bar Graph ---
        # Create a new figure for the individual bar graph
        fig_individual, ax_individual = plt.subplots(
            figsize=(4, 1.5)
        )  # Small figure size
        ax_individual.barh([0], [company_bar_score], color=bar_color, height=0.6)
        ax_individual.axvline(
            current_cutoffs[1], color="grey", linestyle="--", linewidth=0.8
        )
        ax_individual.set_xlim(1, 5)
        ax_individual.set_ylim(-0.3, 0.3)  # Keep consistent y-lim
        ax_individual.set_yticks([])
        ax_individual.set_xticks([])  # No x-axis numbers
        plt.tight_layout()
        individual_file_name = f"{week_number}주차_{cat_info['json_key']}_회사.png"  # Using Korean json_key for filename
        individual_file_path = os.path.join(output_dir, individual_file_name)
        try:
            fig_individual.savefig(individual_file_path, dpi=150)  # Use appropriate DPI
            print(f"Individual company bar graph saved to {individual_file_path}")
        except Exception as e:
            print(
                f"Error saving individual company bar graph {individual_file_name}: {e}"
            )
        plt.close(fig_individual)  # Close the individual figure
        # --- End Individual Save ---

        # 3) Status Text Column (Company Status for this category)
        ax2 = fig.add_subplot(gs[row_idx_in_grid, 2])
        company_status_text, company_status_color = get_status_and_color(
            company_bar_score, current_cutoffs
        )
        ax2.text(
            0.5,
            0.5,
            company_status_text,
            ha="center",
            va="center",
            color=company_status_color,
            fontsize=9,
            fontweight="bold",
        )
        ax2.axis("off")

        # 4) Team-specific Circle Columns (Team Status for this category)
        for j, team_name_key in enumerate(team_names_actual):
            ax_circle = fig.add_subplot(gs[row_idx_in_grid, 3 + j])
            team_val = cat_info["team_scores"].get(team_name_key, default_score)
            _circle_status_text, circle_color = get_status_and_color(
                team_val, current_cutoffs
            )
            ax_circle.add_patch(
                Circle(
                    (0.5, 0.5),
                    radius=0.35,
                    color=circle_color,
                    ec="black",
                    linewidth=0.5,
                )
            )
            ax_circle.axis("off")
            ax_circle.set_aspect("equal", adjustable="box")

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    file_path = os.path.join(output_dir, f"{week_number}주차_번아웃_요약.png")
    try:
        plt.savefig(file_path, dpi=300)
        print(f"Burnout summary table saved to {file_path}")
    except Exception as e:
        print(f"Error saving burnout summary table: {e}")

    plt.close(fig)


def generate_stress_summary_table(week_number=0):
    """
    Generate a summary table and individual bar graphs for Stress and its subcategories.
    """
    output_dir = "data/figures/회사/직무스트레스"  # Updated output directory
    os.makedirs(output_dir, exist_ok=True)

    try:
        with open("data/analysis/analysis.json", "r", encoding="utf-8") as f:
            analysis_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: analysis.json not found at data/analysis/analysis.json")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from data/analysis/analysis.json")
        return

    week_key = f"{week_number}주차"

    stress_categories_config = [
        {
            "name_en": "Overall Stress",
            "is_overall_metric": True,
            "json_key": "stress",
            "cutoff_var": CUTOFF_STRESS,
            "x_axis_limits": (0, 100),
            "company_score": 0.0,
            "team_scores": {},
        },
        {
            "name_en": "Job Demand",
            "is_overall_metric": False,
            "json_key": "직무 요구",
            "cutoff_var": CUTOFF_JOB_DEMAND,
            "x_axis_limits": (0, 100),
            "company_score": 0.0,
            "team_scores": {},
        },
        {
            "name_en": "Job Control",
            "is_overall_metric": False,
            "json_key": "직무 자율",
            "cutoff_var": CUTOFF_INSUFFICIENT_JOB_CONTROL,
            "x_axis_limits": (0, 100),
            "company_score": 0.0,
            "team_scores": {},
        },
        {
            "name_en": "Interpersonal Conflict",
            "is_overall_metric": False,
            "json_key": "관계 갈등",
            "cutoff_var": CUTOFF_INTERPERSONAL_CONFLICT,
            "x_axis_limits": (0, 100),
            "company_score": 0.0,
            "team_scores": {},
        },
        {
            "name_en": "Job Insecurity",
            "is_overall_metric": False,
            "json_key": "직무 불안",
            "cutoff_var": CUTOFF_JOB_INSECURITY,
            "x_axis_limits": (0, 100),
            "company_score": 0.0,
            "team_scores": {},
        },
        {
            "name_en": "Organizational System",
            "is_overall_metric": False,
            "json_key": "조직 체계",
            "cutoff_var": CUTOFF_ORGANIZATIONAL_SYSTEM,
            "x_axis_limits": (0, 100),
            "company_score": 0.0,
            "team_scores": {},
        },
        {
            "name_en": "Inadequate Compensation",
            "is_overall_metric": False,
            "json_key": "보상 부적절",
            "cutoff_var": CUTOFF_LACK_OF_REWARD,
            "x_axis_limits": (0, 100),
            "company_score": 0.0,
            "team_scores": {},
        },
        {
            "name_en": "Workplace Culture",
            "is_overall_metric": False,
            "json_key": "직장 문화",
            "cutoff_var": CUTOFF_OCCUPATIONAL_CLIMATE,
            "x_axis_limits": (0, 100),
            "company_score": 0.0,
            "team_scores": {},
        },
    ]

    team_names_actual = ["상담 1팀", "상담 2팀", "상담 3팀", "상담 4팀"]
    team_display_names_header = ["Team1", "Team2", "Team3", "Team4"]
    default_score = 0.0

    for category_info in stress_categories_config:
        try:
            if category_info["is_overall_metric"]:
                score = analysis_data["groups"]["회사"]["analysis"][week_key][
                    "category_averages"
                ][category_info["json_key"]]
            else:
                score = analysis_data["groups"]["회사"]["analysis"][week_key][
                    "type_averages"
                ]["stress"][category_info["json_key"]]
            category_info["company_score"] = score
        except KeyError:
            print(
                f"Warning: Company average for {category_info['name_en']} ({category_info['json_key']}) for {week_key} not found. Using {default_score}."
            )
            category_info["company_score"] = default_score

        for team_name in team_names_actual:
            try:
                if category_info["is_overall_metric"]:
                    score = analysis_data["groups"][team_name]["analysis"][week_key][
                        "category_averages"
                    ][category_info["json_key"]]
                else:
                    score = analysis_data["groups"][team_name]["analysis"][week_key][
                        "type_averages"
                    ]["stress"][category_info["json_key"]]
                category_info["team_scores"][team_name] = score
            except KeyError:
                print(
                    f"Warning: {team_name} score for {category_info['name_en']} ({category_info['json_key']}) for {week_key} not found. Using {default_score}."
                )
                category_info["team_scores"][team_name] = default_score

    num_data_rows = len(stress_categories_config)
    total_grid_rows = num_data_rows + 1

    fig = plt.figure(figsize=(12, total_grid_rows * 0.9))
    gs = GridSpec(
        nrows=total_grid_rows,
        ncols=7,
        height_ratios=[0.6] + [1] * num_data_rows,
        width_ratios=[2.5, 2.5, 1.2, 0.7, 0.7, 0.7, 0.7],
        wspace=0.4,
        hspace=0.6,
    )

    fig.suptitle(f"Week {week_number} Stress Indicators Summary", fontsize=16, y=0.98)

    def get_status_and_color_stress(score, co, higher_is_worse=True):
        # For stress, higher scores are generally worse.
        # co[0] is warning threshold, co[1] is high risk threshold.
        # If score <= co[0] -> Normal (Green)
        # If co[0] < score <= co[1] -> Warning (Orange)
        # If score > co[1] -> High Risk (Red)
        # This assumes cutoffs are [warning_starts, risk_starts]
        # For metrics where lower is worse, this logic would be inverted if cutoffs represented 'good' thresholds.
        # However, all KOSHA stress cutoffs seem to indicate risk levels, so higher reported score relative to cutoff is worse.

        if higher_is_worse:
            if score <= co[0]:
                return "Normal", "green"
            elif score <= co[1]:
                return "Warning", "orange"
            else:
                return "High Risk", "red"
        else:  # lower_is_worse (Not currently used for these stress metrics as structured)
            if score >= co[1]:  # e.g. score is above the 'good' high threshold
                return "Normal", "green"
            elif (
                score >= co[0]
            ):  # e.g. score is above the 'good' low threshold but below high
                return "Warning", "orange"
            else:  # e.g. score is below the 'good' low threshold
                return "High Risk", "red"

    ax_header_cat = fig.add_subplot(gs[0, 0])
    ax_header_cat.text(
        0.5,
        0.5,
        "Stress Indicator",
        ha="center",
        va="center",
        fontweight="bold",
        fontsize=10,
    )
    ax_header_cat.axis("off")

    ax_header_bar = fig.add_subplot(gs[0, 1])
    ax_header_bar.text(
        0.5,
        0.5,
        "Company Average Score",
        ha="center",
        va="center",
        fontweight="bold",
        fontsize=10,
    )
    ax_header_bar.axis("off")

    ax_header_status = fig.add_subplot(gs[0, 2])
    ax_header_status.text(
        0.5,
        0.5,
        "Company Status",
        ha="center",
        va="center",
        fontweight="bold",
        fontsize=10,
    )
    ax_header_status.axis("off")

    for j, team_dn_header in enumerate(team_display_names_header):
        ax_team_header = fig.add_subplot(gs[0, 3 + j])
        ax_team_header.text(
            0.5,
            0.5,
            team_dn_header,
            ha="center",
            va="center",
            fontweight="bold",
            fontsize=10,
        )
        ax_team_header.axis("off")

    for i, cat_info in enumerate(stress_categories_config):
        row_idx_in_grid = i + 1
        ax0 = fig.add_subplot(gs[row_idx_in_grid, 0])
        ax0.text(0.05, 0.5, cat_info["name_en"], ha="left", va="center", fontsize=9)
        ax0.axis("off")

        ax1 = fig.add_subplot(gs[row_idx_in_grid, 1])
        company_bar_score = cat_info["company_score"]
        current_cutoffs = cat_info["cutoff_var"]
        # For stress, higher score relative to cutoffs means more risk.
        _bar_status, bar_color = get_status_and_color_stress(
            company_bar_score, current_cutoffs, higher_is_worse=True
        )

        ax1.barh([0], [company_bar_score], color=bar_color, height=0.6)
        # ax1.axvline(current_cutoffs[0], color="grey", linestyle="--", linewidth=0.8) # Lower cutoff line
        ax1.axvline(
            current_cutoffs[1], color="grey", linestyle="--", linewidth=0.8
        )  # Higher cutoff line (often the High Risk threshold)
        ax1.set_xlim(cat_info["x_axis_limits"])
        ax1.set_ylim(-0.3, 0.3)
        ax1.set_yticks([])
        ax1.set_xticks([])
        ax1.tick_params(axis="x", labelsize=8)

        fig_individual, ax_individual = plt.subplots(figsize=(4, 1.5))
        ax_individual.barh([0], [company_bar_score], color=bar_color, height=0.6)
        # ax_individual.axvline(current_cutoffs[0], color="grey", linestyle="--", linewidth=0.8)
        ax_individual.axvline(
            current_cutoffs[1], color="grey", linestyle="--", linewidth=0.8
        )
        ax_individual.set_xlim(cat_info["x_axis_limits"])
        ax_individual.set_ylim(-0.3, 0.3)
        ax_individual.set_yticks([])
        ax_individual.set_xticks([])
        plt.tight_layout()
        individual_file_name = f"{week_number}주차_{cat_info['json_key']}_회사.png"
        individual_file_path = os.path.join(output_dir, individual_file_name)
        try:
            fig_individual.savefig(individual_file_path, dpi=150)
            print(
                f"Individual company bar graph for STRESS category {cat_info['name_en']} saved to {individual_file_path}"
            )
        except Exception as e:
            print(
                f"Error saving individual company bar graph {individual_file_name}: {e}"
            )
        plt.close(fig_individual)

        ax2 = fig.add_subplot(gs[row_idx_in_grid, 2])
        company_status_text, company_status_color = get_status_and_color_stress(
            company_bar_score, current_cutoffs, higher_is_worse=True
        )
        ax2.text(
            0.5,
            0.5,
            company_status_text,
            ha="center",
            va="center",
            color=company_status_color,
            fontsize=9,
            fontweight="bold",
        )
        ax2.axis("off")

        for j, team_name_key in enumerate(team_names_actual):
            ax_circle = fig.add_subplot(gs[row_idx_in_grid, 3 + j])
            team_val = cat_info["team_scores"].get(team_name_key, default_score)
            _circle_status_text, circle_color = get_status_and_color_stress(
                team_val, current_cutoffs, higher_is_worse=True
            )
            ax_circle.add_patch(
                Circle(
                    (0.5, 0.5),
                    radius=0.35,
                    color=circle_color,
                    ec="black",
                    linewidth=0.5,
                )
            )
            ax_circle.axis("off")
            ax_circle.set_aspect("equal", adjustable="box")

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    summary_file_path = os.path.join(output_dir, f"{week_number}주차_스트레스_요약.png")
    try:
        plt.savefig(summary_file_path, dpi=300)
        print(f"Stress summary table saved to {summary_file_path}")
    except Exception as e:
        print(f"Error saving stress summary table: {e}")
    plt.close(fig)


def generate_emotional_labor_summary_table(week_number=0):
    """
    Generate a summary table and individual bar graphs for Emotional Labor subcategories.
    """
    # Define the output directory for company-wide figures
    output_dir = "data/figures/회사/감정노동"  # New output directory
    # Create the directory if it doesn't exist, with error handling
    os.makedirs(output_dir, exist_ok=True)

    # Load analysis data from the JSON file
    try:
        # Open and read the JSON file with UTF-8 encoding
        with open("data/analysis/analysis.json", "r", encoding="utf-8") as f:
            # Load the JSON content into a Python dictionary
            analysis_data = json.load(f)
    except FileNotFoundError:  # Handle case where the JSON file is not found
        print(f"Error: analysis.json not found at data/analysis/analysis.json")
        return  # Exit the function if file not found
    except json.JSONDecodeError:  # Handle case where JSON is invalid
        print(f"Error: Could not decode JSON from data/analysis/analysis.json")
        return  # Exit the function if JSON is invalid

    # Define the week key to access data in the JSON structure
    week_key = f"{week_number}주차"

    # CUTOFF_EMOTIONAL_LABOR is a list: [66.67, 66.67, 61.11, 66.67, 33.33]
    # Corresponding to: 감정조절노력및다양성, 고객응대과부하및갈등, 감정부조화및손상, 조직의감시및모니터링, 조직의지지및보호체계
    emotional_labor_categories_config = [
        {
            "name_en": "Emotional Control Effort & Diversity",
            "json_key": "감정조절의 노력 및 다양성",
            "cutoff_val": CUTOFF_EMOTIONAL_LABOR[0],
            "x_axis_limits": (0, 100),
            "company_score": 0.0,
            "team_scores": {},
        },
        {
            "name_en": "Customer Response Overload & Conflict",
            "json_key": "고객응대의 과부하 및 갈등",
            "cutoff_val": CUTOFF_EMOTIONAL_LABOR[1],
            "x_axis_limits": (0, 100),
            "company_score": 0.0,
            "team_scores": {},
        },
        {
            "name_en": "Emotional Dissonance & Damage",
            "json_key": "감정부조화 및 손상",
            "cutoff_val": CUTOFF_EMOTIONAL_LABOR[2],
            "x_axis_limits": (0, 100),
            "company_score": 0.0,
            "team_scores": {},
        },
        {
            "name_en": "Organizational Monitoring",
            "json_key": "조직의 감시 및 모니터링",
            "cutoff_val": CUTOFF_EMOTIONAL_LABOR[3],
            "x_axis_limits": (0, 100),
            "company_score": 0.0,
            "team_scores": {},
        },
        {
            "name_en": "Organizational Support & Protection",
            "json_key": "조직의 지지 및 보호체계",
            "cutoff_val": CUTOFF_EMOTIONAL_LABOR[4],
            "x_axis_limits": (0, 100),
            "company_score": 0.0,
            "team_scores": {},
        },
    ]

    # List of team names to process (actual keys in JSON)
    team_names_actual = ["상담 1팀", "상담 2팀", "상담 3팀", "상담 4팀"]
    # Short display names for team headers in the table (English)
    team_display_names_header = ["Team1", "Team2", "Team3", "Team4"]
    # Default score if data is missing
    default_score = 0.0

    # --- Data Extraction ---
    for category_info in emotional_labor_categories_config:
        try:
            # All emotional labor subcategories are under type_averages.emotional_labor
            score = analysis_data["groups"]["회사"]["analysis"][week_key][
                "type_averages"
            ]["emotional_labor"][category_info["json_key"]]
            category_info["company_score"] = score
        except KeyError:
            print(
                f"Warning: Company average for {category_info['name_en']} ({category_info['json_key']}) for {week_key} not found. Using {default_score}."
            )
            category_info["company_score"] = default_score

        for team_name in team_names_actual:
            try:
                score = analysis_data["groups"][team_name]["analysis"][week_key][
                    "type_averages"
                ]["emotional_labor"][category_info["json_key"]]
                category_info["team_scores"][team_name] = score
            except KeyError:
                print(
                    f"Warning: {team_name} score for {category_info['name_en']} ({category_info['json_key']}) for {week_key} not found. Using {default_score}."
                )
                category_info["team_scores"][team_name] = default_score

    # Number of data rows (one for each emotional labor category)
    num_data_rows = len(emotional_labor_categories_config)
    # Total rows in grid (data rows + 1 header row)
    total_grid_rows = num_data_rows + 1

    # Create the figure and GridSpec
    fig = plt.figure(figsize=(12, total_grid_rows * 0.9))
    gs = GridSpec(
        nrows=total_grid_rows,
        ncols=7,
        height_ratios=[0.6] + [1] * num_data_rows,
        width_ratios=[
            3.0,
            2.5,
            1.2,
            0.7,
            0.7,
            0.7,
            0.7,
        ],  # Adjusted first col width for long names
        wspace=0.4,
        hspace=0.6,
    )

    fig.suptitle(
        f"Week {week_number} Emotional Labor Indicators Summary", fontsize=16, y=0.98
    )

    # Simplified helper function - if score >= cutoff, it's high risk
    def get_status_and_color_emotional_labor(score, cutoff_val):
        if score < cutoff_val:  # Score is better than (below) the threshold
            return "Normal", "green"
        else:  # Score is at or above the threshold (worse)
            return "High Risk", "red"

    # --- Populate Header Row ---
    ax_header_cat = fig.add_subplot(gs[0, 0])
    ax_header_cat.text(
        0.5,
        0.5,
        "Emotional Labor Indicator",
        ha="center",
        va="center",
        fontweight="bold",
        fontsize=9,
    )  # Slightly smaller font for header
    ax_header_cat.axis("off")

    ax_header_bar = fig.add_subplot(gs[0, 1])
    ax_header_bar.text(
        0.5,
        0.5,
        "Company Average Score",
        ha="center",
        va="center",
        fontweight="bold",
        fontsize=10,
    )
    ax_header_bar.axis("off")

    ax_header_status = fig.add_subplot(gs[0, 2])
    ax_header_status.text(
        0.5,
        0.5,
        "Company Status",
        ha="center",
        va="center",
        fontweight="bold",
        fontsize=10,
    )
    ax_header_status.axis("off")

    for j, team_dn_header in enumerate(team_display_names_header):
        ax_team_header = fig.add_subplot(gs[0, 3 + j])
        ax_team_header.text(
            0.5,
            0.5,
            team_dn_header,
            ha="center",
            va="center",
            fontweight="bold",
            fontsize=10,
        )
        ax_team_header.axis("off")

    # --- Populate Data Rows ---
    for i, cat_info in enumerate(emotional_labor_categories_config):
        row_idx_in_grid = i + 1

        # 1) Category Name Column
        ax0 = fig.add_subplot(gs[row_idx_in_grid, 0])
        ax0.text(0.05, 0.5, cat_info["name_en"], ha="left", va="center", fontsize=9)
        ax0.axis("off")

        # 2) Bar Graph Column (Company Average for this category)
        ax1 = fig.add_subplot(gs[row_idx_in_grid, 1])
        company_bar_score = cat_info["company_score"]
        current_cutoff = cat_info["cutoff_val"]

        # Determine status and color based on simplified logic
        _bar_status, bar_color = get_status_and_color_emotional_labor(
            company_bar_score, current_cutoff
        )

        # Draw the bar
        ax1.barh([0], [company_bar_score], color=bar_color, height=0.6)
        # Draw the cutoff line
        ax1.axvline(current_cutoff, color="grey", linestyle="--", linewidth=0.8)
        # Set axis limits and hide ticks
        ax1.set_xlim(cat_info["x_axis_limits"])
        ax1.set_ylim(-0.3, 0.3)
        ax1.set_yticks([])
        ax1.set_xticks([])
        ax1.tick_params(axis="x", labelsize=8)

        # --- Save Individual Company Bar Graph ---
        fig_individual, ax_individual = plt.subplots(figsize=(4, 1.5))
        ax_individual.barh([0], [company_bar_score], color=bar_color, height=0.6)
        ax_individual.axvline(
            current_cutoff, color="grey", linestyle="--", linewidth=0.8
        )
        ax_individual.set_xlim(cat_info["x_axis_limits"])
        ax_individual.set_ylim(-0.3, 0.3)
        ax_individual.set_yticks([])
        ax_individual.set_xticks([])
        plt.tight_layout()
        # Use Korean json_key for filename consistency with other individual graphs
        individual_file_name = f"{week_number}주차_{cat_info['json_key']}_회사.png"
        individual_file_path = os.path.join(output_dir, individual_file_name)
        try:
            fig_individual.savefig(individual_file_path, dpi=150)
            print(
                f"Individual company bar graph for EMOTIONAL LABOR category {cat_info['name_en']} saved to {individual_file_path}"
            )
        except Exception as e:
            print(
                f"Error saving individual company bar graph {individual_file_name}: {e}"
            )
        plt.close(fig_individual)

        # 3) Status Text Column (Company Status for this category)
        ax2 = fig.add_subplot(gs[row_idx_in_grid, 2])
        company_status_text, company_status_color = (
            get_status_and_color_emotional_labor(company_bar_score, current_cutoff)
        )
        ax2.text(
            0.5,
            0.5,
            company_status_text,
            ha="center",
            va="center",
            color=company_status_color,
            fontsize=9,
            fontweight="bold",
        )
        ax2.axis("off")

        # 4) Team-specific Circle Columns (Team Status for this category)
        for j, team_name_key in enumerate(team_names_actual):
            ax_circle = fig.add_subplot(gs[row_idx_in_grid, 3 + j])
            team_val = cat_info["team_scores"].get(team_name_key, default_score)
            _circle_status_text, circle_color = get_status_and_color_emotional_labor(
                team_val, current_cutoff
            )
            ax_circle.add_patch(
                Circle(
                    (0.5, 0.5),
                    radius=0.35,
                    color=circle_color,
                    ec="black",
                    linewidth=0.5,
                )
            )
            ax_circle.axis("off")
            ax_circle.set_aspect("equal", adjustable="box")

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    summary_file_path = os.path.join(output_dir, f"{week_number}주차_감정노동_요약.png")
    try:
        plt.savefig(summary_file_path, dpi=300)
        print(f"Emotional Labor summary table saved to {summary_file_path}")
    except Exception as e:
        print(f"Error saving Emotional Labor summary table: {e}")
    plt.close(fig)


def generate_app_usage_by_date_graph(week_number=0):
    """
    Generate a line graph showing daily app usage for the specified week.

    Parameters:
    - week_number (int): Week number (0, 2, 4, etc.)
    """
    # Create figures directory if it doesn't exist
    output_dir = f"data/figures/회사/앱 사용 기록"
    os.makedirs(output_dir, exist_ok=True)

    # Load app analysis data
    try:
        # Read the app analysis data for the specified week
        with open(
            f"data/analysis/app_analysis_{week_number}주차.json", "r", encoding="utf-8"
        ) as f:
            app_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: app_analysis_{week_number}주차.json not found")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from app_analysis_{week_number}주차.json")
        return

    # Extract daily user count data
    dates = []
    user_counts = []
    day_names = []

    # Sort the dates to ensure they're in chronological order
    sorted_dates = sorted(app_data["daily_user_counts"].keys())

    for date_str in sorted_dates:
        # Convert date string to datetime object for formatting
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")

        # Skip weekends (Saturday = 5, Sunday = 6)
        if date_obj.weekday() >= 5:
            continue

        # Get user count for this date
        count = app_data["daily_user_counts"][date_str]

        # Get day of week in English (Monday, Tuesday, etc.)
        day_of_week = date_obj.strftime("%A")

        # Format date for display (MM-DD)
        formatted_date = date_obj.strftime("%m-%d")

        # Add to our lists
        dates.append(formatted_date)
        user_counts.append(count)
        day_names.append(day_of_week)

    # Create the figure and axis
    plt.figure(figsize=(12, 6))
    plt.style.use("seaborn-v0_8-whitegrid")

    # Plot the line graph
    plt.plot(
        range(len(dates)),
        user_counts,
        marker="o",
        linestyle="-",
        linewidth=2,
        markersize=8,
        color="#1f77b4",
    )

    # Create custom x-tick labels with date and day of week
    x_labels = [f"{date}\n({day})" for date, day in zip(dates, day_names)]

    # Set x-axis ticks and labels
    plt.xticks(range(len(dates)), x_labels, rotation=45, ha="right")

    # Set axis labels and title
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Number of Users", fontsize=12)
    plt.title(
        f"Daily App Usage (Weekdays) - Week {week_number}",
        fontsize=14,
        fontweight="bold",
    )

    # Add a light grid for better readability
    plt.grid(True, linestyle="--", alpha=0.7)

    # Add values on top of each point
    for i, count in enumerate(user_counts):
        plt.text(
            i, count + 0.5, str(count), ha="center", va="bottom", fontweight="bold"
        )

    # Set y-axis to start from 0
    plt.ylim(bottom=0)

    # Adjust layout to make room for x-axis labels
    plt.tight_layout()

    # Save the figure
    plt.savefig(f"{output_dir}/{week_number}주차_앱_사용자수.png", dpi=300)
    plt.close()

    print(f"App usage graph saved to {output_dir}/{week_number}주차_앱_사용자수.png")


def generate_emotion_records_by_date_graph(week_number=0):
    """
    Generate a line graph showing daily emotion records for the specified week.

    Parameters:
    - week_number (int): Week number (0, 2, 4, etc.)
    """
    # Create figures directory if it doesn't exist
    output_dir = f"data/figures/회사/앱 사용 기록"
    os.makedirs(output_dir, exist_ok=True)

    # Load app analysis data
    try:
        # Read the app analysis data for the specified week
        with open(
            f"data/analysis/app_analysis_{week_number}주차.json", "r", encoding="utf-8"
        ) as f:
            app_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: app_analysis_{week_number}주차.json not found")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from app_analysis_{week_number}주차.json")
        return

    # Extract daily emotion record data
    dates = []
    emotion_counts = []
    day_names = []

    # Sort the dates to ensure they're in chronological order
    sorted_dates = sorted(app_data["daily_emotion_records"].keys())

    for date_str in sorted_dates:
        # Convert date string to datetime object for formatting
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")

        # Skip weekends (Saturday = 5, Sunday = 6)
        if date_obj.weekday() >= 5:
            continue

        # Get emotion record count for this date
        count = app_data["daily_emotion_records"][date_str]

        # Get day of week in English (Monday, Tuesday, etc.)
        day_of_week = date_obj.strftime("%A")

        # Format date for display (MM-DD)
        formatted_date = date_obj.strftime("%m-%d")

        # Add to our lists
        dates.append(formatted_date)
        emotion_counts.append(count)
        day_names.append(day_of_week)

    # Create the figure and axis
    plt.figure(figsize=(12, 6))
    plt.style.use("seaborn-v0_8-whitegrid")

    # Plot the line graph with a different color than the user count graph
    plt.plot(
        range(len(dates)),
        emotion_counts,
        marker="o",
        linestyle="-",
        linewidth=2,
        markersize=8,
        color="#ff7f0e",
    )

    # Create custom x-tick labels with date and day of week
    x_labels = [f"{date}\n({day})" for date, day in zip(dates, day_names)]

    # Set x-axis ticks and labels
    plt.xticks(range(len(dates)), x_labels, rotation=45, ha="right")

    # Set axis labels and title
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Number of Emotion Records", fontsize=12)
    plt.title(
        f"Daily Emotion Records (Weekdays) - Week {week_number}",
        fontsize=14,
        fontweight="bold",
    )

    # Add a light grid for better readability
    plt.grid(True, linestyle="--", alpha=0.7)

    # Add values on top of each point
    for i, count in enumerate(emotion_counts):
        plt.text(i, count + 1, str(count), ha="center", va="bottom", fontweight="bold")

    # Set y-axis to start from 0
    plt.ylim(bottom=0)

    # Adjust layout to make room for x-axis labels
    plt.tight_layout()

    # Save the figure
    plt.savefig(f"{output_dir}/{week_number}주차_감정_기록수.png", dpi=300)
    plt.close()

    print(
        f"Emotion records graph saved to {output_dir}/{week_number}주차_감정_기록수.png"
    )


def generate_emotion_distribution_pie_chart(week_number=0):
    """
    Generate a pie chart showing the distribution of positive vs negative emotions for the specified week.

    Parameters:
    - week_number (int): Week number (0, 2, 4, etc.)
    """
    # Create figures directory if it doesn't exist
    output_dir = f"data/figures/회사/앱 사용 기록"
    os.makedirs(output_dir, exist_ok=True)

    # Load app analysis data
    try:
        # Read the app analysis data for the specified week
        with open(
            f"data/analysis/app_analysis_{week_number}주차.json", "r", encoding="utf-8"
        ) as f:
            app_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: app_analysis_{week_number}주차.json not found")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from app_analysis_{week_number}주차.json")
        return

    # Calculate total positive and negative emotions from emotion_categories
    if "emotion_categories" in app_data:
        positive_count = app_data["emotion_categories"]["positive"]["count"]
        negative_count = app_data["emotion_categories"]["negative"]["count"]
    else:
        # If emotion_categories is not available, sum up daily counts
        positive_count = 0
        negative_count = 0
        for date, counts in app_data["daily_emotion_categories"].items():
            positive_count += counts["positive"]
            negative_count += counts["negative"]

    # Calculate total and percentages
    total_emotions = positive_count + negative_count
    positive_percent = (positive_count / total_emotions) * 100
    negative_percent = (negative_count / total_emotions) * 100

    # Create data for pie chart
    emotion_counts = [positive_count, negative_count]
    emotion_labels = [
        f"Positive\n{positive_count} ({positive_percent:.1f}%)",
        f"Negative\n{negative_count} ({negative_percent:.1f}%)",
    ]
    colors = ["#1f77b4", "#d62728"]  # Blue for positive, Red for negative

    # Create figure
    plt.figure(figsize=(10, 8))

    # Create pie chart
    patches, texts, autotexts = plt.pie(
        emotion_counts,
        labels=emotion_labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"edgecolor": "w", "linewidth": 1},
        textprops={"fontsize": 12, "fontweight": "bold"},
    )

    # Customize text style
    for autotext in autotexts:
        autotext.set_fontsize(14)
        autotext.set_fontweight("bold")
        autotext.set_color("white")

    # Draw a circle at the center to make it a donut chart (optional)
    # centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    # plt.gca().add_artist(centre_circle)

    # Equal aspect ratio ensures that pie is drawn as a circle
    plt.axis("equal")

    # Add title
    plt.title(
        f"Emotion Distribution - Week {week_number}",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )

    # Add legend
    plt.legend(
        ["Positive Emotions", "Negative Emotions"],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=2,
        fontsize=12,
    )

    # Adjust layout
    plt.tight_layout()

    # Save the figure
    plt.savefig(
        f"{output_dir}/{week_number}주차_감정_분포.png", dpi=300, bbox_inches="tight"
    )
    plt.close()

    print(
        f"Emotion distribution pie chart saved to {output_dir}/{week_number}주차_감정_분포.png"
    )


def generate_weekday_emotion_distribution_graph(week_number=0):
    """
    Generate a stacked bar chart showing the distribution of positive vs negative emotions
    for each day of the week.

    Parameters:
    - week_number (int): Week number (0, 2, 4, etc.)
    """
    # Create figures directory if it doesn't exist
    output_dir = f"data/figures/회사/앱 사용 기록"
    os.makedirs(output_dir, exist_ok=True)

    # Load app analysis data
    try:
        # Read the app analysis data for the specified week
        with open(
            f"data/analysis/app_analysis_{week_number}주차.json", "r", encoding="utf-8"
        ) as f:
            app_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: app_analysis_{week_number}주차.json not found")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from app_analysis_{week_number}주차.json")
        return

    # Dictionary to hold counts by weekday
    # Initialize with weekdays only (excluding weekends)
    weekday_emotions = {
        "Monday": {"positive": 0, "negative": 0},
        "Tuesday": {"positive": 0, "negative": 0},
        "Wednesday": {"positive": 0, "negative": 0},
        "Thursday": {"positive": 0, "negative": 0},
        "Friday": {"positive": 0, "negative": 0},
    }

    # Process daily emotion data
    for date_str, counts in app_data["daily_emotion_categories"].items():
        # Convert date string to datetime object
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")

        # Get day of week in English
        day_of_week = date_obj.strftime("%A")

        # Add counts to our dictionary (only for weekdays)
        if day_of_week in weekday_emotions:
            weekday_emotions[day_of_week]["positive"] += counts["positive"]
            weekday_emotions[day_of_week]["negative"] += counts["negative"]

    # Prepare data for plotting
    weekdays = []
    positive_percentages = []
    negative_percentages = []

    # Extract data in the correct order (weekdays only)
    for day in [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
    ]:
        if day in weekday_emotions:
            weekdays.append(day)
            pos = weekday_emotions[day]["positive"]
            neg = weekday_emotions[day]["negative"]
            total = pos + neg

            # Calculate percentages (avoid division by zero)
            if total > 0:
                pos_percentage = (pos / total) * 100
                neg_percentage = (neg / total) * 100
            else:
                pos_percentage = 0
                neg_percentage = 0

            positive_percentages.append(pos_percentage)
            negative_percentages.append(neg_percentage)

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))

    # Create the stacked bar chart with normalized heights (100% for each bar)
    # First, plot positive emotions (blue, bottom)
    pos_bars = ax.bar(weekdays, positive_percentages, color="#1f77b4", label="Positive")

    # Then, stack negative emotions on top (red)
    neg_bars = ax.bar(
        weekdays,
        negative_percentages,
        bottom=positive_percentages,
        color="#d62728",
        label="Negative",
    )

    # Add percentage labels on the bars
    for i, percentage in enumerate(positive_percentages):
        # Position the text in the middle of the positive bar
        ax.text(
            i,  # x position (bar index)
            percentage / 2,  # y position (middle of positive bar)
            f"{percentage:.0f}%",  # text (percentage with no decimal places)
            ha="center",
            va="center",
            color="white",
            fontweight="bold",
            fontsize=12,
        )

    # Customize axes and labels
    ax.set_ylabel("Percentage of Emotions (%)", fontsize=12)
    ax.set_title(
        f"Weekday Emotion Distribution (Mon-Fri) - Week {week_number}",
        fontsize=16,
        fontweight="bold",
    )

    # Set y-axis limits to ensure all bars are the same height (0-100%)
    ax.set_ylim(0, 100)

    # Add y-axis tick marks at 0%, 25%, 50%, 75%, and 100%
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])

    # Add grid lines for readability
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Adjust layout
    plt.tight_layout()

    # Save the figure
    plt.savefig(
        f"{output_dir}/{week_number}주차_요일별_감정_분포.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    print(
        f"Weekday emotion distribution graph saved to {output_dir}/{week_number}주차_요일별_감정_분포.png"
    )


def generate_timerange_emotion_distribution_graph(week_number=0):
    """
    Generate a stacked bar chart showing the distribution of positive vs negative emotions
    for each time range of the day.

    Parameters:
    - week_number (int): Week number (0, 2, 4, etc.)
    """
    # Create figures directory if it doesn't exist
    output_dir = f"data/figures/회사/앱 사용 기록"
    os.makedirs(output_dir, exist_ok=True)

    # Load app analysis data
    try:
        # Read the app analysis data for the specified week
        with open(
            f"data/analysis/app_analysis_{week_number}주차.json", "r", encoding="utf-8"
        ) as f:
            app_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: app_analysis_{week_number}주차.json not found")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from app_analysis_{week_number}주차.json")
        return

    # Check if time range emotion data exists
    if "time_range_emotion_categories" not in app_data:
        print("Error: No time range emotion data found in the app analysis data")
        return

    # Process time range emotion data
    time_ranges = []
    positive_percentages = []
    negative_percentages = []

    # Time ranges in the order they should appear on the x-axis
    ordered_time_ranges = [
        "08:00-10:30",
        "10:30-12:00",
        "12:00-13:30",
        "13:30-15:00",
        "15:00-16:30",
        "16:30-19:00",
    ]

    # Extract data in the correct order
    for time_range in ordered_time_ranges:
        if time_range in app_data["time_range_emotion_categories"]:
            time_ranges.append(time_range)
            counts = app_data["time_range_emotion_categories"][time_range]

            # Get positive and negative counts
            pos = counts["positive"]
            neg = counts["negative"]
            total = pos + neg

            # Calculate percentages (avoid division by zero)
            if total > 0:
                pos_percentage = (pos / total) * 100
                neg_percentage = (neg / total) * 100
            else:
                pos_percentage = 0
                neg_percentage = 0

            positive_percentages.append(pos_percentage)
            negative_percentages.append(neg_percentage)

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))

    # Create the stacked bar chart with normalized heights (100% for each bar)
    # First, plot positive emotions (blue, bottom)
    pos_bars = ax.bar(
        time_ranges, positive_percentages, color="#1f77b4", label="Positive"
    )

    # Then, stack negative emotions on top (red)
    neg_bars = ax.bar(
        time_ranges,
        negative_percentages,
        bottom=positive_percentages,
        color="#d62728",
        label="Negative",
    )

    # Add percentage labels on the bars
    for i, percentage in enumerate(positive_percentages):
        # Position the text in the middle of the positive bar
        ax.text(
            i,  # x position (bar index)
            percentage / 2,  # y position (middle of positive bar)
            f"{percentage:.0f}%",  # text (percentage with no decimal places)
            ha="center",
            va="center",
            color="white",
            fontweight="bold",
            fontsize=12,
        )

    # Customize axes and labels
    ax.set_ylabel("Percentage of Emotions (%)", fontsize=12)
    ax.set_title(
        f"Time-of-Day Emotion Distribution - Week {week_number}",
        fontsize=16,
        fontweight="bold",
    )

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha="right")

    # Set y-axis limits to ensure all bars are the same height (0-100%)
    ax.set_ylim(0, 100)

    # Add y-axis tick marks at 0%, 25%, 50%, 75%, and 100%
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])

    # Add grid lines for readability
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Adjust layout
    plt.tight_layout()

    # Save the figure
    plt.savefig(
        f"{output_dir}/{week_number}주차_시간대별_감정_분포.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    print(
        f"Time range emotion distribution graph saved to {output_dir}/{week_number}주차_시간대별_감정_분포.png"
    )


if __name__ == "__main__":
    import argparse

    # Process command line arguments
    parser = argparse.ArgumentParser(description="Generate team distribution graphs")
    parser.add_argument(
        "--week", type=int, default=0, help="Week number (0, 2, 4, etc.)"
    )
    parser.add_argument(
        "--team",
        type=int,
        required=False,
        help="Team number (1, 2, 3, etc.). Not used by all graphs.",
    )
    args = parser.parse_args()

    if args.team is not None:
        generate_bat_primary_distribution_graph(args.week, args.team)
        generate_exhaustion_distribution_graph(args.week, args.team)
        generate_cognitive_regulation_distribution_graph(args.week, args.team)
        generate_emotional_regulation_distribution_graph(args.week, args.team)
        generate_depersonalization_distribution_graph(args.week, args.team)
        generate_stress_distribution_graph(args.week, args.team)
        generate_stress_subcategories_boxplot(args.week, args.team)
        generate_emotional_labor_subcategories_boxplot(args.week, args.team)
    else:
        print("No specific team number provided. Skipping team-specific graphs.")
        print("You can run company-wide reports or specify a --team <number>.")

    generate_burnout_summary_table(args.week)
    generate_stress_summary_table(args.week)
    generate_emotional_labor_summary_table(args.week)
    generate_app_usage_by_date_graph(args.week)
    generate_emotion_records_by_date_graph(args.week)
    generate_emotion_distribution_pie_chart(args.week)
    generate_weekday_emotion_distribution_graph(args.week)
    generate_timerange_emotion_distribution_graph(
        args.week
    )  # Added call to the new function
