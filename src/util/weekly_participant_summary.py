#!/usr/bin/env python3
"""
Weekly Participant Summary Script

This script reads participant data from analysis.json and participants.csv files,
then organizes and prints weekly BAT_secondary data including psychological complaints,
physical complaints, and total scores for each participant.

Column format:
ParticipantID (P1, P2, ...)	Week	Physical	Emotional	Total
"""

import json  # For reading JSON data files
import csv  # For reading CSV data files
import os  # For file path operations
import sys  # For stderr output
from typing import Dict, List, Optional  # For type hints and better code documentation


def load_participants_mapping() -> Dict[str, str]:
    """
    Load participant ID mappings from participants.csv file.

    Returns:
        Dict[str, str]: Dictionary mapping participant ID to their P-number identifier
    """
    # Define the path to the participants CSV file relative to the script location
    participants_file = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "csv", "participants.csv"
    )

    # Initialize empty dictionary to store ID mappings
    id_mapping = {}

    try:
        # Open and read the CSV file
        with open(participants_file, "r", encoding="utf-8") as file:
            # Create CSV reader object
            csv_reader = csv.DictReader(file)
            # Iterate through each row in the CSV
            for row in csv_reader:
                # Map the participant ID to their P-number identifier
                id_mapping[row["아이디"]] = row["식별 기호"]
    except FileNotFoundError:
        # Handle case where participants.csv file is not found
        print(f"Error: Could not find participants file at {participants_file}")
        return {}
    except Exception as e:
        # Handle any other errors during file reading
        print(f"Error reading participants file: {e}")
        return {}

    return id_mapping


def load_analysis_data() -> Dict:
    """
    Load analysis data from analysis.json file.

    Returns:
        Dict: Dictionary containing all participant analysis data
    """
    # Define the path to the analysis JSON file relative to the script location
    analysis_file = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "analysis", "analysis.json"
    )

    try:
        # Open and read the JSON file
        with open(analysis_file, "r", encoding="utf-8") as file:
            # Parse JSON data and return it
            return json.load(file)
    except FileNotFoundError:
        # Handle case where analysis.json file is not found
        print(f"Error: Could not find analysis file at {analysis_file}")
        return {}
    except json.JSONDecodeError as e:
        # Handle case where JSON file is malformed
        print(f"Error parsing JSON file: {e}")
        return {}
    except Exception as e:
        # Handle any other errors during file reading
        print(f"Error reading analysis file: {e}")
        return {}


def extract_weekly_data(analysis_data: Dict, id_mapping: Dict[str, str]) -> List[Dict]:
    """
    Extract weekly BAT_secondary data for all participants.

    Args:
        analysis_data (Dict): Complete analysis data from JSON file
        id_mapping (Dict[str, str]): Mapping from participant ID to P-number

    Returns:
        List[Dict]: List of dictionaries containing participant weekly data
    """
    # Initialize list to store all participant weekly data
    weekly_data = []

    # Check if participants data exists in the analysis file
    if "participants" not in analysis_data:
        print("Error: No participants data found in analysis file")
        return weekly_data

    # Iterate through each participant in the analysis data
    for participant in analysis_data["participants"]:
        # Get participant ID from the data
        participant_id = participant.get("id", "")
        # Get corresponding P-number from mapping, or use original ID if not found
        p_number = id_mapping.get(participant_id, participant_id)

        # Get analysis data for this participant
        participant_analysis = participant.get("analysis", {})

        # Iterate through each week's data for this participant
        for week, week_data in participant_analysis.items():
            # Get BAT_secondary type averages for this week
            bat_secondary = week_data.get("type_averages", {}).get("BAT_secondary", {})

            # Extract psychological and physical complaint scores
            emotional_score = bat_secondary.get(
                "심리적 호소"
            )  # Psychological complaints
            physical_score = bat_secondary.get("신체적 호소")  # Physical complaints

            total = week_data.get("category_averages", {}).get("BAT_secondary", 0)

            # Only process data if both scores are available (not None)
            if emotional_score is not None and physical_score is not None:
                # Calculate total score as sum of emotional and physical scores
                # Create data record for this participant-week combination
                weekly_record = {
                    "ParticipantID": p_number,  # P-number identifier (P1, P2, etc.)
                    "Week": f"T{int(int(week[0])/2 + 1)}",  # Week identifier (0주차, 2주차, etc.)
                    "Physical": physical_score,  # Physical complaint score
                    "Emotional": emotional_score,  # Emotional/psychological complaint score
                    "Total": total,  # Combined total score
                }

                # Add this record to the weekly data list
                weekly_data.append(weekly_record)

    return weekly_data


def sort_data(weekly_data: List[Dict]) -> List[Dict]:
    """
    Sort weekly data by ParticipantID and then by Week.

    Args:
        weekly_data (List[Dict]): Unsorted weekly data

    Returns:
        List[Dict]: Sorted weekly data
    """
    # Define week order for proper sorting (Korean week labels)
    week_order = {"T1": 0, "T2": 1, "T3": 2, "T4": 3}

    # Sort data first by ParticipantID, then by week order
    return sorted(
        weekly_data,
        key=lambda x: (
            # Extract numeric part from P-number for proper numeric sorting (P1, P2, ..., P10, P11, etc.)
            (
                int(x["ParticipantID"][1:])
                if x["ParticipantID"].startswith("P")
                and x["ParticipantID"][1:].isdigit()
                else 999
            ),
            # Sort by week using the defined order
            week_order.get(x["Week"], 999),
        ),
    )


def print_summary(weekly_data: List[Dict]) -> None:
    """
    Print CSV formatted summary of weekly participant data.

    Args:
        weekly_data (List[Dict]): Sorted weekly data to print
    """
    # Print CSV header row with column names
    print("ParticipantID,Week,Physical,Emotional,Total")

    # Print each data record in CSV format
    for record in weekly_data:
        print(
            f"{record['ParticipantID']},{record['Week']},{record['Physical']:.2f},{record['Emotional']:.2f},{record['Total']:.2f}"
        )


def main():
    """
    Main function that orchestrates the data processing and printing.
    """
    # Load participant ID mappings from CSV file
    id_mapping = load_participants_mapping()
    if not id_mapping:
        print("Failed to load participant mappings. Exiting.", file=sys.stderr)
        return

    # Load analysis data from JSON file
    analysis_data = load_analysis_data()
    if not analysis_data:
        print("Failed to load analysis data. Exiting.", file=sys.stderr)
        return

    # Extract weekly BAT_secondary data for all participants
    weekly_data = extract_weekly_data(analysis_data, id_mapping)

    if not weekly_data:
        print("No weekly data found. Exiting.", file=sys.stderr)
        return

    # Sort the data by participant ID and week
    sorted_data = sort_data(weekly_data)

    # Print the CSV formatted summary
    print_summary(sorted_data)


if __name__ == "__main__":
    # Execute main function when script is run directly
    main()
