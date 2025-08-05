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

    print(",탈진,심적 거리,인지적 조절,정서적 조절,총점,심리적 호소,신체적 호소")
    for group in groups:
        print(
            f"{group},"
            f"{analysis['groups'][group]['analysis'][f'{week}주차']['type_averages']['BAT_primary']['탈진']},"
            f"{analysis['groups'][group]['analysis'][f'{week}주차']['type_averages']['BAT_primary']['심적 거리']},"
            f"{analysis['groups'][group]['analysis'][f'{week}주차']['type_averages']['BAT_primary']['인지적 조절']},"
            f"{analysis['groups'][group]['analysis'][f'{week}주차']['type_averages']['BAT_primary']['정서적 조절']},"
            f"{analysis['groups'][group]['analysis'][f'{week}주차']['category_averages']['BAT_primary']},"
            f"{analysis['groups'][group]['analysis'][f'{week}주차']['type_averages']['BAT_secondary']['심리적 호소']},"
            f"{analysis['groups'][group]['analysis'][f'{week}주차']['type_averages']['BAT_secondary']['신체적 호소']}"
        )

    print("")

    print(",정상,준위험,위험")
    for group in groups:
        print(
            f"{group},"
            f"{analysis['groups'][group]['analysis'][f'{week}주차']['risk_levels']['BAT_primary']['정상']},"
            f"{analysis['groups'][group]['analysis'][f'{week}주차']['risk_levels']['BAT_primary']['준위험']},"
            f"{analysis['groups'][group]['analysis'][f'{week}주차']['risk_levels']['BAT_primary']['위험']}"
        )
