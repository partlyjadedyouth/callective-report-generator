#!/usr/bin/env python3
"""
Emotional Labor Summary Script

This script extracts emotional labor scores from the analysis data and prints them in CSV format.
Emotional labor scores are collected every 4 weeks (0주차, 4주차, 8주차, 12주차).
"""

import json
import sys
import csv
from typing import Dict, Any


def load_analysis_data(file_path: str) -> Dict[str, Any]:
    """Load the analysis JSON data from file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def load_participants_mapping(csv_path: str) -> Dict[str, str]:
    """Load participant mapping from CSV file and create a mapping from name+id to 식별 기호."""
    mapping = {}
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['성함']
            user_id = row['아이디']
            identifier = row['식별 기호']
            # For handling duplicate names, use user_id as the primary key for mapping
            # Only use name as fallback if user_id is not available
            mapping[user_id] = identifier
            # Create a combined key for exact matching (name_userid)
            mapping[f"{name}_{user_id}"] = identifier
    return mapping


def week_to_time_symbol(week: str) -> str:
    """Convert week number to time symbol (T1, T3, T5, T7)."""
    week_mapping = {
        "0주차": "T1",
        "4주차": "T3", 
        "8주차": "T5",
        "12주차": "T7"
    }
    return week_mapping.get(week, week)


def get_participant_identifier(participant_data: Dict[str, Any], mapping: Dict[str, str]) -> str:
    """Get the correct participant identifier (식별 기호) using the mapping."""
    name = participant_data.get('name', '')
    user_id = participant_data.get('id', '')
    
    # For handling duplicate names, prioritize user_id-based matching
    # First try user ID match (most reliable for distinguishing duplicate names)
    if user_id and user_id in mapping:
        return mapping[user_id]
    
    # Try combined key (name_userid) for exact matching
    if name and user_id:
        combined_key = f"{name}_{user_id}"
        if combined_key in mapping:
            return mapping[combined_key]
    
    # If no match found, return user_id as fallback
    print(f"Warning: No mapping found for participant {name} ({user_id})", file=sys.stderr)
    return user_id if user_id else name


def extract_emotional_labor_scores(participant_data: Dict[str, Any], participant_id: str) -> list:
    """Extract emotional labor scores for a participant across all measurement weeks."""
    rows = []
    analysis = participant_data.get('analysis', {})
    
    # Process only 4-week intervals (0주차, 4주차, 8주차, 12주차)
    target_weeks = ["0주차", "4주차", "8주차", "12주차"]
    
    for week in target_weeks:
        week_data = analysis.get(week, {})
        type_averages = week_data.get('type_averages', {})
        emotional_labor_data = type_averages.get('emotional_labor', {})
        
        # Skip weeks without emotional labor data
        if not emotional_labor_data or emotional_labor_data == {}:
            continue
            
        time_symbol = week_to_time_symbol(week)
        
        # Extract the 5 emotional labor components
        regulation = emotional_labor_data.get('감정조절의 노력 및 다양성', '')
        overload = emotional_labor_data.get('고객응대의 과부하 및 갈등', '')
        dissonance = emotional_labor_data.get('감정부조화 및 손상', '')
        surveillance = emotional_labor_data.get('조직의 감시 및 모니터링', '')
        support = emotional_labor_data.get('조직의 지지 및 보호체계', '')
        
        row = {
            'Participant': participant_id,
            'Week': time_symbol,
            'Regulation': regulation,
            'Overload': overload,
            'Dissonance': dissonance,
            'Surveillance': surveillance,
            'Support': support
        }
        rows.append(row)
    
    return rows


def format_participant_id(participant_id: str) -> str:
    """Format participant ID to ensure 2-digit number (e.g., P01, P02, P10, P11)."""
    if participant_id.startswith('P'):
        # Extract the number part
        number_part = participant_id[1:]
        try:
            # Convert to integer and format as 2-digit
            num = int(number_part)
            return f"P{num:02d}"
        except ValueError:
            # If conversion fails, return original
            return participant_id
    return participant_id


def print_csv_format(all_rows: list):
    """Print the data in CSV format."""
    # Print header
    headers = ['Participant', 'Week', 'Regulation', 'Overload', 'Dissonance', 'Surveillance', 'Support']
    print(','.join(headers))
    
    # Format participant IDs and sort by participant number and week
    for row in all_rows:
        row['Participant'] = format_participant_id(row['Participant'])
    
    # Sort by participant number (extract number for proper numeric sorting) and week
    def sort_key(row):
        participant_id = row['Participant']
        # Extract numeric part for sorting
        if participant_id.startswith('P'):
            try:
                participant_num = int(participant_id[1:])
            except ValueError:
                participant_num = 999  # fallback for non-numeric IDs
        else:
            participant_num = 999
        return (participant_num, row['Week'])
    
    all_rows.sort(key=sort_key)
    
    # Print data rows
    for row in all_rows:
        values = [str(row[header]) for header in headers]
        print(','.join(values))


def main():
    """Main function to process the analysis data and output CSV."""
    data_file = '/Users/joon/Developer/callective/report_generator/data/analysis/analysis.json'
    participants_file = '/Users/joon/Developer/callective/report_generator/data/csv/participants.csv'
    
    try:
        # Load the analysis data and participant mapping
        data = load_analysis_data(data_file)
        participants = data.get('participants', [])
        participant_mapping = load_participants_mapping(participants_file)
        
        all_rows = []
        
        # Process each participant
        for participant in participants:
            # Get the correct participant identifier from mapping
            participant_id = get_participant_identifier(participant, participant_mapping)
            
            # Extract emotional labor scores for this participant
            participant_rows = extract_emotional_labor_scores(participant, participant_id)
            all_rows.extend(participant_rows)
        
        # Print results in CSV format
        print_csv_format(all_rows)
        
    except FileNotFoundError as e:
        print(f"Error: Could not find the data file: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in data file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()