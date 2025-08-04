#!/usr/bin/env python3
"""
CSV datetime parser script
Transforms datetime format from "Tue Jul 22 2025 19:25:00 GMT+0000 (Coordinated Universal Time)"
to "YYYY-MM-DD HH:mm:ss" format with +9 hours timezone adjustment
"""

import pandas as pd
import os
from datetime import datetime, timedelta


def parse_datetime_format(datetime_str):
    """
    Parse datetime string from GMT format and add 9 hours
    Input format: "Tue Jul 22 2025 19:25:00 GMT+0000 (Coordinated Universal Time)"
    Output format: "YYYY-MM-DD HH:mm:ss"
    """

    try:
        # Extract the main datetime part before "GMT"
        main_part = datetime_str.split(" GMT")[0]
        # Parse the datetime: "Tue Jul 22 2025 19:25:00"
        parsed_dt = datetime.strptime(main_part, "%a %b %d %Y %H:%M:%S")
        # Add 9 hours for timezone adjustment (convert from UTC to KST)
        adjusted_dt = parsed_dt + timedelta(hours=9)
        # Return in the target format
        return adjusted_dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print(f"Error parsing datetime '{datetime_str}': {e}")
        return datetime_str  # Return original if parsing fails


# Configuration
filename = (
    "mindbattery_data_0723_0801.csv"  # Change this variable to process different files
)


def transform_csv_datetime(input_filename, output_dir="data/csv"):
    """
    Transform datetime column in CSV file and save to output directory

    Args:
        input_filename (str): Name of the input CSV file
        output_dir (str): Output directory path (default: "data/csv")
    """

    # Construct full input path - look in data/csv directory first
    input_paths = [
        os.path.join("data/csv", input_filename),
        input_filename,  # Direct path if provided
        os.path.join(os.getcwd(), input_filename),  # Current directory
    ]

    input_path = None
    for path in input_paths:
        if os.path.exists(path):
            input_path = path
            break

    if input_path is None:
        print(
            f"Error: Input file '{input_filename}' not found in any of the expected locations:"
        )
        for path in input_paths:
            print(f"  - {path}")
        return False

    try:
        # Read the CSV file
        print(f"Reading CSV file from: {input_path}")
        df = pd.read_csv(input_path)

        # Check if the datetime column exists
        if "날짜_시간" not in df.columns:
            print("Error: Column '날짜_시간' not found in the CSV file")
            print(f"Available columns: {list(df.columns)}")
            return False

        # Transform the datetime column
        print("Transforming datetime format and adding 9 hours...")
        df["날짜_시간"] = df["날짜_시간"].apply(parse_datetime_format)

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Generate output filename
        base_name = os.path.splitext(os.path.basename(input_filename))[0]
        output_filename = f"{base_name}_transformed.csv"
        output_path = os.path.join(output_dir, output_filename)

        # Save the transformed CSV
        df.to_csv(output_path, index=False)
        print(f"Transformed CSV saved to: {output_path}")

        # Display sample of transformed data
        print("\nSample of transformed data:")
        print(df[["날짜_시간"]].head())

        return True

    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return False


if __name__ == "__main__":
    # Execute the transformation with the configured filename
    success = transform_csv_datetime(filename)

    if success:
        print("\nDatetime transformation completed successfully!")
    else:
        print("\nDatetime transformation failed!")
