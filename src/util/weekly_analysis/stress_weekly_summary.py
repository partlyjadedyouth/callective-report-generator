import json


def load_analysis_data(file_path):
    """Load analysis data from json file, and save it in a dictionary."""
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


if __name__ == "__main__":
    week = 12
    file_path = "data/analysis/analysis.json"
    groups = ["상담 1팀", "상담 2팀", "상담 3팀", "상담 4팀", "회사"]

    analysis = load_analysis_data(file_path)

    print("팀,직무 요구,직무 자율,관계 갈등,직무 불안,조직 체계,보상 부적절,직장 문화,총점")
    for group in groups:
        stress_analysis = analysis['groups'][group]['analysis'][f'{week}주차']['type_averages']['stress']
        print(
            f"{group},"
            f"{stress_analysis['직무 요구']},"
            f"{stress_analysis['직무 자율']},"
            f"{stress_analysis['관계 갈등']},"
            f"{stress_analysis['직무 불안']},"
            f"{stress_analysis['조직 체계']},"
            f"{stress_analysis['보상 부적절']},"
            f"{stress_analysis['직장 문화']},"
            f"{analysis['groups'][group]['analysis'][f'{week}주차']['category_averages']['stress']}"
        )

    print("")

    print(",정상,준위험,위험")
    for group in groups:
        print(
            f"{group},"
            f"{analysis['groups'][group]['analysis'][f'{week}주차']['risk_levels']['stress']['정상']},"
            f"{analysis['groups'][group]['analysis'][f'{week}주차']['risk_levels']['stress']['준위험']},"
            f"{analysis['groups'][group]['analysis'][f'{week}주차']['risk_levels']['stress']['위험']}"
        )