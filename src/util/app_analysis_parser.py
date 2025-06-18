#!/usr/bin/env python3
"""
Generate multi-week records CSV by matching app analysis data with participants data.
This script processes multiple app analysis JSON files and participants CSV to create
a summary of user activity records across multiple weeks.
"""

import json  # Import JSON library for reading JSON files
import pandas as pd  # Import pandas for CSV operations and data manipulation
import sys  # Import sys for command line arguments
import os  # Import os for file path operations
from collections import (
    defaultdict,
)  # Import defaultdict for counting records efficiently


def load_app_analysis_data(json_file_path):
    """
    Load app analysis data from JSON file.

    Args:
        json_file_path (str): Path to the JSON file containing app analysis data

    Returns:
        dict: Loaded JSON data containing emotion records and daily statistics, or None if file doesn't exist
    """
    if not os.path.exists(json_file_path):  # Check if file exists
        print(f"Warning: File not found: {json_file_path}")  # Print warning message
        return None  # Return None if file doesn't exist

    with open(
        json_file_path, "r", encoding="utf-8"
    ) as file:  # Open JSON file with UTF-8 encoding for Korean text
        return json.load(file)  # Load and return JSON data


def load_participants_data(csv_file_path):
    """
    Load participants data from CSV file.

    Args:
        csv_file_path (str): Path to the CSV file containing participant information

    Returns:
        pd.DataFrame: DataFrame containing participant information
    """
    return pd.read_csv(csv_file_path)  # Load CSV file using pandas


def count_user_records(emotion_records):
    """
    Count the number of emotion/factor records for each user.

    Args:
        emotion_records (list): List of emotion record dictionaries

    Returns:
        dict: Dictionary mapping user_id to their record count
    """
    user_record_counts = defaultdict(
        int
    )  # Initialize defaultdict to count records per user

    for record in emotion_records:  # Iterate through each emotion record
        user_id = record["user_id"]  # Extract user_id from the record
        user_record_counts[user_id] += 1  # Increment the count for this user

    return dict(user_record_counts)  # Convert defaultdict to regular dict and return


def load_multi_week_data(project_root, week_list):
    """
    Load app analysis data for multiple weeks.

    Args:
        project_root (str): Path to the project root directory
        week_list (list): List of week strings (e.g., ["0주차", "2주차", "4주차"])

    Returns:
        dict: Dictionary mapping week_number to user_record_counts
    """
    multi_week_data = {}  # Initialize dictionary to store data for all weeks

    for week in week_list:  # Iterate through each week in the list
        print(f"Processing {week}...")  # Print status message

        # Construct the file path for this week's data
        app_analysis_file = os.path.join(
            project_root, "data", "analysis", f"app_analysis_{week}.json"
        )  # Path to app analysis JSON for this week

        # Load data for this week
        app_data = load_app_analysis_data(
            app_analysis_file
        )  # Load app analysis JSON data

        if app_data is not None:  # Check if data was successfully loaded
            # Count user records for this week
            user_record_counts = count_user_records(
                app_data["emotion_records"]
            )  # Count records per user for this week
            multi_week_data[week] = user_record_counts  # Store data for this week
            print(
                f"  - Found {len(user_record_counts)} users with records"
            )  # Print user count
        else:
            multi_week_data[week] = {}  # Store empty dict if no data found
            print(f"  - No data found for {week}")  # Print warning message

    return multi_week_data  # Return all weeks data


def create_multi_week_output(participants_df, multi_week_data, week_list):
    """
    Create output data with columns for each week.

    Args:
        participants_df (pd.DataFrame): DataFrame containing participant information
        multi_week_data (dict): Dictionary mapping week to user_record_counts
        week_list (list): List of week strings in desired order

    Returns:
        list: List of dictionaries containing matched data for CSV output
    """
    output_data = []  # Initialize list to store output data

    for (
        _,
        participant,
    ) in participants_df.iterrows():  # Iterate through each participant row
        user_id = participant["아이디"]  # Extract user ID from participant data
        name = participant["성함"]  # Extract name from participant data
        identifier = participant[
            "식별 기호"
        ]  # Extract identifier code from participant data

        # Create base output record with participant information
        output_record = {
            "이름": name,  # Name column
            "식별기호": identifier,  # Identifier column
            "ID": user_id,  # ID column
        }

        # Add record counts for each week as separate columns
        for week in week_list:  # Iterate through each week in order
            # Get record count for this user and week, default to 0 if no records found
            week_data = multi_week_data.get(week, {})  # Get data for this week
            record_count = week_data.get(user_id, 0)  # Get count for this user
            output_record[week] = record_count  # Add week column with record count

        output_data.append(output_record)  # Add record to output data list

    return output_data  # Return completed output data


def generate_multi_week_records_csv(
    project_root, participants_file, output_file, week_list
):
    """
    Main function to generate multi-week records CSV file.

    Args:
        project_root (str): Path to the project root directory
        participants_file (str): Path to participants CSV file
        output_file (str): Path for output CSV file
        week_list (list): List of week strings to analyze
    """
    print(
        f"Analyzing weeks: {', '.join(week_list)}"
    )  # Print list of weeks being analyzed

    print(
        f"Loading participants data from {participants_file}..."
    )  # Print status message
    participants_df = load_participants_data(
        participants_file
    )  # Load participants CSV data

    print("Loading multi-week app analysis data...")  # Print status message
    multi_week_data = load_multi_week_data(
        project_root, week_list
    )  # Load data for all weeks

    print("Creating multi-week output data...")  # Print status message
    output_data = create_multi_week_output(
        participants_df, multi_week_data, week_list
    )  # Create output data structure

    print(f"Creating output CSV file: {output_file}")  # Print status message
    output_df = pd.DataFrame(output_data)  # Convert output data to DataFrame
    output_df.to_csv(
        output_file, index=False, encoding="utf-8-sig"
    )  # Save to CSV with UTF-8-sig encoding for Excel compatibility

    print(f"Successfully generated {output_file}")  # Print success message
    print(f"Total participants: {len(output_data)}")  # Print total participant count

    # Print summary statistics for each week
    for week in week_list:  # Iterate through each week
        participants_with_records = sum(
            1 for record in output_data if record[week] > 0
        )  # Count participants with records for this week
        total_records = sum(
            record[week] for record in output_data
        )  # Sum total records for this week
        print(
            f"  {week}: {participants_with_records} participants, {total_records} total records"
        )  # Print week summary


if __name__ == "__main__":
    # Define file paths relative to the script location
    script_dir = os.path.dirname(
        os.path.abspath(__file__)
    )  # Get directory where script is located (src/util)
    project_root = os.path.dirname(
        os.path.dirname(script_dir)
    )  # Get project root directory (grandparent of util, parent of src)

    # Define list of weeks to analyze - modify this list as needed
    week_list = ["0주차", "2주차", "4주차"]  # List of weeks to analyze

    # Define input and output file paths
    participants_file = os.path.join(
        project_root, "data", "csv", "participants.csv"
    )  # Path to participants CSV

    # Create output filename based on analyzed weeks
    week_suffix = "_".join(week_list)  # Join weeks with underscore
    output_file = os.path.join(
        project_root, "data", "csv", f"app_weekly_records_{week_suffix}.csv"
    )  # Path for output CSV with weeks in filename

    # Check if participants file exists
    if not os.path.exists(participants_file):  # Check if participants file exists
        print(
            f"Error: Participants file not found: {participants_file}"
        )  # Print error message
        sys.exit(1)  # Exit with error code

    # Generate the multi-week CSV file
    generate_multi_week_records_csv(
        project_root, participants_file, output_file, week_list
    )  # Call main function
