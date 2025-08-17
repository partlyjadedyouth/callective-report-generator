#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to analyze the presence of text in the '마음_기록_입력_내용_(텍스트)' column
from final_data_parsed.csv and create a pie chart visualization.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os


def analyze_text_records(file_path):
    """
    Analyzes the CSV file to count records with and without text entries.
    """
    df = pd.read_csv(file_path)
    text_column = "마음_기록_입력_내용_(텍스트)"

    with_text = df[text_column].notna().sum()
    without_text = df[text_column].isna().sum()

    return with_text, without_text


def create_pie_chart(with_text_count, without_text_count, output_path):
    """
    Creates and saves a pie chart of text vs. no-text records.
    """
    # Set font for Korean characters
    plt.rcParams["font.family"] = "AppleGothic"
    plt.rcParams["axes.unicode_minus"] = False

    labels = ["텍스트 기록 있음", "텍스트 기록 없음"]
    sizes = [with_text_count, without_text_count]
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
    )

    plt.title(
        "텍스트 기록 유무 비율",
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
    Main function to run the text record analysis.
    """
    input_file = "data/figures/final/final_data_parsed.csv"
    output_file = "data/figures/final/8-텍스트-기록-비율.png"

    try:
        print("Analyzing text records...")
        with_text, without_text = analyze_text_records(input_file)

        total_records = with_text + without_text
        print(f"Total records analyzed: {total_records:,}")
        print(f"Records with text: {with_text:,} ({with_text/total_records*100:.1f}%)")
        print(
            f"Records without text: {without_text:,} ({without_text/total_records*100:.1f}%)"
        )

        print("\nCreating pie chart...")
        create_pie_chart(with_text, without_text, output_file)

        print("Analysis completed successfully!")

    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
