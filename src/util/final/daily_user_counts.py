#!/usr/bin/env python3
"""
Script to fetch and consolidate daily user counts from app analysis files.
Fetches data from app_analysis_n주차.json files where n = 0, 2, 4, 6, 8, 10, 12.
"""

import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime


def fetch_daily_user_counts():
    """
    Fetch daily user counts from multiple app analysis files.

    Returns:
        dict: Dictionary with date strings as keys and user counts as values
    """
    # Define the base path for analysis files
    data_dir = Path("data/analysis")

    # Define the week numbers to fetch (0, 2, 4, 6, 8, 10, 12)
    week_numbers = [0, 2, 4, 6, 8, 10, 12]

    # Initialize the consolidated daily user counts dictionary
    daily_user_counts = {}

    # Process each week file
    for week_num in week_numbers:
        file_path = data_dir / f"app_analysis_{week_num}주차.json"

        # Check if file exists
        if not file_path.exists():
            print(f"Warning: File {file_path} does not exist, skipping...")
            continue

        try:
            # Load the JSON file
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract daily_user_counts from this file
            if "daily_user_counts" in data:
                file_daily_counts = data["daily_user_counts"]

                # Add all entries to the consolidated dictionary
                for date, count in file_daily_counts.items():
                    daily_user_counts[date] = count

                print(
                    f"Loaded {len(file_daily_counts)} daily counts from {file_path.name}"
                )
            else:
                print(f"Warning: 'daily_user_counts' not found in {file_path.name}")

        except json.JSONDecodeError as e:
            print(f"Error reading JSON from {file_path}: {e}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    return daily_user_counts


def main():
    """
    Main function
    """
    # Fetch daily user counts from multiple app analysis files
    daily_user_counts = fetch_daily_user_counts()

    # Sort dates to ensure proper chronological order
    sorted_dates = sorted(daily_user_counts.keys())

    # Create x-axis labels with date and day of week (e.g., "8/17\nSun")
    x_labels = []
    for date in sorted_dates:
        # Parse the date string (assumed format: YYYY-MM-DD)
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        # Format as MM/DD with day of week abbreviation
        date_label = f"{date_obj.month}/{date_obj.day}\n{date_obj.strftime('%a')}"
        x_labels.append(date_label)

    # Get corresponding user counts in the same order
    user_counts = [daily_user_counts[date] for date in sorted_dates]

    # Create a larger figure to accommodate longer x-axis
    plt.figure(figsize=(40, 8))

    # Draw a broken line graph with markers
    plt.plot(range(len(x_labels)), user_counts, marker="o", linewidth=2, markersize=6)

    # Set x-axis labels and rotate them for better readability
    plt.xticks(range(len(x_labels)), x_labels)

    # Add y-axis value annotations on every point
    for i, count in enumerate(user_counts):
        plt.annotate(
            str(count),
            (i, count),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
        )

    # Add title and labels
    plt.title("Daily User Counts", fontsize=16, fontweight="bold")
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("User Count", fontsize=12)

    # Add text box to show sum and average.
    stats_text = f"Total: {sum(user_counts)} records\nAverage: {round(sum(user_counts) / len(user_counts), 2)} records per day"
    plt.text(0.05, 2.5, stats_text)

    # Add grid for better readability
    plt.grid(True, alpha=0.3)

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Generate a directory data/figures/final
    figdir = "data/figures/final"
    os.makedirs(figdir, exist_ok=True)

    # Save plot in the directory above
    plt.savefig(f"{figdir}/1-앱 평균 사용자수.png", dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    # Execute the main function
    result = main()
