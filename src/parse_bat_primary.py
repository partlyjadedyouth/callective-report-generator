# 필요한 라이브러리 가져오기
import pandas as pd
import json
import os
from datetime import datetime

# CSV 파일 경로 지정
csv_file_path = "data/csv/google_sheet_export_20250501.csv"

# BAT 프라이머리 설문지 데이터를 정의한 JSON 파일 경로
bat_primary_json_path = "data/questionnaires/bat_primary_questionnaires.json"

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

# BAT 프라이머리 데이터만 추출
bat_primary_df = df[["타임스탬프", "성명", "소속", "직무"] + list(primary_cols)]

# 추출된 결과를 CSV 파일로 저장
output_file = f"data/csv/bat_primary_results_{datetime.now().strftime("%Y%m%d")}.csv"
bat_primary_df.to_csv(output_file, index=False, encoding="utf-8")

print(f"BAT 프라이머리 설문지 결과가 '{output_file}'에 저장되었습니다.")
