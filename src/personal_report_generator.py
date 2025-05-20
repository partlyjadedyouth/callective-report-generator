import json
import os
from playwright.sync_api import sync_playwright
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# 절단점 값을 가져오기 위한 임포트
from cutoff_values import (
    CUTOFF_BURNOUT_PRIMARY,
    CUTOFF_BURNOUT_EXHAUSTION,
    CUTOFF_BURNOUT_DEPERSONALIZATION,
    CUTOFF_BURNOUT_COGNITIVE_REGULATION,
    CUTOFF_BURNOUT_EMOTIONAL_REGULATION,
    CUTOFF_BURNOUT_SECONDARY,
    CUTOFF_STRESS,
    CUTOFF_STRESS_MALE,
    CUTOFF_EMOTIONAL_LABOR,
    CUTOFF_EMOTIONAL_LABOR_MALE,
    CUTOFF_JOB_DEMAND,
    CUTOFF_JOB_DEMAND_MALE,
    CUTOFF_INSUFFICIENT_JOB_CONTROL,
    CUTOFF_INSUFFICIENT_JOB_CONTROL_MALE,
    CUTOFF_INTERPERSONAL_CONFLICT,
    CUTOFF_INTERPERSONAL_CONFLICT_MALE,
    CUTOFF_JOB_INSECURITY,
    CUTOFF_JOB_INSECURITY_MALE,
    CUTOFF_ORGANIZATIONAL_SYSTEM,
    CUTOFF_ORGANIZATIONAL_SYSTEM_MALE,
    CUTOFF_LACK_OF_REWARD,
    CUTOFF_LACK_OF_REWARD_MALE,
    CUTOFF_OCCUPATIONAL_CLIMATE,
    CUTOFF_OCCUPATIONAL_CLIMATE_MALE,
)

# 파일 저장 전 디렉토리 경로 확인 및 생성
# os.makedirs()는 해당 경로의 모든 디렉토리를 생성함
# exist_ok=True 옵션은 디렉토리가 이미 존재해도 오류를 발생시키지 않음
os.makedirs("data/reports/html", exist_ok=True)
os.makedirs("data/reports/pdf", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("data/reports/html/상담 1팀", exist_ok=True)
os.makedirs("data/reports/html/상담 2팀", exist_ok=True)
os.makedirs("data/reports/html/상담 3팀", exist_ok=True)
os.makedirs("data/reports/html/상담 4팀", exist_ok=True)
os.makedirs("data/reports/pdf/상담 1팀", exist_ok=True)
os.makedirs("data/reports/pdf/상담 2팀", exist_ok=True)
os.makedirs("data/reports/pdf/상담 3팀", exist_ok=True)
os.makedirs("data/reports/pdf/상담 4팀", exist_ok=True)

# analysis.json 파일 경로 설정
analysis_file_path = "data/analysis/analysis.json"

# JSON 파일 열기 및 데이터 로드
with open(analysis_file_path, "r", encoding="utf-8") as file:
    # JSON 파일을 파이썬 딕셔너리로 변환
    analysis_data = json.load(file)

# Jinja2 템플릿 환경 설정
# FileSystemLoader는 템플릿 파일이 위치한 디렉토리를 지정함
env = Environment(loader=FileSystemLoader("templates/"))
# 템플릿 파일 로드
template = env.get_template("personal_template.html")

# 각 참여자에 대해 반복 수행
participants = analysis_data["participants"]

for participant in participants:
    # 참여자 정보
    name = participant["name"]
    team = participant["team"]
    role = participant["role"]
    week = (len(participant["analysis"]) - 1) * 2

    # 직무 스트레스와 감정노동 데이터 표시 여부 결정
    # 0주차, 4주차, 8주차 등 4의 배수 주차에만 데이터를 표시함
    show_stress_and_emotional_labor = week % 4 == 0

    # 참여자의 성별 확인 (기본값은 여성)
    gender = participant.get("gender", "여성")
    is_male = gender == "남성"  # 한국어 성별 표기 사용 ("남성" vs "여성")

    # 성별에 맞는 절단점 선택
    # 번아웃 관련 절단점은 성별 차이가 없으므로 그대로 사용
    cutoff_burnout_primary = CUTOFF_BURNOUT_PRIMARY
    cutoff_burnout_exhaustion = CUTOFF_BURNOUT_EXHAUSTION
    cutoff_burnout_depersonalization = CUTOFF_BURNOUT_DEPERSONALIZATION
    cutoff_burnout_cognitive_regulation = CUTOFF_BURNOUT_COGNITIVE_REGULATION
    cutoff_burnout_emotional_regulation = CUTOFF_BURNOUT_EMOTIONAL_REGULATION
    cutoff_burnout_secondary = CUTOFF_BURNOUT_SECONDARY

    # 성별에 따라 다른 절단점 적용
    cutoff_stress = CUTOFF_STRESS_MALE if is_male else CUTOFF_STRESS
    cutoff_emotional_labor = (
        CUTOFF_EMOTIONAL_LABOR_MALE if is_male else CUTOFF_EMOTIONAL_LABOR
    )

    # 직무 스트레스 요인 절단점 (성별에 따라 다름)
    cutoff_job_demand = CUTOFF_JOB_DEMAND_MALE if is_male else CUTOFF_JOB_DEMAND
    cutoff_insufficient_job_control = (
        CUTOFF_INSUFFICIENT_JOB_CONTROL_MALE
        if is_male
        else CUTOFF_INSUFFICIENT_JOB_CONTROL
    )
    cutoff_interpersonal_conflict = (
        CUTOFF_INTERPERSONAL_CONFLICT_MALE if is_male else CUTOFF_INTERPERSONAL_CONFLICT
    )
    cutoff_job_insecurity = (
        CUTOFF_JOB_INSECURITY_MALE if is_male else CUTOFF_JOB_INSECURITY
    )
    cutoff_organizational_system = (
        CUTOFF_ORGANIZATIONAL_SYSTEM_MALE if is_male else CUTOFF_ORGANIZATIONAL_SYSTEM
    )
    cutoff_lack_of_reward = (
        CUTOFF_LACK_OF_REWARD_MALE if is_male else CUTOFF_LACK_OF_REWARD
    )
    cutoff_occupational_climate = (
        CUTOFF_OCCUPATIONAL_CLIMATE_MALE if is_male else CUTOFF_OCCUPATIONAL_CLIMATE
    )

    # 해당 참여자의 심리검사 점수
    burnout_primary_this_week = participant["analysis"][f"{week}주차"][
        "category_averages"
    ]["BAT_primary"]
    burnout_secondary_this_week = participant["analysis"][f"{week}주차"][
        "category_averages"
    ]["BAT_secondary"]
    stress_this_week = participant["analysis"][f"{week}주차"]["category_averages"][
        "stress"
    ]
    emotional_labor_this_week = participant["analysis"][f"{week}주차"]["type_averages"][
        "emotional_labor"
    ]

    # 탈진 점수 추출
    burnout_exhaustion_this_week = participant["analysis"][f"{week}주차"][
        "type_averages"
    ]["BAT_primary"].get("탈진", 0)

    # 심적 거리 점수 추출
    burnout_depersonalization_this_week = participant["analysis"][f"{week}주차"][
        "type_averages"
    ]["BAT_primary"].get("심적 거리", 0)

    # 인지적 조절 점수 추출
    burnout_cognitive_regulation_this_week = participant["analysis"][f"{week}주차"][
        "type_averages"
    ]["BAT_primary"].get("인지적 조절", 0)

    # 정서적 조절 점수 추출
    burnout_emotional_regulation_this_week = participant["analysis"][f"{week}주차"][
        "type_averages"
    ]["BAT_primary"].get("정서적 조절", 0)

    # 해당 참여자의 지난 주의 심리검사 점수
    burnout_primary_last_week = (
        participant["analysis"][f"{week - 2}주차"]["category_averages"]["BAT_primary"]
        if week > 0
        else 0
    )
    burnout_secondary_last_week = (
        participant["analysis"][f"{week - 2}주차"]["category_averages"]["BAT_secondary"]
        if week > 0
        else 0
    )
    stress_last_week = (
        participant["analysis"][f"{week - 2}주차"]["category_averages"]["stress"]
        if week > 0
        else 0
    )
    emotional_labor_last_week = (
        participant["analysis"][f"{week - 2}주차"]["type_averages"]["emotional_labor"]
        if week > 0
        else []
    )

    # 지난 주의 정서적 조절 점수 추출
    burnout_emotional_regulation_last_week = (
        participant["analysis"][f"{week - 2}주차"]["type_averages"]["BAT_primary"].get(
            "정서적 조절", 0
        )
        if week > 0
        else 0
    )

    # 금주의 회사 평균 심리검사 점수
    company_burnout_primary_this_week = analysis_data["groups"]["회사"]["analysis"][
        f"{week}주차"
    ]["category_averages"]["BAT_primary"]
    company_burnout_secondary_this_week = analysis_data["groups"]["회사"]["analysis"][
        f"{week}주차"
    ]["category_averages"]["BAT_secondary"]
    company_stress_this_week = analysis_data["groups"]["회사"]["analysis"][
        f"{week}주차"
    ]["category_averages"]["stress"]
    company_emotional_labor_this_week = analysis_data["groups"]["회사"]["analysis"][
        f"{week}주차"
    ]["type_averages"]["emotional_labor"]

    # 회사 평균 정서적 조절 점수 추출
    company_burnout_emotional_regulation_this_week = analysis_data["groups"]["회사"][
        "analysis"
    ][f"{week}주차"]["type_averages"]["BAT_primary"].get("정서적 조절", 0)

    # 템플릿에 전달할 컨텍스트 데이터 준비
    context = {
        "name": name,
        "team": team,
        "role": role,
        "week": week,
        "gender": gender,
        "show_stress_and_emotional_labor": show_stress_and_emotional_labor,  # 직무 스트레스와 감정노동 데이터 표시 여부
        "cutoff_burnout_primary": cutoff_burnout_primary,
        "cutoff_burnout_secondary": cutoff_burnout_secondary,
        "cutoff_burnout_exhaustion": cutoff_burnout_exhaustion,
        "cutoff_burnout_depersonalization": cutoff_burnout_depersonalization,
        "cutoff_burnout_cognitive_regulation": cutoff_burnout_cognitive_regulation,
        "cutoff_burnout_emotional_regulation": cutoff_burnout_emotional_regulation,
        "cutoff_stress": cutoff_stress,
        "cutoff_emotional_labor": cutoff_emotional_labor,
        "cutoff_job_demand": cutoff_job_demand,
        "cutoff_insufficient_job_control": cutoff_insufficient_job_control,
        "cutoff_interpersonal_conflict": cutoff_interpersonal_conflict,
        "cutoff_job_insecurity": cutoff_job_insecurity,
        "cutoff_organizational_system": cutoff_organizational_system,
        "cutoff_lack_of_reward": cutoff_lack_of_reward,
        "cutoff_occupational_climate": cutoff_occupational_climate,
        "burnout_primary_this_week": burnout_primary_this_week,
        "burnout_secondary_this_week": burnout_secondary_this_week,
        "burnout_exhaustion_this_week": burnout_exhaustion_this_week,
        "burnout_depersonalization_this_week": burnout_depersonalization_this_week,
        "burnout_cognitive_regulation_this_week": burnout_cognitive_regulation_this_week,
        "burnout_emotional_regulation_this_week": burnout_emotional_regulation_this_week,
        "stress_this_week": stress_this_week,
        "emotional_labor_this_week": emotional_labor_this_week,
        "burnout_primary_last_week": burnout_primary_last_week,
        "burnout_secondary_last_week": burnout_secondary_last_week,
        "stress_last_week": stress_last_week,
        "emotional_labor_last_week": emotional_labor_last_week,
        "burnout_emotional_regulation_last_week": burnout_emotional_regulation_last_week,
        "company_burnout_primary_this_week": company_burnout_primary_this_week,
        "company_burnout_secondary_this_week": company_burnout_secondary_this_week,
        "company_burnout_emotional_regulation_this_week": company_burnout_emotional_regulation_this_week,
        "company_stress_this_week": company_stress_this_week,
        "company_emotional_labor_this_week": company_emotional_labor_this_week,
        "participant": participant,
        "el_categories": [
            {
                "key": "감정조절의 노력 및 다양성",
                "cutoff_val": cutoff_emotional_labor[0],
            },
            {
                "key": "고객응대의 과부하 및 갈등",
                "cutoff_val": cutoff_emotional_labor[1],
            },
            {"key": "감정부조화 및 손상", "cutoff_val": cutoff_emotional_labor[2]},
            {"key": "조직의 감시 및 모니터링", "cutoff_val": cutoff_emotional_labor[3]},
            {"key": "조직의 지지 및 보호체계", "cutoff_val": cutoff_emotional_labor[4]},
        ],
    }

    # Jinja2 템플릿을 사용하여 HTML 리포트 생성
    html = template.render(context)

    # HTML 파일 저장 경로
    html_path = Path(
        f"data/reports/html/{team}/{team}_{name}_{week}주차.html"
    ).resolve()

    with open(html_path, "w", encoding="utf-8") as file:
        # 파일 쓰기 작업 계속 진행
        file.write(html)

    # PDF 파일 생성
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # page.goto(f"file://{html_path}") # Navigate to the local HTML file path
        page.goto(
            f"file://{html_path}", wait_until="domcontentloaded"
        )  # Navigate to the local HTML file path and wait for DOM content to be loaded
        page.wait_for_load_state(
            "networkidle"
        )  # Wait until the network is idle, allowing Tailwind CSS to process and apply styles # Wait until the network is idle, allowing Tailwind CSS to process and apply styles
        # page.pdf(path=f"data/reports/pdf/{name}_{week}주차.pdf", format="A4") # Generate PDF # Generate PDF
        page.pdf(
            path=f"data/reports/pdf/{team}/{team}_{name}_{week}주차.pdf",
            format="A4",
            print_background=True,
        )  # Generate PDF, ensuring background graphics (like colors) are printed
        # browser.close() # Close the browser # Close the browser
        browser.close()  # Close the browser
