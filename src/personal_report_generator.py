import json
import os
from playwright.sync_api import sync_playwright
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# 파일 저장 전 디렉토리 경로 확인 및 생성
# os.makedirs()는 해당 경로의 모든 디렉토리를 생성함
# exist_ok=True 옵션은 디렉토리가 이미 존재해도 오류를 발생시키지 않음
os.makedirs("data/reports/html", exist_ok=True)
os.makedirs("data/reports/pdf", exist_ok=True)
os.makedirs("src/templates", exist_ok=True)

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
template = env.get_template("report_template.html")

# 절단점
cutoff_burnout_primary = [2.58, 3.01]
cutoff_burnout_secondary = [2.84, 3.34]
cutoff_stress = [44.4, 50.0, 55.6]
cutoff_emotional_labor = [76.66, 72.21, 63.88, 49.99, 45.23]

# 각 참여자에 대해 반복 수행
participants = analysis_data["participants"]

for participant in participants:
    # 참여자 정보
    name = participant["name"]
    team = participant["team"]
    role = participant["role"]
    week = (len(participant["analysis"]) - 1) * 2

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

    # 템플릿에 전달할 컨텍스트 데이터 준비
    context = {
        "name": name,
        "team": team,
        "role": role,
        "week": week,
        "cutoff_burnout_primary": cutoff_burnout_primary,
        "cutoff_burnout_secondary": cutoff_burnout_secondary,
        "cutoff_stress": cutoff_stress,
        "cutoff_emotional_labor": cutoff_emotional_labor,
        "burnout_primary_this_week": burnout_primary_this_week,
        "burnout_secondary_this_week": burnout_secondary_this_week,
        "stress_this_week": stress_this_week,
        "emotional_labor_this_week": emotional_labor_this_week,
        "burnout_primary_last_week": burnout_primary_last_week,
        "burnout_secondary_last_week": burnout_secondary_last_week,
        "stress_last_week": stress_last_week,
        "emotional_labor_last_week": emotional_labor_last_week,
        "company_burnout_primary_this_week": company_burnout_primary_this_week,
        "company_burnout_secondary_this_week": company_burnout_secondary_this_week,
        "company_stress_this_week": company_stress_this_week,
        "company_emotional_labor_this_week": company_emotional_labor_this_week,
        "participant": participant,
    }

    # Jinja2 템플릿을 사용하여 HTML 리포트 생성
    html = template.render(context)

    # HTML 파일 저장 경로
    html_path = Path(f"data/reports/html/{name}_{week}주차.html").resolve()

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
        # page.wait_for_timeout(2000)  # 2초 대기 # Wait for a fixed 2 seconds
        page.wait_for_load_state(
            "networkidle"
        )  # Wait until the network is idle, allowing Tailwind CSS to process and apply styles # Wait until the network is idle, allowing Tailwind CSS to process and apply styles
        # page.pdf(path=f"data/reports/pdf/{name}_{week}주차.pdf", format="A4") # Generate PDF # Generate PDF
        page.pdf(
            path=f"data/reports/pdf/{name}_{week}주차.pdf",
            format="A4",
            print_background=True,
        )  # Generate PDF, ensuring background graphics (like colors) are printed
        # browser.close() # Close the browser # Close the browser
        browser.close()  # Close the browser
