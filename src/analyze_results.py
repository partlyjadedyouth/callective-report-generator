#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Survey Results Analyzer

This script analyzes the survey results from the 'results' directory:
1. Calculates per-participant averages for BAT_primary, BAT_secondary, emotional_labor, and stress
2. Calculates per-participant type-specific averages within each category
3. Generates summary statistics for all employees and individual teams
4. Saves the analysis as a JSON file in the 'data/analysis' directory
5. Generates a CSV file with risk level distribution data
"""

# Import required libraries
import os  # Library for operating system functionality
import json  # Library for handling JSON data
import statistics  # Library for statistical calculations
import csv  # Library for handling CSV files
from collections import (
    defaultdict,
)  # Library to create dictionaries with default values
from pathlib import Path  # Library for handling file paths
from cutoff_values import (
    CUTOFF_BURNOUT_PRIMARY,
    CUTOFF_STRESS,  # Import cutoff values for stress risk assessment
    CUTOFF_STRESS_MALE,  # Import male cutoff values for stress risk assessment
)  # Import cutoff values for burnout risk assessment


def load_participant_ids(csv_file="data/csv/participants.csv"):
    """
    Load participant IDs and gender information from a CSV file, using name and team as matching criteria.

    Args:
        csv_file (str): Path to the CSV file containing participant information

    Returns:
        dict: Dictionary mapping (name, team) tuples to participant information (id and gender)
    """
    # Dictionary to store participant information with name and team as keys
    participant_info = {}

    # Check if the CSV file exists
    if not os.path.exists(csv_file):
        print(
            f"Warning: Participants CSV file '{csv_file}' not found. No IDs will be added."
        )
        return participant_info

    # Read the CSV file
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Iterate through each row in the CSV
            for row in reader:
                # Extract name, team, ID, and gender
                # Note: CSV column names must match the expected values
                name = row.get("성함", "").strip()
                team = row.get("소속", "").strip()
                participant_id = row.get("아이디", "").strip()
                gender = row.get("성별", "").strip()  # Get gender information

                # Skip rows with missing data
                if not (name and team):
                    continue

                # Store participant information with name and team as key
                participant_info[(name, team)] = {
                    "id": participant_id,
                    "gender": gender,
                }

        print(f"Loaded {len(participant_info)} participant records from {csv_file}")
        return participant_info

    except Exception as e:
        print(f"Error loading participant information: {e}")
        return {}


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

    # Load participant information from CSV
    participant_info = load_participant_ids()

    # Dictionary to store all participants with their weekly analyses
    # Structure: { "unique_id": { "name": "", "team": "", "role": "", "phone": "", "email": "", "gender": "", "analysis": { "0주차": {...}, "2주차": {...} } } }
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

        # Extract week number from filename
        try:
            week_num = int(file_name.replace("주차", ""))
            is_week_2_or_later = week_num >= 2
        except ValueError:
            print(f"Warning: Could not extract week number from {file_name}")
            is_week_2_or_later = False

        # Process each participant's results for this week
        for participant in results:
            name = participant.get("name", "Unknown")  # Get participant name
            team = participant.get("team", "Unknown")  # Get participant team
            role = participant.get("role", "Unknown")  # Get participant role
            phone = participant.get("phone", "")  # Get participant phone
            email = participant.get("email", "")  # Get participant email

            # We'll use a combination of name and team as the unique identifier
            # This handles cases where multiple people have the same name
            unique_id = f"{name}_{team}"

            # 2주차 이후에는 전화번호로 이전 참가자와 일치시킵니다
            # For weeks 2+, we need special handling for participants with missing team info
            # Try to find a match based on phone number, which is usually consistent
            existing_participant_key = None

            if is_week_2_or_later and (team == "Unknown" or not team):
                # If we have a phone number, use it to match with existing participants
                if phone:
                    for key, participant_data in all_participants.items():
                        if (
                            participant_data.get("phone") == phone
                            and participant_data.get("name") == name
                        ):
                            existing_participant_key = key
                            break

                # If no match by phone, try to match by name and look at teams from participants.csv
                if not existing_participant_key:
                    # Find all previous entries with the same name
                    matching_keys = [
                        key
                        for key, data in all_participants.items()
                        if data.get("name") == name
                    ]

                    if len(matching_keys) == 1:
                        # If there's only one previous participant with this name, use that
                        existing_participant_key = matching_keys[0]
                    elif len(matching_keys) > 1:
                        # If there are multiple, try to match using participant_info
                        matched_with_csv = False
                        for (p_name, p_team), p_data in participant_info.items():
                            if p_name == name:
                                # Check if we have a participant with this name and team
                                potential_key = f"{name}_{p_team}"
                                if potential_key in all_participants:
                                    existing_participant_key = potential_key
                                    matched_with_csv = True
                                    break

                        # If still no match, use email or any other identifier if available
                        if not matched_with_csv and email:
                            for key in matching_keys:
                                if all_participants[key].get("email") == email:
                                    existing_participant_key = key
                                    break

            # If we found an existing participant, use that instead of creating a new entry
            if existing_participant_key and existing_participant_key != unique_id:
                unique_id = existing_participant_key

            # We only create a new entry if it doesn't exist already
            if unique_id not in all_participants:
                all_participants[unique_id] = {
                    "name": name,
                    "team": team,
                    "role": role,
                    "phone": phone,
                    "email": email,
                    "analysis": {},
                }

                # Add ID and gender from participants.csv if available
                matched_participant = None
                for (p_name, p_team), p_data in participant_info.items():
                    # First try exact match on both name and team
                    if p_name == name and p_team == team:
                        matched_participant = p_data
                        # Update team info
                        all_participants[unique_id]["team"] = p_team
                        break
                    # If no exact match, try matching just by name if we don't have a good team value
                    elif (
                        p_name == name
                        and (team == "Unknown" or not team)
                        and matched_participant is None
                    ):
                        matched_participant = p_data
                        # Update team from participants.csv
                        all_participants[unique_id]["team"] = p_team

                if matched_participant:
                    all_participants[unique_id]["id"] = matched_participant.get(
                        "id", ""
                    )
                    all_participants[unique_id]["gender"] = matched_participant.get(
                        "gender", ""
                    )

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
            all_participants[unique_id]["analysis"][file_name] = weekly_analysis

    # Convert the dictionary of participants to a list, ensuring the output format matches what's expected
    participants_list = []
    for participant_data in all_participants.values():
        # Create a clean version of the participant data without phone/email if not necessary for output
        output_participant = {
            "name": participant_data["name"],
            "team": participant_data["team"],
            "role": participant_data["role"],
            "id": (
                participant_data["id"]
                if "id" in participant_data and participant_data["id"]
                else None
            ),
            "gender": participant_data.get(
                "gender", ""
            ),  # Use get() with default empty string
            "analysis": participant_data["analysis"],
        }

        participants_list.append(output_participant)

    # Generate team and overall analysis
    group_analysis = generate_group_analysis(all_participants)

    # Combine individual and group analysis
    final_analysis = {"participants": participants_list, "groups": group_analysis}

    # Save the analysis results to JSON file
    output_file = os.path.join(output_dir, "analysis.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_analysis, f, ensure_ascii=False, indent=2)

    # Generate and save risk levels CSV file
    generate_risk_levels_csv(group_analysis, output_dir)

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
            participant_id: data
            for participant_id, data in all_participants.items()
            if filter_func(data)
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
            week_data = {
                "category_averages": {},
                "type_averages": {},
                "risk_levels": {},
            }

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

            # Initialize counters for BAT_primary risk levels
            bat_primary_risk_counts = {
                "정상": 0,  # Normal - BAT_primary <= CUTOFF_BURNOUT_PRIMARY[0]
                "준위험": 0,  # Caution - CUTOFF_BURNOUT_PRIMARY[0] < BAT_primary <= CUTOFF_BURNOUT_PRIMARY[1]
                "위험": 0,  # Risk - BAT_primary > CUTOFF_BURNOUT_PRIMARY[1]
            }

            # Initialize counters for stress risk levels
            stress_risk_counts = {
                "정상": 0,  # Normal - stress <= CUTOFF_STRESS[0]
                "준위험": 0,  # Caution - CUTOFF_STRESS[0] < stress <= CUTOFF_STRESS[1]
                "위험": 0,  # Risk - stress > CUTOFF_STRESS[1]
            }

            # Collect data from all participants in this group for this week
            for participant_data in filtered_participants.values():
                if week in participant_data["analysis"]:
                    participant_week_data = participant_data["analysis"][week]
                    gender = participant_data.get("gender", "")

                    # Collect category averages
                    for category, value in participant_week_data[
                        "category_averages"
                    ].items():
                        if value is not None:
                            category_scores[category].append(value)

                            # Count BAT_primary risk levels
                            if category == "BAT_primary":
                                if value <= CUTOFF_BURNOUT_PRIMARY[0]:
                                    bat_primary_risk_counts["정상"] += 1
                                elif value <= CUTOFF_BURNOUT_PRIMARY[1]:
                                    bat_primary_risk_counts["준위험"] += 1
                                else:
                                    bat_primary_risk_counts["위험"] += 1

                            # Count stress risk levels based on gender
                            elif category == "stress":
                                # Use male cutoff for male participants, female cutoff for others
                                cutoff = (
                                    CUTOFF_STRESS_MALE
                                    if gender == "남"
                                    else CUTOFF_STRESS
                                )
                                if value <= cutoff[0]:
                                    stress_risk_counts["정상"] += 1
                                elif value <= cutoff[1]:
                                    stress_risk_counts["준위험"] += 1
                                else:
                                    stress_risk_counts["위험"] += 1

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

            # Add BAT_primary risk level counts to the week data
            week_data["risk_levels"]["BAT_primary"] = bat_primary_risk_counts

            # Add stress risk level counts to the week data
            week_data["risk_levels"]["stress"] = stress_risk_counts

            # Add this week's analysis to the group's analysis
            group_analysis[group_name]["analysis"][week] = week_data

        # Add participant count to the group data
        group_analysis[group_name]["participant_count"] = len(filtered_participants)

    return group_analysis


def generate_risk_levels_csv(group_analysis, output_dir):
    """
    Generate a CSV file with risk level data for each week and group.

    Args:
        group_analysis (dict): Dictionary containing analysis for all employees and each team
        output_dir (str): Directory to save the output CSV file

    Returns:
        str: Path to the saved CSV file
    """
    # Get all weeks available across all groups
    all_weeks = set()
    for group_data in group_analysis.values():
        all_weeks.update(group_data["analysis"].keys())

    # Sort weeks to ensure consistent order
    sorted_weeks = sorted(all_weeks)

    # Group names in the desired order
    group_names = [
        "회사",
        "상담 1팀",
        "상담 2팀",
        "상담 3팀",
        "상담 4팀",
    ]

    # Define the CSV file path
    csv_file_path = os.path.join(output_dir, "risk_levels.csv")

    # Create and write to the CSV file
    with open(csv_file_path, "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write header rows
        for week in sorted_weeks:
            # Write burnout score header
            csvwriter.writerow([f"{week} 번아웃 총점"])
            row = []
            for group_name in group_names:
                if (
                    group_name in group_analysis
                    and week in group_analysis[group_name]["analysis"]
                ):
                    bat_primary_score = group_analysis[group_name]["analysis"][week][
                        "category_averages"
                    ].get("BAT_primary")
                    row.append(
                        bat_primary_score if bat_primary_score is not None else "N/A"
                    )
                else:
                    row.append("N/A")
            csvwriter.writerow(row)

            # Write stress score header
            csvwriter.writerow([f"{week} 직무스트레스 총점"])
            row = []
            for group_name in group_names:
                if (
                    group_name in group_analysis
                    and week in group_analysis[group_name]["analysis"]
                ):
                    stress_score = group_analysis[group_name]["analysis"][week][
                        "category_averages"
                    ].get("stress")
                    row.append(stress_score if stress_score is not None else "N/A")
                else:
                    row.append("N/A")
            csvwriter.writerow(row)

            # Write burnout distribution header
            csvwriter.writerow([f"{week} 번아웃 분포"])

            # Write the header for distribution labels - now grouped by team and gender
            header_row = [""]
            for group in group_names:
                header_row.extend([f"{group} 정상", f"{group} 준위험", f"{group} 위험"])
            csvwriter.writerow(header_row)

            # Write burnout distribution counts - now grouped by team and gender
            row = ["인원수"]
            for group_name in group_names:
                if (
                    group_name in group_analysis
                    and week in group_analysis[group_name]["analysis"]
                ):
                    risk_counts = group_analysis[group_name]["analysis"][week][
                        "risk_levels"
                    ].get("BAT_primary", {})
                    row.append(risk_counts.get("정상", 0))
                    row.append(risk_counts.get("준위험", 0))
                    row.append(risk_counts.get("위험", 0))
                else:
                    row.extend(["N/A", "N/A", "N/A"])
            csvwriter.writerow(row)

            # Write stress distribution header
            csvwriter.writerow([f"{week} 직무스트레스 분포"])

            # Write the header for distribution labels - now grouped by team and gender
            header_row = [""]
            for group in group_names:
                header_row.extend([f"{group} 정상", f"{group} 준위험", f"{group} 위험"])
            csvwriter.writerow(header_row)

            # Write stress distribution counts - now grouped by team and gender
            row = ["인원수"]
            for group_name in group_names:
                if (
                    group_name in group_analysis
                    and week in group_analysis[group_name]["analysis"]
                ):
                    risk_counts = group_analysis[group_name]["analysis"][week][
                        "risk_levels"
                    ].get("stress", {})
                    row.append(risk_counts.get("정상", 0))
                    row.append(risk_counts.get("준위험", 0))
                    row.append(risk_counts.get("위험", 0))
                else:
                    row.extend(["N/A", "N/A", "N/A"])
            csvwriter.writerow(row)

            # Add a blank row between weeks for better readability
            csvwriter.writerow([])

    print(f"Risk levels CSV file created at {csv_file_path}")
    return csv_file_path


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
