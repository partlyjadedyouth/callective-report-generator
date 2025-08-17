#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to analyze the distribution of intervention activities from final_data_parsed.csv
and create a pie chart visualization.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os


def analyze_intervention_distribution(file_path):
    """
    Analyzes the CSV file to count the occurrences of each intervention activity.
    """
    df = pd.read_csv(file_path)
    intervention_column = "중재_활동_이름"

    # Drop rows where the intervention name is missing and count the occurrences of each activity
    intervention_counts = df[intervention_column].dropna().value_counts()

    return intervention_counts


def create_bar_chart(intervention_counts, output_path):
    """
    Creates and saves a bar chart of the intervention distribution.
    """
    # Set font for Korean characters
    plt.rcParams["font.family"] = "AppleGothic"
    plt.rcParams["axes.unicode_minus"] = False

    # Data is already sorted by value_counts()
    labels = intervention_counts.index
    counts = intervention_counts.values

    num_colors = len(labels)
    colors = plt.cm.get_cmap("tab20c", num_colors).colors

    plt.figure(figsize=(14, 8))
    
    bars = plt.bar(labels, counts, color=colors)

    plt.title(
        "중재 활동 분포",
        fontsize=18,
        fontweight="bold",
        pad=20,
    )
    plt.xlabel("중재 활동", fontsize=12)
    plt.ylabel("횟수", fontsize=12)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(fontsize=10)

    # Add counts on top of each bar
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval}', va='bottom', ha='center', fontsize=10)

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Bar chart saved to: {output_path}")


def main():
    """
    Main function to run the intervention distribution analysis.
    """
    input_file = "data/figures/final/final_data_parsed.csv"
    output_file = "data/figures/final/10-중재-활동-분포-막대.png"

    try:
        print("Analyzing intervention distribution...")
        intervention_counts = analyze_intervention_distribution(input_file)

        print("\nIntervention Activity Counts:")
        print(intervention_counts)

        print("\nCreating bar chart...")
        create_bar_chart(intervention_counts, output_file)

        print("Analysis completed successfully!")

    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file}")
    except Exception as e:
        print(f"An error occurred: {e}")



if __name__ == "__main__":
    main()
