#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to analyze the presence of intervention activities in the '중재_활동_이름' column
from final_data_parsed.csv and create a pie chart visualization.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

def analyze_intervention_records(file_path):
    """
    Analyzes the CSV file to count records with and without intervention entries.
    """
    df = pd.read_csv(file_path)
    intervention_column = "중재_활동_이름"

    with_intervention = df[intervention_column].notna().sum()
    without_intervention = df[intervention_column].isna().sum()

    return with_intervention, without_intervention

def create_pie_chart(with_intervention_count, without_intervention_count, output_path):
    """
    Creates and saves a pie chart of intervention vs. no-intervention records.
    """
    # Set font for Korean characters
    plt.rcParams['font.family'] = 'AppleGothic'
    plt.rcParams['axes.unicode_minus'] = False

    labels = ["중재 활동 기록 있음", "중재 활동 기록 없음"]
    sizes = [with_intervention_count, without_intervention_count]
    colors = ["cornflowerblue", "indianred"]
    explode = (0.05, 0.05)

    plt.figure(figsize=(10, 8))

    wedges, texts, autotexts = plt.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90,
        textprops={"fontsize": 12, "fontweight": "bold"},
        explode=explode
    )

    plt.title(
        "중재 활동 기록 유무 비율",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )

    for i, text in enumerate(texts):
        count = sizes[i]
        text.set_text(f"{labels[i]}\n({count:,} 건)")

    plt.axis("equal")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Pie chart saved to: {output_path}")

def main():
    """
    Main function to run the intervention record analysis.
    """
    input_file = "data/figures/final/final_data_parsed.csv"
    output_file = "data/figures/final/9-중재-활동-기록-비율.png"

    try:
        print("Analyzing intervention records...")
        with_intervention, without_intervention = analyze_intervention_records(input_file)

        total_records = with_intervention + without_intervention
        print(f"Total records analyzed: {total_records:,}")
        print(f"Records with intervention: {with_intervention:,} ({with_intervention/total_records*100:.1f}%)")
        print(f"Records without intervention: {without_intervention:,} ({without_intervention/total_records*100:.1f}%)")

        print("\nCreating pie chart...")
        create_pie_chart(with_intervention, without_intervention, output_file)

        print("Analysis completed successfully!")

    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
