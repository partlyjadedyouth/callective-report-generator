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

    # Set cutoff values for BAT_primary (from personal_report_generator.py)
    cutoff_burnout_primary = [2.58, 3.01]

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


if __name__ == "__main__":
    import argparse

    # Process command line arguments
    parser = argparse.ArgumentParser(
        description="Generate BAT_primary distribution graph"
    )
    parser.add_argument(
        "--week", type=int, default=0, help="Week number (0, 2, 4, etc.)"
    )
    parser.add_argument(
        "--team", type=int, required=True, help="Team number (1, 2, 3, etc.)"
    )
    args = parser.parse_args()

    # Call the graph generation function
    generate_bat_primary_distribution_graph(args.week, args.team)
