#!/usr/bin/env python3
"""
T4 주차 앱 사용 횟수 분석기
각 참여자가 T4(6주차)에 앱을 몇 번이나 사용했는지 분석하는 스크립트

사용법:
    python t4_app_usage_counter.py
"""

import json  # JSON 파일을 읽기 위한 라이브러리
import os  # 파일 경로 처리를 위한 라이브러리
import csv  # CSV 파일 읽기를 위한 라이브러리
from typing import Dict, List  # 타입 힌트를 위한 모듈
from collections import defaultdict  # 딕셔너리 기본값 설정을 위한 모듈


def load_participants() -> Dict[str, str]:
    """
    참여자 CSV 파일에서 user_id와 식별 기호(P1, P2, ...)의 매핑을 로드합니다.

    Returns:
        Dict[str, str]: user_id를 키로, 식별 기호를 값으로 하는 딕셔너리
    """
    participants = {}  # 참여자 정보를 저장할 딕셔너리 초기화

    # 참여자 CSV 파일 경로 설정 (프로젝트 루트 기준)
    csv_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "csv", "participants.csv"
    )

    # CSV 파일을 열어서 참여자 정보 읽기
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)  # CSV를 딕셔너리 형태로 읽는 리더 생성
        for row in reader:  # 각 행에 대해 반복
            user_id = row["아이디"]  # 아이디 컬럼에서 user_id 추출
            participant_code = row["식별 기호"]  # 식별 기호 컬럼에서 참여자 코드 추출
            participants[user_id] = participant_code  # 딕셔너리에 매핑 저장

    return participants  # 참여자 매핑 딕셔너리 반환


def load_t4_app_analysis_data() -> List[Dict]:
    """
    T4(6주차) 앱 분석 JSON 파일에서 감정 기록 데이터를 로드합니다.

    Returns:
        List[Dict]: 감정 기록 리스트
    """
    # JSON 파일 경로 생성 (프로젝트 루트 기준)
    json_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "data",
        "analysis",
        "app_analysis_6주차.json",
    )

    # JSON 파일이 존재하는지 확인
    if not os.path.exists(json_path):
        print(
            f"경고: {json_path} 파일이 존재하지 않습니다."
        )  # 파일이 없으면 경고 메시지 출력
        return []  # 빈 리스트 반환

    # JSON 파일 로드
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)  # JSON 데이터를 파이썬 객체로 로드

    # emotion_records 키에서 감정 기록 데이터 추출하여 반환
    return data.get("emotion_records", [])


def analyze_t4_app_usage():
    """
    T4 주차의 감정 기록을 분석하여 각 참여자별 앱 사용 횟수를 계산합니다.
    """
    print("=== T4 주차 앱 사용 횟수 분석 ===\n")  # 분석 시작 메시지 출력

    # 참여자 매핑 정보 로드
    participants = load_participants()
    print(f"총 {len(participants)}명의 참여자 정보를 로드했습니다.\n")  # 참여자 수 출력

    # T4 주차 감정 기록 데이터 로드
    print("T4(6주차) 데이터 분석 중...")  # 분석 중 메시지 출력
    emotion_records = load_t4_app_analysis_data()
    print(
        f"  - {len(emotion_records)}개의 감정 기록 처리 완료\n"
    )  # 처리된 기록 수 출력

    # 참여자별 앱 사용 횟수를 저장할 딕셔너리
    usage_counts = defaultdict(int)

    # 각 감정 기록에 대해 분석
    for record in emotion_records:
        user_id = record.get("user_id")  # 사용자 ID 추출

        # 참여자 매핑에서 해당 사용자의 식별 기호 찾기
        participant_code = participants.get(user_id)

        # 참여자 매핑에 없는 사용자는 건너뛰기
        if not participant_code:
            continue

        # 해당 참여자의 앱 사용 횟수 증가 (감정 기록 1개 = 앱 사용 1회)
        usage_counts[participant_code] += 1

    print("=== T4 주차 앱 사용 횟수 결과 (CSV 형식) ===")  # 결과 출력 시작 메시지

    # CSV 헤더 출력
    print("Participant,T4_Usage_Count")

    # 참여자별로 자연수 순서로 정렬하여 결과 출력 (P1, P2, ..., P10, P11, ...)
    def sort_participant_key(participant_code):
        """참여자 코드에서 숫자 부분을 추출하여 정렬 키로 사용"""
        return int(participant_code[1:])  # P1 -> 1, P10 -> 10

    # 모든 참여자에 대해 사용 횟수 출력 (사용하지 않은 참여자는 0으로 표시)
    all_participants = set(participants.values())  # 모든 참여자 식별 기호 세트

    for participant_code in sorted(all_participants, key=sort_participant_key):
        usage_count = usage_counts[participant_code]  # 해당 참여자의 앱 사용 횟수

        # CSV 형식으로 출력
        print(f"{participant_code},{usage_count}")

    # 통계 정보 출력
    print(f"\n=== 통계 정보 ===")
    total_usage = sum(usage_counts.values())  # 총 앱 사용 횟수
    active_participants = len(
        [count for count in usage_counts.values() if count > 0]
    )  # 앱을 사용한 참여자 수
    print(f"총 앱 사용 횟수: {total_usage}")
    print(f"앱을 사용한 참여자 수: {active_participants}/{len(all_participants)}")
    if active_participants > 0:
        avg_usage = total_usage / active_participants  # 활성 참여자 평균 사용 횟수
        print(f"활성 참여자 평균 사용 횟수: {avg_usage:.2f}")


def main():
    """
    메인 함수: 스크립트의 진입점
    """
    try:
        analyze_t4_app_usage()  # T4 앱 사용 분석 실행
    except Exception as e:
        print(f"오류 발생: {e}")  # 오류가 발생하면 메시지 출력


if __name__ == "__main__":
    main()  # 스크립트가 직접 실행될 때 메인 함수 호출
