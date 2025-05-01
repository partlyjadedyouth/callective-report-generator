#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Report Generator Main Script

This script coordinates the process of:
1. Fetching data from a Google Spreadsheet using its key
2. Saving the data as a CSV file
3. Parsing the data to generate BAT primary results
"""

# Import required libraries
import argparse  # Library for parsing command-line arguments
import os  # Library for operating system functionality
from datetime import datetime  # Library for working with dates and times

# Import custom modules
from fetch_spreadsheet import (
    fetch_google_sheet,
    save_to_csv,
)  # Import functions for fetching and saving spreadsheet data
from parse_bat_primary import (
    parse_bat_primary_results,
)  # Import function for parsing BAT primary results


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
        "--sheet_name",
        type=str,
        default=None,  # Add optional argument for sheet name
        help="Specific sheet name/gid (optional)",
    )
    parser.add_argument(
        "--csv_dir",
        type=str,
        default="data/csv",  # Add argument for CSV directory
        help="Directory to save CSV files (default: data/csv)",
    )
    parser.add_argument(
        "--results_dir",
        type=str,
        default="data/results",  # Add argument for results directory
        help="Directory to save results (default: data/results)",
    )
    parser.add_argument(
        "--questionnaire_path",
        type=str,  # Add argument for questionnaire path
        default="data/questionnaires/bat_primary_questionnaires.json",
        help="Path to the BAT primary questionnaire JSON file",
    )

    # Parse the command-line arguments
    args = parser.parse_args()  # Parse arguments

    # Generate today's date string for filenames
    today = datetime.now().strftime("%Y%m%d")  # Format current date as YYYYMMDD

    # Create necessary directories if they don't exist
    os.makedirs(args.csv_dir, exist_ok=True)  # Create CSV directory if it doesn't exist
    os.makedirs(
        args.results_dir, exist_ok=True
    )  # Create results directory if it doesn't exist

    # Define the CSV output path
    csv_path = os.path.join(
        args.csv_dir, f"google_sheet_export_{today}.csv"
    )  # Construct path for CSV output file

    # Step 1: Fetch data from Google Spreadsheet
    print(
        f"Fetching data from Google Spreadsheet: {args.sheet_key}"
    )  # Print status message
    sheet_data = fetch_google_sheet(
        args.sheet_key, args.sheet_name
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

    # Step 3: Parse the CSV data to generate BAT primary results
    print("Parsing BAT primary results...")  # Print status message
    result_file = parse_bat_primary_results(  # Parse BAT primary results
        csv_path=saved_path,
        questionnaire_path=args.questionnaire_path,
        output_dir=args.results_dir,
        date_suffix=today,
    )

    # Check if results were successfully generated
    if result_file:  # If results were generated
        print(
            f"Process completed successfully. Results saved to {result_file}"
        )  # Print success message
        return 0  # Return success code
    else:
        print("Failed to generate BAT primary results.")  # Print error message
        return 1  # Return error code


if __name__ == "__main__":
    """
    Execute the main function when the script is run directly.

    Example usage:
    python src/main.py --sheet_key=1ZyVnhjCnsWN8zKS1Aov4yHnR_Hjdm1DuLDCIeWqwc48
    """
    exit(main())  # Run main function and use its return code as exit code
