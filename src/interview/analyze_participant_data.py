#!/usr/bin/env python3
"""
Interview Analysis Script - Analyzes participant app usage data from week 0-12

This script analyzes app usage data for all participants across weeks 0-12 and generates
individual participant reports with emotion records, app usage rankings, time-based analysis,
emotion percentages, and intervention activity percentages.
"""

import pandas as pd
import os
import sys
from datetime import datetime
from collections import Counter

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ParticipantAnalyzer:
    def __init__(self, base_path="/Users/joon/Developer/callective/report_generator"):
        """
        Initialize the analyzer with base paths for data files

        Args:
            base_path (str): Base path to the project directory
        """
        self.base_path = base_path
        self.csv_path = os.path.join(base_path, "data", "csv")
        self.output_path = os.path.join(base_path, "data", "interview")

        # Define emotion categories for analysis
        self.positive_emotions = ["행복해요", "신나요", "만족스러워요", "차분해요"]
        self.negative_emotions = ["슬퍼요", "우울해요", "불안해요", "화가나요"]

        # Initialize data containers
        self.participants_data = {}
        self.all_app_usage_data = []
        self.emotion_records = []

    def load_participants(self):
        """Load participant information from CSV file"""
        participants_file = os.path.join(self.csv_path, "participants.csv")
        try:
            # Read participants data with proper encoding
            participants_df = pd.read_csv(participants_file, encoding="utf-8")

            # Create participant mapping dictionary
            for _, row in participants_df.iterrows():
                participant_id = row["식별 기호"]  # P1, P2, etc.
                participant_name = row["성함"]  # Name in Korean
                participant_login_id = row["아이디"]  # Login ID

                self.participants_data[participant_id] = {
                    "name": participant_name,
                    "login_id": participant_login_id,
                    "phone": row["휴대전화 네자리"],
                    "team": row["소속"],
                    "role": row["직무"],
                    "gender": row["성별"],
                }

            print(f"✓ Loaded {len(self.participants_data)} participants")
            return True

        except Exception as e:
            print(f"✗ Error loading participants: {e}")
            return False

    def load_app_usage_data(self):
        """Load app usage data from all weekly CSV files"""
        # Define the weeks we have data for
        weeks = ["0주차", "2주차", "4주차", "6주차", "8주차", "10주차", "12주차"]

        for week in weeks:
            filename = f"app_usage_data_{week}.csv"
            filepath = os.path.join(self.csv_path, filename)

            if os.path.exists(filepath):
                try:
                    # Read the CSV file
                    df = pd.read_csv(filepath, encoding="utf-8")

                    # Normalize column names - weeks 6-12 have underscores instead of spaces
                    column_mapping = {
                        '선택한_감정': '선택한 감정',
                        '날짜_시간': '날짜 / 시간', 
                        '중재_활동_이름': '중재 활동 이름',
                        '마음_기록_입력_내용_(텍스트)': '마음 기록 입력 내용 (텍스트)'
                    }
                    
                    # Rename columns to standardize format
                    df = df.rename(columns=column_mapping)

                    # Add week information to each record
                    df["주차"] = week

                    # Append to our collection
                    self.all_app_usage_data.append(df)

                    print(f"✓ Loaded {filename}: {len(df)} records")

                except Exception as e:
                    print(f"✗ Error loading {filename}: {e}")
            else:
                print(f"⚠ File not found: {filename}")

        # Combine all app usage data
        if self.all_app_usage_data:
            self.combined_app_data = pd.concat(
                self.all_app_usage_data, ignore_index=True
            )
            print(f"✓ Total app usage records: {len(self.combined_app_data)}")
        else:
            print("✗ No app usage data loaded")

    def analyze_participant_emotions(self, participant_id, participant_name, login_id):
        """
        Analyze emotion records for a specific participant

        Args:
            participant_id (str): Participant ID (P1, P2, etc.)
            participant_name (str): Participant name
            login_id (str): Participant login ID

        Returns:
            dict: Analysis results for the participant
        """
        # Filter data for this participant using both name and ID matching (fix boolean logic)
        participant_records = self.combined_app_data[
            (self.combined_app_data["성함"] == participant_name) &
            (self.combined_app_data["ID"] == login_id)
        ].copy()

        # Basic emotion counts
        total_records = len(participant_records)

        # Count positive and negative emotions from emotion records only
        emotion_series = participant_records["선택한 감정"].dropna()
        positive_count = sum(1 for emotion in emotion_series if emotion in self.positive_emotions)
        negative_count = sum(1 for emotion in emotion_series if emotion in self.negative_emotions)

        # Emotion percentages
        emotion_counts = Counter(participant_records["선택한 감정"].dropna())
        emotion_percentages = {}

        if total_records > 0:
            for emotion, count in emotion_counts.items():
                emotion_percentages[emotion] = (count / total_records) * 100

        # 마음 기록 (heart records) - written emotional content
        heart_records = []
        for _, record in participant_records.iterrows():
            if (
                pd.notna(record["마음 기록 입력 내용 (텍스트)"])
                and record["마음 기록 입력 내용 (텍스트)"].strip()
            ):
                heart_record = {
                    "content": record["마음 기록 입력 내용 (텍스트)"],
                    "timestamp": record["날짜 / 시간"],
                    "emotion": record["선택한 감정"],
                }
                heart_records.append(heart_record)

        # 중재 활동 (intervention activities) analysis
        intervention_activities = participant_records["중재 활동 이름"].dropna()
        intervention_counts = Counter(intervention_activities)
        intervention_percentages = {}

        total_interventions = len(intervention_activities)
        if total_interventions > 0:
            for activity, count in intervention_counts.items():
                intervention_percentages[activity] = (count / total_interventions) * 100

        # Time-based analysis (by hour ranges)
        time_analysis = self.analyze_time_patterns(participant_records)

        return {
            "total_records": total_records,
            "positive_records": positive_count,
            "negative_records": negative_count,
            "emotion_percentages": emotion_percentages,
            "heart_records": heart_records,
            "intervention_percentages": intervention_percentages,
            "time_analysis": time_analysis,
            "raw_data_count": len(participant_records),
        }

    def analyze_time_patterns(self, participant_records):
        """
        Analyze emotion patterns by time ranges

        Args:
            participant_records (DataFrame): Records for a specific participant

        Returns:
            dict: Time-based emotion analysis
        """
        # Use work-hour based time ranges matching existing analysis
        time_ranges = {
            "08:00-10:30 (오전)": [],
            "10:30-12:00 (오전)": [],
            "12:00-13:30 (점심)": [],
            "13:30-15:00 (오후)": [],
            "15:00-16:30 (오후)": [],
            "16:30-19:00 (저녁)": [],
        }

        for _, record in participant_records.iterrows():
            if pd.notna(record["날짜 / 시간"]):
                try:
                    # Parse the datetime string
                    dt_str = str(record["날짜 / 시간"])
                    # Handle various datetime formats
                    if " " in dt_str:
                        time_part = dt_str.split(" ")[1]
                        hour = int(time_part.split(":")[0])

                        emotion = record["선택한 감정"]

                        # Parse time more precisely for work-hour analysis
                        time_parts = time_part.split(":")
                        hour = int(time_parts[0])
                        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                        time_minutes = hour * 60 + minute
                        
                        # Categorize into work-hour time ranges
                        if 8 * 60 <= time_minutes < 10 * 60 + 30:  # 08:00-10:30
                            time_ranges["08:00-10:30 (오전)"].append(emotion)
                        elif 10 * 60 + 30 <= time_minutes < 12 * 60:  # 10:30-12:00
                            time_ranges["10:30-12:00 (오전)"].append(emotion)
                        elif 12 * 60 <= time_minutes < 13 * 60 + 30:  # 12:00-13:30
                            time_ranges["12:00-13:30 (점심)"].append(emotion)
                        elif 13 * 60 + 30 <= time_minutes < 15 * 60:  # 13:30-15:00
                            time_ranges["13:30-15:00 (오후)"].append(emotion)
                        elif 15 * 60 <= time_minutes < 16 * 60 + 30:  # 15:00-16:30
                            time_ranges["15:00-16:30 (오후)"].append(emotion)
                        elif 16 * 60 + 30 <= time_minutes < 19 * 60:  # 16:30-19:00
                            time_ranges["16:30-19:00 (저녁)"].append(emotion)

                except (ValueError, IndexError):
                    continue  # Skip invalid datetime formats

        # Count emotions for each time range
        time_analysis = {}
        for time_range, emotions in time_ranges.items():
            time_analysis[time_range] = {
                "total": len(emotions),
                "emotions": Counter(emotions),
            }

        return time_analysis

    def calculate_app_usage_ranking(self):
        """Calculate app usage ranking for all participants"""
        # Count total records per participant
        participant_usage = {}

        for participant_id, participant_info in self.participants_data.items():
            participant_name = participant_info["name"]
            login_id = participant_info["login_id"]

            # Count records for this participant (fix boolean logic)
            participant_records = self.combined_app_data[
                (self.combined_app_data["성함"] == participant_name) &
                (self.combined_app_data["ID"] == login_id)
            ]

            participant_usage[participant_id] = len(participant_records)

        # Sort participants by usage (descending)
        sorted_usage = sorted(
            participant_usage.items(), key=lambda x: x[1], reverse=True
        )

        # Create ranking dictionary
        rankings = {}
        for rank, (participant_id, usage_count) in enumerate(sorted_usage, 1):
            rankings[participant_id] = {
                "rank": rank,
                "usage_count": usage_count,
                "total_participants": len(self.participants_data),
            }

        return rankings

    def generate_participant_report(self, participant_id):
        """
        Generate a comprehensive report for a specific participant

        Args:
            participant_id (str): Participant ID (P1, P2, etc.)
        """
        if participant_id not in self.participants_data:
            print(f"✗ Participant {participant_id} not found")
            return

        participant_info = self.participants_data[participant_id]
        participant_name = participant_info["name"]
        login_id = participant_info["login_id"]

        print(f"📊 Analyzing {participant_id} {participant_name}...")

        # Perform analysis
        analysis = self.analyze_participant_emotions(
            participant_id, participant_name, login_id
        )
        rankings = self.calculate_app_usage_ranking()

        # Get participant ranking
        participant_ranking = rankings.get(
            participant_id, {"rank": "N/A", "usage_count": 0}
        )

        # Generate report content
        report_lines = []
        report_lines.append(
            f"=== {participant_id} {participant_name} 앱 사용 분석 보고서 ==="
        )
        report_lines.append(f"분석 기간: 0주차 - 12주차")
        report_lines.append(
            f"생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append("")

        # 1. 감정 기록 통계
        report_lines.append("📈 감정 기록 통계 (0주차-12주차)")
        report_lines.append(f"• 총 감정 기록 수: {analysis['total_records']}개")
        report_lines.append(f"• 긍정적 감정 기록: {analysis['positive_records']}개")
        report_lines.append(f"• 부정적 감정 기록: {analysis['negative_records']}개")
        report_lines.append("")

        # 2. 앱 사용 순위
        report_lines.append("🏆 앱 사용 순위")
        report_lines.append(
            f"• 전체 참가자 중 {participant_ranking['rank']}위 (총 {participant_ranking.get('total_participants', 43)}명 중)"
        )
        report_lines.append(
            f"• 총 앱 사용 기록: {participant_ranking['usage_count']}회"
        )
        report_lines.append("")

        # 3. 시간대별 감정 기록 분석
        report_lines.append("⏰ 시간대별 감정 기록 분석")
        for time_range, data in analysis["time_analysis"].items():
            if data["total"] > 0:
                report_lines.append(f"• {time_range}: {data['total']}개 기록")
                for emotion, count in data["emotions"].most_common(3):  # Top 3 emotions
                    percentage = (count / data["total"]) * 100
                    report_lines.append(f"  - {emotion}: {count}회 ({percentage:.1f}%)")
            else:
                report_lines.append(f"• {time_range}: 기록 없음")
        report_lines.append("")

        # 4. 마음 기록 내용
        report_lines.append("💭 마음 기록 내용")
        if analysis["heart_records"]:
            report_lines.append(f"총 {len(analysis['heart_records'])}개의 마음 기록:")
            for i, record in enumerate(
                analysis["heart_records"][:10], 1
            ):  # Show up to 10 records
                report_lines.append(f"{i}. [{record['timestamp']}] {record['emotion']}")
                report_lines.append(f"   \"{record['content']}\"")
                if i < len(analysis["heart_records"]):
                    report_lines.append("")

            if len(analysis["heart_records"]) > 10:
                report_lines.append(
                    f"... 및 {len(analysis['heart_records']) - 10}개 추가 기록"
                )
        else:
            report_lines.append("마음 기록이 없습니다.")
        report_lines.append("")

        # 5. 감정별 비율
        report_lines.append("😊 감정별 기록 비율")
        if analysis["emotion_percentages"]:
            # Sort emotions by percentage (descending)
            sorted_emotions = sorted(
                analysis["emotion_percentages"].items(),
                key=lambda x: x[1],
                reverse=True,
            )
            for emotion, percentage in sorted_emotions:
                report_lines.append(f"• {emotion}: {percentage:.1f}%")
        else:
            report_lines.append("감정 기록이 없습니다.")
        report_lines.append("")

        # 6. 중재 활동 비율
        report_lines.append("🎯 중재 활동 참여 비율")
        if analysis["intervention_percentages"]:
            # Sort interventions by percentage (descending)
            sorted_interventions = sorted(
                analysis["intervention_percentages"].items(),
                key=lambda x: x[1],
                reverse=True,
            )
            for activity, percentage in sorted_interventions:
                report_lines.append(f"• {activity}: {percentage:.1f}%")
        else:
            report_lines.append("중재 활동 기록이 없습니다.")

        # Write report to file
        participant_dir = os.path.join(
            self.output_path, f"{participant_id} {participant_name}"
        )
        if not os.path.exists(participant_dir):
            os.makedirs(participant_dir)

        report_filename = f"{participant_id}_{participant_name}_분석보고서.txt"
        report_filepath = os.path.join(participant_dir, report_filename)

        try:
            with open(report_filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(report_lines))

            print(f"✓ Report generated: {report_filepath}")

        except Exception as e:
            print(f"✗ Error writing report for {participant_id}: {e}")

    def run_analysis(self):
        """Run the complete analysis for all participants"""
        print("🚀 Starting Interview Analysis...")
        print("=" * 50)

        # Load participants data
        if not self.load_participants():
            return False

        # Load app usage data
        self.load_app_usage_data()

        if not hasattr(self, "combined_app_data") or self.combined_app_data.empty:
            print("✗ No app usage data available for analysis")
            return False

        print("\n📊 Generating participant reports...")
        print("=" * 50)

        # Generate reports for all participants
        success_count = 0
        for participant_id in self.participants_data.keys():
            try:
                self.generate_participant_report(participant_id)
                success_count += 1
            except Exception as e:
                print(f"✗ Error analyzing {participant_id}: {e}")

        print(f"\n✅ Analysis complete!")
        print(
            f"Successfully generated {success_count}/{len(self.participants_data)} participant reports"
        )
        print(f"Reports saved to: {self.output_path}")

        return True


def main():
    """Main function to run the analysis"""
    print("Interview Participant Analysis Script")
    print("=" * 40)

    # Initialize analyzer
    analyzer = ParticipantAnalyzer()

    # Run the complete analysis
    success = analyzer.run_analysis()

    if success:
        print("\n🎉 All participant reports have been generated successfully!")
    else:
        print("\n❌ Analysis failed. Please check the error messages above.")

    return success


if __name__ == "__main__":
    main()
