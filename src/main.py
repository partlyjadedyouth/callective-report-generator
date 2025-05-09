#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Report Generator Main Script

This script coordinates the process of:
1. Fetching data from a Google Spreadsheet using its key
2. Saving the data as a CSV file
3. Parsing the data to generate questionnaire results for multiple questionnaire types
4. Analyzing the survey results and generating per-participant statistics across weeks
5. Fetching app usage data from another Google Spreadsheet and saving it as a CSV
6. Analyzing app usage data and generating app_analysis.json
7. Generating personal reports for all participants
8. Generating team figures for visualization
"""

# Import required libraries
import argparse  # Library for parsing command-line arguments
import os  # Library for operating system functionality
import subprocess  # Library for running external processes
import json  # Library for handling JSON data

# Import custom modules
from fetch_spreadsheet import (
    fetch_google_sheet,
    save_to_csv,
)  # Import functions for fetching and saving spreadsheet data
from parse_raw import (
    parse_bat_primary_results,
)  # Import function for parsing questionnaire results
from analyze_results import analyze_results  # Import function for analyzing results
from analyze_app_usage import (
    analyze_app_usage,
)  # Import function for analyzing app usage data
from generate_team_figures import (
    generate_bat_primary_distribution_graph,
    generate_exhaustion_distribution_graph,
    generate_cognitive_regulation_distribution_graph,
    generate_emotional_regulation_distribution_graph,
    generate_depersonalization_distribution_graph,
    generate_stress_distribution_graph,
)  # Import functions for generating team figures


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
        "--app_usage_sheet_key",
        type=str,
        required=False,  # Add optional argument for app usage spreadsheet key
        help="Google Spreadsheet key/ID for app usage data",
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

    # Step 3: Fetch app usage data if specified
    app_usage_saved_path = None  # Initialize app usage saved path
    if args.app_usage_sheet_key:  # If app usage spreadsheet key is provided
        # Define the app usage CSV output path
        app_usage_csv_path = os.path.join(
            csv_dir, f"app_usage_data_{week_suffix}.csv"
        )  # Construct path for app usage CSV output file

        print(
            f"Fetching app usage data from Google Spreadsheet: {args.app_usage_sheet_key}"
        )  # Print status message
        app_usage_data = fetch_google_sheet(
            args.app_usage_sheet_key, sheet_name
        )  # Fetch app usage spreadsheet data

        # Check if app usage data was successfully fetched
        if not app_usage_data:  # If no app usage data was fetched
            print(
                "Failed to fetch app usage data from Google Spreadsheet. Continuing without app usage data."
            )  # Print warning message
        else:
            # Save the fetched app usage data to a CSV file
            print(
                f"Saving app usage data to CSV: {app_usage_csv_path}"
            )  # Print status message
            app_usage_saved_path = save_to_csv(
                app_usage_data, app_usage_csv_path
            )  # Save app usage data to CSV file

            # Check if app usage CSV was successfully saved
            if not app_usage_saved_path:  # If saving failed
                print(
                    "Failed to save app usage data to CSV file. Continuing without app usage data."
                )  # Print warning message
            else:
                print(
                    f"App usage data saved successfully to {app_usage_saved_path}"
                )  # Print success message

    # Step 4: Prepare questionnaire paths dictionary
    questionnaire_paths = {  # Create dictionary of questionnaire paths
        "BAT_primary": bat_primary_path,  # BAT primary path
        "BAT_secondary": bat_secondary_path,  # BAT secondary path
        "emotional_labor": emotional_labor_path,  # Emotional labor path
        "stress": stress_path,  # Stress path
    }

    # Step 5: Parse the CSV data to generate questionnaire results
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

    # Step 6: Analyze the survey results for each participant
    print(
        "Analyzing survey results for each participant across all weeks..."
    )  # Print status message
    analysis_file = analyze_results(  # Analyze the survey results
        results_dir=results_dir, output_dir=analysis_dir
    )

    # Check if analysis was successfully generated
    if not analysis_file:  # If analysis failed
        print("Failed to analyze survey results.")  # Print error message
        return 1  # Return error code

    print(
        f"Participant analysis results saved to {analysis_file}"
    )  # Print success message

    # Step 7: Analyze app usage data if available
    app_analysis_file = None  # Initialize app analysis file path
    if app_usage_saved_path:  # If app usage data was saved
        print("Analyzing app usage data...")  # Print status message
        app_analysis_file = analyze_app_usage(  # Analyze app usage data
            csv_dir=csv_dir, output_dir=analysis_dir
        )

        # Check if app usage analysis was successfully generated
        if not app_analysis_file:  # If app usage analysis failed
            print(
                "Failed to analyze app usage data. Continuing without app usage analysis."
            )  # Print warning message
        else:
            print(
                f"App usage analysis results saved to {app_analysis_file}"
            )  # Print success message

    # Print success message for the whole process
    success_message = f"Process completed successfully. Results saved to {result_file} and participant analysis to {analysis_file}"
    if app_analysis_file:  # If app usage analysis was generated
        success_message += f", app usage analysis to {app_analysis_file}"
    print(success_message)  # Print success message

    # Step 8: Generate personal reports
    print("Generating personal reports...")  # Print status message
    try:
        # Define the path to the personal report generator script
        personal_report_script = (
            "src/personal_report_generator.py"  # Path to the script
        )
        # Execute the personal report generator script
        subprocess.run(
            ["python3", personal_report_script], check=True
        )  # Run the script using python3 and check for errors
        print(f"Successfully generated personal reports.")  # Print success message

        # Step 9: Generate team figures
        print("Generating team figures...")  # Print status message

        # Load analysis data to determine teams
        with open(analysis_file, "r", encoding="utf-8") as f:  # Open analysis file
            analysis_data = json.load(f)  # Load JSON data

        # Extract all unique team numbers
        team_numbers = set()  # Initialize empty set for team numbers
        for participant in analysis_data[
            "participants"
        ]:  # Iterate through each participant
            team_name = participant["team"]  # Get team name
            if team_name.startswith("상담 ") and team_name.endswith(
                "팀"
            ):  # Check if team name has expected format
                try:
                    # Extract team number from the team name (e.g., "상담 1팀" -> 1)
                    team_number = int(team_name[3:-1])  # Extract and convert to integer
                    team_numbers.add(team_number)  # Add to set of team numbers
                except (
                    ValueError
                ):  # Handle case where team number isn't a valid integer
                    pass  # Skip this team

        # Generate figures for all teams
        for team_number in sorted(
            team_numbers
        ):  # Iterate through team numbers in order
            try:
                print(
                    f"Generating figures for team {team_number}..."
                )  # Print progress message
                # Generate BAT primary distribution graph
                generate_bat_primary_distribution_graph(
                    args.week, team_number
                )  # Generate BAT primary figures for this team
                # Generate exhaustion distribution graph
                generate_exhaustion_distribution_graph(
                    args.week, team_number
                )  # Generate exhaustion figures for this team
                # Generate cognitive regulation distribution graph
                generate_cognitive_regulation_distribution_graph(
                    args.week, team_number
                )  # Generate cognitive regulation figures for this team
                # Generate emotional regulation distribution graph
                generate_emotional_regulation_distribution_graph(
                    args.week, team_number
                )  # Generate emotional regulation figures for this team
                # Generate depersonalization distribution graph
                generate_depersonalization_distribution_graph(
                    args.week, team_number
                )  # Generate depersonalization figures for this team
                # Generate stress distribution graph
                generate_stress_distribution_graph(
                    args.week, team_number
                )  # Generate stress figures for this team
            except Exception as e:  # Catch any errors that occur
                print(
                    f"Error generating figures for team {team_number}: {e}"
                )  # Print error message

        print("Successfully generated team figures.")  # Print success message
        return 0  # Return success code
    except subprocess.CalledProcessError as e:  # Catch errors during script execution
        print(f"Failed to generate personal reports: {e}")  # Print error message
        return 1  # Return error code
    except FileNotFoundError:  # Catch error if script not found
        print(
            f"Error: The script {personal_report_script} was not found."
        )  # Print file not found error
        return 1  # Return error code


if __name__ == "__main__":
    """
    Execute the main function when the script is run directly.

    Example usage:
    python src/main.py --sheet_key=asdf --week=0 --app_usage_sheet_key=qwerty
    """
    exit(main())  # Run main function and use its return code as exit code
