#!/usr/bin/env python3
"""
Script to fetch daily emotion counts from consolidated app analysis file.
Reads data from data/figures/final/app_analysis_final.json.
"""

import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime


def fetch_daily_emotion_counts():
    """
    Fetch daily emotion counts from consolidated app analysis file.

    Returns:
        dict: Dictionary with date strings as keys and emotion counts as values
    """
    # Define the path to the consolidated analysis file
    file_path = Path("data/figures/final/app_analysis_final.json")

    # Check if file exists
    if not file_path.exists():
        print(f"Error: File {file_path} does not exist.")
        return {}

    try:
        # Load the JSON file
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract daily_emotion_records from this file
        if "daily_emotion_records" in data:
            daily_emotion_records = data["daily_emotion_records"]
            print(f"Loaded {len(daily_emotion_records)} emotion records from {file_path.name}")
            return daily_emotion_records
        else:
            print(f"Warning: 'daily_emotion_records' not found in {file_path.name}")
            return {}

    except json.JSONDecodeError as e:
        print(f"Error reading JSON from {file_path}: {e}")
        return {}
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return {}


def main():
    """
    Main function
    """
    # Fetch daily emotion records from multiple app analysis files
    daily_emotion_records = fetch_daily_emotion_counts()

    # Sort dates to ensure proper chronological order
    sorted_dates = sorted(daily_emotion_records.keys())

    # Create x-axis labels with date and day of week (e.g., "8/17\nSun")
    x_labels = []
    for date in sorted_dates:
        # Parse the date string (assumed format: YYYY-MM-DD)
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        # Format as MM/DD with day of week abbreviation
        date_label = f"{date_obj.month}/{date_obj.day}\n{date_obj.strftime('%a')}"
        x_labels.append(date_label)

    # Get corresponding emotion record counts in the same order
    emotion_counts = [daily_emotion_records[date] for date in sorted_dates]

    # Create a larger figure to accommodate longer x-axis
    plt.figure(figsize=(40, 8))

    # Draw a broken line graph with markers
    plt.plot(
        range(len(x_labels)), emotion_counts, marker="o", linewidth=2, markersize=6
    )

    # Set x-axis labels
    plt.xticks(range(len(x_labels)), x_labels)

    # Add y-axis value annotations on every point
    for i, count in enumerate(emotion_counts):
        plt.annotate(
            str(count),
            (i, count),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
        )

    # Add title and labels
    plt.title("Daily Emotion Records", fontsize=16, fontweight="bold")
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Emotion Record Count", fontsize=12)

    # Add text box to show sum and average.
    stats_text = f"Total: {sum(emotion_counts)} records\nAverage: {round(sum(emotion_counts) / len(emotion_counts), 2)} records per day"
    plt.text(0.05, 0.95, stats_text)

    # Add grid for better readability
    plt.grid(True, alpha=0.3)

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Generate a directory data/figures/final
    figdir = "data/figures/final"
    os.makedirs(figdir, exist_ok=True)

    # Save plot in the directory above
    plt.savefig(f"{figdir}/2-감정 데이터 총 기록 수.png", dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    # Execute the main function
    result = main()
