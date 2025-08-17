#!/usr/bin/env python3
"""
Detailed Emotion Analysis Script

This script analyzes app usage data to count individual emotion types for each participant
across all weeks from app_usage_data*.csv files, with separate columns for each emotion.
"""

import csv
import sys
import glob
import os
import unicodedata
from typing import Dict, Any, List
from collections import defaultdict


def load_participants_mapping(csv_path: str) -> Dict[str, str]:
    """Load participant mapping from CSV file and create a mapping from user_id to 식별 기호.
    
    For handling duplicate names (동명이인), prioritize user_id as the primary key.
    This ensures participants like P10 and P29 with the same name are distinguished correctly.
    """
    mapping = {}
    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row["성함"]
            user_id = row["아이디"]
            identifier = row["식별 기호"]
            # For handling duplicate names (동명이인), use user_id as the primary key
            mapping[user_id] = identifier
            # Create a combined key for exact matching (name_userid) - most reliable method  
            mapping[f"{name}_{user_id}"] = identifier
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


def get_emotion_mappings() -> Dict[str, str]:
    """Define mapping from Korean emotions to English column names."""
    emotion_mapping = {
        # Positive emotions
        "신나요": "P_Excited",
        "행복해요": "P_Happy", 
        "만족스러워요": "P_Satisfied",
        "차분해요": "P_Calm",
        # Negative emotions
        "우울해요": "N_Depressed",
        "슬퍼요": "N_Sad",
        "불안해요": "N_Anxious",
        "화가나요": "N_Angry",
    }
    return emotion_mapping


def load_app_usage_csv_files(data_dir: str) -> Dict[str, Dict[str, Dict[str, int]]]:
    """Load all app_usage_data CSV files and count individual emotions per user per week."""
    csv_files = glob.glob(os.path.join(data_dir, "app_usage_data_*.csv"))
    emotion_mapping = get_emotion_mappings()
    
    # Initialize with all emotion types
    def create_emotion_dict():
        return {col: 0 for col in emotion_mapping.values()}
    
    user_emotions = defaultdict(lambda: defaultdict(create_emotion_dict))

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

                    # Map Korean emotion to English column name and count
                    if emotion in emotion_mapping:
                        english_emotion = emotion_mapping[emotion]
                        user_emotions[user_id][time_symbol][english_emotion] += 1

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
    user_emotions: Dict[str, Dict[str, Dict[str, int]]], participant_mapping: Dict[str, str]
):
    """Print the data in CSV format."""
    # Define all possible time symbols in order
    all_time_symbols = ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]
    
    # Define emotion columns in the specified order
    emotion_columns = [
        "P_Excited", "P_Happy", "P_Satisfied", "P_Calm",
        "N_Depressed", "N_Sad", "N_Anxious", "N_Angry"
    ]

    # Print header
    headers = ["Participant", "Week"] + emotion_columns
    print(",".join(headers))

    # Create a mapping from participant ID to emotion counts
    participant_emotions = {}

    # Initialize all participants with zero emotions for all weeks
    for user_id, participant_id in participant_mapping.items():
        formatted_id = format_participant_id(participant_id)
        participant_emotions[formatted_id] = defaultdict(
            lambda: {col: 0 for col in emotion_columns}
        )

    # Map user emotions to participants (merging with initialized zeros)
    for user_id, emotions_by_week in user_emotions.items():
        if user_id in participant_mapping:
            participant_id = format_participant_id(participant_mapping[user_id])
            # Update the existing defaultdict instead of overriding it
            for week, emotion_counts in emotions_by_week.items():
                participant_emotions[participant_id][week] = emotion_counts
        else:
            # Critical error: user not found in mapping - this could indicate duplicate name handling issues
            print(f"Error: User '{user_id}' not found in participant mapping", file=sys.stderr)
            print(f"Error: This may indicate duplicate name handling issues (동명이인)", file=sys.stderr)
            print(f"Error: Verify that participant mapping includes user_id '{user_id}'", file=sys.stderr)

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
            emotion_counts = emotions.get(time_symbol, {col: 0 for col in emotion_columns})
            
            row = [participant_id, time_symbol]
            
            # Add counts for each emotion column
            for emotion_col in emotion_columns:
                count = emotion_counts.get(emotion_col, 0)
                row.append(str(count))

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