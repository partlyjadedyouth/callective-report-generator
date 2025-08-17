import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

"""
Fetch time_range_emotion_categories
"""
# Define the base path for analysis files
data_dir = Path("data/analysis")

# Define the week numbers to fetch (0, 2, 4, 6, 8, 10, 12)
week_numbers = [0, 2, 4, 6, 8, 10, 12]

# Initialize dictionary
time_range_emotion_categories = {}

# Process each file
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
        if "time_range_emotion_categories" in data:
            file_time_range = data["time_range_emotion_categories"]

            for time_range in file_time_range.keys():
                if time_range in time_range_emotion_categories:
                    time_range_emotion_categories[time_range][
                        "positive"
                    ] += file_time_range[time_range]["positive"]
                    time_range_emotion_categories[time_range][
                        "negative"
                    ] += file_time_range[time_range]["negative"]
                else:
                    time_range_emotion_categories[time_range] = file_time_range[
                        time_range
                    ]

            print(f"Loaded from {file_path.name}")
        else:
            print(
                f"Warning: 'time_range_emotion_categories' not found in {file_path.name}"
            )

    except json.JSONDecodeError as e:
        print(f"Error reading JSON from {file_path}: {e}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

print(time_range_emotion_categories)

# Extract data for visualization
time_ranges = list(time_range_emotion_categories.keys())
positive_counts = [time_range_emotion_categories[tr]["positive"] for tr in time_ranges]
negative_counts = [time_range_emotion_categories[tr]["negative"] for tr in time_ranges]

# Calculate totals for percentage calculation
total_counts = [pos + neg for pos, neg in zip(positive_counts, negative_counts)]

# Create the stacked bar chart
fig, ax = plt.subplots(figsize=(12, 8))

# Create bar positions
x_pos = range(len(time_ranges))

# Create stacked bars (red for negative on bottom, blue for positive on top)
bars_negative = ax.bar(x_pos, negative_counts, color="red", alpha=0.7, label="Negative")
bars_positive = ax.bar(
    x_pos,
    positive_counts,
    bottom=negative_counts,
    color="blue",
    alpha=0.7,
    label="Positive",
)

# Add labels showing count and percentage for each segment
for i, (neg_count, pos_count, total) in enumerate(
    zip(negative_counts, positive_counts, total_counts)
):
    if total > 0:  # Avoid division by zero
        # Label for negative (red) bar
        if neg_count > 0:
            neg_percentage = (neg_count / total) * 100
            ax.text(
                i,
                neg_count / 2,
                f"{neg_count}\n({neg_percentage:.1f}%)",
                ha="center",
                va="center",
                fontweight="bold",
                color="white",
                fontsize=10,
            )

        # Label for positive (blue) bar
        if pos_count > 0:
            pos_percentage = (pos_count / total) * 100
            ax.text(
                i,
                neg_count + pos_count / 2,
                f"{pos_count}\n({pos_percentage:.1f}%)",
                ha="center",
                va="center",
                fontweight="bold",
                color="white",
                fontsize=10,
            )

        # Add total count on top of each bar
        ax.text(
            i,
            total,
            f"{total}",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=10,
        )

# Configure chart appearance
ax.set_xlabel("Time Range", fontsize=12, fontweight="bold")
ax.set_ylabel("Number of Emotion Records", fontsize=12, fontweight="bold")
ax.set_title(
    "Emotion Records by Time Range\n(Positive vs Negative)",
    fontsize=14,
    fontweight="bold",
)
ax.set_xticks(x_pos)
ax.set_xticklabels(time_ranges, rotation=45, ha="right")
ax.legend(loc="upper right")
ax.grid(axis="y", alpha=0.3)

# Adjust layout and save/display the plot
plt.tight_layout()
# Generate a directory data/figures/final
figdir = "data/figures/final"
os.makedirs(figdir, exist_ok=True)

# Save plot in the directory above
plt.savefig(f"{figdir}/3-시간대 별 감정 기록.png", dpi=300, bbox_inches="tight")
