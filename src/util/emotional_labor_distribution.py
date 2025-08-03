#!/usr/bin/env python3
"""
Emotional Labor Distribution Summary Script

This script extracts emotional labor risk level distributions from the groups analysis data 
and prints them in CSV format. Emotional labor distributions are collected every 4 weeks 
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


def extract_emotional_labor_distribution(data: Dict[str, Any]) -> Dict[str, Dict[str, Dict[str, int]]]:
    """Extract emotional labor risk level distributions for all weeks and components."""
    groups = data.get('groups', {})
    company_data = groups.get('회사', {})
    analysis = company_data.get('analysis', {})
    
    # Target weeks for emotional labor data (every 4 weeks)
    target_weeks = ["0주차", "4주차", "8주차", "12주차"]
    
    # Emotional labor components mapping
    components = {
        "Regulation": "감정조절의 노력 및 다양성",
        "Overload": "고객응대의 과부하 및 갈등", 
        "Dissonance": "감정부조화 및 손상",
        "Surveillance": "조직의 감시 및 모니터링",
        "Support": "조직의 지지 및 보호체계"
    }
    
    distribution_data = {}
    
    for week in target_weeks:
        week_data = analysis.get(week, {})
        risk_levels = week_data.get('risk_levels', {})
        emotional_labor_risk = risk_levels.get('emotional_labor', {})
        
        # Skip weeks without emotional labor risk data
        if not emotional_labor_risk:
            continue
            
        time_symbol = week_to_time_symbol(week)
        distribution_data[time_symbol] = {}
        
        # Extract data for each component
        for component_en, component_kr in components.items():
            component_data = emotional_labor_risk.get(component_kr, {})
            
            # Extract risk level counts (only Normal and Risk for emotional labor)
            normal = component_data.get('정상', 0)      # Normal
            risk = component_data.get('위험', 0)        # Risk
            
            distribution_data[time_symbol][component_en] = {
                'Normal': normal,
                'Risk': risk
            }
    
    return distribution_data


def print_csv_format(distribution_data: Dict[str, Dict[str, Dict[str, int]]]):
    """Print the data in CSV format."""
    # Get all time symbols and sort them
    time_symbols = sorted(distribution_data.keys(), key=lambda x: int(x[1:]))
    
    # Build header with component-time combinations (component first, then time)
    headers = ['Category']
    components = ["Regulation", "Overload", "Dissonance", "Surveillance", "Support"]
    
    for component in components:
        for time_symbol in time_symbols:
            headers.append(f"{time_symbol}_{component}")
    
    print(','.join(headers))
    
    # Print data rows for each category
    categories = ['Normal', 'Risk']
    
    for category in categories:
        row = [category]
        for component in components:
            for time_symbol in time_symbols:
                count = distribution_data.get(time_symbol, {}).get(component, {}).get(category, 0)
                row.append(str(count))
        print(','.join(row))


def main():
    """Main function to process the analysis data and output CSV."""
    data_file = '/Users/joon/Developer/callective/report_generator/data/analysis/analysis.json'
    
    try:
        # Load the analysis data
        data = load_analysis_data(data_file)
        
        # Extract emotional labor distribution data
        distribution_data = extract_emotional_labor_distribution(data)
        
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