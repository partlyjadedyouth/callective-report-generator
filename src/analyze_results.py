#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Survey Results Analyzer

This script analyzes the survey results from the 'results' directory:
1. Calculates per-participant averages for BAT_primary, BAT_secondary, emotional_labor, and stress
2. Calculates per-participant type-specific averages within each category
3. Generates summary statistics for all employees and individual teams
4. Saves the analysis as a JSON file in the 'data/analysis' directory
"""

# Import required libraries
import os  # Library for operating system functionality
import json  # Library for handling JSON data
import statistics  # Library for statistical calculations
from collections import (
    defaultdict,
)  # Library to create dictionaries with default values
from pathlib import Path  # Library for handling file paths


def analyze_results(results_dir="data/results", output_dir="data/analysis"):
    """
    Analyze survey results and generate statistics for each participant.

    Args:
        results_dir (str): Directory containing the survey result files
        output_dir (str): Directory to save the analysis output

    Returns:
        str: Path to the saved analysis file or None if no results were found
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Dictionary to store all participants with their weekly analyses
    # Structure: { "name": { "name": "", "team": "", "role": "", "analysis": { "0주차": {...}, "2주차": {...} } } }
    all_participants = {}

    # Get all JSON files in the results directory
    result_files = list(Path(results_dir).glob("*.json"))

    if not result_files:
        print("No result files found in the results directory.")
        return None

    # Load questionnaire data for type-based analysis
    questionnaire_types = load_questionnaire_types()

    # Load questionnaire data to determine max scores and question counts
    questionnaire_data = load_questionnaire_data()

    # Process each result file (each week)
    for result_file in result_files:
        file_name = (
            result_file.stem
        )  # Get the filename without extension (e.g., "0주차")

        # Read the result file
        with open(result_file, "r", encoding="utf-8") as f:
            results = json.load(f)

        # Check if there are results to analyze
        if not results:
            print(f"No data found in {result_file}. Skipping.")
            continue

        # Process each participant's results for this week
        for participant in results:
            name = participant.get("name", "Unknown")
            team = participant.get("team", "Unknown")
            role = participant.get("role", "Unknown")

            # If this participant isn't in all_participants yet, add them
            if name not in all_participants:
                all_participants[name] = {
                    "name": name,
                    "team": team,
                    "role": role,
                    "analysis": {},
                }

            # Initialize analysis for this week
            weekly_analysis = {"category_averages": {}, "type_averages": {}}

            # Dictionary to store scores by category and type for this participant
            category_scores = {
                "BAT_primary": [],
                "BAT_secondary": [],
                "emotional_labor": [],
                "stress": [],
            }

            # Dictionary to store raw scores (not averages) by type for emotional_labor and stress
            type_raw_scores = {
                "emotional_labor": defaultdict(list),
                "stress": defaultdict(list),
            }

            # Dictionary for BAT categories that use traditional averaging
            type_scores = {
                "BAT_primary": defaultdict(list),
                "BAT_secondary": defaultdict(list),
            }

            # Process each category for this participant
            for category in [
                "BAT_primary",
                "BAT_secondary",
                "emotional_labor",
                "stress",
            ]:
                if category in participant.get("scores", {}):
                    # Get scores for this category
                    scores = participant["scores"][category]

                    # Add all scores to the category_scores list
                    category_scores[category].extend(scores.values())

                    # Add scores to the appropriate type_scores list
                    for question, score in scores.items():
                        if (
                            category in questionnaire_types
                            and question in questionnaire_types[category]
                        ):
                            question_type = questionnaire_types[category][question]

                            if category in ["BAT_primary", "BAT_secondary"]:
                                # Use traditional averaging for BAT categories
                                type_scores[category][question_type].append(score)
                            else:
                                # Store raw scores for emotional_labor and stress
                                type_raw_scores[category][question_type].append(score)

            # Calculate category averages for this participant
            for category, scores in category_scores.items():
                if scores:
                    if category in ["BAT_primary", "BAT_secondary"]:
                        # Use traditional averaging for BAT categories
                        weekly_analysis["category_averages"][category] = round(
                            statistics.mean(scores), 2
                        )
                    else:
                        # Use scaled formula for emotional_labor and stress
                        # 환산점수 = (해당 영역의 각문항에 주어진 점수의 합 - 문항개수) / (해당 영역의 예상 가능한 최고 총점 - 문항개수) × 100
                        question_count = len(scores)
                        if question_count > 0:
                            sum_scores = sum(scores)
                            max_possible_score = (
                                question_count * 4
                            )  # 각 문항의 최고 점수가 4라고 가정

                            if (
                                max_possible_score > question_count
                            ):  # 분모가 0이 아닌지 확인
                                scaled_score = (
                                    (sum_scores - question_count)
                                    / (max_possible_score - question_count)
                                ) * 100
                                weekly_analysis["category_averages"][category] = round(
                                    scaled_score, 2
                                )
                            else:
                                weekly_analysis["category_averages"][category] = None
                        else:
                            weekly_analysis["category_averages"][category] = None
                else:
                    weekly_analysis["category_averages"][category] = None

            # Calculate type averages for BAT categories
            for category, types_dict in type_scores.items():
                weekly_analysis["type_averages"][category] = {}
                for question_type, scores in types_dict.items():
                    if scores:
                        weekly_analysis["type_averages"][category][question_type] = (
                            round(statistics.mean(scores), 2)
                        )
                    else:
                        weekly_analysis["type_averages"][category][question_type] = None

            # Calculate type scaled scores for emotional_labor and stress
            for category, types_dict in type_raw_scores.items():
                weekly_analysis["type_averages"][category] = {}
                for question_type, scores in types_dict.items():
                    if scores:
                        question_count = len(scores)
                        sum_scores = sum(scores)
                        max_possible_score = (
                            question_count * 4
                        )  # 각 문항의 최고 점수가 4라고 가정

                        if (
                            max_possible_score > question_count
                        ):  # 분모가 0이 아닌지 확인
                            scaled_score = (
                                (sum_scores - question_count)
                                / (max_possible_score - question_count)
                            ) * 100
                            weekly_analysis["type_averages"][category][
                                question_type
                            ] = round(scaled_score, 2)
                        else:
                            weekly_analysis["type_averages"][category][
                                question_type
                            ] = None
                    else:
                        weekly_analysis["type_averages"][category][question_type] = None

            # Add this week's analysis to the participant's analysis
            all_participants[name]["analysis"][file_name] = weekly_analysis

    # Convert the dictionary of participants to a list
    participants_list = list(all_participants.values())

    # Generate team and overall analysis
    group_analysis = generate_group_analysis(all_participants)

    # Combine individual and group analysis
    final_analysis = {"participants": participants_list, "groups": group_analysis}

    # Save the analysis results to JSON file
    output_file = os.path.join(output_dir, "analysis.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_analysis, f, ensure_ascii=False, indent=2)

    print(f"Participant and group analysis completed and saved to {output_file}")
    return output_file


def generate_group_analysis(all_participants):
    """
    Generate analysis for all employees and individual teams.

    Args:
        all_participants (dict): Dictionary of all participants and their analysis

    Returns:
        dict: Dictionary containing analysis for all employees and each team
    """
    # Define the groups to analyze
    groups = {
        "회사": lambda p: True,  # All employees
        "상담 1팀": lambda p: p.get("team") == "상담 1팀",
        "상담 2팀": lambda p: p.get("team") == "상담 2팀",
        "상담 3팀": lambda p: p.get("team") == "상담 3팀",
        "상담 4팀": lambda p: p.get("team") == "상담 4팀",
    }

    group_analysis = {}

    # For each group, calculate aggregated data
    for group_name, filter_func in groups.items():
        group_analysis[group_name] = {"analysis": {}}

        # Filter participants belonging to this group
        filtered_participants = {
            name: data for name, data in all_participants.items() if filter_func(data)
        }

        if not filtered_participants:
            print(f"No participants found for group: {group_name}")
            continue

        # Get all the weeks available across all participants
        all_weeks = set()
        for participant_data in filtered_participants.values():
            all_weeks.update(participant_data["analysis"].keys())

        # For each week, calculate aggregated statistics
        for week in all_weeks:
            week_data = {"category_averages": {}, "type_averages": {}}

            # Collect all scores for this week across participants in this group
            category_scores = {
                "BAT_primary": [],
                "BAT_secondary": [],
                "emotional_labor": [],
                "stress": [],
            }

            type_scores = {
                "BAT_primary": defaultdict(list),
                "BAT_secondary": defaultdict(list),
                "emotional_labor": defaultdict(list),
                "stress": defaultdict(list),
            }

            # Collect data from all participants in this group for this week
            for participant_data in filtered_participants.values():
                if week in participant_data["analysis"]:
                    participant_week_data = participant_data["analysis"][week]

                    # Collect category averages
                    for category, value in participant_week_data[
                        "category_averages"
                    ].items():
                        if value is not None:
                            category_scores[category].append(value)

                    # Collect type averages
                    for category, type_data in participant_week_data[
                        "type_averages"
                    ].items():
                        for type_name, value in type_data.items():
                            if value is not None:
                                type_scores[category][type_name].append(value)

            # Calculate category averages for this group and week
            for category, scores in category_scores.items():
                if scores:
                    week_data["category_averages"][category] = round(
                        statistics.mean(scores), 2
                    )
                else:
                    week_data["category_averages"][category] = None

            # Calculate type averages for this group and week
            for category, types_dict in type_scores.items():
                week_data["type_averages"][category] = {}
                for type_name, scores in types_dict.items():
                    if scores:
                        week_data["type_averages"][category][type_name] = round(
                            statistics.mean(scores), 2
                        )
                    else:
                        week_data["type_averages"][category][type_name] = None

            # Add this week's analysis to the group's analysis
            group_analysis[group_name]["analysis"][week] = week_data

        # Add participant count to the group data
        group_analysis[group_name]["participant_count"] = len(filtered_participants)

    return group_analysis


def load_questionnaire_types():
    """
    Load the questionnaire type mappings from the questionnaire JSON files.

    Returns:
        dict: Dictionary mapping question IDs to their types for each category
    """
    questionnaires_dir = "data/questionnaires"
    questionnaire_files = {
        "BAT_primary": "bat_primary_questionnaires.json",
        "BAT_secondary": "bat_secondary_questionnaires.json",
        "emotional_labor": "emotional_labor_questionnaires.json",
        "stress": "stress_questionnaires.json",
    }

    type_mappings = {}

    # Load each questionnaire file
    for category, filename in questionnaire_files.items():
        filepath = os.path.join(questionnaires_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                questionnaire_data = json.load(f)

            # Create mapping of question ID to question type
            if category in questionnaire_data:
                type_mappings[category] = {}
                for question_id, question_info in questionnaire_data[category].items():
                    if "type" in question_info:
                        type_mappings[category][question_id] = question_info["type"]

    return type_mappings


def load_questionnaire_data():
    """
    Load the questionnaire data to determine max scores and question counts.

    Returns:
        dict: Dictionary containing questionnaire data
    """
    questionnaires_dir = "data/questionnaires"
    questionnaire_files = {
        "BAT_primary": "bat_primary_questionnaires.json",
        "BAT_secondary": "bat_secondary_questionnaires.json",
        "emotional_labor": "emotional_labor_questionnaires.json",
        "stress": "stress_questionnaires.json",
    }

    questionnaire_data = {}

    # Load each questionnaire file
    for category, filename in questionnaire_files.items():
        filepath = os.path.join(questionnaires_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                questionnaire_data[category] = json.load(f)

    return questionnaire_data


if __name__ == "__main__":
    """
    Execute the analysis function when the script is run directly.
    """
    analyze_results()
