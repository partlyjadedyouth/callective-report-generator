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

# 절단점 값을 가져오기 위한 임포트
from cutoff_values import (
    CUTOFF_BURNOUT_PRIMARY,
    CUTOFF_BURNOUT_EXHAUSTION,
    CUTOFF_BURNOUT_DEPERSONALIZATION,
    CUTOFF_BURNOUT_COGNITIVE_REGULATION,
    CUTOFF_BURNOUT_EMOTIONAL_REGULATION,
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

    # Get the maximum y value for filling background colors
    ax = plt.gca()
    ymax = ax.get_ylim()[1]

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
    plt.savefig(f"{output_dir}/bat_primary_week{week_number}.png", dpi=300)
    plt.close()

    print(f"Graph saved to {output_dir}/bat_primary_week{week_number}.png")


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
    plt.savefig(f"{output_dir}/exhaustion_week{week_number}.png", dpi=300)
    plt.close()

    print(f"Graph saved to {output_dir}/exhaustion_week{week_number}.png")


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
    plt.savefig(f"{output_dir}/cognitive_regulation_week{week_number}.png", dpi=300)
    plt.close()

    print(f"Graph saved to {output_dir}/cognitive_regulation_week{week_number}.png")


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
    plt.savefig(f"{output_dir}/emotional_regulation_week{week_number}.png", dpi=300)
    plt.close()

    print(f"Graph saved to {output_dir}/emotional_regulation_week{week_number}.png")


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
    plt.savefig(f"{output_dir}/depersonalization_week{week_number}.png", dpi=300)
    plt.close()

    print(f"Graph saved to {output_dir}/depersonalization_week{week_number}.png")


if __name__ == "__main__":
    import argparse

    # Process command line arguments
    parser = argparse.ArgumentParser(description="Generate team distribution graphs")
    parser.add_argument(
        "--week", type=int, default=0, help="Week number (0, 2, 4, etc.)"
    )
    parser.add_argument(
        "--team", type=int, required=True, help="Team number (1, 2, 3, etc.)"
    )
    args = parser.parse_args()

    # Call the graph generation functions
    generate_bat_primary_distribution_graph(args.week, args.team)
    generate_exhaustion_distribution_graph(args.week, args.team)
    generate_cognitive_regulation_distribution_graph(args.week, args.team)
    generate_emotional_regulation_distribution_graph(args.week, args.team)
    generate_depersonalization_distribution_graph(args.week, args.team)
