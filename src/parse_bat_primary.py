#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BAT Primary Results Parser

This script parses CSV data exported from Google Sheets containing BAT primary questionnaire responses
and generates a structured JSON file with the scores calculated based on the questionnaire definitions.
"""

# 필요한 라이브러리 가져오기
import pandas as pd  # 데이터프레임 처리를 위한 pandas 라이브러리
import json  # JSON 파일 처리를 위한 라이브러리
import os  # 파일 및 디렉토리 조작을 위한 라이브러리
from datetime import datetime  # 날짜 및 시간 처리를 위한 라이브러리


def parse_bat_primary_results(
    csv_path, questionnaire_path, output_dir="data/results", date_suffix=None
):
    """
    Parse BAT primary questionnaire results from CSV and generate a JSON file with calculated scores.

    Args:
        csv_path (str): Path to the CSV file containing questionnaire responses
        questionnaire_path (str): Path to the JSON file containing BAT primary questionnaire definitions
        output_dir (str): Directory to save the results JSON file
        date_suffix (str): Date suffix for the output filename. If None, today's date is used.

    Returns:
        str: Path to the generated results file, or None if an error occurred
    """
    try:
        # 날짜 접미사가 제공되지 않은 경우 오늘 날짜 사용
        if date_suffix is None:  # 날짜 접미사가 없는 경우
            date_suffix = datetime.now().strftime(
                "%Y%m%d"
            )  # 오늘 날짜를 YYYYMMDD 형식으로 포맷

        # 결과 저장 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)  # 출력 디렉토리가 없으면 생성

        # CSV 파일 로드
        # 인코딩은 UTF-8로 설정하여 한글이 깨지지 않도록 함
        print(f"Loading CSV data from: {csv_path}")  # 로드 중인 CSV 파일 경로 출력
        df = pd.read_csv(
            csv_path, encoding="utf-8"
        )  # CSV 파일을 판다스 데이터프레임으로 로드

        # BAT 프라이머리 설문지 JSON 데이터 로드
        print(
            f"Loading questionnaire definition from: {questionnaire_path}"
        )  # 로드 중인 설문지 정의 파일 경로 출력
        with open(
            questionnaire_path, "r", encoding="utf-8"
        ) as f:  # 설문지 JSON 파일 열기
            bat_primary_data = json.load(f)  # JSON 데이터 로드

        # BAT 프라이머리 질문 수 확인 (JSON에서)
        num_primary_questions = len(
            bat_primary_data["BAT-primary"]
        )  # 설문지에서 질문 수 계산

        # BAT 프라이머리 질문 열 이름 매핑 (CSV에서)
        # 인덱스 6부터 시작하는 이유는 타임스탬프, 성명 등의 기본 정보가 앞에 있기 때문
        primary_cols = df.columns[
            6 : 6 + num_primary_questions
        ]  # CSV에서 질문 열 이름 추출

        # 각 응답자에 대한 JSON 생성
        result_list = []  # 결과를 저장할 빈 리스트 생성

        # 각 행(응답자)에 대해 처리
        print(f"Processing {len(df)} responses...")  # 처리 중인 응답 수 출력
        for _, row in df.iterrows():  # 각 행(응답자)에 대해 반복
            # 기본 정보 추출
            person_data = {  # 개인 데이터 딕셔너리 생성
                "name": (
                    row["성명"].strip() if pd.notna(row["성명"]) else ""
                ),  # 이름(공백 제거 및 NaN 처리)
                "team": row["소속"] if pd.notna(row["소속"]) else "",  # 소속팀
                "role": row["직무"] if pd.notna(row["직무"]) else "",  # 직무
                "scores": {},  # 점수를 저장할 빈 딕셔너리
            }

            # 각 질문에 대한 점수 계산
            for i, col in enumerate(primary_cols):  # 각 질문 열에 대해 반복
                # 질문 번호 계산 (1부터 시작)
                q_num = i + 1  # 질문 번호 계산
                q_key = f"Q{q_num}"  # 질문 키 생성 (Q1, Q2, ...)

                # JSON에서 해당 질문의 점수 매핑 가져오기
                score_mapping = bat_primary_data["BAT-primary"][q_key][
                    "scores"
                ]  # 질문에 대한 점수 매핑 가져오기

                # 응답에 해당하는 점수 추출
                response = row[col]  # 응답 값 가져오기

                # NaN 응답 처리
                if pd.isna(response):  # 응답이 NaN인 경우
                    score = 0  # 점수를 0으로 설정
                else:
                    # 응답에 해당하는 점수 찾기, 매핑이 없으면 0 반환
                    score = score_mapping.get(
                        str(response), 0
                    )  # 응답에 해당하는 점수 가져오기

                # 점수 저장
                person_data["scores"][q_key] = score  # 점수를 개인 데이터에 저장

            # 결과 리스트에 추가
            result_list.append(person_data)  # 개인 데이터를 결과 리스트에 추가

        # 전체 결과를 하나의 JSON 파일로 저장
        output_file = f"{output_dir}/bat_primary_results_{date_suffix}.json"  # 출력 파일 경로 생성

        print(f"Saving results to: {output_file}")  # 저장 중인 출력 파일 경로 출력
        with open(output_file, "w", encoding="utf-8") as f:  # JSON 파일 열기
            json.dump(
                result_list, f, ensure_ascii=False, indent=2
            )  # 결과를 JSON 형식으로 저장

        print(
            f"BAT 프라이머리 설문지 결과가 '{output_file}'에 저장되었습니다."
        )  # 성공 메시지 출력
        return output_file  # 출력 파일 경로 반환

    except Exception as e:  # 예외 처리
        print(f"Error processing BAT primary results: {e}")  # 오류 메시지 출력
        return None  # 오류 발생 시 None 반환


# 스크립트가 직접 실행될 때 실행되는 코드
if __name__ == "__main__":
    # 오늘 날짜 형식
    today = datetime.now().strftime("%Y%m%d")  # 오늘 날짜를 YYYYMMDD 형식으로 포맷

    # 기본 파일 경로 설정
    csv_file_path = f"data/csv/google_sheet_export_{today}.csv"  # CSV 파일 경로
    bat_primary_json_path = (
        "data/questionnaires/bat_primary_questionnaires.json"  # 설문지 정의 파일 경로
    )

    # 함수 직접 호출
    parse_bat_primary_results(
        csv_path=csv_file_path, questionnaire_path=bat_primary_json_path
    )  # parse_bat_primary_results 함수 호출
