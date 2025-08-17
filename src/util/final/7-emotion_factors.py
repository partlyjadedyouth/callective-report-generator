#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to analyze emotion factors from app_analysis_final.json
and create pie chart visualizations for each emotion.
"""

import json
import matplotlib.pyplot as plt
import os
from collections import Counter

# Set font for Korean characters
plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def load_emotion_data(file_path):
    """Load emotion records from JSON file"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("emotion_records", [])


def analyze_emotion_factors(emotion_records):
    """Analyze the factors associated with each emotion."""
    emotion_factors = {}
    for record in emotion_records:
        emotion = record.get("emotion")
        factors = record.get("factors")
        if emotion and factors:
            if emotion not in emotion_factors:
                emotion_factors[emotion] = []
            emotion_factors[emotion].extend(factors)
    return emotion_factors


def create_factor_pie_chart(emotion, factors, factor_color_map, output_path):
    """Create and save a pie chart for the factors of a single emotion."""
    factor_counts = Counter(factors)

    # Sort factors by count in descending order
    sorted_factors = sorted(
        factor_counts.items(), key=lambda item: item[1], reverse=True
    )
    labels = [factor for factor, count in sorted_factors]
    sizes = [count for factor, count in sorted_factors]

    # Get colors from the predefined map
    colors = [factor_color_map[factor] for factor in labels]

    plt.figure(figsize=(12, 10))
    wedges, texts, autotexts = plt.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct=lambda p: "{:.1f}%\n({:d})".format(
            p, int(round(p * sum(sizes) / 100.0))
        ),
        startangle=90,
        textprops={"fontsize": 12},
    )

    plt.title(
        f"'{emotion}' 감정의 원인",
        fontsize=18,
        fontweight="bold",
        pad=20,
    )

    plt.axis("equal")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Pie chart for '{emotion}' saved to: {output_path}")


def main():
    """Main function to run the emotion factor analysis."""
    input_file = "data/figures/final/app_analysis_final.json"
    output_dir = "data/figures/final"

    try:
        print("Loading emotion data...")
        emotion_records = load_emotion_data(input_file)
        print(f"Loaded {len(emotion_records):,} emotion records")

        print("\nAnalyzing emotion factors...")
        emotion_factors = analyze_emotion_factors(emotion_records)

        # Create a consistent color map for all factors
        all_factors = set()
        for factors in emotion_factors.values():
            all_factors.update(factors)

        color_palette = plt.cm.get_cmap("tab20c", len(all_factors))
        factor_color_map = {
            factor: color_palette(i) for i, factor in enumerate(all_factors)
        }

        for emotion, factors in emotion_factors.items():
            if factors:
                output_file = os.path.join(output_dir, f"7-{emotion}_요인_분석.png")
                create_factor_pie_chart(emotion, factors, factor_color_map, output_file)

        print("\nAnalysis completed successfully!")

    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file}")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")


if __name__ == "__main__":
    main()
