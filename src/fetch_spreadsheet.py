#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Spreadsheet to CSV Converter
This script fetches data from a public Google Spreadsheet and saves it as a CSV file.
"""

# Import the requests library to make HTTP requests to Google Sheets
import requests  # HTTP 요청을 보내기 위한 requests 라이브러리

# Import csv module to handle CSV file operations
import csv  # CSV 파일 작업을 위한 모듈

# Import datetime to add timestamp to the output filename
from datetime import datetime  # 파일 이름에 타임스탬프를 추가하기 위한 datetime 모듈

# Import os module for file path operations
import os  # 파일 경로 작업을 위한 os 모듈


# Define the function to fetch spreadsheet data
def fetch_google_sheet(sheet_id, sheet_name=None):
    """
    Fetches data from a public Google Spreadsheet.

    Args:
        sheet_id (str): The ID of the Google Spreadsheet
        sheet_name (str, optional): The name or gid of the specific sheet to export.
                                   If None, exports the first sheet.

    Returns:
        list: A list of rows with the spreadsheet data, or empty list if error occurs
    """
    # Construct the URL for the Google Sheets export API (CSV format)
    base_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export"  # Google Sheets API 엑스포트 URL 구성

    # Set up parameters for the request
    params = {
        "format": "csv",  # CSV 형식으로 요청
        "id": sheet_id,  # 스프레드시트 ID
    }

    # If a specific sheet name is provided, add it to the parameters
    if sheet_name:
        params["gid"] = sheet_name  # 특정 시트 이름이 제공된 경우 파라미터에 추가

    # Print status message
    print(f"Fetching data from Google Spreadsheet: {sheet_id}")  # 상태 메시지 출력

    try:
        # Make the HTTP GET request to fetch the spreadsheet data
        response = requests.get(base_url, params=params)  # HTTP GET 요청 보내기

        # Raise an exception if the request was unsuccessful
        response.raise_for_status()  # 요청이 실패한 경우 예외 발생

        # Decode the response content from bytes to string
        content = response.content.decode("utf-8")  # 응답 내용을 UTF-8로 디코딩

        # Parse the CSV content into a list of rows
        csv_data = list(csv.reader(content.splitlines()))  # CSV 내용을 행 목록으로 파싱

        # Print success message with row count
        print(f"Successfully fetched {len(csv_data)} rows of data")  # 성공 메시지 출력

        # Return the parsed CSV data
        return csv_data  # 파싱된 CSV 데이터 반환

    except requests.exceptions.RequestException as e:
        # Print error message if request fails
        print(f"Error fetching spreadsheet: {e}")  # 요청 실패 시 오류 메시지 출력
        # Return an empty list if there was an error
        return []  # 오류 발생 시 빈 목록 반환


# Define the function to save data as a CSV file
def save_to_csv(data, filename=None):
    """
    Saves the provided data to a CSV file.

    Args:
        data (list): A list of rows to save as CSV
        filename (str, optional): The name of the output file.
                                If None, generates a name with timestamp.

    Returns:
        str: The path to the saved CSV file, or None if an error occurred
    """
    try:
        # Generate a default filename with timestamp if none is provided
        if not filename:
            # Ensure the csv directory exists
            os.makedirs("data/csv", exist_ok=True)  # CSV 디렉토리가 없는 경우 생성

            # Get current timestamp in a format suitable for a filename
            timestamp = datetime.now().strftime(
                "%Y%m%d"
            )  # 파일 이름에 적합한 타임스탬프 형식 생성

            # Create filename with the timestamp
            filename = f"data/csv/google_sheet_export_{timestamp}.csv"  # 타임스탬프가 포함된 파일 이름 생성

        # Ensure the target directory exists
        os.makedirs(
            os.path.dirname(filename), exist_ok=True
        )  # 대상 디렉토리가 없는 경우 생성

        # Open the file for writing
        with open(
            filename, "w", newline="", encoding="utf-8"
        ) as csvfile:  # 파일 쓰기 모드로 열기
            # Create a CSV writer object
            csv_writer = csv.writer(csvfile)  # CSV 작성자 객체 생성

            # Write all rows to the CSV file
            csv_writer.writerows(data)  # 모든 행을 CSV 파일에 쓰기

        # Print success message with file path
        print(
            f"CSV file saved successfully: {os.path.abspath(filename)}"
        )  # 성공 메시지 출력

        # Return the absolute path of the saved file
        return os.path.abspath(filename)  # 저장된 파일의 절대 경로 반환

    except Exception as e:
        # Print error message if saving fails
        print(f"Error saving CSV file: {e}")  # 저장 실패 시 오류 메시지 출력
        # Return None if there was an error
        return None  # 오류 발생 시 None 반환


# Main execution block
def main():
    """
    Main function to execute the script when run directly.

    This is for command-line usage and can be run as:
    python fetch_spreadsheet.py SPREADSHEET_ID [SHEET_NAME]
    """
    import argparse  # 명령줄 인수 파싱을 위한 argparse 모듈 가져오기

    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Fetch data from a Google Spreadsheet"
    )  # 인수 파서 생성
    parser.add_argument(
        "sheet_id", type=str, help="Google Spreadsheet ID/key"
    )  # 스프레드시트 ID 인수 추가
    parser.add_argument(
        "--sheet_name",
        type=str,
        default=None,
        help="Specific sheet name/gid (optional)",
    )  # 시트 이름 인수 추가
    parser.add_argument(
        "--output", type=str, default=None, help="Output CSV file path (optional)"
    )  # 출력 파일 경로 인수 추가

    # Parse the command-line arguments
    args = parser.parse_args()  # 명령줄 인수 파싱

    # Fetch data from the Google Spreadsheet
    sheet_data = fetch_google_sheet(
        args.sheet_id, args.sheet_name
    )  # 구글 스프레드시트에서 데이터 가져오기

    # Check if data was successfully fetched
    if sheet_data:
        # Save the fetched data to a CSV file
        output_file = save_to_csv(
            sheet_data, args.output
        )  # 가져온 데이터를 CSV 파일로 저장

        # Check if the CSV file was successfully saved
        if output_file:
            # Print final success message
            print(
                f"Process completed successfully. Output file: {output_file}"
            )  # 최종 성공 메시지 출력
            return 0  # 성공 시 0 반환
        else:
            # Print error message if saving failed
            print("Failed to save data to CSV file.")  # 저장 실패 시 오류 메시지 출력
            return 1  # 실패 시 1 반환
    else:
        # Print error message if fetching failed
        print(
            "Failed to fetch data from Google Spreadsheet."
        )  # 가져오기 실패 시 오류 메시지 출력
        return 1  # 실패 시 1 반환


# Execute the main function when script is run directly
if __name__ == "__main__":
    # Call the main function
    exit(main())  # main 함수 호출 및 반환 값을 종료 코드로 사용
