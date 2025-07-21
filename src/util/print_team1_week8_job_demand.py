import json  # Import the json module to handle JSON file operations

# Define the path to the analysis.json file
ANALYSIS_JSON_PATH = (
    "data/analysis/analysis.json"  # Relative path from this script to the JSON file
)

# Open the analysis.json file in read mode with UTF-8 encoding
with open(ANALYSIS_JSON_PATH, "r", encoding="utf-8") as f:
    # Load the JSON data into a Python dictionary
    data = json.load(f)

# Extract the list of participants from the loaded data
participants = data[
    "participants"
]  # 'participants' is a list of participant dictionaries

# Iterate over each participant in the list
for participant in participants:
    # Check if the participant's team is '상담 1팀'
    if participant.get("team") == "상담 1팀":
        # Get the participant's name for display
        name = participant.get("name", "Unknown")  # Use 'Unknown' if name is missing
        # Get the analysis dictionary for this participant
        analysis = participant.get("analysis", {})
        # Get the 8주차 (week 8) analysis, if it exists
        week8 = analysis.get("8주차", {})
        # Get the type_averages dictionary for week 8
        type_averages = week8.get("type_averages", {})
        # Get the stress dictionary from type_averages
        stress = type_averages.get("stress", {})
        # Get the '직무 요구' (Job Demand) value, if it exists
        job_demand = stress.get("직무 불안")
        # Print the participant's name and their week 8 '직무 요구' value
        print(f"{name}: {job_demand}")  # Output format: Name: Value
