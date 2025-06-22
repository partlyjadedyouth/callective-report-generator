#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Emotional Labor Risk Summary Generator

This script generates a CSV-formatted summary of emotional labor risk levels
for T1 (0주차) and T3 (4주차) across all five emotional labor subcategories.
The output shows the count of normal and risk groups for each time point and category.
"""

# Import required libraries
import json  # Library for handling JSON data
import csv  # Library for handling CSV files
import sys  # Library for system-specific parameters and functions
from pathlib import Path  # Library for handling file paths


def load_analysis_data(analysis_file="data/analysis/analysis.json"):
    """
    Load analysis data from JSON file.

    Args:
        analysis_file (str): Path to the analysis JSON file

    Returns:
        dict: Analysis data loaded from JSON file
    """
    try:
        # Load analysis data from JSON file
        with open(analysis_file, "r", encoding="utf-8") as f:
            analysis_data = json.load(f)
        return analysis_data
    except FileNotFoundError:
        print(f"Error: Analysis file not found at {analysis_file}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {analysis_file}")
        return None


def generate_emotional_labor_risk_summary(analysis_data):
    """
    Generate emotional labor risk summary in CSV format.

    Args:
        analysis_data (dict): Analysis data containing risk level information

    Returns:
        list: List of rows for CSV output
    """
    # Define the mapping between English column names and Korean category names
    category_mapping = {
        "Regulation": "감정조절의 노력 및 다양성",
        "Overload": "고객응대의 과부하 및 갈등",
        "Dissonance": "감정부조화 및 손상",
        "Surveilance": "조직의 감시 및 모니터링",
        "Support": "조직의 지지 및 보호체계",
    }

    # Define time points mapping
    time_mapping = {
        "T1": "0주차",  # T1 corresponds to week 0
        "T3": "4주차",  # T3 corresponds to week 4
    }

    # Get company-wide analysis data
    company_data = analysis_data.get("groups", {}).get("회사", {}).get("analysis", {})

    # Create header row with all column combinations
    header = ["Category"]
    for time_point in ["T1", "T3"]:
        for category in [
            "Regulation",
            "Overload",
            "Dissonance",
            "Surveilance",
            "Support",
        ]:
            header.append(f"{time_point}_{category}")

    # Initialize data rows for Normal and Risk groups
    normal_row = ["Normal"]
    risk_row = ["Risk"]

    # Extract data for each time point and category combination
    for time_point, week in time_mapping.items():
        for category, korean_name in category_mapping.items():
            # Get emotional labor risk data for this week
            week_data = company_data.get(week, {})
            emotional_labor_risks = week_data.get("risk_levels", {}).get(
                "emotional_labor", {}
            )
            category_data = emotional_labor_risks.get(
                korean_name, {"정상": 0, "위험": 0}
            )

            # Add counts to respective rows
            normal_row.append(category_data.get("정상", 0))
            risk_row.append(category_data.get("위험", 0))

    # Return the complete CSV data
    return [header, normal_row, risk_row]


def print_csv_summary(csv_data):
    """
    Print CSV data to console in proper CSV format.

    Args:
        csv_data (list): List of rows to print as CSV
    """
    # Print header with explanation
    print("Emotional Labor Risk Summary (Company-wide)")
    print("=" * 80)
    print("Time Points: T1 = 0주차 (Week 0), T3 = 4주차 (Week 4)")
    print("Categories: Regulation, Overload, Dissonance, Surveilance, Support")
    print("Values: Count of participants in Normal/Risk groups")
    print("=" * 80)
    print()

    # Print CSV data
    for row in csv_data:
        # Convert all values to strings and join with commas
        row_str = ",".join(str(cell) for cell in row)
        print(row_str)


def save_csv_file(
    csv_data, output_file="data/analysis/emotional_labor_risk_summary.csv"
):
    """
    Save CSV data to file.

    Args:
        csv_data (list): List of rows to save as CSV
        output_file (str): Path to output CSV file
    """
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write CSV data to file
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(csv_data)

        print(f"\nCSV file saved to: {output_file}")

    except Exception as e:
        print(f"Error saving CSV file: {e}")


def main():
    """
    Main function to generate and print emotional labor risk summary.
    """
    # Load analysis data from JSON file
    analysis_data = load_analysis_data()

    if analysis_data is None:
        print("Failed to load analysis data. Exiting.")
        sys.exit(1)

    # Generate emotional labor risk summary
    csv_data = generate_emotional_labor_risk_summary(analysis_data)

    # Print CSV summary to console
    print_csv_summary(csv_data)

    # Save CSV file
    save_csv_file(csv_data)


if __name__ == "__main__":
    main()
