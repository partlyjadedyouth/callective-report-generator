#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
App Usage Data Analyzer

이 스크립트는 앱 사용 데이터를 분석하여 app_analysis.json 파일을 생성합니다:
1. data/csv 디렉토리에서 app_usage_data CSV 파일을 읽어들입니다
2. 참가자별로 데이터를 분류합니다
3. analysis.json과 유사한 형식으로 결과를 저장합니다 (성별 정보 제외)
4. 한글 필드 이름을 그대로 유지합니다
"""

# 필요한 라이브러리 가져오기
import os  # 운영 체제 기능을 위한 라이브러리
import json  # JSON 데이터 처리를 위한 라이브러리
import pandas as pd  # 데이터 분석을 위한 pandas 라이브러리
import statistics  # 통계 계산을 위한 라이브러리
from collections import defaultdict  # 기본값이 있는 딕셔너리 생성을 위한 라이브러리
from pathlib import Path  # 파일 경로 처리를 위한 라이브러리
import re  # 정규 표현식 처리를 위한 라이브러리


def analyze_app_usage(csv_dir="data/csv", output_dir="data/analysis"):
    """
    앱 사용 데이터를 분석하고 참가자별 통계를 생성합니다.

    Args:
        csv_dir (str): 앱 사용 데이터 CSV 파일이 있는 디렉토리
        output_dir (str): 분석 결과를 저장할 디렉토리

    Returns:
        str: 저장된 분석 파일 경로 또는 결과가 없는 경우 None
    """
    # 출력 디렉토리가 없는 경우 생성
    os.makedirs(output_dir, exist_ok=True)  # 디렉토리가 없으면 생성

    # 모든 참가자를 저장할 딕셔너리
    # 구조: { "name": { "name": "", "team": "", "role": "", "app_usage": { "0주차": {...} } } }
    all_participants = {}  # 모든 참가자 정보를 저장할 딕셔너리

    # CSV 디렉토리에서 app_usage_data 파일 찾기
    app_usage_files = list(
        Path(csv_dir).glob("app_usage_data_*.csv")
    )  # 앱 사용 데이터 CSV 파일 목록 가져오기

    if not app_usage_files:  # 파일이 없는 경우
        print("앱 사용 데이터 CSV 파일을 찾을 수 없습니다.")  # 오류 메시지 출력
        return None  # None 반환

    # 각 앱 사용 데이터 파일 처리
    for app_usage_file in app_usage_files:  # 각 파일에 대해
        # 파일명에서 주차 정보 추출 (예: "app_usage_data_0주차.csv" -> "0주차")
        week_suffix_match = re.search(
            r"app_usage_data_(.+?)\.csv", app_usage_file.name
        )  # 주차 정보 추출
        if week_suffix_match:  # 주차 정보가 있는 경우
            week_suffix = week_suffix_match.group(1)  # 주차 정보 추출
        else:  # 주차 정보가 없는 경우
            week_suffix = "unknown"  # 알 수 없음으로 설정

        # CSV 파일 읽기
        try:  # 파일 읽기 시도
            # 파일의 내용을 먼저 읽어서 헤더 구조 확인
            with open(app_usage_file, "r", encoding="utf-8") as f:  # 파일 열기
                lines = f.readlines()  # 모든 줄 읽기

            if len(lines) < 3:  # 파일이 비어있거나 너무 짧은 경우
                print(
                    f"{app_usage_file} 파일이 비어있거나 너무 짧습니다."
                )  # 오류 메시지 출력
                continue  # 다음 파일로 넘어가기

            # 두 번째 줄을 헤더로 사용 (첫 번째 줄은 큰 카테고리 헤더)
            header_line = lines[1].strip()  # 두 번째 줄을 헤더로 사용
            column_names = [
                col.strip() for col in header_line.split(",")
            ]  # 열 이름 추출

            # '날짜 / 시간' 열을 'datetime'으로 변경
            for i, name in enumerate(column_names):
                if name == "날짜 / 시간":
                    column_names[i] = "datetime"

            # CSV 파일 다시 읽기, 이번에는 두 번째 줄을 헤더로 사용하고 첫 두 줄은 건너뛰기
            df = pd.read_csv(
                app_usage_file,
                encoding="utf-8",
                header=None,  # 헤더 없음으로 읽기
                skiprows=2,  # 첫 두 줄 건너뛰기
                names=column_names,  # 직접 열 이름 지정
            )  # CSV 파일 읽기

            # NaN 값을 빈 문자열로 대체
            df = df.fillna("")  # NaN 값을 빈 문자열로 대체

        except Exception as e:  # 오류 발생 시
            print(f"{app_usage_file} 파일을 읽는 중 오류 발생: {e}")  # 오류 메시지 출력
            continue  # 다음 파일로 넘어가기

        # 데이터 처리
        # 각 참가자별로 데이터 그룹화
        for _, row in df.iterrows():  # 각 행에 대해
            # 기본 정보 추출
            name = row.get("성함", "Unknown")  # 이름 추출
            team = row.get("콜센터 업종 (팀 소속)", "Unknown")  # 팀 추출
            role = row.get("근무지 (직무)", "Unknown")  # 역할 추출

            # 참가자가 아직 없는 경우 추가
            if name not in all_participants:  # 참가자가 없는 경우
                all_participants[name] = {  # 참가자 정보 추가
                    "name": name,  # 이름
                    "team": team,  # 팀
                    "role": role,  # 역할
                    "app_usage": {},  # 앱 사용 데이터
                }

            # 참가자의 주차별 데이터 초기화
            if (
                week_suffix not in all_participants[name]["app_usage"]
            ):  # 주차 데이터가 없는 경우
                all_participants[name]["app_usage"][week_suffix] = (
                    {  # 주차 데이터 초기화
                        "records": [],  # 기록 목록
                        "category_averages": {},  # 카테고리 평균
                    }
                )

            # 앱 사용 데이터 레코드 생성
            record = {  # 레코드 생성
                "datetime": row.get("datetime", ""),  # 날짜/시간
                "수면": row.get("수면", ""),  # 수면
                "컨디션": row.get("컨디션", ""),  # 컨디션
                "기분": row.get("기분", ""),  # 기분
                "걱정": row.get("걱정", ""),  # 걱정
                "선택한 감정": row.get("선택한 감정", ""),  # 선택한 감정
                "선택한 요인": row.get("선택한 요인", ""),  # 선택한 요인
                "마음 기록 입력 내용 (텍스트)": row.get(
                    "마음 기록 입력 내용 (텍스트)", ""
                ),  # 마음 기록 내용
                "배터리 변동량 1": row.get("배터리 변동량 1", ""),  # 배터리 변동량 1
                "감정 기록 후 배터리 값": row.get(
                    "감정 기록 후 배터리 값", ""
                ),  # 감정 기록 후 배터리 값
                "중재 활동 이름": row.get("중재 활동 이름", ""),  # 중재 활동 이름
                "배터리 변동량 2": row.get("배터리 변동량 2", ""),  # 배터리 변동량 2
                "중재 활동 후 배터리 값": row.get(
                    "중재 활동 후 배터리 값", ""
                ),  # 중재 활동 후 배터리 값
            }

            # 레코드 추가
            all_participants[name]["app_usage"][week_suffix]["records"].append(
                record
            )  # 레코드 추가

        # 각 참가자의 주차별 평균 계산
        for name, participant in all_participants.items():  # 각 참가자에 대해
            if week_suffix in participant["app_usage"]:  # 주차 데이터가 있는 경우
                records = participant["app_usage"][week_suffix][
                    "records"
                ]  # 레코드 목록 가져오기

                # 수치형 필드들에 대한 평균 계산
                numeric_fields = [
                    "수면",
                    "컨디션",
                    "기분",
                    "걱정",
                    "배터리 변동량 1",
                    "감정 기록 후 배터리 값",
                    "배터리 변동량 2",
                    "중재 활동 후 배터리 값",
                ]  # 수치형 필드
                averages = {}  # 평균값 저장 딕셔너리

                for field in numeric_fields:  # 각 필드에 대해
                    values = []  # 값 목록 초기화
                    for record in records:  # 각 레코드에 대해
                        value = record[field]  # 값 가져오기
                        # 값이 비어있지 않고 NaN이 아닌 경우에만 추가
                        if (
                            value != "" and value != "nan" and not pd.isna(value)
                        ):  # 값이 있는 경우
                            try:  # 값 변환 시도
                                values.append(float(value))  # 값 추가
                            except (ValueError, TypeError):  # 변환 실패 시
                                pass  # 무시

                    if values:  # 값이 있는 경우
                        averages[field] = round(statistics.mean(values), 2)  # 평균 계산
                    else:  # 값이 없는 경우
                        averages[field] = None  # None으로 설정

                # 감정 및 요인 분포 계산
                emotion_counts = defaultdict(int)  # 감정 카운트
                factor_counts = defaultdict(int)  # 요인 카운트

                for record in records:  # 각 레코드에 대해
                    emotion = record["선택한 감정"]  # 감정 추출
                    factor = record["선택한 요인"]  # 요인 추출

                    if (
                        emotion and not pd.isna(emotion) and emotion != "nan"
                    ):  # 감정이 있는 경우
                        emotion_counts[emotion] += 1  # 감정 카운트 증가

                    if (
                        factor and not pd.isna(factor) and factor != "nan"
                    ):  # 요인이 있는 경우
                        # 쉼표로 분리된 요인 처리
                        if (
                            isinstance(factor, str) and "," in factor
                        ):  # 쉼표로 분리된 경우
                            for f in factor.split(","):  # 각 요인에 대해
                                f = f.strip()  # 공백 제거
                                if f:  # 요인이 있는 경우
                                    factor_counts[f] += 1  # 요인 카운트 증가
                        else:  # 단일 요인인 경우
                            factor_counts[factor] += 1  # 요인 카운트 증가

                # 중재 활동 분포 계산
                activity_counts = defaultdict(int)  # 활동 카운트
                activity_effects = defaultdict(list)  # 활동 효과

                for record in records:  # 각 레코드에 대해
                    activity = record["중재 활동 이름"]  # 활동 이름 추출
                    change = record["배터리 변동량 2"]  # 배터리 변동량 추출

                    if (
                        activity
                        and not pd.isna(activity)
                        and activity != "nan"
                        and change
                        and not pd.isna(change)
                        and change != "nan"
                    ):  # 활동과 변동량이 있는 경우
                        try:  # 값 변환 시도
                            float_change = float(change)  # 값 변환
                            activity_counts[activity] += 1  # 활동 카운트 증가
                            activity_effects[activity].append(
                                float_change
                            )  # 활동 효과 추가
                        except (ValueError, TypeError):  # 변환 실패 시
                            pass  # 무시

                # 평균, 분포 결과 저장
                participant["app_usage"][week_suffix][
                    "category_averages"
                ] = averages  # 평균 저장
                participant["app_usage"][week_suffix]["emotion_distribution"] = {
                    k: v for k, v in emotion_counts.items()
                }  # 감정 분포 저장
                participant["app_usage"][week_suffix]["factor_distribution"] = {
                    k: v for k, v in factor_counts.items()
                }  # 요인 분포 저장

                # 중재 활동 효과 저장
                activity_analysis = {}  # 활동 분석
                for activity, effects in activity_effects.items():  # 각 활동에 대해
                    activity_analysis[activity] = {  # 활동 분석 저장
                        "count": activity_counts[activity],  # 횟수
                        "avg_effect": (
                            round(statistics.mean(effects), 2) if effects else None
                        ),  # 평균 효과
                    }

                participant["app_usage"][week_suffix][
                    "activity_analysis"
                ] = activity_analysis  # 활동 분석 저장

    # 참가자 딕셔너리를 리스트로 변환
    participants_list = list(all_participants.values())  # 참가자 리스트 생성

    # 최종 분석 결과 생성
    final_analysis = {"participants": participants_list}  # 최종 분석 결과

    # 분석 결과를 JSON 파일로 저장
    output_file = os.path.join(output_dir, "app_analysis.json")  # 출력 파일 경로
    with open(output_file, "w", encoding="utf-8") as f:  # 파일 열기
        json.dump(final_analysis, f, ensure_ascii=False, indent=2)  # JSON으로 저장

    print(
        f"앱 사용 데이터 분석이 완료되었고 {output_file}에 저장되었습니다"
    )  # 성공 메시지 출력
    return output_file  # 파일 경로 반환


if __name__ == "__main__":
    """
    스크립트가 직접 실행될 때 메인 함수 실행
    """
    analyze_app_usage()  # 앱 사용 데이터 분석 실행
