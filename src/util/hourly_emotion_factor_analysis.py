#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hourly Emotion Factor Analysis Script
6주차 앱 분석 데이터를 기반으로 시간대별 감정 요인 분석표를 생성하는 스크립트
"""

import json
import pandas as pd
from typing import Dict


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


def analyze_emotion_factors_by_time_range(data: Dict) -> pd.DataFrame:
    """
    시간대별 감정 요인을 분석하여 데이터프레임을 생성하는 함수

    Args:
        data (Dict): 앱 분석 JSON 데이터

    Returns:
        pd.DataFrame: 시간대별 감정 요인 분석 결과 테이블
    """
    # 분석할 시간대 정의 (업무 시간 중심으로)
    target_time_ranges = [
        "08:00-10:30",
        "10:30-12:00",
        "12:00-13:30",
        "13:30-15:00",
        "15:00-16:30",
        "16:30-19:00",
    ]

    # 결과를 저장할 딕셔너리 초기화
    time_analysis = {}

    # 모든 가능한 요인들
    factors = [
        "업무 외 요인",
        "잘 모르겠음",
        "대인 관계",
        "업무량",
        "업무 처리 능력",
        "고객과의 관계",
    ]

    # time_range_detailed_emotions 데이터에서 분석
    time_range_data = data.get("time_range_detailed_emotions", {})

    for time_range in target_time_ranges:
        # 각 시간대별 데이터 초기화
        time_analysis[time_range] = {}

        # 모든 요인에 대해 긍정/부정 카운트 초기화
        for factor in factors:
            factor_clean = factor.replace(" ", "_")
            time_analysis[time_range][f"긍정_{factor_clean}"] = 0
            time_analysis[time_range][f"부정_{factor_clean}"] = 0

        # 해당 시간대 데이터가 존재하는 경우 처리
        if time_range in time_range_data:
            range_data = time_range_data[time_range]

            # 긍정 감정 요인 처리
            if "positive" in range_data and "factors" in range_data["positive"]:
                positive_factors = range_data["positive"]["factors"]
                for factor, count in positive_factors.items():
                    factor_clean = factor.replace(" ", "_")
                    column_name = f"긍정_{factor_clean}"
                    if column_name in time_analysis[time_range]:
                        time_analysis[time_range][column_name] = count

            # 부정 감정 요인 처리
            if "negative" in range_data and "factors" in range_data["negative"]:
                negative_factors = range_data["negative"]["factors"]
                for factor, count in negative_factors.items():
                    factor_clean = factor.replace(" ", "_")
                    column_name = f"부정_{factor_clean}"
                    if column_name in time_analysis[time_range]:
                        time_analysis[time_range][column_name] = count

        # 각 시간대별 총합 계산
        total_count = sum(time_analysis[time_range].values())
        time_analysis[time_range]["합계"] = total_count

    # 데이터프레임으로 변환
    df = pd.DataFrame.from_dict(time_analysis, orient="index")

    # 컬럼 순서 정렬 (요청된 순서에 맞춰)
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

    # 시간대 컬럼 추가
    df.reset_index(inplace=True)
    df.rename(columns={"index": "시간대"}, inplace=True)

    return df


def main():
    """
    메인 실행 함수
    """
    # 데이터 파일 경로
    data_file = "data/analysis/app_analysis_6주차.json"

    try:
        # JSON 데이터 로드
        print("6주차 앱 분석 데이터를 로딩 중...")
        data = load_app_analysis_data(data_file)

        # 시간대별 감정 요인 분석
        print("시간대별 감정 요인 분석을 수행 중...")
        analysis_df = analyze_emotion_factors_by_time_range(data)

        # 결과를 CSV 형식으로 출력
        print("\n=== 시간대별 감정 요인 분석 결과 (CSV 형식) ===")
        print(analysis_df.to_csv(index=False, encoding="utf-8"))

    except FileNotFoundError:
        print(f"오류: {data_file} 파일을 찾을 수 없습니다.")
    except json.JSONDecodeError:
        print(f"오류: {data_file} 파일의 JSON 형식이 올바르지 않습니다.")
    except Exception as e:
        print(f"오류 발생: {str(e)}")


if __name__ == "__main__":
    main()
