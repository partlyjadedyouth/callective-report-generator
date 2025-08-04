#!/usr/bin/env python3
"""
Emotion Analysis Script

This script analyzes app usage data to count positive and negative emotions
recorded by each participant across all weeks from app_usage_data*.csv files.
"""

import csv
import sys
import glob
import os
import unicodedata
from typing import Dict, Any, Set
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
    # Normalize Unicode to handle different encodings of Korean characters
    normalized_week = unicodedata.normalize("NFC", week_str)

    week_mapping = {
        "0주차": "T1",  # Week 0
        "2주차": "T2",  # Week 2
        "4주차": "T3",  # Week 4
        "6주차": "T4",  # Week 6
        "8주차": "T5",  # Week 8
        "10주차": "T6",  # Week 10
        "12주차": "T7",  # Week 12
    }
    return week_mapping.get(normalized_week, normalized_week)


def extract_week_from_filename(filename: str) -> str:
    """Extract week information from filename (e.g., app_usage_data_0주차.csv -> 0주차)."""
    basename = os.path.basename(filename)
    # Extract the week part from app_usage_data_Xn주차.csv
    if "app_usage_data_" in basename and ".csv" in basename:
        week_part = basename.replace("app_usage_data_", "").replace(".csv", "")
        return week_part
    return ""


def categorize_emotions() -> tuple[Set[str], Set[str]]:
    """Define positive and negative emotion categories."""
    positive_emotions = [
        "신나요",
        "행복해요",
        "만족스러워요",
        "차분해요",
    ]  # List of positive emotions
    negative_emotions = [
        "우울해요",
        "슬퍼요",
        "불안해요",
        "화가나요",
    ]  # List of negative emotions

    return positive_emotions, negative_emotions


def load_app_usage_csv_files(data_dir: str) -> Dict[str, Dict[str, Dict[str, int]]]:
    """Load all app_usage_data CSV files and count emotions per user per week."""
    csv_files = glob.glob(os.path.join(data_dir, "app_usage_data_*.csv"))
    user_emotions = defaultdict(
        lambda: defaultdict(lambda: {"positive": 0, "negative": 0})
    )

    positive_emotions, negative_emotions = categorize_emotions()

    for file_path in csv_files:
        week_str = extract_week_from_filename(file_path)
        if not week_str:
            continue

        time_symbol = week_to_time_symbol(week_str)

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    user_id = row.get("ID", "")
                    if not user_id:
                        continue

                    # Get the selected emotion from both possible columns
                    emotion = (
                        row.get("선택한 감정") or row.get("선택한_감정") or ""
                    ).strip()
                    if not emotion or emotion == "NULL":
                        continue

                    # Categorize and count the emotion
                    if emotion in positive_emotions:
                        user_emotions[user_id][time_symbol]["positive"] += 1
                    elif emotion in negative_emotions:
                        user_emotions[user_id][time_symbol]["negative"] += 1
                    # Ignore emotions that don't fit either category

        except (FileNotFoundError, UnicodeDecodeError) as e:
            print(f"Warning: Could not load {file_path}: {e}", file=sys.stderr)
            continue

    return user_emotions


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
    user_emotions: Dict[str, Dict[str, Dict[str, int]]],
    participant_mapping: Dict[str, str],
):
    """Print the data in CSV format."""
    # Define all possible time symbols in order
    all_time_symbols = ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]

    # Print header
    headers = ["Participant", "Week", "Positive", "Negative"]
    print(",".join(headers))

    # Create a mapping from participant ID to emotion counts
    participant_emotions = {}

    # Initialize all participants with zero emotions for all weeks
    for user_id, participant_id in participant_mapping.items():
        formatted_id = format_participant_id(participant_id)
        participant_emotions[formatted_id] = defaultdict(
            lambda: {"positive": 0, "negative": 0}
        )

    # Map user emotions to participants (merging with initialized zeros)
    for user_id, emotions_by_week in user_emotions.items():
        if user_id in participant_mapping:
            participant_id = format_participant_id(participant_mapping[user_id])
            # Update the existing defaultdict instead of overriding it
            for week, emotion_counts in emotions_by_week.items():
                participant_emotions[participant_id][week] = emotion_counts
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

    sorted_participants = sorted(participant_emotions.keys(), key=sort_key)

    # Print data rows for each participant and week combination
    for participant_id in sorted_participants:
        emotions = participant_emotions[participant_id]

        for time_symbol in all_time_symbols:
            emotion_counts = emotions.get(time_symbol, {"positive": 0, "negative": 0})
            positive_count = emotion_counts["positive"]
            negative_count = emotion_counts["negative"]

            row = [
                participant_id,
                time_symbol,
                str(positive_count),
                str(negative_count),
            ]
            print(",".join(row))


def main():
    """Main function to process the app usage data and output CSV."""
    data_dir = "data/csv"
    participants_file = "data/csv/participants.csv"

    try:
        # Load participant mapping
        participant_mapping = load_participants_mapping(participants_file)

        # Load and process app usage CSV files
        user_emotions = load_app_usage_csv_files(data_dir)

        # Print results in CSV format
        print_csv_format(user_emotions, participant_mapping)

    except FileNotFoundError as e:
        print(f"Error: Could not find required file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
