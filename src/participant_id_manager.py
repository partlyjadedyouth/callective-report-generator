#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Participant ID Manager

이 모듈은 참가자 식별과 동명이인 구분을 위한 공통 함수들을 제공합니다.
코드베이스 전체에서 일관된 방식으로 참가자를 식별하기 위해 사용됩니다.
"""

import os  # 파일 및 디렉토리 조작을 위한 라이브러리
import csv  # CSV 파일 처리를 위한 라이브러리


def generate_unique_id(name, team):
    """
    이름과 팀 정보를 사용하여 고유 식별자를 생성합니다.

    Args:
        name (str): 참가자 이름
        team (str): 참가자 소속 팀

    Returns:
        str: 고유 식별자 (name_team 형식)
    """
    # 입력값 정리 - 공백 제거 및 빈 값 처리
    name = name.strip() if name else "Unknown"  # 이름이 없으면 "Unknown" 사용
    team = team.strip() if team else "Unknown"  # 팀이 없으면 "Unknown" 사용

    # 고유 ID 생성 (name_team 형식)
    unique_id = f"{name}_{team}"

    return unique_id


def load_participant_ids(csv_file="data/csv/participants.csv"):
    """
    CSV 파일에서 참가자 ID와 성별 정보를 로드합니다.
    이름과 팀을 매칭 기준으로 사용합니다.

    Args:
        csv_file (str): 참가자 정보가 포함된 CSV 파일 경로

    Returns:
        dict: (name, team) 튜플을 키로 하고 참가자 정보(id, gender)를 값으로 하는 사전
    """
    # 참가자 정보를 저장할 사전 초기화
    participant_info = {}

    # CSV 파일이 존재하는지 확인
    if not os.path.exists(csv_file):
        print(
            f"경고: 참가자 CSV 파일 '{csv_file}'을 찾을 수 없습니다. ID가 추가되지 않습니다."
        )
        return participant_info

    # CSV 파일 읽기
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # CSV의 각 행 순회
            for row in reader:
                # 이름, 팀, ID, 성별 추출
                # 참고: CSV 열 이름이 예상 값과 일치해야 함
                name = row.get("성함", "").strip()
                team = row.get("소속", "").strip()
                participant_id = row.get("아이디", "").strip()
                gender = row.get("성별", "").strip()  # 성별 정보 가져오기

                # 데이터가 없는 행 건너뛰기
                if not (name and team):
                    continue

                # 이름과 팀을 키로 하여 참가자 정보 저장
                participant_info[(name, team)] = {
                    "id": participant_id,
                    "gender": gender,
                }

        print(f"{csv_file}에서 {len(participant_info)}개의 참가자 기록을 로드했습니다.")
        return participant_info

    except Exception as e:
        print(f"참가자 정보 로딩 중 오류 발생: {e}")
        return {}


def find_matching_participant(all_participants, name, team, phone=None, email=None):
    """
    기존 참가자 목록에서 일치하는 참가자를 찾습니다.
    여러 식별자(이름, 팀, 전화번호, 이메일)를 사용하여 동명이인을 구분합니다.

    Args:
        all_participants (dict): 기존 참가자 정보가 들어있는 사전
        name (str): 참가자 이름
        team (str): 참가자 소속 팀
        phone (str, optional): 참가자 전화번호
        email (str, optional): 참가자 이메일

    Returns:
        str: 일치하는 참가자의 고유 ID 또는 None (일치하는 참가자가 없는 경우)
    """
    # 기본 고유 ID 생성
    default_unique_id = generate_unique_id(name, team)

    # 기본 ID로 참가자가 이미 있는지 확인
    if default_unique_id in all_participants:
        return default_unique_id

    # 팀 정보가 없거나 "Unknown"인 경우 다른 식별자로 매칭 시도
    if team == "Unknown" or not team:
        # 1. 전화번호로 매칭 시도
        if phone:
            for key, participant_data in all_participants.items():
                if (
                    participant_data.get("phone") == phone
                    and participant_data.get("name") == name
                ):
                    return key

        # 2. 동일한 이름의 참가자 찾기
        matching_keys = [
            key for key, data in all_participants.items() if data.get("name") == name
        ]

        # 동일한 이름의 참가자가 하나만 있는 경우
        if len(matching_keys) == 1:
            return matching_keys[0]

        # 3. 이메일로 매칭 시도 (동일한 이름의 참가자가 여러 명인 경우)
        if email and matching_keys:
            for key in matching_keys:
                if all_participants[key].get("email") == email:
                    return key

    # 일치하는 참가자를 찾지 못한 경우
    return None


def match_with_csv_data(name, team, participant_info):
    """
    CSV 파일의 참가자 정보와 매칭합니다.

    Args:
        name (str): 참가자 이름
        team (str): 참가자 소속 팀
        participant_info (dict): CSV에서 로드한 참가자 정보 사전

    Returns:
        tuple: (matched_team, matched_participant) - 매칭된 팀과 참가자 정보
    """
    matched_participant = None
    matched_team = team

    for (p_name, p_team), p_data in participant_info.items():
        # 이름과 팀으로 정확히 일치하는 경우
        if p_name == name and p_team == team:
            matched_participant = p_data
            matched_team = p_team
            break
        # 이름만 일치하고 팀 정보가 없거나 "Unknown"인 경우
        elif (
            p_name == name
            and (team == "Unknown" or not team)
            and matched_participant is None
        ):
            matched_participant = p_data
            matched_team = p_team

    return matched_team, matched_participant
