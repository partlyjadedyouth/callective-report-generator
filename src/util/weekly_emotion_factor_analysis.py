#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weekly Emotion Factor Analysis Script
6주차 앱 분석 데이터를 기반으로 요일별 감정 요인 분석표를 생성하는 스크립트
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple


def load_app_analysis_data(file_path: str) -> Dict:
    """
    앱 분석 JSON 파일을 로드하는 함수

    Args:
        file_path (str): JSON 파일 경로

    Returns:
        Dict: 로드된 JSON 데이터
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_weekday_korean(date_str: str) -> str:
    """
    날짜 문자열을 받아서 한국어 요일을 반환하는 함수

    Args:
        date_str (str): YYYY-MM-DD 형식의 날짜 문자열

    Returns:
        str: 한국어 요일 (월요일, 화요일, 수요일, 목요일, 금요일)
    """
    # 날짜 문자열을 datetime 객체로 변환
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    # 요일 매핑 (Monday=0, Sunday=6)
    weekday_map = {
        0: "월요일",  # Monday
        1: "화요일",  # Tuesday
        2: "수요일",  # Wednesday
        3: "목요일",  # Thursday
        4: "금요일",  # Friday
        5: "토요일",  # Saturday
        6: "일요일",  # Sunday
    }

    return weekday_map[date_obj.weekday()]


def classify_emotion_type(emotion: str) -> str:
    """
    감정을 긍정/부정으로 분류하는 함수

    Args:
        emotion (str): 감정 상태

    Returns:
        str: '긍정' 또는 '부정'
    """
    # 긍정적인 감정들
    positive_emotions = [
        "행복해요",
        "차분해요",
        "기뻐요",
        "만족해요",
        "편안해요",
        "신나요",
    ]

    # 부정적인 감정들
    negative_emotions = [
        "우울해요",
        "화가나요",
        "불안해요",
        "슬퍼요",
        "짜증나요",
        "스트레스받아요",
        "피곤해요",
    ]

    if emotion in positive_emotions:
        return "긍정"
    elif emotion in negative_emotions:
        return "부정"
    else:
        return "부정"  # 기본값은 부정으로 분류


def analyze_emotion_factors_by_weekday(data: Dict) -> pd.DataFrame:
    """
    요일별 감정 요인을 분석하여 데이터프레임을 생성하는 함수

    Args:
        data (Dict): 앱 분석 JSON 데이터

    Returns:
        pd.DataFrame: 요일별 감정 요인 분석 결과 테이블
    """
    # 결과를 저장할 딕셔너리 초기화
    weekday_analysis = {
        "월요일": {},
        "화요일": {},
        "수요일": {},
        "목요일": {},
        "금요일": {},
    }

    # 모든 가능한 요인들과 감정 타입 조합
    factors = [
        "업무_외_요인",
        "잘_모르겠음",
        "대인_관계",
        "업무량",
        "업무_처리_능력",
        "고객과의_관계",
    ]
    emotion_types = ["긍정", "부정"]

    # 각 요일별로 초기화
    for weekday in weekday_analysis.keys():
        for emotion_type in emotion_types:
            for factor in factors:
                column_name = f"{emotion_type}_{factor}"
                weekday_analysis[weekday][column_name] = 0
        weekday_analysis[weekday]["합계"] = 0

    # emotion_records 데이터를 순회하면서 분석
    for record in data["emotion_records"]:
        date = record["date"]
        emotion = record["emotion"]
        factors_list = record["factors"]

        # 날짜에서 요일 추출
        weekday = get_weekday_korean(date)

        # 주중(월~금)만 처리
        if weekday not in weekday_analysis:
            continue

        # 감정 타입 분류
        emotion_type = classify_emotion_type(emotion)

        # 각 요인에 대해 카운트 증가
        for factor in factors_list:
            # 요인명을 컬럼명 형식으로 변환
            factor_clean = factor.replace(" ", "_")
            column_name = f"{emotion_type}_{factor_clean}"

            if column_name in weekday_analysis[weekday]:
                weekday_analysis[weekday][column_name] += 1

            # 전체 레코드 수 증가
            weekday_analysis[weekday]["합계"] += 1

    # 데이터프레임으로 변환
    df = pd.DataFrame.from_dict(weekday_analysis, orient="index")

    # 컬럼 순서 정렬
    column_order = [
        "긍정_업무_외_요인",
        "긍정_잘_모르겠음",
        "긍정_대인_관계",
        "긍정_업무량",
        "긍정_업무_처리_능력",
        "긍정_고객과의_관계",
        "부정_업무량",
        "부정_잘_모르겠음",
        "부정_업무_외_요인",
        "부정_대인_관계",
        "부정_업무_처리_능력",
        "부정_고객과의_관계",
        "합계",
    ]

    # 존재하는 컬럼만 선택
    available_columns = [col for col in column_order if col in df.columns]
    df = df[available_columns]

    # 요일 컬럼 추가
    df.reset_index(inplace=True)
    df.rename(columns={"index": "요일"}, inplace=True)

    return df


def main():
    """
    메인 실행 함수
    """
    # 데이터 파일 경로
    data_file = "data/analysis/app_analysis_10주차.json"

    try:
        # JSON 데이터 로드
        print("8주차 앱 분석 데이터를 로딩 중...")
        data = load_app_analysis_data(data_file)
        print(f"총 {len(data['emotion_records'])}개의 감정 기록을 발견했습니다.")

        # 요일별 감정 요인 분석
        print("요일별 감정 요인 분석을 수행 중...")
        analysis_df = analyze_emotion_factors_by_weekday(data)

        # 결과를 CSV 형식으로 출력
        print("\n=== 요일별 감정 요인 분석 결과 (CSV 형식) ===")
        print(analysis_df.to_csv(index=False, encoding="utf-8"))

    except FileNotFoundError:
        print(f"오류: {data_file} 파일을 찾을 수 없습니다.")
    except json.JSONDecodeError:
        print(f"오류: {data_file} 파일의 JSON 형식이 올바르지 않습니다.")
    except Exception as e:
        print(f"오류 발생: {str(e)}")


if __name__ == "__main__":
    main()
