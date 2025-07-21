#!/usr/bin/env python3
"""
8주차 팀별 직무스트레스 점수 요약 CSV 출력 스크립트

이 스크립트는 analysis.json 파일에서 8주차 직무스트레스 데이터를 읽어
팀별 스트레스 점수와 위험 수준별 인원수를 CSV 형식으로 출력합니다.
"""

import json  # JSON 파일 처리를 위한 모듈
import os  # 파일 시스템 작업을 위한 모듈
import sys  # 시스템 관련 작업을 위한 모듈


def find_analysis_file():
    """
    analysis.json 파일의 경로를 찾는 함수

    Returns:
        str: analysis.json 파일의 절대 경로

    Raises:
        FileNotFoundError: analysis.json 파일을 찾을 수 없는 경우
    """
    # 현재 스크립트의 디렉토리를 기준으로 프로젝트 루트를 찾습니다
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 가능한 경로들을 정의합니다
    possible_paths = [
        # 프로젝트 루트에서 상대 경로로 찾기
        os.path.join(current_dir, "..", "..", "data", "analysis", "analysis.json"),
        # 현재 작업 디렉토리에서 찾기
        os.path.join(os.getcwd(), "data", "analysis", "analysis.json"),
        # 직접 상대 경로
        "data/analysis/analysis.json",
    ]

    # 각 경로를 확인하여 파일이 존재하는지 검사합니다
    for path in possible_paths:
        # 경로를 절대 경로로 변환합니다
        abs_path = os.path.abspath(path)
        # 파일이 존재하는지 확인합니다
        if os.path.exists(abs_path):
            return abs_path

    # 파일을 찾을 수 없는 경우 오류를 발생시킵니다
    raise FileNotFoundError(
        f"analysis.json 파일을 찾을 수 없습니다. 다음 경로들을 확인했습니다:\n"
        + "\n".join(possible_paths)
    )


def load_analysis_data():
    """
    analysis.json 파일을 로드하는 함수

    Returns:
        dict: 로드된 분석 데이터

    Raises:
        FileNotFoundError: 파일을 찾을 수 없는 경우
        json.JSONDecodeError: JSON 디코딩 오류가 발생한 경우
    """
    try:
        # analysis.json 파일 경로를 찾습니다
        file_path = find_analysis_file()
        print(f"분석 데이터를 로드하는 중: {file_path}")

        # JSON 파일을 읽어들입니다
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print("분석 데이터 로드 완료")
        return data

    except FileNotFoundError as e:
        # 파일을 찾을 수 없는 경우 오류 메시지를 출력합니다
        print(f"오류: {e}")
        sys.exit(1)

    except json.JSONDecodeError as e:
        # JSON 디코딩 오류가 발생한 경우 오류 메시지를 출력합니다
        print(f"JSON 디코딩 오류: {e}")
        sys.exit(1)


def extract_week8_stress_data(analysis_data):
    """
    8주차 데이터에서 팀별 직무스트레스 점수를 추출하는 함수

    Args:
        analysis_data (dict): 분석 데이터

    Returns:
        dict: 팀별 8주차 직무스트레스 점수 데이터
    """
    # 결과를 저장할 딕셔너리를 초기화합니다
    week8_stress_data = {}

    # groups 데이터가 있는지 확인합니다
    if "groups" not in analysis_data:
        print("오류: groups 데이터를 찾을 수 없습니다.")
        return week8_stress_data

    groups = analysis_data["groups"]

    # 추출할 팀 목록을 정의합니다 (순서 중요)
    team_order = ["상담 1팀", "상담 2팀", "상담 3팀", "상담 4팀", "회사"]

    # 각 팀/그룹에 대해 8주차 스트레스 데이터를 추출합니다
    for team_name in team_order:
        # 팀 데이터가 존재하는지 확인합니다
        if team_name not in groups:
            print(f"경고: {team_name} 데이터를 찾을 수 없습니다.")
            continue

        team_data = groups[team_name]

        # 8주차 분석 데이터가 있는지 확인합니다
        if "analysis" not in team_data or "8주차" not in team_data["analysis"]:
            print(f"경고: {team_name}의 8주차 데이터를 찾을 수 없습니다.")
            continue

        week8_analysis = team_data["analysis"]["8주차"]

        # 각 지표별 점수를 추출합니다
        team_scores = {}

        # stress 총점을 category_averages에서 가져옵니다
        if (
            "category_averages" in week8_analysis
            and "stress" in week8_analysis["category_averages"]
        ):
            team_scores["총점"] = week8_analysis["category_averages"]["stress"]
        else:
            team_scores["총점"] = None
            print(f"경고: {team_name}의 stress 총점을 찾을 수 없습니다.")

        # type_averages에서 세부 점수들을 가져옵니다
        if "type_averages" in week8_analysis:
            type_averages = week8_analysis["type_averages"]

            # stress 세부 점수들을 추출합니다
            if "stress" in type_averages:
                stress_scores = type_averages["stress"]
                team_scores["직무 요구"] = stress_scores.get("직무 요구")
                team_scores["직무 자율"] = stress_scores.get("직무 자율")
                team_scores["관계 갈등"] = stress_scores.get("관계 갈등")
                team_scores["직무 불안"] = stress_scores.get("직무 불안")
                team_scores["조직 체계"] = stress_scores.get("조직 체계")
                team_scores["보상 부적절"] = stress_scores.get("보상 부적절")
                team_scores["직장 문화"] = stress_scores.get("직장 문화")
            else:
                print(f"경고: {team_name}의 stress 세부 데이터를 찾을 수 없습니다.")
                # 모든 세부 점수를 None으로 설정합니다
                team_scores["직무 요구"] = None
                team_scores["직무 자율"] = None
                team_scores["관계 갈등"] = None
                team_scores["직무 불안"] = None
                team_scores["조직 체계"] = None
                team_scores["보상 부적절"] = None
                team_scores["직장 문화"] = None
        else:
            print(f"경고: {team_name}의 type_averages 데이터를 찾을 수 없습니다.")
            # 모든 세부 점수를 None으로 설정합니다
            for key in [
                "직무 요구",
                "직무 자율",
                "관계 갈등",
                "직무 불안",
                "조직 체계",
                "보상 부적절",
                "직장 문화",
            ]:
                team_scores[key] = None

        # 팀 데이터를 결과 딕셔너리에 저장합니다
        week8_stress_data[team_name] = team_scores

    return week8_stress_data


def extract_week8_stress_risk_levels(analysis_data):
    """
    8주차 데이터에서 팀별 stress 위험 수준별 인원수를 추출하는 함수

    Args:
        analysis_data (dict): 분석 데이터

    Returns:
        dict: 팀별 8주차 stress 위험 수준별 인원수 데이터
    """
    # 결과를 저장할 딕셔너리를 초기화합니다
    risk_data = {}

    # groups 데이터가 있는지 확인합니다
    if "groups" not in analysis_data:
        print("오류: groups 데이터를 찾을 수 없습니다.")
        return risk_data

    groups = analysis_data["groups"]

    # 추출할 팀 목록을 정의합니다 (순서 중요)
    team_order = ["상담 1팀", "상담 2팀", "상담 3팀", "상담 4팀", "회사"]

    # 각 팀/그룹에 대해 8주차 위험 수준 데이터를 추출합니다
    for team_name in team_order:
        # 팀 데이터가 존재하는지 확인합니다
        if team_name not in groups:
            print(f"경고: {team_name} 데이터를 찾을 수 없습니다.")
            continue

        team_data = groups[team_name]

        # 8주차 분석 데이터가 있는지 확인합니다
        if "analysis" not in team_data or "8주차" not in team_data["analysis"]:
            print(f"경고: {team_name}의 8주차 데이터를 찾을 수 없습니다.")
            continue

        week8_analysis = team_data["analysis"]["8주차"]

        # risk_levels 데이터에서 stress 위험 수준별 인원수를 추출합니다
        team_risk = {}

        if (
            "risk_levels" in week8_analysis
            and "stress" in week8_analysis["risk_levels"]
        ):
            stress_risk = week8_analysis["risk_levels"]["stress"]

            # 각 위험 수준별 인원수를 추출합니다
            team_risk["정상"] = stress_risk.get("정상", 0)
            team_risk["준위험"] = stress_risk.get("준위험", 0)
            team_risk["위험"] = stress_risk.get("위험", 0)
        else:
            print(f"경고: {team_name}의 stress 위험 수준 데이터를 찾을 수 없습니다.")
            # 모든 위험 수준을 0으로 설정합니다
            team_risk["정상"] = 0
            team_risk["준위험"] = 0
            team_risk["위험"] = 0

        # 팀 데이터를 결과 딕셔너리에 저장합니다
        risk_data[team_name] = team_risk

    return risk_data


def format_score(score):
    """
    점수를 CSV 출력용으로 포맷팅하는 함수

    Args:
        score (float or None): 점수 값

    Returns:
        str: 포맷팅된 점수 문자열
    """
    # 점수가 None인 경우 빈 문자열을 반환합니다
    if score is None:
        return ""

    # 소수점 둘째 자리까지 반올림하여 반환합니다
    return f"{score:.2f}"


def print_stress_csv_table(week8_stress_data):
    """
    8주차 직무스트레스 데이터를 CSV 형식으로 출력하는 함수

    Args:
        week8_stress_data (dict): 팀별 8주차 직무스트레스 점수 데이터
    """
    # CSV 헤더를 정의합니다
    headers = [
        "",
        "직무 요구",
        "직무 자율",
        "관계 갈등",
        "직무 불안",
        "조직 체계",
        "보상 부적절",
        "직장 문화",
        "총점",
    ]

    # 헤더를 CSV 형식으로 출력합니다
    print(",".join(headers))

    # 팀 순서를 정의합니다
    team_order = ["상담 1팀", "상담 2팀", "상담 3팀", "상담 4팀", "회사"]

    # 각 팀의 데이터를 CSV 형식으로 출력합니다
    for team_name in team_order:
        # 팀 데이터가 존재하는지 확인합니다
        if team_name not in week8_stress_data:
            print(f"경고: {team_name} 데이터가 없습니다.")
            continue

        # 팀 이름을 표시용으로 변환합니다 (회사 -> 회사 전체)
        display_name = "회사 전체" if team_name == "회사" else team_name

        # 각 지표의 점수를 가져옵니다
        team_scores = week8_stress_data[team_name]

        # CSV 행을 구성합니다
        row = [
            display_name,
            format_score(team_scores.get("직무 요구")),
            format_score(team_scores.get("직무 자율")),
            format_score(team_scores.get("관계 갈등")),
            format_score(team_scores.get("직무 불안")),
            format_score(team_scores.get("조직 체계")),
            format_score(team_scores.get("보상 부적절")),
            format_score(team_scores.get("직장 문화")),
            format_score(team_scores.get("총점")),
        ]

        # CSV 행을 출력합니다
        print(",".join(row))


def print_stress_risk_levels_csv_table(risk_data):
    """
    8주차 stress 위험 수준별 인원수를 CSV 형식으로 출력하는 함수

    Args:
        risk_data (dict): 팀별 8주차 stress 위험 수준별 인원수 데이터
    """
    # CSV 헤더를 정의합니다
    headers = ["", "정상", "준위험", "위험"]

    # 헤더를 CSV 형식으로 출력합니다
    print(",".join(headers))

    # 팀 순서를 정의합니다
    team_order = ["상담 1팀", "상담 2팀", "상담 3팀", "상담 4팀", "회사"]

    # 각 팀의 위험 수준별 인원수를 CSV 형식으로 출력합니다
    for team_name in team_order:
        # 팀 데이터가 존재하는지 확인합니다
        if team_name not in risk_data:
            print(f"경고: {team_name} 위험 수준 데이터가 없습니다.")
            continue

        # 팀 이름을 표시용으로 변환합니다 (회사 -> 회사 전체)
        display_name = "회사 전체" if team_name == "회사" else team_name

        # 각 위험 수준별 인원수를 가져옵니다
        team_risk = risk_data[team_name]

        # CSV 행을 구성합니다
        row = [
            display_name,
            str(team_risk.get("정상", 0)),
            str(team_risk.get("준위험", 0)),
            str(team_risk.get("위험", 0)),
        ]

        # CSV 행을 출력합니다
        print(",".join(row))


def main():
    """
    메인 함수 - 스크립트의 진입점
    """
    print("=== 8주차 팀별 직무스트레스 점수 요약 (CSV 형식) ===\n")

    try:
        # 분석 데이터를 로드합니다
        analysis_data = load_analysis_data()

        # 8주차 스트레스 점수 데이터를 추출합니다
        print("8주차 직무스트레스 점수 데이터를 추출하는 중...")
        week8_stress_data = extract_week8_stress_data(analysis_data)

        # 8주차 스트레스 위험 수준 데이터를 추출합니다
        print("8주차 직무스트레스 위험 수준 데이터를 추출하는 중...")
        stress_risk_data = extract_week8_stress_risk_levels(analysis_data)

        # 추출된 데이터가 있는지 확인합니다
        if not week8_stress_data and not stress_risk_data:
            print("추출된 8주차 직무스트레스 데이터가 없습니다.")
            return

        # 직무스트레스 점수 표를 출력합니다
        if week8_stress_data:
            print(
                f"총 {len(week8_stress_data)}개 팀/그룹의 직무스트레스 점수 데이터를 추출했습니다.\n"
            )
            print("=== 직무스트레스 점수 CSV 형식 출력 ===")
            print_stress_csv_table(week8_stress_data)
            print()

        # 위험 수준별 인원수 표를 출력합니다
        if stress_risk_data:
            print(
                f"총 {len(stress_risk_data)}개 팀/그룹의 위험 수준 데이터를 추출했습니다.\n"
            )
            print("=== 직무스트레스 위험 수준별 인원수 CSV 형식 출력 ===")
            print_stress_risk_levels_csv_table(stress_risk_data)

    except Exception as e:
        # 예상치 못한 오류가 발생한 경우 오류 메시지를 출력합니다
        print(f"오류가 발생했습니다: {e}")
        import traceback

        traceback.print_exc()


# 스크립트가 직접 실행될 때 main 함수를 호출합니다
if __name__ == "__main__":
    main()
