#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Report Generator Main Script

This script coordinates the process of:
1. Fetching data from a Google Spreadsheet using its key
2. Saving the data as a CSV file
3. Parsing the data to generate questionnaire results for multiple questionnaire types
4. Analyzing the survey results and generating per-participant statistics across weeks
"""

# Import required libraries
import argparse  # Library for parsing command-line arguments
import os  # Library for operating system functionality

# Import custom modules
from fetch_spreadsheet import (
    fetch_google_sheet,
    save_to_csv,
)  # Import functions for fetching and saving spreadsheet data
from parse_raw import (
    parse_bat_primary_results,
)  # Import function for parsing questionnaire results
from analyze_results import analyze_results  # Import function for analyzing results


def main():
    """
    Main function to execute the report generation process.
    """
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Generate reports from Google Spreadsheet data"
    )  # Create argument parser
    parser.add_argument(
        "--sheet_key",
        type=str,
        required=True,  # Add argument for spreadsheet key
        help="Google Spreadsheet key/ID",
    )
    parser.add_argument(
        "--week",
        type=int,
        default=0,  # Add argument for week number with default value of 0
        help="Week number to use in file names (e.g., 0 for '0주차')",
    )

    # Parse the command-line arguments
    args = parser.parse_args()  # Parse arguments

    # Set default values for other parameters
    sheet_name = None  # Default sheet name is None
    csv_dir = "data/csv"  # Default directory for CSV files
    results_dir = "data/results"  # Default directory for results
    analysis_dir = "data/analysis"  # Default directory for analysis results

    # Default questionnaire paths
    bat_primary_path = "data/questionnaires/bat_primary_questionnaires.json"  # Default BAT primary path
    bat_secondary_path = "data/questionnaires/bat_secondary_questionnaires.json"  # Default BAT secondary path
    emotional_labor_path = "data/questionnaires/emotional_labor_questionnaires.json"  # Default emotional labor path
    stress_path = (
        "data/questionnaires/stress_questionnaires.json"  # Default stress path
    )

    # Create week suffix for filenames
    week_suffix = f"{args.week}주차"  # Format week number as "0주차", "1주차", etc.

    # Create necessary directories if they don't exist
    os.makedirs(csv_dir, exist_ok=True)  # Create CSV directory if it doesn't exist
    os.makedirs(
        results_dir, exist_ok=True
    )  # Create results directory if it doesn't exist
    os.makedirs(
        analysis_dir, exist_ok=True
    )  # Create analysis directory if it doesn't exist

    # Define the CSV output path
    csv_path = os.path.join(
        csv_dir, f"google_sheet_export_{week_suffix}.csv"
    )  # Construct path for CSV output file

    # Step 1: Fetch data from Google Spreadsheet
    print(
        f"Fetching data from Google Spreadsheet: {args.sheet_key}"
    )  # Print status message
    sheet_data = fetch_google_sheet(
        args.sheet_key, sheet_name
    )  # Fetch spreadsheet data

    # Check if data was successfully fetched
    if not sheet_data:  # If no data was fetched
        print(
            "Failed to fetch data from Google Spreadsheet. Exiting."
        )  # Print error message
        return 1  # Return error code

    # Step 2: Save the fetched data to a CSV file
    print(f"Saving data to CSV: {csv_path}")  # Print status message
    saved_path = save_to_csv(sheet_data, csv_path)  # Save data to CSV file

    # Check if CSV was successfully saved
    if not saved_path:  # If saving failed
        print("Failed to save data to CSV file. Exiting.")  # Print error message
        return 1  # Return error code

    # Step 3: Prepare questionnaire paths dictionary
    questionnaire_paths = {  # Create dictionary of questionnaire paths
        "BAT_primary": bat_primary_path,  # BAT primary path
        "BAT_secondary": bat_secondary_path,  # BAT secondary path
        "emotional_labor": emotional_labor_path,  # Emotional labor path
        "stress": stress_path,  # Stress path
    }

    # Step 4: Parse the CSV data to generate questionnaire results
    print("Parsing questionnaire results...")  # Print status message
    result_file = parse_bat_primary_results(  # Parse questionnaire results
        csv_path=saved_path,
        questionnaire_path=questionnaire_paths,
        output_dir=results_dir,
        week_suffix=week_suffix,
    )

    # Check if results were successfully generated
    if not result_file:  # If results were not generated
        print("Failed to generate questionnaire results.")  # Print error message
        return 1  # Return error code

    # Step 5: Analyze the survey results for each participant
    print(
        "Analyzing survey results for each participant across all weeks..."
    )  # Print status message
    analysis_file = analyze_results(  # Analyze the survey results
        results_dir=results_dir, output_dir=analysis_dir
    )

    # Check if analysis was successfully generated
    if analysis_file:  # If analysis was generated
        print(
            f"Participant analysis results saved to {analysis_file}"
        )  # Print success message
        print(
            f"Process completed successfully. Results saved to {result_file} and participant analysis to {analysis_file}"
        )  # Print success message
        return 0  # Return success code
    else:
        print("Failed to analyze survey results.")  # Print error message
        return 1  # Return error code


if __name__ == "__main__":
    """
    Execute the main function when the script is run directly.

    Example usage:
    python src/main.py --sheet_key=asdf --week=0
    """
    exit(main())  # Run main function and use its return code as exit code
