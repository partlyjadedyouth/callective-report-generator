# context7: Import the pandas library, which is essential for data manipulation and analysis in Python.
import pandas as pd

# context7: Read the participants' information from the CSV file into a DataFrame.
participants = pd.read_csv("data/csv/participants.csv")

# context7: Filter the DataFrame to include only rows where the '소속' (team) column is '상담 1팀'.
team1 = participants[participants["소속"] == "상담 2팀"]

# context7: Extract the list of phone numbers (last 4 digits) for all members in '상담 1팀'.
team1_phones = team1["휴대전화 네자리"].astype(str).tolist()

# context7: Read the 8th week results JSON file into a DataFrame.
results = pd.read_json("data/results/8주차.json")

# context7: Filter the results DataFrame to include only rows where the 'phone' value is in the list of '상담 1팀' phone numbers.
team1_results = results[results["phone"].astype(str).isin(team1_phones)]

# context7: Iterate over each member's result in the filtered DataFrame.
for idx, row in team1_results.iterrows():
    # context7: Print the participant's name and phone number for identification.
    print(f"Name: {row['name']}, Phone: {row['phone']}")
    # context7: Extract the 'stress' scores dictionary from the 'scores' column.
    stress_scores = row["scores"]["stress"]
    # context7: Iterate over each question and its score in the 'stress' dictionary.
    for q_num, score in stress_scores.items():
        # context7: Print the question number and the corresponding score.
        print(f"{q_num}: {score}")
    # context7: Print a separator line for readability between participants.
    print("-" * 40)
