# 필요한 라이브러리 가져오기
import pandas as pd
import json
import os
from datetime import datetime

today = datetime.now().strftime("%Y%m%d")

# CSV 파일 경로 지정
csv_file_path = "data/csv/google_sheet_export_{today}.csv"

# BAT 프라이머리 설문지 데이터를 정의한 JSON 파일 경로
bat_primary_json_path = "data/questionnaires/bat_primary_questionnaires.json"

# 결과 저장 디렉토리 생성
output_dir = "data/results"
os.makedirs(output_dir, exist_ok=True)

# CSV 파일 로드
# 인코딩은 UTF-8로 설정하여 한글이 깨지지 않도록 함
df = pd.read_csv(csv_file_path, encoding="utf-8")

# BAT 프라이머리 설문지 JSON 데이터 로드
with open(bat_primary_json_path, "r", encoding="utf-8") as f:
    bat_primary_data = json.load(f)

# BAT 프라이머리 질문 수 확인 (JSON에서)
num_primary_questions = len(bat_primary_data["BAT-primary"])

# BAT 프라이머리 질문 열 이름 매핑 (CSV에서)
# 인덱스 6부터 시작하는 이유는 타임스탬프, 성명 등의 기본 정보가 앞에 있기 때문
primary_cols = df.columns[6 : 6 + num_primary_questions]

# 각 응답자에 대한 JSON 생성
result_list = []

# 각 행(응답자)에 대해 처리
for _, row in df.iterrows():
    # 기본 정보 추출
    person_data = {
        "name": row["성명"].strip(),  # 앞뒤 공백 제거
        "team": row["소속"],
        "role": row["직무"],
        "scores": {},
    }

    # 각 질문에 대한 점수 계산
    for i, col in enumerate(primary_cols):
        # 질문 번호 계산 (1부터 시작)
        q_num = i + 1
        q_key = f"Q{q_num}"

        # JSON에서 해당 질문의 점수 매핑 가져오기
        score_mapping = bat_primary_data["BAT-primary"][q_key]["scores"]

        # 응답에 해당하는 점수 추출
        response = row[col]
        score = score_mapping.get(response, 0)  # 매핑이 없으면 0점 처리

        # 점수 저장
        person_data["scores"][q_key] = score

    # 결과 리스트에 추가
    result_list.append(person_data)

# 전체 결과를 하나의 JSON 파일로 저장
output_file = f"{output_dir}/bat_primary_results_{today}.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(result_list, f, ensure_ascii=False, indent=2)

print(f"BAT 프라이머리 설문지 결과가 '{output_file}'에 저장되었습니다.")
