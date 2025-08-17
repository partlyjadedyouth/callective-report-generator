#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to analyze positive vs negative emotions from app_analysis_final.json
and create a pie chart visualization.
"""

import json
import matplotlib.pyplot as plt
import os


def load_emotion_data(file_path):
    """Load emotion records from JSON file"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("emotion_records", [])


def categorize_emotions():
    """Define positive and negative emotion categories in Korean"""
    positive_emotions = {
        "행복해요",  # happy
        "신나요",  # excited
        "만족스러워요",  # satisfied
        "차분해요",  # calm
    }

    negative_emotions = {
        "우울해요",  # depressed
        "슬퍼요",  # sad
        "화가나요",  # angry
        "불안해요",  # anxious
    }

    return positive_emotions, negative_emotions


def analyze_emotions(emotion_records):
    """Count positive vs negative emotions from the records"""
    positive_emotions, negative_emotions = categorize_emotions()

    positive_count = 0
    negative_count = 0
    unknown_emotions = set()

    # Count emotions from all records
    for record in emotion_records:
        emotion = record.get("emotion", "")

        if emotion in positive_emotions:
            positive_count += 1
        elif emotion in negative_emotions:
            negative_count += 1
        else:
            unknown_emotions.add(emotion)

    # Print unknown emotions for debugging
    if unknown_emotions:
        print(f"Unknown emotions found: {unknown_emotions}")

    return positive_count, negative_count


def create_pie_chart(positive_count, negative_count, output_path):
    """Create and save pie chart of positive vs negative emotions"""

    # Data for pie chart
    labels = ["Positive Emotions", "Negative Emotions"]
    sizes = [positive_count, negative_count]
    colors = [
        "cornflowerblue",
        "indianred",
    ]  # Match color theme from time_range_emotions.py
    explode = (0.05, 0.05)  # Slightly separate both slices

    # Create figure and axis
    plt.figure(figsize=(10, 8))

    # Create pie chart
    wedges, texts, autotexts = plt.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90,
        textprops={"fontsize": 12, "fontweight": "bold"},
    )

    # Customize the chart
    plt.title(
        "Positive vs Negative Emotion Distribution",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )

    # Add count information to labels
    for i, text in enumerate(texts):
        count = sizes[i]
        text.set_text(f"{labels[i]}\n({count:,} records)")

    # Equal aspect ratio ensures pie chart is circular
    plt.axis("equal")

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the chart
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()  # Close the figure to free memory

    print(f"Pie chart saved to: {output_path}")


def main():
    """Main function to run the emotion analysis"""

    # File paths
    input_file = "data/figures/final/app_analysis_final.json"
    output_file = "data/figures/final/4-긍정 및 부정 감정 비율.png"

    try:
        # Load emotion data
        print("Loading emotion data...")
        emotion_records = load_emotion_data(input_file)
        print(f"Loaded {len(emotion_records):,} emotion records")

        # Analyze emotions
        print("Analyzing emotions...")
        positive_count, negative_count = analyze_emotions(emotion_records)

        total_count = positive_count + negative_count
        print(f"\\nEmotion Analysis Results:")
        print(
            f"Positive emotions: {positive_count:,} ({positive_count/total_count*100:.1f}%)"
        )
        print(
            f"Negative emotions: {negative_count:,} ({negative_count/total_count*100:.1f}%)"
        )
        print(f"Total emotion records: {total_count:,}")

        # Create pie chart
        print(f"\\nCreating pie chart...")
        create_pie_chart(positive_count, negative_count, output_file)

        print("Analysis completed successfully!")

    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file}")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")


if __name__ == "__main__":
    main()
