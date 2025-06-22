#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
App Usage Data Analyzer

This script analyzes app usage data from CSV files:
1. Counts unique app users per day (identified by ID)
2. Counts emotion records per day
3. Only includes data from users whose IDs exist in participants.csv
4. Processes factors ("선택한 요인") into lists when separated by semicolons
5. Counts positive and negative emotions and their associated factors
6. Analyzes emotions by day and time ranges
7. Saves analysis results to a JSON file in the data/analysis directory
"""

# Import required libraries
import os  # Library for operating system functionality
import csv  # Library for handling CSV files
import json  # Library for handling JSON data
from collections import defaultdict  # Library for dictionaries with default values
from datetime import datetime, time  # Library for date and time handling


def load_valid_ids(csv_file="data/csv/participants.csv"):
    """
    Load participant IDs from a CSV file to determine which user data to include in analysis.

    Args:
        csv_file (str): Path to the CSV file containing participant information

    Returns:
        set: Set of valid participant IDs
    """
    # Set to store valid participant IDs
    valid_ids = set()

    # Check if the CSV file exists
    if not os.path.exists(csv_file):
        print(f"Warning: Participants CSV file '{csv_file}' not found.")
        return valid_ids

    # Read the CSV file
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Iterate through each row in the CSV
            for row in reader:
                # Extract ID
                participant_id = row.get("아이디", "").strip()

                # Skip rows with missing IDs
                if not participant_id:
                    continue

                # Store participant ID
                valid_ids.add(participant_id)

        print(f"Loaded {len(valid_ids)} valid participant IDs from {csv_file}")
        return valid_ids

    except Exception as e:
        print(f"Error loading participant IDs: {e}")
        return set()


def get_time_range(dt):
    """
    Determine which time range a datetime falls into.

    Args:
        dt (datetime): The datetime object

    Returns:
        str: The time range label
    """
    # Extract the time component
    t = dt.time()

    # Define time ranges
    if time(0, 0) <= t < time(8, 0):
        return "00:00-08:00"
    elif time(8, 0) <= t < time(10, 30):
        return "08:00-10:30"
    elif time(10, 30) <= t < time(12, 0):
        return "10:30-12:00"
    elif time(12, 0) <= t < time(13, 30):
        return "12:00-13:30"
    elif time(13, 30) <= t < time(15, 0):
        return "13:30-15:00"
    elif time(15, 0) <= t < time(16, 30):
        return "15:00-16:30"
    elif time(16, 30) <= t < time(19, 0):
        return "16:30-19:00"
    else:  # time(19, 0) <= t <= time(23, 59)
        return "19:00-24:00"


def analyze_app_usage(week=0, csv_dir="data/csv", output_dir="data/analysis"):
    """
    Analyze app usage data for the specified week.

    Args:
        week (int): Week number (e.g., 0 for "0주차")
        csv_dir (str): Directory containing the app usage CSV file
        output_dir (str): Directory to save the analysis output

    Returns:
        str: Path to the saved analysis file or None if no data was found
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Define week suffix for file names
    week_suffix = f"{week}주차"

    # Define the app usage data file path
    app_usage_file = os.path.join(csv_dir, f"app_usage_data_{week_suffix}.csv")

    # Check if the app usage file exists
    if not os.path.exists(app_usage_file):
        print(f"App usage data file '{app_usage_file}' not found.")
        return None

    # Load valid participant IDs
    valid_ids = load_valid_ids()

    if not valid_ids:
        print("No valid participant IDs found. Analysis will be empty.")

    # Define positive and negative emotion categories
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

    # Initialize dictionaries to store analysis results
    daily_users = defaultdict(set)  # Dictionary to store unique users per day
    daily_emotion_records = defaultdict(
        int
    )  # Dictionary to store emotion record counts per day
    daily_factors_list = defaultdict(list)  # Dictionary to store factor lists per day
    factor_counts = defaultdict(int)  # Dictionary to count occurrences of each factor
    emotion_records_with_factors = []  # List to store all emotion records with factors

    # Initialize emotion category counters
    positive_emotion_count = 0  # Counter for positive emotions
    negative_emotion_count = 0  # Counter for negative emotions
    positive_factors = defaultdict(
        int
    )  # Dictionary to count factors in positive emotions
    negative_factors = defaultdict(
        int
    )  # Dictionary to count factors in negative emotions

    # Initialize daily emotion category counters
    daily_emotion_categories = defaultdict(lambda: {"positive": 0, "negative": 0})

    # Initialize time range emotion category counters
    time_range_emotion_categories = {
        "00:00-08:00": {"positive": 0, "negative": 0},
        "08:00-10:30": {"positive": 0, "negative": 0},
        "10:30-12:00": {"positive": 0, "negative": 0},
        "12:00-13:30": {"positive": 0, "negative": 0},
        "13:30-15:00": {"positive": 0, "negative": 0},
        "15:00-16:30": {"positive": 0, "negative": 0},
        "16:30-19:00": {"positive": 0, "negative": 0},
        "19:00-24:00": {"positive": 0, "negative": 0},
    }

    # Initialize detailed emotion categories per time range
    time_range_detailed_emotions = {
        "00:00-08:00": {
            "positive": {"count": 0, "factors": defaultdict(int)},
            "negative": {"count": 0, "factors": defaultdict(int)},
        },
        "08:00-10:30": {
            "positive": {"count": 0, "factors": defaultdict(int)},
            "negative": {"count": 0, "factors": defaultdict(int)},
        },
        "10:30-12:00": {
            "positive": {"count": 0, "factors": defaultdict(int)},
            "negative": {"count": 0, "factors": defaultdict(int)},
        },
        "12:00-13:30": {
            "positive": {"count": 0, "factors": defaultdict(int)},
            "negative": {"count": 0, "factors": defaultdict(int)},
        },
        "13:30-15:00": {
            "positive": {"count": 0, "factors": defaultdict(int)},
            "negative": {"count": 0, "factors": defaultdict(int)},
        },
        "15:00-16:30": {
            "positive": {"count": 0, "factors": defaultdict(int)},
            "negative": {"count": 0, "factors": defaultdict(int)},
        },
        "16:30-19:00": {
            "positive": {"count": 0, "factors": defaultdict(int)},
            "negative": {"count": 0, "factors": defaultdict(int)},
        },
        "19:00-24:00": {
            "positive": {"count": 0, "factors": defaultdict(int)},
            "negative": {"count": 0, "factors": defaultdict(int)},
        },
    }

    # Initialize day of week emotion categories
    day_of_week_emotion_categories = {
        "Monday": {
            "positive": {"count": 0, "factors": defaultdict(int)},
            "negative": {"count": 0, "factors": defaultdict(int)},
        },
        "Tuesday": {
            "positive": {"count": 0, "factors": defaultdict(int)},
            "negative": {"count": 0, "factors": defaultdict(int)},
        },
        "Wednesday": {
            "positive": {"count": 0, "factors": defaultdict(int)},
            "negative": {"count": 0, "factors": defaultdict(int)},
        },
        "Thursday": {
            "positive": {"count": 0, "factors": defaultdict(int)},
            "negative": {"count": 0, "factors": defaultdict(int)},
        },
        "Friday": {
            "positive": {"count": 0, "factors": defaultdict(int)},
            "negative": {"count": 0, "factors": defaultdict(int)},
        },
        "Saturday": {
            "positive": {"count": 0, "factors": defaultdict(int)},
            "negative": {"count": 0, "factors": defaultdict(int)},
        },
        "Sunday": {
            "positive": {"count": 0, "factors": defaultdict(int)},
            "negative": {"count": 0, "factors": defaultdict(int)},
        },
    }

    # Korean day of week names mapping
    korean_day_names = {
        "Monday": "월요일",
        "Tuesday": "화요일",
        "Wednesday": "수요일",
        "Thursday": "목요일",
        "Friday": "금요일",
        "Saturday": "토요일",
        "Sunday": "일요일",
    }

    # Read the app usage data file
    try:
        with open(app_usage_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Iterate through each row in the CSV
            for row in reader:
                # Extract ID, date, and factors
                user_id = row.get("ID", "").strip()
                date_str = row.get("날짜_시간", "").strip()
                factors_str = row.get("선택한_요인", "").strip()
                emotion = row.get("선택한_감정", "").strip()

                # Skip rows with missing IDs or dates or if the ID is not in the valid IDs list
                if not user_id or not date_str or user_id not in valid_ids:
                    continue

                try:
                    # Parse the date string to extract just the date part
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    date = date_obj.strftime("%Y-%m-%d")

                    # Get day of week
                    day_of_week = date_obj.strftime(
                        "%A"
                    )  # Returns full name: Monday, Tuesday, etc.

                    # Get time range for this record
                    time_range = get_time_range(date_obj)

                    # Add user to daily users
                    daily_users[date].add(user_id)

                    # Increment emotion record count for the day
                    daily_emotion_records[date] += 1

                    # Process factors - split by semicolon if present
                    factors = []
                    if factors_str:
                        # Split factors by semicolon and strip whitespace
                        factors = [factor.strip() for factor in factors_str.split(";")]

                        # Store factors as a list
                        record = {
                            "date": date,
                            "user_id": user_id,
                            "emotion": emotion,
                            "factors": factors,
                        }
                        emotion_records_with_factors.append(record)

                        # Add factors to daily factors list
                        daily_factors_list[date].append(factors)

                        # Count occurrences of each factor
                        for factor in factors:
                            factor_counts[factor] += 1

                            # Count factors by emotion category
                            if emotion in positive_emotions:
                                positive_factors[factor] += 1
                            elif emotion in negative_emotions:
                                negative_factors[factor] += 1

                    # Count emotions by category
                    if emotion in positive_emotions:
                        positive_emotion_count += 1
                        daily_emotion_categories[date]["positive"] += 1

                        # Only count in time range categories if it's not weekend (Saturday or Sunday)
                        if day_of_week not in ["Saturday", "Sunday"]:
                            time_range_emotion_categories[time_range]["positive"] += 1
                            time_range_detailed_emotions[time_range]["positive"][
                                "count"
                            ] += 1

                            # Count factors for this time range (only on weekdays)
                            for factor in factors:
                                time_range_detailed_emotions[time_range]["positive"][
                                    "factors"
                                ][factor] += 1

                        day_of_week_emotion_categories[day_of_week]["positive"][
                            "count"
                        ] += 1

                        # Count factors for day of week (includes all days)
                        for factor in factors:
                            day_of_week_emotion_categories[day_of_week]["positive"][
                                "factors"
                            ][factor] += 1

                    elif emotion in negative_emotions:
                        negative_emotion_count += 1
                        daily_emotion_categories[date]["negative"] += 1

                        # Only count in time range categories if it's not weekend (Saturday or Sunday)
                        if day_of_week not in ["Saturday", "Sunday"]:
                            time_range_emotion_categories[time_range]["negative"] += 1
                            time_range_detailed_emotions[time_range]["negative"][
                                "count"
                            ] += 1

                            # Count factors for this time range (only on weekdays)
                            for factor in factors:
                                time_range_detailed_emotions[time_range]["negative"][
                                    "factors"
                                ][factor] += 1

                        day_of_week_emotion_categories[day_of_week]["negative"][
                            "count"
                        ] += 1

                        # Count factors for day of week (includes all days)
                        for factor in factors:
                            day_of_week_emotion_categories[day_of_week]["negative"][
                                "factors"
                            ][factor] += 1

                except (ValueError, TypeError):
                    # Skip rows with invalid date format
                    continue

        # Convert daily users from sets to counts
        daily_user_counts = {date: len(users) for date, users in daily_users.items()}

        # Sort factor counts by frequency (descending)
        sorted_factor_counts = dict(
            sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)
        )
        sorted_positive_factors = dict(
            sorted(positive_factors.items(), key=lambda x: x[1], reverse=True)
        )
        sorted_negative_factors = dict(
            sorted(negative_factors.items(), key=lambda x: x[1], reverse=True)
        )

        # Convert defaultdicts to regular dicts and sort factors by frequency
        for time_range in time_range_detailed_emotions:
            for category in ["positive", "negative"]:
                # Convert defaultdict to regular dict and sort
                factors_dict = dict(
                    time_range_detailed_emotions[time_range][category]["factors"]
                )
                time_range_detailed_emotions[time_range][category]["factors"] = dict(
                    sorted(factors_dict.items(), key=lambda x: x[1], reverse=True)
                )
                # Add emotions list
                time_range_detailed_emotions[time_range][category]["emotions"] = (
                    positive_emotions if category == "positive" else negative_emotions
                )

        # Convert day of week defaultdicts to regular dicts and sort factors by frequency
        day_of_week_emotion_categories_korean = {}
        for day in day_of_week_emotion_categories:
            korean_day = korean_day_names[day]
            day_of_week_emotion_categories_korean[korean_day] = {}

            for category in ["positive", "negative"]:
                day_of_week_emotion_categories_korean[korean_day][category] = {
                    "count": day_of_week_emotion_categories[day][category]["count"],
                    "emotions": (
                        positive_emotions
                        if category == "positive"
                        else negative_emotions
                    ),
                    "factors": dict(
                        sorted(
                            dict(
                                day_of_week_emotion_categories[day][category]["factors"]
                            ).items(),
                            key=lambda x: x[1],
                            reverse=True,
                        )
                    ),
                }

        # Prepare analysis results
        analysis_results = {
            "daily_user_counts": daily_user_counts,
            "daily_emotion_records": daily_emotion_records,
            "factor_counts": sorted_factor_counts,
            "emotion_records": emotion_records_with_factors,
            "total_users": len(
                set().union(*daily_users.values()) if daily_users else set()
            ),
            "total_emotion_records": sum(daily_emotion_records.values()),
            "total_factors": sum(factor_counts.values()),
            "emotion_categories": {
                "positive": {
                    "count": positive_emotion_count,
                    "emotions": positive_emotions,
                    "factors": sorted_positive_factors,
                },
                "negative": {
                    "count": negative_emotion_count,
                    "emotions": negative_emotions,
                    "factors": sorted_negative_factors,
                },
            },
            "daily_emotion_categories": dict(daily_emotion_categories),
            "time_range_emotion_categories": time_range_emotion_categories,
            "time_range_detailed_emotions": dict(time_range_detailed_emotions),
            "day_of_week_emotion_categories": day_of_week_emotion_categories_korean,
        }

        # Save the analysis results to a JSON file
        output_file = os.path.join(output_dir, f"app_analysis_{week_suffix}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)

        print(
            f"App usage analysis for week {week} completed and saved to {output_file}"
        )
        print(f"Total unique users: {analysis_results['total_users']}")
        print(f"Total emotion records: {analysis_results['total_emotion_records']}")
        print(f"Total factors: {analysis_results['total_factors']}")
        print(f"Positive emotions: {positive_emotion_count}")
        print(f"Negative emotions: {negative_emotion_count}")

        return output_file

    except Exception as e:
        print(f"Error analyzing app usage data: {e}")
        return None


if __name__ == "__main__":
    """
    Execute the analysis function when the script is run directly.

    Example usage:
    python src/analyze_app_usage.py
    """
    analyze_app_usage(6)  # Analyze data for week 6 by default
