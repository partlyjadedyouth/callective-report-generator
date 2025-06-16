import pandas as pd
import json  # Import json module to handle JSON file reading


def load_data_files():
    """Load JSON and CSV data files and return the data structures"""
    # Define file paths
    json_file_path = "data/analysis/analysis.json"  # Path to analysis JSON file
    participants_csv_path = "data/csv/participants.csv"  # Path to participants CSV file

    # Read JSON file
    with open(json_file_path, "r") as file:  # Open JSON file in read mode
        analysis = json.load(file)  # Load JSON content into dictionary

    # Read CSV file
    participants_csv = pd.read_csv(participants_csv_path)  # Load CSV into DataFrame

    return analysis, participants_csv


def create_name_to_symbol_mapping(participants_csv):
    """Create mapping dictionary from participant names to identification symbols (P1, P2, ...)"""
    return dict(
        zip(
            participants_csv["성함"].str.strip(),  # Strip whitespace from names
            participants_csv["식별 기호"].str.strip(),  # Strip whitespace from symbols
        )
    )


def extract_participant_basic_info(analysis, name_to_symbol_mapping):
    """Extract basic participant information and create DataFrame"""
    participants_data = []  # Initialize list for participant data

    # Loop through each participant
    for participant in analysis["participants"]:
        participant_info = {
            "이름": participant["name"],  # Participant name
            "식별기호": name_to_symbol_mapping.get(
                participant["name"], "Unknown"
            ),  # P1, P2, ... symbol
            "ID": participant["id"],  # Original ID
            "팀": participant["team"],  # Team information
            "역할": participant["role"],  # Role information
            "성별": participant["gender"],  # Gender information
        }
        participants_data.append(participant_info)

    # Sort by identification symbol
    participants_data.sort(
        key=lambda x: int(x["식별기호"][1:])
    )  # Sort by number after "P"

    return pd.DataFrame(participants_data)


def extract_weekly_analysis_scores(week_data):
    """Extract all analysis scores from weekly data"""
    scores = {}  # Initialize scores dictionary

    # Extract BAT_primary scores
    scores["번아웃 핵심증상"] = week_data["category_averages"].get("BAT_primary", None)
    bat_primary_types = week_data["type_averages"].get("BAT_primary", {})
    scores.update(
        {
            "탈진": bat_primary_types.get("탈진", None),
            "심적 거리": bat_primary_types.get("심적 거리", None),
            "인지적 조절": bat_primary_types.get("인지적 조절", None),
            "정서적 조절": bat_primary_types.get("정서적 조절", None),
        }
    )

    # Extract emotional_labor scores
    scores["감정 노동"] = week_data["category_averages"].get("emotional_labor", None)
    emotional_labor_types = week_data["type_averages"].get("emotional_labor", {})
    scores.update(
        {
            "감정조절의 노력 및 다양성": emotional_labor_types.get(
                "감정조절의 노력 및 다양성", None
            ),
            "고객응대의 과부하 및 갈등": emotional_labor_types.get(
                "고객응대의 과부하 및 갈등", None
            ),
            "감정부조화 및 손상": emotional_labor_types.get("감정부조화 및 손상", None),
            "조직의 감시 및 모니터링": emotional_labor_types.get(
                "조직의 감시 및 모니터링", None
            ),
            "조직의 지지 및 보호체계": emotional_labor_types.get(
                "조직의 지지 및 보호체계", None
            ),
        }
    )

    # Extract stress scores
    scores["직무 스트레스"] = week_data["category_averages"].get("stress", None)
    stress_types = week_data["type_averages"].get("stress", {})
    scores.update(
        {
            "직무 요구": stress_types.get("직무 요구", None),
            "직무 자율": stress_types.get("직무 자율", None),
            "관계 갈등": stress_types.get("관계 갈등", None),
            "직무 불안": stress_types.get("직무 불안", None),
            "조직 체계": stress_types.get("조직 체계", None),
            "보상 부적절": stress_types.get("보상 부적절", None),
            "직장 문화": stress_types.get("직장 문화", None),
        }
    )

    return scores


def create_weekly_analysis_dataframe(analysis, name_to_symbol_mapping):
    """Create DataFrame with weekly analysis data for all participants"""
    weekly_analysis_data = []  # Initialize list for weekly data

    # Process each participant
    for participant in analysis["participants"]:
        participant_name = participant["name"]  # Get participant name
        participant_symbol = name_to_symbol_mapping.get(
            participant_name, "Unknown"
        )  # Get P1, P2, ... symbol
        participant_id = participant["id"]  # Get participant ID

        # Process each week for this participant
        for week, week_data in participant["analysis"].items():
            # Create base record with participant info
            weekly_record = {
                "이름": participant_name,
                "식별기호": participant_symbol,
                "ID": participant_id,
                "주차": week,
            }

            # Extract and add all analysis scores
            analysis_scores = extract_weekly_analysis_scores(week_data)
            weekly_record.update(analysis_scores)

            # Add record to list
            weekly_analysis_data.append(weekly_record)

    # Create DataFrame
    df_weekly = pd.DataFrame(weekly_analysis_data)

    # Sort by identification symbol and week
    week_order = {"0주차": 0, "2주차": 2, "4주차": 4}  # Define week ordering
    df_weekly["week_sort"] = df_weekly["주차"].map(week_order)  # Create sort column
    df_weekly["symbol_sort"] = df_weekly["식별기호"].apply(
        lambda x: int(x[1:]) if isinstance(x, str) and x.startswith("P") else 999
    )  # Create symbol sort column

    # Sort and clean up
    df_weekly = df_weekly.sort_values(
        ["symbol_sort", "week_sort"]
    )  # Sort by symbol and week
    df_weekly = df_weekly.drop(
        ["week_sort", "symbol_sort"], axis=1
    )  # Remove sort columns
    df_weekly.reset_index(drop=True, inplace=True)  # Reset index

    return df_weekly


def print_dataframe_summary(df):
    """Print summary information about the DataFrame"""
    print("주차별 분석 데이터 DataFrame:")  # Print header
    print(f"총 레코드 수: {len(df)}")  # Print total records
    print(f"컬럼 수: {len(df.columns)}")  # Print column count
    print("\n컬럼 목록:")  # Print column list header
    print(df.columns.tolist())  # Print all column names
    print("\n첫 10개 레코드:")  # Print first 10 records header
    print(df.head(10))  # Display first 10 rows


def save_dataframe_to_csv(df, filename):
    """Save DataFrame to CSV file"""
    df.to_csv(filename, index=False)


# Main execution
if __name__ == "__main__":
    # Load data files
    analysis, participants_csv = load_data_files()

    # Create name to symbol mapping
    name_to_symbol_mapping = create_name_to_symbol_mapping(participants_csv)

    # Create basic participant info DataFrame
    df_basic = extract_participant_basic_info(analysis, name_to_symbol_mapping)

    # Create weekly analysis DataFrame
    df = create_weekly_analysis_dataframe(analysis, name_to_symbol_mapping)

    # Print summary
    print_dataframe_summary(df)

    # Save DataFrame to CSV
    save_dataframe_to_csv(df, "data/csv/weekly_analysis.csv")
