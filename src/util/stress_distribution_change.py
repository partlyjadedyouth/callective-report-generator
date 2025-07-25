#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
직무 스트레스 분포 변화 분석 스크립트

이 스크립트는 4주차와 8주차 사이에 직무 스트레스 점수의 분포 카테고리가
변경된 참가자(정상→준위험, 준위험→위험 등)를 식별하고,
그들의 이름, 소속 팀, 성별, 점수 변동량을 출력합니다.
"""

# 필요한 라이브러리 임포트
import json  # JSON 파일을 처리하기 위한 라이브러리
import os  # 파일 경로 관리를 위한 라이브러리
import sys  # 시스템 경로 관리를 위한 라이브러리

# 현재 스크립트의 절대 경로 획득
current_dir = os.path.dirname(os.path.abspath(__file__))
# 프로젝트 루트 디렉토리 경로 계산 (현재 파일이 src/util/에 있다고 가정)
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
# src 디렉토리 경로 계산
src_dir = os.path.join(project_root, "src")

# src 디렉토리를 Python 경로에 추가 (모듈 임포트를 위해)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 직무 스트레스 절단점 임포트 (성별에 따라 다른 절단점 사용)
from cutoff_values import CUTOFF_STRESS, CUTOFF_STRESS_MALE

# 참가자 ID 관리 모듈 임포트 (이제 동적 경로로 찾을 수 있음)
from participant_id_manager import generate_unique_id


def get_risk_level(score, gender):
    """
    직무 스트레스 점수와 성별에 따른 위험 수준 결정 함수

    Args:
        score (float): 직무 스트레스 점수
        gender (str): 성별 ('남성' 또는 '여성')

    Returns:
        str: '정상', '준위험', 또는 '위험' 분류
    """
    # 성별에 따라 적절한 절단점 선택
    if gender == "남성":
        cutoff_values = CUTOFF_STRESS_MALE  # 남성용 절단점 사용
    else:
        cutoff_values = CUTOFF_STRESS  # 여성용 절단점 사용 (기본값)

    # 점수에 따른 위험 수준 분류
    if score < cutoff_values[0]:  # 첫 번째 절단점보다 낮으면 정상
        return "정상"
    elif score < cutoff_values[1]:  # 두 번째 절단점보다 낮으면 준위험
        return "준위험"
    else:  # 그 외는 위험
        return "위험"


def find_analysis_file():
    """
    analysis.json 파일의 경로를 동적으로 찾는 함수

    Returns:
        str: analysis.json 파일의 절대 경로

    Raises:
        FileNotFoundError: 파일을 찾을 수 없는 경우
    """
    # 가능한 경로들을 순서대로 확인
    possible_paths = [
        os.path.join(
            project_root, "data", "analysis", "analysis.json"
        ),  # 프로젝트 루트 기준
        os.path.join(
            current_dir, "..", "..", "data", "analysis", "analysis.json"
        ),  # 현재 파일 기준
        os.path.join(
            os.getcwd(), "data", "analysis", "analysis.json"
        ),  # 작업 디렉토리 기준
        "data/analysis/analysis.json",  # 상대 경로
    ]

    # 각 경로를 확인하여 파일이 존재하는지 검사
    for path in possible_paths:
        if os.path.exists(path):
            return path

    # 파일을 찾지 못한 경우 오류 발생
    raise FileNotFoundError(
        f"analysis.json 파일을 찾을 수 없습니다. 다음 경로들을 확인했습니다:\n"
        + "\n".join(f"  - {path}" for path in possible_paths)
    )


def main():
    """
    메인 함수: 데이터 로드, 분석 및 결과 출력
    """
    try:
        # 분석 파일 경로를 동적으로 찾기
        analysis_file = find_analysis_file()
        print(f"분석 파일 경로: {analysis_file}")  # 디버깅을 위한 경로 출력

    except FileNotFoundError as e:
        # 파일을 찾지 못한 경우 오류 메시지 출력 후 종료
        print(f"오류: {e}")
        return

    # JSON 파일 로드
    with open(analysis_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 분류 변경된 참가자 추적을 위한 리스트
    changed_participants = []

    # 참가자 ID 목록 생성 (동명이인 처리용)
    participant_ids = {}  # {unique_id: participant_info}

    # 각 참가자 순회
    for participant in data["participants"]:
        name = participant["name"]  # 참가자 이름
        team = participant["team"]  # 참가자 팀
        gender = participant.get("gender", "여성")  # 참가자 성별 (기본값: 여성)

        # 고유 ID 생성
        unique_id = generate_unique_id(name, team)

        # 참가자 정보를 고유 ID로 저장
        participant_ids[unique_id] = participant

        analysis = participant["analysis"]  # 참가자 분석 데이터

        # 4주차와 8주차 데이터가 모두 있는지 확인
        if "4주차" in analysis and "8주차" in analysis:
            # 4주차와 8주차의 직무 스트레스 점수 추출
            score_week4 = analysis["4주차"]["category_averages"].get("stress")
            score_week8 = analysis["8주차"]["category_averages"].get("stress")

            # 두 점수 모두 있는지 확인 (null이 아닌지 확인)
            if score_week4 is not None and score_week8 is not None:
                # 위험 수준 결정 (성별 고려)
                risk_level_week4 = get_risk_level(score_week4, gender)
                risk_level_week8 = get_risk_level(score_week8, gender)

                # 위험 수준이 변경되었는지 확인
                if risk_level_week4 != risk_level_week8:
                    # 변동량 계산
                    score_change = score_week8 - score_week4

                    # 결과 추가
                    changed_participants.append(
                        {
                            "name": name,
                            "team": team,  # 팀 정보 추가
                            "gender": gender,  # 성별 정보 추가
                            "unique_id": unique_id,  # 고유 ID 추가
                            "week4_score": score_week4,
                            "week8_score": score_week8,
                            "score_change": score_change,
                            "week4_risk_level": risk_level_week4,
                            "week8_risk_level": risk_level_week8,
                        }
                    )

    # 팀 기준으로 오름차순 정렬
    changed_participants.sort(key=lambda p: p["team"])

    # 결과 출력
    print(
        f"총 {len(changed_participants)}명의 참가자가 직무 스트레스 위험 수준 변화를 보였습니다.\n"
    )

    # 헤더 형식 정의 (성별 컬럼 추가)
    header_format = "{:<10} {:<12} {:<6} {:<12} {:<12} {:<12} {:<12} {:<12}"
    data_format = "{:<10} {:<12} {:<6} {:<12.2f} {:<12.2f} {:<12} {:<12} {:<12}"

    # 헤더 출력
    print(
        header_format.format(
            "이름",
            "소속 팀",
            "성별",
            "4주차 점수",
            "8주차 점수",
            "변동량",
            "4주차 분류",
            "8주차 분류",
        )
    )
    print("-" * 90)

    # 각 변경된 참가자의 세부 정보 출력
    for p in changed_participants:
        # 변동량 방향에 따라 '+' 기호 표시
        change_str = (
            f"+{p['score_change']:.2f}"
            if p["score_change"] > 0
            else f"{p['score_change']:.2f}"
        )

        print(
            data_format.format(
                p["name"],
                p["team"],
                p["gender"],
                p["week4_score"],
                p["week8_score"],
                change_str,
                p["week4_risk_level"],
                p["week8_risk_level"],
            )
        )

    # 성별별 통계 추가 출력
    print("\n" + "=" * 90)
    print("성별별 변화 통계:")
    print("-" * 90)

    # 성별별 그룹화
    male_participants = [p for p in changed_participants if p["gender"] == "남성"]
    female_participants = [p for p in changed_participants if p["gender"] == "여성"]

    print(f"남성: {len(male_participants)}명")
    print(f"여성: {len(female_participants)}명")

    # 변화 방향별 통계
    print("\n변화 방향별 통계:")
    print("-" * 90)

    # 위험도 증가/감소 통계
    risk_increased = [p for p in changed_participants if p["score_change"] > 0]
    risk_decreased = [p for p in changed_participants if p["score_change"] < 0]

    print(f"스트레스 증가: {len(risk_increased)}명")
    print(f"스트레스 감소: {len(risk_decreased)}명")


if __name__ == "__main__":
    main()
