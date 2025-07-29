#!/usr/bin/env python3
"""
상세 감정별 기록 횟수 분석기
각 참여자가 매주 특정 감정(신나요, 행복해요, 만족스러워요 등)을 몇 번이나 기록했는지 분석하는 스크립트

사용법:
    python detailed_emotion_counter.py
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


def classify_emotion_detailed(emotion: str) -> str:
    """
    감정을 상세 카테고리로 분류합니다.

    Args:
        emotion (str): 감정 문자열 (예: "행복해요", "우울해요")

    Returns:
        str: 감정 카테고리 키 (예: "P_Happy", "N_Depressed")
    """
    # 감정과 카테고리 매핑 딕셔너리
    emotion_mapping = {
        "신나요": "P_Excited",  # 긍정 - 신남
        "행복해요": "P_Happy",  # 긍정 - 행복
        "만족스러워요": "P_Satisfied",  # 긍정 - 만족
        "차분해요": "P_Calm",  # 긍정 - 차분
        "우울해요": "N_Depressed",  # 부정 - 우울
        "슬퍼요": "N_Sad",  # 부정 - 슬픔
        "불안해요": "N_Anxious",  # 부정 - 불안
        "화가나요": "N_Angry",  # 부정 - 화남
    }

    # 매핑에서 해당 감정의 카테고리 반환, 없으면 None 반환
    return emotion_mapping.get(emotion, None)


def get_week_code(week_number: int) -> str:
    """
    주차 번호를 주차 코드로 변환합니다.

    Args:
        week_number (int): 주차 번호 (0, 2, 4, 6)

    Returns:
        str: 주차 코드 (T1, T2, T3, T4)
    """
    # 주차 번호와 코드 매핑 딕셔너리
    week_mapping = {
        0: "T1",  # 0주차 -> T1
        2: "T2",  # 2주차 -> T2
        4: "T3",  # 4주차 -> T3
        6: "T4",  # 6주차 -> T4
        8: "T5",  # 8주차 -> T5 (추가 주차)
        10: "T6",  # 10주차 -> T6 (추가 주차)
        12: "T7",  # 12주차 -> T7 (추가 주차)
    }
    return week_mapping.get(
        week_number, f"T{week_number//2 + 1}"
    )  # 매핑에 없으면 계산으로 처리


def load_app_analysis_data(week: int) -> List[Dict]:
    """
    특정 주차의 앱 분석 JSON 파일에서 감정 기록 데이터를 로드합니다.

    Args:
        week (int): 주차 번호 (0, 2, 4, 6)

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
        f"app_analysis_{week}주차.json",
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


def initialize_emotion_counts() -> Dict[str, int]:
    """
    감정 카운트를 위한 초기 딕셔너리를 생성합니다.

    Returns:
        Dict[str, int]: 모든 감정 카테고리가 0으로 초기화된 딕셔너리
    """
    return {
        "P_Excited": 0,  # 긍정 - 신남
        "P_Happy": 0,  # 긍정 - 행복
        "P_Satisfied": 0,  # 긍정 - 만족
        "P_Calm": 0,  # 긍정 - 차분
        "N_Depressed": 0,  # 부정 - 우울
        "N_Sad": 0,  # 부정 - 슬픔
        "N_Anxious": 0,  # 부정 - 불안
        "N_Angry": 0,  # 부정 - 화남
    }


def analyze_detailed_emotions():
    """
    모든 주차의 감정 기록을 분석하여 각 참여자별 상세 감정 기록 횟수를 계산합니다.
    """
    print("=== 상세 감정별 기록 횟수 분석 ===\n")  # 분석 시작 메시지 출력

    # 참여자 매핑 정보 로드
    participants = load_participants()
    print(f"총 {len(participants)}명의 참여자 정보를 로드했습니다.\n")  # 참여자 수 출력

    # 결과를 저장할 딕셔너리 (participant_code -> week_code -> emotion_counts)
    results = defaultdict(lambda: defaultdict(initialize_emotion_counts))

    # 분석할 주차 리스트
    weeks = [0, 2, 4, 6, 8, 10, 12]  # 주차 번호 리스트 (0, 2, 4, 6, 8, 10, 12)

    # 각 주차별로 분석 수행
    for week in weeks:
        week_code = get_week_code(week)  # 주차 코드 생성
        print(f"{week}주차 ({week_code}) 데이터 분석 중...")  # 현재 분석 중인 주차 출력

        # 해당 주차의 감정 기록 데이터 로드
        emotion_records = load_app_analysis_data(week)

        # 각 감정 기록에 대해 분석
        for record in emotion_records:
            user_id = record.get("user_id")  # 사용자 ID 추출
            emotion = record.get("emotion")  # 감정 추출

            # 참여자 매핑에서 해당 사용자의 식별 기호 찾기
            participant_code = participants.get(user_id)

            # 참여자 매핑에 없는 사용자는 건너뛰기
            if not participant_code:
                continue

            # 감정을 상세 카테고리로 분류
            emotion_category = classify_emotion_detailed(emotion)

            # 분류되지 않은 감정은 건너뛰기
            if not emotion_category:
                continue

            # 해당 참여자의 해당 주차 해당 감정 카운트 증가
            results[participant_code][week_code][emotion_category] += 1

        print(
            f"  - {len(emotion_records)}개의 감정 기록 처리 완료"
        )  # 처리된 기록 수 출력

    print("\n=== 분석 결과 (CSV 형식) ===")  # 결과 출력 시작 메시지

    # CSV 헤더 출력
    print(
        "Participant,Week,P_Excited,P_Happy,P_Satisfied,P_Calm,N_Depressed,N_Sad,N_Anxious,N_Angry"
    )

    # 참여자별로 자연수 순서로 정렬하여 결과 출력 (P1, P2, ..., P10, P11, ...)
    def sort_participant_key(participant_code):
        """참여자 코드에서 숫자 부분을 추출하여 정렬 키로 사용"""
        return int(participant_code[1:])  # P1 -> 1, P10 -> 10

    for participant_code in sorted(results.keys(), key=sort_participant_key):
        # 각 주차별로 결과 출력
        for week_code in [f"T{week//2 + 1}" for week in weeks]:
            emotion_counts = results[participant_code][
                week_code
            ]  # 해당 주차의 감정 카운트

            # CSV 형식으로 한 줄 출력 (참여자, 주차, 각 감정별 카운트)
            print(
                f"{participant_code},{week_code},"
                f"{emotion_counts['P_Excited']},"
                f"{emotion_counts['P_Happy']},"
                f"{emotion_counts['P_Satisfied']},"
                f"{emotion_counts['P_Calm']},"
                f"{emotion_counts['N_Depressed']},"
                f"{emotion_counts['N_Sad']},"
                f"{emotion_counts['N_Anxious']},"
                f"{emotion_counts['N_Angry']}"
            )


def main():
    """
    메인 함수: 스크립트의 진입점
    """
    try:
        analyze_detailed_emotions()  # 상세 감정 분석 실행
    except Exception as e:
        print(f"오류 발생: {e}")  # 오류가 발생하면 메시지 출력


if __name__ == "__main__":
    main()  # 스크립트가 직접 실행될 때 메인 함수 호출
