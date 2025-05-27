#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BAT Primary 분포 변화 분석 스크립트

이 스크립트는 0주차와 2주차 사이에 BAT Primary 점수의 분포 카테고리가
변경된 참가자(정상→준위험, 준위험→위험 등)를 식별하고,
그들의 이름, 소속 팀, 점수 변동량을 출력합니다.
"""

# 필요한 라이브러리 임포트
import json  # JSON 파일을 처리하기 위한 라이브러리
import os  # 파일 경로 관리를 위한 라이브러리
from cutoff_values import CUTOFF_BURNOUT_PRIMARY  # 번아웃 절단점 임포트

# 참가자 ID 관리 모듈 임포트
from participant_id_manager import generate_unique_id


def get_risk_level(score):
    """
    BAT Primary 점수에 따른 위험 수준 결정 함수

    Args:
        score (float): BAT Primary 점수

    Returns:
        str: '정상', '준위험', 또는 '위험' 분류
    """
    if score < CUTOFF_BURNOUT_PRIMARY[0]:  # 첫 번째 절단점보다 낮으면 정상
        return "정상"
    elif score < CUTOFF_BURNOUT_PRIMARY[1]:  # 두 번째 절단점보다 낮으면 준위험
        return "준위험"
    else:  # 그 외는 위험
        return "위험"


def main():
    """
    메인 함수: 데이터 로드, 분석 및 결과 출력
    """
    # 분석 파일 경로
    analysis_file = "data/analysis/analysis.json"

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

        # 고유 ID 생성
        unique_id = generate_unique_id(name, team)

        # 참가자 정보를 고유 ID로 저장
        participant_ids[unique_id] = participant

        analysis = participant["analysis"]  # 참가자 분석 데이터

        # 0주차와 2주차 데이터가 모두 있는지 확인
        if "0주차" in analysis and "2주차" in analysis:
            # 0주차와 2주차의 BAT Primary 점수 추출
            score_week0 = analysis["0주차"]["category_averages"].get("BAT_primary")
            score_week2 = analysis["2주차"]["category_averages"].get("BAT_primary")

            # 두 점수 모두 있는지 확인
            if score_week0 is not None and score_week2 is not None:
                # 위험 수준 결정
                risk_level_week0 = get_risk_level(score_week0)
                risk_level_week2 = get_risk_level(score_week2)

                # 위험 수준이 변경되었는지 확인
                if risk_level_week0 != risk_level_week2:
                    # 변동량 계산
                    score_change = score_week2 - score_week0

                    # 결과 추가
                    changed_participants.append(
                        {
                            "name": name,
                            "team": team,  # 팀 정보 추가
                            "unique_id": unique_id,  # 고유 ID 추가
                            "week0_score": score_week0,
                            "week2_score": score_week2,
                            "score_change": score_change,
                            "week0_risk_level": risk_level_week0,
                            "week2_risk_level": risk_level_week2,
                        }
                    )

    # 팀 기준으로 오름차순 정렬
    changed_participants.sort(key=lambda p: p["team"])

    # 결과 출력
    print(
        f"총 {len(changed_participants)}명의 참가자가 BAT Primary 위험 수준 변화를 보였습니다.\n"
    )

    # 헤더 형식 정의
    header_format = "{:<10} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12}"
    data_format = "{:<10} {:<12} {:<12.2f} {:<12.2f} {:<12} {:<12} {:<12}"

    # 헤더 출력
    print(
        header_format.format(
            "이름",
            "소속 팀",
            "0주차 점수",
            "2주차 점수",
            "변동량",
            "0주차 분류",
            "2주차 분류",
        )
    )
    print("-" * 80)

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
                p["week0_score"],
                p["week2_score"],
                change_str,
                p["week0_risk_level"],
                p["week2_risk_level"],
            )
        )


if __name__ == "__main__":
    main()
