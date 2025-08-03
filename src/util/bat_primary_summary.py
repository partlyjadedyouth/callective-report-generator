#!/usr/bin/env python3
"""
BAT Primary Summary Script

This script extracts BAT_primary scores from the analysis data and prints them in CSV format.
BAT_primary scores are collected every 2 weeks (0주차, 2주차, 4주차, 6주차, 8주차, 10주차, 12주차).
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
            # Create mapping using both name and id as keys
            mapping[name] = identifier
            mapping[user_id] = identifier
            # Also create a combined key for exact matching
            mapping[f"{name}_{user_id}"] = identifier
    return mapping


def week_to_time_symbol(week: str) -> str:
    """Convert week number to time symbol (T1, T2, T3, T4, T5, T6, T7)."""
    week_mapping = {
        "0주차": "T1",   # Week 0
        "2주차": "T2",   # Week 2
        "4주차": "T3",   # Week 4
        "6주차": "T4",   # Week 6
        "8주차": "T5",   # Week 8
        "10주차": "T6",  # Week 10
        "12주차": "T7"   # Week 12
    }
    return week_mapping.get(week, week)


def get_participant_identifier(participant_data: Dict[str, Any], mapping: Dict[str, str]) -> str:
    """Get the correct participant identifier (식별 기호) using the mapping."""
    name = participant_data.get('name', '')
    user_id = participant_data.get('id', '')
    
    # Try to find the identifier using different keys
    # First try exact name match
    if name in mapping:
        return mapping[name]
    
    # Then try user ID match
    if user_id in mapping:
        return mapping[user_id]
    
    # Try combined key
    combined_key = f"{name}_{user_id}"
    if combined_key in mapping:
        return mapping[combined_key]
    
    # If no match found, return user_id as fallback
    print(f"Warning: No mapping found for participant {name} ({user_id})", file=sys.stderr)
    return user_id


def extract_bat_primary_scores(participant_data: Dict[str, Any], participant_id: str) -> list:
    """Extract BAT_primary scores for a participant across all measurement weeks."""
    rows = []
    analysis = participant_data.get('analysis', {})
    
    # Process all 2-week intervals (0주차, 2주차, 4주차, 6주차, 8주차, 10주차, 12주차)
    target_weeks = ["0주차", "2주차", "4주차", "6주차", "8주차", "10주차", "12주차"]
    
    for week in target_weeks:
        week_data = analysis.get(week, {})
        
        # Get total BAT_primary score from category_averages
        category_averages = week_data.get('category_averages', {})
        total_score = category_averages.get('BAT_primary', '')
        
        # Get individual component scores from type_averages
        type_averages = week_data.get('type_averages', {})
        bat_primary_data = type_averages.get('BAT_primary', {})
        
        # Skip weeks without BAT_primary data
        if not bat_primary_data and total_score == '':
            continue
            
        time_symbol = week_to_time_symbol(week)
        
        # Extract the 4 BAT_primary components
        exhaustion = bat_primary_data.get('탈진', '')  # Exhaustion
        distance = bat_primary_data.get('심적 거리', '')  # Distance
        cognitive = bat_primary_data.get('인지적 조절', '')  # Cognitive
        psychological = bat_primary_data.get('정서적 조절', '')  # Psychological
        
        row = {
            'Participant': participant_id,
            'Week': time_symbol,
            'Total': total_score,
            'Exhaustion': exhaustion,
            'Distance': distance,
            'Cognitive': cognitive,
            'Psychological': psychological
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
    headers = ['Participant', 'Week', 'Total', 'Exhaustion', 'Distance', 'Cognitive', 'Psychological']
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
        
        # Extract week number for sorting
        week = row['Week']
        if week.startswith('T'):
            try:
                week_num = int(week[1:])
            except ValueError:
                week_num = 999
        else:
            week_num = 999
            
        return (participant_num, week_num)
    
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
            
            # Extract BAT_primary scores for this participant
            participant_rows = extract_bat_primary_scores(participant, participant_id)
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