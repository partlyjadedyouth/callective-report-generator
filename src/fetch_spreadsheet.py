#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Spreadsheet to CSV Converter
This script fetches data from a public Google Spreadsheet and saves it as a CSV file.
"""

# Import the requests library to make HTTP requests to Google Sheets
import requests

# Import csv module to handle CSV file operations
import csv

# Import datetime to add timestamp to the output filename
from datetime import datetime

# Import os module for file path operations
import os

# Define the Google Spreadsheet ID from the provided URL
SPREADSHEET_ID = "1ZyVnhjCnsWN8zKS1Aov4yHnR_Hjdm1DuLDCIeWqwc48"


# Define the function to fetch spreadsheet data
def fetch_google_sheet(sheet_id, sheet_name=None):
    """
    Fetches data from a public Google Spreadsheet.

    Args:
        sheet_id (str): The ID of the Google Spreadsheet
        sheet_name (str, optional): The name of the specific sheet to export.
                                   If None, exports the first sheet.

    Returns:
        list: A list of rows with the spreadsheet data
    """
    # Construct the URL for the Google Sheets export API (CSV format)
    base_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export"

    # Set up parameters for the request
    params = {
        "format": "csv",  # Request CSV format
        "id": sheet_id,  # The spreadsheet ID
    }

    # If a specific sheet name is provided, add it to the parameters
    if sheet_name:
        params["gid"] = sheet_name

    # Print status message
    print(f"Fetching data from Google Spreadsheet: {sheet_id}")

    try:
        # Make the HTTP GET request to fetch the spreadsheet data
        response = requests.get(base_url, params=params)

        # Raise an exception if the request was unsuccessful
        response.raise_for_status()

        # Decode the response content from bytes to string
        content = response.content.decode("utf-8")

        # Parse the CSV content into a list of rows
        csv_data = list(csv.reader(content.splitlines()))

        # Print success message with row count
        print(f"Successfully fetched {len(csv_data)} rows of data")

        # Return the parsed CSV data
        return csv_data

    except requests.exceptions.RequestException as e:
        # Print error message if request fails
        print(f"Error fetching spreadsheet: {e}")
        # Return an empty list if there was an error
        return []


# Define the function to save data as a CSV file
def save_to_csv(data, filename=None):
    """
    Saves the provided data to a CSV file.

    Args:
        data (list): A list of rows to save as CSV
        filename (str, optional): The name of the output file.
                                If None, generates a name with timestamp.

    Returns:
        str: The path to the saved CSV file
    """
    # Generate a default filename with timestamp if none is provided
    if not filename:
        # Get current timestamp in a format suitable for a filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create filename with the timestamp
        filename = f"google_sheet_export_{timestamp}.csv"

    try:
        # Open the file for writing
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            # Create a CSV writer object
            csv_writer = csv.writer(csvfile)

            # Write all rows to the CSV file
            csv_writer.writerows(data)

        # Print success message with file path
        print(f"CSV file saved successfully: {os.path.abspath(filename)}")

        # Return the absolute path of the saved file
        return os.path.abspath(filename)

    except Exception as e:
        # Print error message if saving fails
        print(f"Error saving CSV file: {e}")
        # Return None if there was an error
        return None


# Main execution block
def main():
    """
    Main function to execute the script.
    """
    # Fetch data from the Google Spreadsheet
    sheet_data = fetch_google_sheet(SPREADSHEET_ID)

    # Check if data was successfully fetched
    if sheet_data:
        # Save the fetched data to a CSV file
        output_file = save_to_csv(sheet_data)

        # Check if the CSV file was successfully saved
        if output_file:
            # Print final success message
            print(f"Process completed successfully. Output file: {output_file}")
        else:
            # Print error message if saving failed
            print("Failed to save data to CSV file.")
    else:
        # Print error message if fetching failed
        print("Failed to fetch data from Google Spreadsheet.")


# Execute the main function when script is run directly
if __name__ == "__main__":
    # Call the main function
    main()
