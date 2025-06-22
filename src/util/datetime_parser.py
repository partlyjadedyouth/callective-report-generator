import pandas as pd  # Import pandas library for data manipulation and CSV handling
from datetime import datetime  # Import datetime module for date and time operations


def convert_datetime_format():
    """
    Function to read CSV file and convert datetime column to YYYY-MM-DD HH:mm:ss format
    """
    # Define the path to the CSV file that contains the data to be processed
    csv_file_path = "data/csv/mindbattery_data_2025-06-21.csv"

    # Read the CSV file into a pandas DataFrame for data manipulation
    print(
        "Reading CSV file..."
    )  # Print status message to inform user about current operation
    df = pd.read_csv(csv_file_path)  # Load CSV data into DataFrame

    # Display basic information about the loaded DataFrame
    print(f"Loaded {len(df)} rows of data")  # Print number of rows loaded
    print(
        f"Columns in the dataset: {list(df.columns)}"
    )  # Print all column names for verification

    # Check if the '날짜_시간' column exists in the DataFrame
    if "날짜_시간" not in df.columns:  # Verify that the target column exists
        print(
            "Error: '날짜_시간' column not found in the dataset"
        )  # Print error message if column missing
        return None  # Exit function early if column doesn't exist

    # Display the original format of the datetime column (first 5 entries)
    print(
        "\nOriginal datetime format (first 5 entries):"
    )  # Print header for original format display
    print(df["날짜_시간"].head())  # Show first 5 entries of the datetime column

    # Convert the '날짜_시간' column to pandas datetime format with UTC timezone
    print(
        "\nConverting datetime format..."
    )  # Print status message for conversion process

    # First, clean the datetime strings by removing the timezone description part
    # Remove the " (Coordinated Universal Time)" part from the datetime strings
    df["날짜_시간"] = df["날짜_시간"].str.replace(
        r" \(Coordinated Universal Time\)", "", regex=True
    )  # Remove timezone description using regex substitution

    # Now convert the cleaned datetime strings to pandas datetime objects
    df["날짜_시간"] = pd.to_datetime(
        df["날짜_시간"], utc=True
    )  # Parse strings to datetime objects with UTC timezone

    # Remove the UTC timezone information to get naive datetime objects
    df["날짜_시간"] = df["날짜_시간"].dt.tz_convert(
        None
    )  # Convert to local time and remove timezone info

    # Add 9 hours to convert UTC time to Korean Standard Time (KST = UTC+9)
    print(
        "Adding 9 hours to convert UTC to Korean Standard Time..."
    )  # Print status message for timezone conversion
    df["날짜_시간"] = df["날짜_시간"] + pd.Timedelta(
        hours=9
    )  # Add 9 hours using pandas Timedelta

    # Display the datetime after adding 9 hours (first 5 entries)
    print(
        "\nDatetime after adding 9 hours (first 5 entries):"
    )  # Print header for timezone-adjusted display
    print(df["날짜_시간"].head())  # Show first 5 entries after adding 9 hours

    # Format the datetime objects to the desired string format: YYYY-MM-DD HH:mm:ss
    df["날짜_시간"] = df["날짜_시간"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )  # Convert to desired string format

    # Display the converted format of the datetime column (first 5 entries)
    print(
        "\nConverted datetime format (first 5 entries):"
    )  # Print header for converted format display
    print(
        df["날짜_시간"].head()
    )  # Show first 5 entries of the converted datetime column

    # Create output filename with timestamp to avoid overwriting existing files
    output_filename = (
        "data/csv/mindbattery_data_converted.csv"  # Define output file path
    )

    # Save the DataFrame with converted datetime format back to a new CSV file
    print(
        f"\nSaving converted data to {output_filename}..."
    )  # Print status message for save operation
    df.to_csv(output_filename, index=False)  # Save DataFrame to CSV without row indices

    # Print completion message with summary information
    print(
        f"Successfully converted and saved {len(df)} rows of data"
    )  # Confirm successful completion
    print(
        f"Datetime column '날짜_시간' converted to YYYY-MM-DD HH:mm:ss format with +9 hours (KST)"
    )  # Confirm format conversion and timezone adjustment

    # Return the processed DataFrame for further use if needed
    return df  # Return the processed DataFrame


# Main execution block - runs only when script is executed directly
if __name__ == "__main__":  # Check if script is run directly (not imported)
    print("Starting datetime conversion process...")  # Print initial status message

    # Execute the datetime conversion function
    result_df = (
        convert_datetime_format()
    )  # Call the conversion function and store result

    # Check if conversion was successful and print final status
    if result_df is not None:  # Verify that conversion completed successfully
        print("\nDatetime conversion completed successfully!")  # Print success message
    else:  # Handle case where conversion failed
        print(
            "\nDatetime conversion failed. Please check the error messages above."
        )  # Print failure message
