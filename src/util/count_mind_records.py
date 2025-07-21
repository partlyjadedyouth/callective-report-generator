import pandas as pd  # Import pandas library for data manipulation
from collections import Counter  # Import Counter to count participant entries


def count_mind_records():
    """
    Count the number of mind record entries for each participant from app_usage_data_0주차.csv
    Uses participant identifiers from participants.csv and includes participants with 0 entries.

    This function reads both CSV files, maps participant IDs to their identifiers,
    counts how many times each participant entered text in the mind record column,
    and outputs the results in CSV format to console including those with 0 entries.
    """

    # Read the participants.csv file to get the mapping of IDs to identifiers
    # This file contains the official participant identifiers (P1, P2, etc.)
    try:
        participants_df = pd.read_csv("data/csv/participants.csv", encoding="utf-8-sig")
    except UnicodeDecodeError:
        # If utf-8-sig fails, try with euc-kr encoding
        participants_df = pd.read_csv("data/csv/participants.csv", encoding="euc-kr")

    # Read the app usage data CSV file using pandas with proper encoding
    # Korean CSV files often use utf-8-sig or euc-kr encoding
    try:
        df = pd.read_csv("data/csv/app_usage_data_6주차.csv", encoding="utf-8-sig")
    except UnicodeDecodeError:
        # If utf-8-sig fails, try with euc-kr encoding
        df = pd.read_csv("data/csv/app_usage_data_6주차.csv", encoding="euc-kr")

    # Create mapping from participant ID to identifier (P1, P2, etc.)
    # Use dictionary comprehension to map 아이디 -> 식별 기호
    id_to_identifier = dict(
        zip(participants_df["아이디"], participants_df["식별 기호"])
    )

    # Define the column name for mind record text input
    mind_record_column = "마음_기록_입력_내용_(텍스트)"
    id_column = "ID"  # Column containing participant IDs

    # Filter rows where mind record text is not empty/null
    # Use pd.notna() to check for non-null values and str.strip() to remove whitespace
    valid_records = df[
        df[mind_record_column].notna()
        & (df[mind_record_column].astype(str).str.strip() != "")
        & (df[mind_record_column].astype(str).str.strip() != "NULL")
    ]

    # Count entries per participant ID
    participant_counts = Counter(valid_records[id_column])

    # Print CSV header
    print("식별 기호,마음 기록 입력 횟수")

    # Sort participants by their identifier for consistent ordering (P1, P2, P3, ...)
    sorted_participants = sorted(
        participants_df["아이디"],
        key=lambda x: int(id_to_identifier[x][1:]) if x in id_to_identifier else 999,
    )

    # Print results for each participant in CSV format, including those with 0 entries
    total_entries = 0  # Keep track of total entries for summary
    participants_with_data = 0  # Count participants who have data in the usage file

    for participant_id in sorted_participants:
        # Get the identifier from the mapping (P1, P2, etc.)
        identifier = id_to_identifier.get(participant_id, f"UNKNOWN_{participant_id}")

        # Get count of mind records for this participant (0 if not found)
        count = participant_counts.get(participant_id, 0)

        # Only count participants who appear in the usage data
        if participant_id in df[id_column].values:
            participants_with_data += 1

        total_entries += count  # Add to total count

        # Output in CSV format
        print(f"{identifier},{count}")

    # Print summary information as comments (these won't affect CSV parsing)
    print(f"\n# 총 참여자 수 (participants.csv): {len(participants_df)}")
    print(f"# 사용 데이터에 등장한 참여자 수: {participants_with_data}")
    print(f"# 총 마음 기록 입력 건수: {total_entries}")


if __name__ == "__main__":
    # Execute the main function when script is run directly
    count_mind_records()
