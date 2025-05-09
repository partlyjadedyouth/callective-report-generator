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
    plt.savefig(f"{output_dir}/stress_week{week_number}.png", dpi=300)
    plt.close()

    print(f"Graph saved to {output_dir}/stress_week{week_number}.png")


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

    # Korean stress subcategories
    subcategories = [
        "직무 요구",
        "직무 자율",
        "관계 갈등",
        "직무 불안",
        "조직 체계",
        "보상 부적절",
        "직장 문화",
    ]

    # English translations for display
    subcategories_english = [
        "Job Demand",
        "Job Control",
        "Interpersonal Conflict",
        "Job Insecurity",
        "Organizational System",
        "Inadequate Compensation",
        "Workplace Culture",
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
    # Convert dictionary to list of values for box plot
    box_data = [subcategory_data[subcat] for subcat in subcategories]

    # Create horizontal box plot with English labels
    box = plt.boxplot(
        box_data,
        vert=False,  # Horizontal orientation
        patch_artist=True,  # Fill boxes with color
        labels=subcategories_english,  # Use English subcategory names as labels
    )

    # Calculate medians for each subcategory
    medians = [np.median(data) if len(data) > 0 else 0 for data in box_data]

    # Choose colors based on median values and cutoff values
    box_colors = []
    for i, subcat in enumerate(subcategories):
        median = medians[i]
        cutoff = cutoff_map[subcat]

        # Determine color based on median value compared to cutoffs
        if median < cutoff[0]:
            # Normal range (green)
            box_colors.append("lightgreen")
        elif median < cutoff[1]:
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

    # Add text with median values and cutoffs
    for i, subcat in enumerate(subcategories):
        cutoff = cutoff_map[subcat]
        plt.text(
            95,
            i + 1,
            f"Median: {medians[i]:.1f}\nCutoffs: {cutoff[0]}/{cutoff[1]}",
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
    plt.savefig(f"{output_dir}/stress_subcategories_week{week_number}.png", dpi=300)
    plt.close()

    print(
        f"Stress subcategories box plot saved to {output_dir}/stress_subcategories_week{week_number}.png"
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

    # Create horizontal box plot with English labels
    box = plt.boxplot(
        box_data,
        vert=False,  # Horizontal orientation
        patch_artist=True,  # Fill boxes with color
        labels=subcategories_english,  # Use English subcategory names as labels
    )

    # Calculate medians for each subcategory
    medians = [np.median(data) if len(data) > 0 else 0 for data in box_data]

    # Choose colors based on median values and cutoff values
    box_colors = []
    for i, subcat in enumerate(subcategories):
        median = medians[i]
        cutoff = cutoff_map[subcat]

        # Determine color based on median value compared to cutoff
        # Only two levels: normal and high risk
        if median < cutoff:
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

    # Add text with median values and cutoffs
    for i, subcat in enumerate(subcategories):
        cutoff = cutoff_map[subcat]
        plt.text(
            95,
            i + 1,
            f"Median: {medians[i]:.1f}\nCutoff: {cutoff}",
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
        f"{output_dir}/emotional_labor_subcategories_week{week_number}.png", dpi=300
    )
    plt.close()

    print(
        f"Emotional labor subcategories box plot saved to {output_dir}/emotional_labor_subcategories_week{week_number}.png"
    )


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

    generate_bat_primary_distribution_graph(args.week, args.team)
    generate_exhaustion_distribution_graph(args.week, args.team)
    generate_cognitive_regulation_distribution_graph(args.week, args.team)
    generate_emotional_regulation_distribution_graph(args.week, args.team)
    generate_depersonalization_distribution_graph(args.week, args.team)
    generate_stress_distribution_graph(args.week, args.team)
    generate_stress_subcategories_boxplot(args.week, args.team)
    generate_emotional_labor_subcategories_boxplot(args.week, args.team)
