#!/usr/bin/env python3
"""
User Record Summary Script

This script counts the number of emotion records for each user across all weeks
from app_analysis*.json files and maps them to participant IDs.
"""

import json
import sys
import csv
import glob
import os
from typing import Dict, Any
from collections import defaultdict


def load_participants_mapping(csv_path: str) -> Dict[str, str]:
    """Load participant mapping from CSV file and create a mapping from user_id to 식별 기호."""
    mapping = {}
    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            user_id = row["아이디"]
            identifier = row["식별 기호"]
            mapping[user_id] = identifier
    return mapping


def week_to_time_symbol(week_str: str) -> str:
    """Convert week string to time symbol (T1, T2, T3, T4, T5, T6, T7)."""
    week_mapping = {
        "0주차": "T1",  # Week 0
        "2주차": "T2",  # Week 2
        "4주차": "T3",  # Week 4
        "6주차": "T4",  # Week 6
        "8주차": "T5",  # Week 8
        "10주차": "T6",  # Week 10
        "12주차": "T7",  # Week 12
    }
    return week_mapping.get(week_str, week_str)


def extract_week_from_filename(filename: str) -> str:
    """Extract week information from filename (e.g., app_analysis_0주차.json -> 0주차)."""
    basename = os.path.basename(filename)
    # Extract the week part from app_analysis_Xn주차.json
    if "app_analysis_" in basename and ".json" in basename:
        week_part = basename.replace("app_analysis_", "").replace(".json", "")
        return week_part
    return ""


def load_app_analysis_files(data_dir: str) -> Dict[str, Dict[str, int]]:
    """Load all app_analysis files and count records per user per week."""
    app_files = glob.glob(os.path.join(data_dir, "app_analysis_*.json"))
    user_records = defaultdict(lambda: defaultdict(int))

    for file_path in app_files:
        week_str = extract_week_from_filename(file_path)
        if not week_str:
            continue

        time_symbol = week_to_time_symbol(week_str)

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            emotion_records = data.get("emotion_records", [])

            # Count records per user for this week
            for record in emotion_records:
                user_id = record.get("user_id", "")
                if user_id:
                    user_records[user_id][time_symbol] += 1

        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not load {file_path}: {e}", file=sys.stderr)
            continue

    return user_records


def format_participant_id(participant_id: str) -> str:
    """Format participant ID to ensure 2-digit number (e.g., P01, P02, P10, P11)."""
    if participant_id.startswith("P"):
        # Extract the number part
        number_part = participant_id[1:]
        try:
            # Convert to integer and format as 2-digit
            num = int(number_part)
            return f"P{num:02d}"
        except ValueError:
            # If conversion fails, return original
            return participant_id
    return participant_id


def print_csv_format(
    user_records: Dict[str, Dict[str, int]], participant_mapping: Dict[str, str]
):
    """Print the data in CSV format."""
    # Define all possible time symbols in order
    all_time_symbols = ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]

    # Print header
    headers = ["Participant"] + all_time_symbols
    print(",".join(headers))

    # Create a mapping from participant ID to record counts
    participant_records = {}

    # Initialize all participants with zero records
    for user_id, participant_id in participant_mapping.items():
        formatted_id = format_participant_id(participant_id)
        participant_records[formatted_id] = defaultdict(int)

    # Map user records to participants (overriding zeros where data exists)
    for user_id, records in user_records.items():
        if user_id in participant_mapping:
            participant_id = format_participant_id(participant_mapping[user_id])
            participant_records[participant_id] = records
        else:
            # If user not found in mapping, skip or use user_id as fallback
            print(
                f"Warning: User {user_id} not found in participant mapping",
                file=sys.stderr,
            )

    # Sort participants by numeric part of ID
    def sort_key(participant_id):
        if participant_id.startswith("P"):
            try:
                return int(participant_id[1:])
            except ValueError:
                return 999
        return 999

    sorted_participants = sorted(participant_records.keys(), key=sort_key)

    # Print data rows
    for participant_id in sorted_participants:
        records = participant_records[participant_id]
        row = [participant_id]

        for time_symbol in all_time_symbols:
            count = records.get(time_symbol, 0)
            row.append(str(count))

        print(",".join(row))


def main():
    """Main function to process the app analysis data and output CSV."""
    data_dir = "data/analysis"
    participants_file = "data/csv/participants.csv"

    try:
        # Load participant mapping
        participant_mapping = load_participants_mapping(participants_file)

        # Load and process app analysis files
        user_records = load_app_analysis_files(data_dir)

        # Print results in CSV format
        print_csv_format(user_records, participant_mapping)

    except FileNotFoundError as e:
        print(f"Error: Could not find required file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
