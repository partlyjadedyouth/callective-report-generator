#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Questionnaire Results Parser

This script parses CSV data exported from Google Sheets containing multiple questionnaire responses
and generates a structured JSON file with calculated scores based on questionnaire definitions.
"""

# Import required libraries
import pandas as pd  # Library for data manipulation and analysis
import json  # Library for JSON data handling
import os  # Library for file and directory operations

# 참가자 ID 관리 모듈 임포트
from participant_id_manager import generate_unique_id


def parse_bat_primary_results(
    csv_path, questionnaire_path, output_dir="data/results", week_suffix="0주차"
):
    """
    Parse questionnaire results from CSV and generate a JSON file with calculated scores for all questionnaire types.

    Args:
        csv_path (str): Path to the CSV file containing questionnaire responses
        questionnaire_path (str): Path to the JSON file containing questionnaire definitions
                                 (can be a dict with paths to each questionnaire type)
        output_dir (str): Directory to save the results JSON file
        week_suffix (str): Week suffix for the output filename, e.g., "0주차". Default is "0주차".

    Returns:
        str: Path to the generated results file, or None if an error occurred
    """
    try:
        # Ensure output directory exists
        os.makedirs(
            output_dir, exist_ok=True
        )  # Create output directory if it doesn't exist

        # Extract week number from week_suffix
        week_num = int(week_suffix.replace("주차", ""))  # Convert "X주차" to integer X

        # Determine if this is week 2 or later (different format)
        is_week_2_or_later = week_num >= 2  # Check if week number is 2 or greater

        # Load CSV data - explicitly specify the dtype for phone column to keep leading zeros
        print(f"Loading CSV data from: {csv_path}")  # Print status message
        df = pd.read_csv(
            csv_path, encoding="utf-8", dtype={"휴대폰 번호 뒷자리 (4자리)": str}
        )  # Load CSV file as pandas DataFrame with phone numbers as strings

        # Prepare questionnaire paths
        questionnaire_paths = {}  # Dictionary to store questionnaire paths
        if isinstance(
            questionnaire_path, dict
        ):  # If questionnaire_path is a dictionary
            questionnaire_paths = questionnaire_path  # Use it directly
        else:
            # If a single path is provided, determine type from filename
            base_path = os.path.dirname(
                questionnaire_path
            )  # Get directory of questionnaire file
            questionnaire_types = [
                "bat_primary",
                "bat_secondary",
                "emotional_labor",
                "stress",
            ]  # All questionnaire types

            # If a single path is provided, check if it's for BAT primary and load others
            if (
                "bat_primary" in questionnaire_path.lower()
            ):  # If path is for BAT primary
                questionnaire_paths["BAT_primary"] = (
                    questionnaire_path  # Set as BAT primary path
                )

                # Automatically load other questionnaire definitions based on naming convention
                for q_type in questionnaire_types:  # For each questionnaire type
                    if (
                        "bat_primary" != q_type
                    ):  # Skip BAT primary as we already have it
                        q_path = os.path.join(
                            base_path, f"{q_type}_questionnaires.json"
                        )  # Construct path
                        if os.path.exists(q_path):  # If file exists
                            type_key = q_type.replace(
                                "bat_", "BAT_"
                            )  # Convert to proper format (e.g., 'bat_primary' to 'BAT_primary')
                            questionnaire_paths[type_key] = (
                                q_path  # Add to paths dictionary
                            )
            else:
                # If path doesn't contain 'bat_primary', assume it's the only one to process
                basename = os.path.basename(questionnaire_path)  # Get filename
                q_type = next(
                    (t for t in questionnaire_types if t in basename.lower()), "unknown"
                )  # Extract type
                type_key = q_type.replace("bat_", "BAT_")  # Convert to proper format
                questionnaire_paths[type_key] = (
                    questionnaire_path  # Add to paths dictionary
                )

        # Load all questionnaire definitions
        questionnaire_data = {}  # Dictionary to store questionnaire data
        q_columns = {}  # Dictionary to store column indices for each questionnaire

        # Determine if stress and emotional labor questionnaires should be included
        include_stress_emotional = (
            week_num % 4 == 0
        )  # Only include these every 4 weeks (0, 4, 8, 12, etc.)

        # Determine columns for each questionnaire type
        # Starting column is different based on week (week 2+ has fewer initial columns)
        current_col = (
            3 if is_week_2_or_later else 6
        )  # Start from column 3 for week 2+ (missing team, role, email)

        for (
            q_type,
            q_path,
        ) in questionnaire_paths.items():  # For each questionnaire type
            # Skip stress and emotional labor questionnaires if not relevant for this week
            if not include_stress_emotional and q_type in ["emotional_labor", "stress"]:
                continue  # Skip this questionnaire type

            print(
                f"Loading {q_type} questionnaire from: {q_path}"
            )  # Print status message

            # Load questionnaire definition
            with open(q_path, "r", encoding="utf-8") as f:  # Open questionnaire file
                q_data = json.load(f)  # Load JSON data

                # Get actual questionnaire key (e.g., 'BAT-primary' instead of 'BAT_primary')
                q_key = next(iter(q_data.keys()))  # Get first key in JSON data
                questionnaire_data[q_type] = q_data[q_key]  # Store questionnaire data

                # Calculate column range for this questionnaire
                num_questions = len(q_data[q_key])  # Get number of questions
                q_columns[q_type] = (
                    current_col,
                    current_col + num_questions - 1,
                )  # Store column range
                current_col += num_questions  # Update current column index

        # Process each row (respondent)
        result_list = []  # List to store results
        print(f"Processing {len(df)} responses...")  # Print status message

        for _, row in df.iterrows():  # For each row (respondent)
            # Process phone number to ensure it's properly formatted with 4 digits
            phone_number = ""  # Initialize phone number variable
            if pd.notna(
                row["휴대폰 번호 뒷자리 (4자리)"]
            ):  # If phone number is not NaN
                # Get phone number as string and ensure it's exactly 4 digits with leading zeros if needed
                phone_raw = str(
                    row["휴대폰 번호 뒷자리 (4자리)"]
                ).strip()  # Get raw phone number and strip whitespace
                phone_number = phone_raw.zfill(
                    4
                )  # Pad with leading zeros if needed to make 4 digits

            # 이름과 소속 정보 추출 (공백 제거)
            name = row["성명"].strip() if pd.notna(row["성명"]) else ""

            # 팀 정보는 2주차 이후에는 없을 수 있음
            team = ""
            if not is_week_2_or_later and pd.notna(row["소속"]):
                team = row["소속"].strip()

            # Extract basic information
            person_data = {  # Create person data dictionary
                "name": name,  # 이름
                "phone": phone_number,  # 전화번호
                "scores": {},  # Initialize scores dictionary
            }

            # Only include team, role, and email fields for week 0-1
            if not is_week_2_or_later:
                person_data.update(
                    {
                        "team": team,  # 팀
                        "role": (
                            row["직무"].strip() if pd.notna(row["직무"]) else ""
                        ),  # 직무
                        "email": (
                            row["설문 결과 전송을 위한 이메일 주소 (오타 주의)"].strip()
                            if pd.notna(
                                row["설문 결과 전송을 위한 이메일 주소 (오타 주의)"]
                            )
                            else ""
                        ),  # 이메일
                    }
                )

            # Process each questionnaire type
            for q_type, (
                start_col,
                end_col,
            ) in q_columns.items():  # For each questionnaire type
                person_data["scores"][
                    q_type
                ] = {}  # Initialize scores for this questionnaire type
                q_data = questionnaire_data[q_type]  # Get questionnaire data

                # Check if we have enough columns in the CSV
                if end_col >= len(
                    df.columns
                ):  # If column index exceeds available columns
                    print(
                        f"Warning: Column index {end_col} exceeds CSV columns ({len(df.columns)}). "
                        f"Skipping {q_type} questionnaire."
                    )
                    continue  # Skip this questionnaire type

                # Get columns for this questionnaire type
                q_cols = df.columns[start_col : end_col + 1]  # Get column names

                # Calculate scores for each question
                for i, col in enumerate(q_cols):  # For each question column
                    q_num = i + 1  # Calculate question number
                    q_key = f"Q{q_num}"  # Construct question key (e.g., "Q1")

                    # Get score mapping for this question
                    if q_key in q_data:  # If question exists in definition
                        score_mapping = q_data[q_key]["scores"]  # Get score mapping

                        # Get response and calculate score
                        response = row[col]  # Get response value

                        # Handle missing responses
                        if pd.isna(response):  # If response is NaN
                            score = 0  # Set score to 0
                        else:
                            # Convert response to string if needed and find corresponding score
                            response_str = str(response)  # Convert to string
                            score = score_mapping.get(
                                response_str, 0
                            )  # Get score (default to 0 if not found)

                        # Store score
                        person_data["scores"][q_type][
                            q_key
                        ] = score  # Store score in person data

            # Add person data to result list
            result_list.append(person_data)  # Add to results list

        # Generate output file path
        output_file = f"{output_dir}/{week_suffix}.json"  # Construct output file path with week suffix

        # Save results to JSON file
        print(f"Saving results to: {output_file}")  # Print status message
        with open(output_file, "w", encoding="utf-8") as f:  # Open output file
            json.dump(result_list, f, ensure_ascii=False, indent=2)  # Write JSON data

        print(
            f"Successfully processed {len(result_list)} responses."
        )  # Print status message
        return output_file  # Return path to the generated file

    except Exception as e:
        print(f"Error parsing questionnaire results: {e}")  # Print error message
        return None  # Return None to indicate an error occurred


# Run as standalone script
if __name__ == "__main__":
    # Set up command-line argument parsing
    import argparse  # Library for parsing command-line arguments

    parser = argparse.ArgumentParser(
        description="Parse questionnaire results from a CSV file"
    )  # Create argument parser
    parser.add_argument(
        "--csv_path",
        type=str,
        required=True,
        help="Path to the CSV file containing questionnaire responses",
    )  # Add CSV path argument
    parser.add_argument(
        "--week",
        type=int,
        default=0,
        help="Week number to use in file names (e.g., 0 for '0주차')",
    )  # Add week number argument

    # Parse the command-line arguments
    args = parser.parse_args()  # Parse arguments

    # Create week suffix
    week_suffix = f"{args.week}주차"  # Format week number as "0주차", "1주차", etc.

    # Set questionnaire paths
    questionnaire_paths = {  # Dictionary of questionnaire paths
        "BAT_primary": "data/questionnaires/bat_primary_questionnaires.json",
        "BAT_secondary": "data/questionnaires/bat_secondary_questionnaires.json",
        "emotional_labor": "data/questionnaires/emotional_labor_questionnaires.json",
        "stress": "data/questionnaires/stress_questionnaires.json",
    }

    # Parse results
    result_file = parse_bat_primary_results(  # Call parsing function
        csv_path=args.csv_path,
        questionnaire_path=questionnaire_paths,
        output_dir="data/results",
        week_suffix=week_suffix,
    )

    # Check if results were successfully generated
    if result_file:  # If results were generated
        print(
            f"Process completed successfully. Results saved to {result_file}"
        )  # Print success message
        exit(0)  # Exit with success code
    else:
        print("Failed to generate questionnaire results.")  # Print error message
        exit(1)  # Exit with error code
