#!/usr/bin/env python3
"""
Stress Distribution Summary Script

This script extracts stress risk level distributions from the groups analysis data 
and prints them in CSV format. Stress distributions are collected every 4 weeks 
(0주차, 4주차, 8주차, 12주차).
"""

import json
import sys
from typing import Dict, Any


def load_analysis_data(file_path: str) -> Dict[str, Any]:
    """Load the analysis JSON data from file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def week_to_time_symbol(week: str) -> str:
    """Convert week number to time symbol (T1, T3, T5, T7)."""
    week_mapping = {
        "0주차": "T1",   # Week 0
        "4주차": "T3",   # Week 4
        "8주차": "T5",   # Week 8
        "12주차": "T7"   # Week 12
    }
    return week_mapping.get(week, week)


def extract_stress_distribution(data: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
    """Extract stress risk level distributions for all weeks."""
    groups = data.get('groups', {})
    company_data = groups.get('회사', {})
    analysis = company_data.get('analysis', {})
    
    # Target weeks for stress data (every 4 weeks)
    target_weeks = ["0주차", "4주차", "8주차", "12주차"]
    
    distribution_data = {}
    
    for week in target_weeks:
        week_data = analysis.get(week, {})
        risk_levels = week_data.get('risk_levels', {})
        stress_risk = risk_levels.get('stress', {})
        
        # Skip weeks without stress risk data
        if not stress_risk:
            continue
            
        time_symbol = week_to_time_symbol(week)
        
        # Extract risk level counts
        normal = stress_risk.get('정상', 0)      # Normal
        semi = stress_risk.get('준위험', 0)      # Semi-risk
        risk = stress_risk.get('위험', 0)        # Risk
        
        distribution_data[time_symbol] = {
            'Normal': normal,
            'Semi': semi, 
            'Risk': risk
        }
    
    return distribution_data


def print_csv_format(distribution_data: Dict[str, Dict[str, int]]):
    """Print the data in CSV format."""
    # Get all time symbols and sort them
    time_symbols = sorted(distribution_data.keys(), key=lambda x: int(x[1:]))
    
    # Print header
    headers = ['Category'] + time_symbols
    print(','.join(headers))
    
    # Print data rows for each category
    categories = ['Normal', 'Semi', 'Risk']
    
    for category in categories:
        row = [category]
        for time_symbol in time_symbols:
            count = distribution_data.get(time_symbol, {}).get(category, 0)
            row.append(str(count))
        print(','.join(row))


def main():
    """Main function to process the analysis data and output CSV."""
    data_file = '/Users/joon/Developer/callective/report_generator/data/analysis/analysis.json'
    
    try:
        # Load the analysis data
        data = load_analysis_data(data_file)
        
        # Extract stress distribution data
        distribution_data = extract_stress_distribution(data)
        
        # Print results in CSV format
        print_csv_format(distribution_data)
        
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