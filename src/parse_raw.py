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
from datetime import datetime  # Library for date and time handling


def parse_bat_primary_results(
    csv_path, questionnaire_path, output_dir="data/results", date_suffix=None
):
    """
    Parse questionnaire results from CSV and generate a JSON file with calculated scores for all questionnaire types.

    Args:
        csv_path (str): Path to the CSV file containing questionnaire responses
        questionnaire_path (str): Path to the JSON file containing questionnaire definitions
                                 (can be a dict with paths to each questionnaire type)
        output_dir (str): Directory to save the results JSON file
        date_suffix (str): Date suffix for the output filename. If None, today's date is used.

    Returns:
        str: Path to the generated results file, or None if an error occurred
    """
    try:
        # Use today's date if no date suffix is provided
        if date_suffix is None:  # If no date suffix is provided
            date_suffix = datetime.now().strftime(
                "%Y%m%d"
            )  # Format current date as YYYYMMDD

        # Ensure output directory exists
        os.makedirs(
            output_dir, exist_ok=True
        )  # Create output directory if it doesn't exist

        # Load CSV data
        print(f"Loading CSV data from: {csv_path}")  # Print status message
        df = pd.read_csv(
            csv_path, encoding="utf-8"
        )  # Load CSV file as pandas DataFrame

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

        # Determine columns for each questionnaire type
        current_col = 6  # Start from column 6 (after basic info columns)

        for (
            q_type,
            q_path,
        ) in questionnaire_paths.items():  # For each questionnaire type
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
            # Extract basic information
            person_data = {  # Create person data dictionary
                "name": (
                    row["성명"].strip() if pd.notna(row["성명"]) else ""
                ),  # Name (trimmed, handle NaN)
                "team": row["소속"] if pd.notna(row["소속"]) else "",  # Team
                "role": row["직무"] if pd.notna(row["직무"]) else "",  # Role
                "email": (
                    row["설문 결과 전송을 위한 이메일 주소 (오타 주의)"]
                    if pd.notna(row["설문 결과 전송을 위한 이메일 주소 (오타 주의)"])
                    else ""
                ),  # Email
                "scores": {},  # Initialize scores dictionary
            }

            # Process each questionnaire type
            for q_type, (
                start_col,
                end_col,
            ) in q_columns.items():  # For each questionnaire type
                person_data["scores"][
                    q_type
                ] = {}  # Initialize scores for this questionnaire type
                q_data = questionnaire_data[q_type]  # Get questionnaire data

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
        output_file = f"{output_dir}/questionnaire_results_{date_suffix}.json"  # Construct output file path

        # Save results to JSON file
        print(f"Saving results to: {output_file}")  # Print status message
        with open(output_file, "w", encoding="utf-8") as f:  # Open output file
            json.dump(result_list, f, ensure_ascii=False, indent=2)  # Write JSON data

        print(
            f"All questionnaire results saved to '{output_file}'"
        )  # Print success message
        return output_file  # Return output file path

    except Exception as e:  # Handle exceptions
        print(f"Error processing questionnaire results: {e}")  # Print error message
        import traceback  # Import traceback module

        traceback.print_exc()  # Print exception traceback
        return None  # Return None on error


# Run as standalone script
if __name__ == "__main__":
    # Get today's date
    today = datetime.now().strftime("%Y%m%d")  # Format current date as YYYYMMDD

    # Set default file paths
    csv_file_path = f"data/csv/google_sheet_export_{today}.csv"  # Default CSV file path

    # Set questionnaire paths
    questionnaire_paths = {  # Dictionary of questionnaire paths
        "BAT_primary": "data/questionnaires/bat_primary_questionnaires.json",
        "BAT_secondary": "data/questionnaires/bat_secondary_questionnaires.json",
        "emotional_labor": "data/questionnaires/emotional_labor_questionnaires.json",
        "stress": "data/questionnaires/stress_questionnaires.json",
    }

    # Parse results
    parse_bat_primary_results(  # Call parsing function
        csv_path=csv_file_path, questionnaire_path=questionnaire_paths
    )
