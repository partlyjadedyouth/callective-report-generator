# 필요한 JSON 라이브러리 임포트
import json
import os

# 파일 저장 전 디렉토리 경로 확인 및 생성
# os.makedirs()는 해당 경로의 모든 디렉토리를 생성함
# exist_ok=True 옵션은 디렉토리가 이미 존재해도 오류를 발생시키지 않음
os.makedirs("data/reports/html", exist_ok=True)
os.makedirs("data/reports/pdf", exist_ok=True)

# analysis.json 파일 경로 설정
analysis_file_path = "data/analysis/analysis.json"

# JSON 파일 열기 및 데이터 로드
with open(analysis_file_path, "r", encoding="utf-8") as file:
    # JSON 파일을 파이썬 딕셔너리로 변환
    analysis_data = json.load(file)

# 절단점
cutoff_burnout_primary = [2.58, 3.01]
cutoff_burnout_secondary = [2.84, 3.34]
cutoff_stress = [44.4, 50.0, 55.6]
cutoff_emotional_labor = [76.66, 72.21, 63.88, 49.99, 45.23]

# 각 참여자에 대해 반복 수행
participants = analysis_data["participants"]

for participant in participants:
    # output
    html = ""

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

    # 참여자의 결과를 바탕으로 HTML 리포트 생성
    html = f"""
    <!doctype html>
<html>

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>

<body class="m-0 p-0 overflow-hidden">
    <div class="w-screen h-screen flex flex-col items-center p-10 gap-10">
        <!-- 제목 -->
        <div class="flex flex-col items-center">
            <h1 class="text-5xl font-bold">설문조사 리포트 ({week}주차)</h1>
            <h2 class="text-3xl font-semibold mt-3">{name} / {team} / {role}</h2>
        </div>

        <!-- 1행 -->
        <div class="w-full grid grid-cols-2 gap-6">
            <!-- 번아웃 핵심 증상 -->
            <div class="flex flex-col items-start w-full px-5">
                <h3 class="text-2xl font-semibold">번아웃 핵심 증상</h3>
                <h4 class="text-lg">탈진, 정신적 거리감, 인지적 조절, 정서적 조절</h4>
                <hr class="w-full border-t border-black my-2">

                <!-- 차트 분석 -->
                <div class="flex w-full justify-between mt-3">
                    <!-- 수평 척도 컨테이너 -->
                    <div class="w-full flex flex-col items-center">
                        <!-- 실제 척도 라인 -->
                        <div class="relative w-full h-4">
                            <!-- 배경 라인 -->
                            <div class="absolute w-full h-2 bg-gray-200 top-1/2 -translate-y-1/2"></div>

                            <!-- 정상 구간 -->
                            <div class="absolute h-2 bg-green-400 top-1/2 -translate-y-1/2"
                                style="width: {(cutoff_burnout_primary[0] - 1) * 25}%; left: 0%;"></div>

                            <!-- 위험 구간 -->
                            <div class="absolute h-2 bg-yellow-400 top-1/2 -translate-y-1/2"
                                style="width: {(cutoff_burnout_primary[1] - cutoff_burnout_primary[0]) * 25}%; left: {(cutoff_burnout_primary[0] - 1) * 25}%;"></div>

                            <!-- 고위험 구간 -->
                            <div class="absolute h-2 bg-red-400 top-1/2 -translate-y-1/2"
                                style="width: {(5 - cutoff_burnout_primary[1]) * 25}%; left: {(cutoff_burnout_primary[1] - 1) * 25}%;"></div>

                            <!-- 경계선 마커 -->
                            <div class="absolute w-0.5 h-5 bg-gray-600 top-1/2 -translate-y-1/2" style="left: 0%;">
                            </div>
                            <div class="absolute w-0.5 h-5 bg-gray-600 top-1/2 -translate-y-1/2" style="left: 25%;">
                            </div>
                            <div class="absolute w-0.5 h-5 bg-gray-600 top-1/2 -translate-y-1/2" style="left: 50%;">
                            </div>
                            <div class="absolute w-0.5 h-5 bg-gray-600 top-1/2 -translate-y-1/2" style="left: 75%;">
                            </div>
                            <div class="absolute w-0.5 h-5 bg-gray-600 top-1/2 -translate-y-1/2" style="left: 100%;">
                            </div>

                            <!-- 현재 위치 표시 - 점 -->
                            <div class="absolute w-3 h-3 bg-gray-600 rounded-full top-1/2 -translate-y-1/2"
                                style="left: {(burnout_primary_this_week - 1) * 25}%; transform: translateX(-50%);"></div>
                        </div>

                        <!-- 척도 숫자 -->
                        <div class="w-full flex justify-between mt-1 text-sm">
                            <span>1</span>
                            <span>2</span>
                            <span>3</span>
                            <span>4</span>
                            <span>5</span>
                        </div>

                        <!-- 현재 값 표시 -->
                        <div class="flex flex-col w-full">
                            <hr class="w-full border-t border-gray-300 my-3">
                            <!-- 첫번째 행 -->
                            <div class="flex justify-between mb-3">
                                <div class="font-medium">점수</div>
                                <div class="font-medium text-{'green' if burnout_primary_this_week <= cutoff_burnout_primary[0] else 'yellow' if burnout_primary_this_week <= cutoff_burnout_primary[1] else 'red'}-600">{burnout_primary_this_week} ({'정상' if burnout_primary_this_week <= cutoff_burnout_primary[0] else '위험' if burnout_primary_this_week <= cutoff_burnout_primary[1] else '고위험'})</div>
                            </div>
                            <hr class="w-full border-t border-gray-300 mb-3">

                            <!-- 두번째 행 -->
                            {"""<div class="flex justify-between mb-3">
                                <div class="font-medium">지난 설문 대비</div>
                                <div class="font-medium text-{}">{}{}</div>
                            </div>
                            <hr class="w-full border-t border-gray-300 mb-3">""".format(
                                # 번아웃 점수는 낮을수록 좋으므로 증가했으면 빨간색, 감소했거나 그대로이면 녹색
                                "red-600" if burnout_primary_this_week > burnout_primary_last_week else "green-600",
                                # 증가 또는 감소 표시
                                "+" if burnout_primary_this_week > burnout_primary_last_week else "",
                                # 점수 차이 계산 및 소수점 2자리까지 표시
                                round(burnout_primary_this_week - burnout_primary_last_week, 2)
                            ) if week > 0 else ""}

                            <!-- 세번째 행 -->
                            <div class="flex justify-between mb-3">
                                <div class="font-medium">회사 평균</div>
                                <div class="font-medium text-{"green" if company_burnout_primary_this_week <= cutoff_burnout_primary[0] else "yellow" if company_burnout_primary_this_week <= cutoff_burnout_primary[1] else "red"}-600">{company_burnout_primary_this_week} ({'정상' if company_burnout_primary_this_week <= cutoff_burnout_primary[0] else '위험' if company_burnout_primary_this_week <= cutoff_burnout_primary[1] else '고위험'})</div>
                            </div>
                        </div>

                        <!-- n주차 결과 -->
                        <hr class="w-full border-t border-black mb-3">
                        <div class="w-full grid grid-cols-7 px-2 gap-x-3">
                            <!-- 0주차 -->
                            {f"""<div class="flex flex-col items-center w-full">
                                <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["0주차"]["category_averages"]["BAT_primary"] <= cutoff_burnout_primary[0] else "yellow" if participant["analysis"]["0주차"]["category_averages"]["BAT_primary"] <= cutoff_burnout_primary[1] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                <div class="text-xs">0주차</div>
                            </div>""" if week >= 0 else "<div class='hidden'></div>"}
                            <!-- 2주차 -->
                            {f"""<div class="flex flex-col items-center w-full">
                                <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["2주차"]["category_averages"]["BAT_primary"] <= cutoff_burnout_primary[0] else "yellow" if participant["analysis"]["2주차"]["category_averages"]["BAT_primary"] <= cutoff_burnout_primary[1] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                <div class="text-xs">2주차</div>
                            </div>""" if week >= 2 else "<div class='hidden'></div>"}
                            <!-- 4주차 -->
                            {f"""<div class="flex flex-col items-center w-full">
                                <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["4주차"]["category_averages"]["BAT_primary"] <= cutoff_burnout_primary[0] else "yellow" if participant["analysis"]["4주차"]["category_averages"]["BAT_primary"] <= cutoff_burnout_primary[1] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                <div class="text-xs">4주차</div>
                            </div>""" if week >= 4 else "<div class='hidden'></div>"}
                            <!-- 6주차 -->
                            {f"""<div class="flex flex-col items-center w-full">
                                <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["6주차"]["category_averages"]["BAT_primary"] <= cutoff_burnout_primary[0] else "yellow" if participant["analysis"]["6주차"]["category_averages"]["BAT_primary"] <= cutoff_burnout_primary[1] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                <div class="text-xs">6주차</div>
                            </div>""" if week >= 6 else "<div class='hidden'></div>"}
                            <!-- 8주차 -->
                            {f"""<div class="flex flex-col items-center w-full">
                                <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["8주차"]["category_averages"]["BAT_primary"] <= cutoff_burnout_primary[0] else "yellow" if participant["analysis"]["8주차"]["category_averages"]["BAT_primary"] <= cutoff_burnout_primary[1] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                <div class="text-xs">8주차</div>
                            </div>""" if week >= 8 else "<div class='hidden'></div>"}
                            <!-- 10주차 -->
                            {f"""<div class="flex flex-col items-center w-full">
                                <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["10주차"]["category_averages"]["BAT_primary"] <= cutoff_burnout_primary[0] else "yellow" if participant["analysis"]["10주차"]["category_averages"]["BAT_primary"] <= cutoff_burnout_primary[1] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                <div class="text-xs">10주차</div>
                            </div>""" if week >= 10 else "<div class='hidden'></div>"}
                            <!-- 12주차 -->
                            {f"""<div class="flex flex-col items-center w-full">
                                <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["12주차"]["category_averages"]["BAT_primary"] <= cutoff_burnout_primary[0] else "yellow" if participant["analysis"]["12주차"]["category_averages"]["BAT_primary"] <= cutoff_burnout_primary[1] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                <div class="text-xs">12주차</div>
                            </div>""" if week >= 12 else "<div class='hidden'></div>"}
                        </div>
                    </div>
                </div>
            </div>

            <!-- 번아웃 2차적 증상 -->
            <div class="flex flex-col items-start w-full px-5">
                <h3 class="text-2xl font-semibold">번아웃 2차적 증상</h3>
                <h4 class="text-lg">심리적 호소, 신체적 호소</h4>
                <hr class="w-full border-t border-black my-2">

                <!-- 차트 분석 -->
                <div class="flex w-full justify-between mt-3">
                    <!-- 수평 척도 컨테이너 -->
                    <div class="w-full flex flex-col items-center">
                        <!-- 실제 척도 라인 -->
                        <div class="relative w-full h-4">
                            <!-- 배경 라인 -->
                            <div class="absolute w-full h-2 bg-gray-200 top-1/2 -translate-y-1/2"></div>

                            <!-- 정상 구간 -->
                            <div class="absolute h-2 bg-green-400 top-1/2 -translate-y-1/2"
                                style="width: {(cutoff_burnout_secondary[0] - 1) * 25}%; left: 0%;"></div>

                            <!-- 위험 구간 (2.85-3.34) -->
                            <div class="absolute h-2 bg-yellow-400 top-1/2 -translate-y-1/2"
                                style="width: {(cutoff_burnout_secondary[1] - cutoff_burnout_secondary[0]) * 25}%; left: {(cutoff_burnout_secondary[0] - 1) * 25}%;"></div>

                            <!-- 고위험 구간 (3.35-5.00) -->
                            <div class="absolute h-2 bg-red-400 top-1/2 -translate-y-1/2"
                                style="width: {(5 - cutoff_burnout_secondary[1]) * 25}%; left: {(cutoff_burnout_secondary[1] - 1) * 25}%;"></div>

                            <!-- 경계선 마커 -->
                            <div class="absolute w-0.5 h-5 bg-gray-600 top-1/2 -translate-y-1/2" style="left: 0%;">
                            </div>
                            <div class="absolute w-0.5 h-5 bg-gray-600 top-1/2 -translate-y-1/2" style="left: 25%;">
                            </div>
                            <div class="absolute w-0.5 h-5 bg-gray-600 top-1/2 -translate-y-1/2" style="left: 50%;">
                            </div>
                            <div class="absolute w-0.5 h-5 bg-gray-600 top-1/2 -translate-y-1/2" style="left: 75%;">
                            </div>
                            <div class="absolute w-0.5 h-5 bg-gray-600 top-1/2 -translate-y-1/2" style="left: 100%;">
                            </div>

                            <!-- 현재 위치 표시 - 점 -->
                            <div class="absolute w-3 h-3 bg-gray-600 rounded-full top-1/2 -translate-y-1/2"
                                style="left: {(burnout_secondary_this_week - 1) * 25}%; transform: translateX(-50%);"></div>
                        </div>

                        <!-- 척도 숫자 -->
                        <div class="w-full flex justify-between mt-1 text-sm">
                            <span>1</span>
                            <span>2</span>
                            <span>3</span>
                            <span>4</span>
                            <span>5</span>
                        </div>

                        <!-- 현재 값 표시 -->
                        <div class="flex flex-col w-full">
                            <hr class="w-full border-t border-gray-300 my-3">
                            <!-- 첫번째 행 -->
                            <div class="flex justify-between mb-3">
                                <div class="font-medium">점수</div>
                                <div class="font-medium text-{'green' if burnout_secondary_this_week <= cutoff_burnout_secondary[0] else 'yellow' if burnout_secondary_this_week <= cutoff_burnout_secondary[1] else 'red'}-600">{burnout_secondary_this_week} ({'정상' if burnout_secondary_this_week <= cutoff_burnout_secondary[0] else '위험' if burnout_secondary_this_week <= cutoff_burnout_secondary[1] else '고위험'})</div>
                            </div>
                            <hr class="w-full border-t border-gray-300 mb-3">

                            <!-- 두번째 행 -->
                            {"""<div class="flex justify-between mb-3">
                                <div class="font-medium">지난 설문 대비</div>
                                <div class="font-medium text-{}">{}{}</div>
                            </div>
                            <hr class="w-full border-t border-gray-300 mb-3">""".format(
                                # 번아웃 점수는 낮을수록 좋으므로 증가했으면 빨간색, 감소했거나 그대로이면 녹색
                                "red-600" if burnout_secondary_this_week > burnout_secondary_last_week else "green-600",
                                # 증가 또는 감소 표시
                                "+" if burnout_secondary_this_week > burnout_secondary_last_week else "",
                                # 점수 차이 계산 및 소수점 2자리까지 표시
                                round(burnout_secondary_this_week - burnout_secondary_last_week, 2)
                            ) if week > 0 else ""}

                            <!-- 세번째 행 -->
                            <div class="flex justify-between mb-3">
                                <div class="font-medium">회사 평균</div>
                                <div class="font-medium text-{"green" if company_burnout_secondary_this_week <= cutoff_burnout_secondary[0] else "yellow" if company_burnout_secondary_this_week <= cutoff_burnout_secondary[1] else "red"}-600">{company_burnout_secondary_this_week} ({'정상' if company_burnout_secondary_this_week <= cutoff_burnout_secondary[0] else '위험' if company_burnout_secondary_this_week <= cutoff_burnout_secondary[1] else '고위험'})</div>
                            </div>

                            <!-- n주차 결과 -->
                            <hr class="w-full border-t border-black mb-3">
                            <div class="grid grid-cols-7 px-2 gap-x-3">
                                <!-- 0주차 -->
                                {f"""<div class="flex flex-col items-center w-full">
                                    <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["0주차"]["category_averages"]["BAT_secondary"] <= cutoff_burnout_secondary[0] else "yellow" if participant["analysis"]["0주차"]["category_averages"]["BAT_secondary"] <= cutoff_burnout_secondary[1] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                    <div class="text-xs">0주차</div>
                                </div>""" if week >= 0 else "<div class='hidden'></div>"}
                                <!-- 2주차 -->
                                {f"""<div class="flex flex-col items-center w-full">
                                    <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["2주차"]["category_averages"]["BAT_secondary"] <= cutoff_burnout_secondary[0] else "yellow" if participant["analysis"]["2주차"]["category_averages"]["BAT_secondary"] <= cutoff_burnout_secondary[1] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                    <div class="text-xs">2주차</div>
                                </div>""" if week >= 2 else "<div class='hidden'></div>"}
                                <!-- 4주차 -->
                                {f"""<div class="flex flex-col items-center w-full">
                                    <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["4주차"]["category_averages"]["BAT_secondary"] <= cutoff_burnout_secondary[0] else "yellow" if participant["analysis"]["4주차"]["category_averages"]["BAT_secondary"] <= cutoff_burnout_secondary[1] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                    <div class="text-xs">4주차</div>
                                </div>""" if week >= 4 else "<div class='hidden'></div>"}
                                <!-- 6주차 -->
                                {f"""<div class="flex flex-col items-center w-full">
                                    <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["6주차"]["category_averages"]["BAT_secondary"] <= cutoff_burnout_secondary[0] else "yellow" if participant["analysis"]["6주차"]["category_averages"]["BAT_secondary"] <= cutoff_burnout_secondary[1] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                    <div class="text-xs">6주차</div>
                                </div>""" if week >= 6 else "<div class='hidden'></div>"}
                                <!-- 8주차 -->
                                {f"""<div class="flex flex-col items-center w-full">
                                    <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["8주차"]["category_averages"]["BAT_secondary"] <= cutoff_burnout_secondary[0] else "yellow" if participant["analysis"]["8주차"]["category_averages"]["BAT_secondary"] <= cutoff_burnout_secondary[1] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                    <div class="text-xs">8주차</div>
                                </div>""" if week >= 8 else "<div class='hidden'></div>"}
                                <!-- 10주차 -->
                                {f"""<div class="flex flex-col items-center w-full">
                                    <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["10주차"]["category_averages"]["BAT_secondary"] <= cutoff_burnout_secondary[0] else "yellow" if participant["analysis"]["10주차"]["category_averages"]["BAT_secondary"] <= cutoff_burnout_secondary[1] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                    <div class="text-xs">10주차</div>
                                </div>""" if week >= 10 else "<div class='hidden'></div>"}
                                <!-- 12주차 -->
                                {f"""<div class="flex flex-col items-center w-full">
                                    <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["12주차"]["category_averages"]["BAT_secondary"] <= cutoff_burnout_secondary[0] else "yellow" if participant["analysis"]["12주차"]["category_averages"]["BAT_secondary"] <= cutoff_burnout_secondary[1] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                    <div class="text-xs">12주차</div>
                                </div>""" if week >= 12 else "<div class='hidden'></div>"}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 2행 -->
        <div class="w-full grid grid-cols-2 gap-6">
            <!-- 직무 스트레스 -->
            <div class="flex flex-col items-start w-full px-5">
                <h3 class="text-2xl font-semibold">직무 스트레스</h3>
                <hr class="w-full border-t border-black my-2">

                <!-- 차트 분석 -->
                <div class="flex w-full justify-between mt-3">
                    <!-- 수평 척도 컨테이너 -->
                    <div class="w-full flex flex-col items-center">
                        <!-- 실제 척도 라인 -->
                        <div class="relative w-full h-4">
                            <!-- 배경 라인 -->
                            <div class="absolute w-full h-2 bg-gray-200 top-1/2 -translate-y-1/2"></div>

                            <!-- 정상 구간 -->
                            <div class="absolute h-2 bg-green-400 top-1/2 -translate-y-1/2"
                                style="width: {cutoff_stress[0]}%; left: 0%;"></div>

                            <!-- 주의 구간 -->
                            <div class="absolute h-2 bg-yellow-400 top-1/2 -translate-y-1/2"
                                style="width: {cutoff_stress[1] - cutoff_stress[0]}%; left: {cutoff_stress[0]}%;"></div>

                            <!-- 위험 구간 -->
                            <div class="absolute h-2 bg-orange-400 top-1/2 -translate-y-1/2"
                                style="width: {cutoff_stress[2] - cutoff_stress[1]}%; left: {cutoff_stress[1]}%;"></div>

                            <!-- 고위험 구간 -->
                            <div class="absolute h-2 bg-red-400 top-1/2 -translate-y-1/2"
                                style="width: {100 - cutoff_stress[2]}%; left: {cutoff_stress[2]}%;"></div>

                            <!-- 경계선 마커 -->
                            <div class="absolute w-0.5 h-5 bg-gray-600 top-1/2 -translate-y-1/2" style="left: 0%;">
                            </div>
                            <div class="absolute w-0.5 h-5 bg-gray-600 top-1/2 -translate-y-1/2" style="left: 25%;">
                            </div>
                            <div class="absolute w-0.5 h-5 bg-gray-600 top-1/2 -translate-y-1/2" style="left: 50%;">
                            </div>
                            <div class="absolute w-0.5 h-5 bg-gray-600 top-1/2 -translate-y-1/2" style="left: 75%;">
                            </div>
                            <div class="absolute w-0.5 h-5 bg-gray-600 top-1/2 -translate-y-1/2" style="left: 100%;">
                            </div>

                            <!-- 현재 위치 표시 - 점 -->
                            <div class="absolute w-3 h-3 bg-gray-600 rounded-full top-1/2 -translate-y-1/2"
                                style="left: {stress_this_week}%; transform: translateX(-50%);"></div>
                        </div>

                        <!-- 척도 숫자 -->
                        <div class="w-full flex justify-between mt-1 text-sm">
                            <span>0</span>
                            <span>25</span>
                            <span>50</span>
                            <span>75</span>
                            <span>100</span>
                        </div>

                        <!-- 현재 값 표시 -->
                        <div class="flex flex-col w-full">
                            <hr class="w-full border-t border-gray-300 my-3">
                            <!-- 첫번째 행 -->
                            <div class="flex justify-between mb-3">
                                <div class="font-medium">점수</div>
                                <div class="font-medium text-{"green" if stress_this_week <= cutoff_stress[0] else "yellow" if stress_this_week <= cutoff_stress[1] else "red"}-600">{stress_this_week} ({'정상' if stress_this_week <= cutoff_stress[0] else '위험' if stress_this_week <= cutoff_stress[1] else '고위험'})</div>
                            </div>
                            <hr class="w-full border-t border-gray-300 mb-3">

                            <!-- 두번째 행 -->
                            {"""<div class="flex justify-between mb-3">
                                <div class="font-medium">지난 설문 대비</div>
                                <div class="font-medium text-{}">{}{}</div>
                            </div>
                            <hr class="w-full border-t border-gray-300 mb-3">""".format(
                                # 번아웃 점수는 낮을수록 좋으므로 증가했으면 빨간색, 감소했거나 그대로이면 녹색
                                "red-600" if stress_this_week > stress_last_week else "green-600",
                                # 증가 또는 감소 표시
                                "+" if stress_this_week > stress_last_week else "",
                                # 점수 차이 계산 및 소수점 2자리까지 표시
                                round(stress_this_week - stress_last_week, 2)
                            ) if week > 0 else ""}

                            <!-- 세번째 행 -->
                            <div class="flex justify-between mb-3">
                                <div class="font-medium">회사 평균</div>
                                <div class="font-medium text-{"green" if company_stress_this_week <= cutoff_stress[0] else "yellow" if company_stress_this_week <= cutoff_stress[1] else "red"}-600">{company_stress_this_week} ({'정상' if company_stress_this_week <= cutoff_stress[0] else '위험' if company_stress_this_week <= cutoff_stress[1] else '고위험'})</div>
                            </div>

                            <!-- n주차 결과 -->
                            <hr class="w-full border-t border-black mb-3">
                            <div class="grid grid-cols-7 px-2 gap-x-3">
                                <!-- 0주차 -->
                                {f"""<div class="flex flex-col items-center w-full">
                                    <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["0주차"]["category_averages"]["stress"] <= cutoff_stress[0] else "yellow" if participant["analysis"]["0주차"]["category_averages"]["stress"] <= cutoff_stress[1] else "orange" if participant["analysis"]["0주차"]["category_averages"]["stress"] <= cutoff_stress[2] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                    <div class="text-xs">0주차</div>
                                </div>""" if week >= 0 else "<div class='hidden'></div>"}
                                <!-- 2주차 -->
                                {f"""<div class="flex flex-col items-center w-full">
                                    <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["2주차"]["category_averages"]["stress"] <= cutoff_stress[0] else "yellow" if participant["analysis"]["2주차"]["category_averages"]["stress"] <= cutoff_stress[1] else "orange" if participant["analysis"]["2주차"]["category_averages"]["stress"] <= cutoff_stress[2] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                    <div class="text-xs">2주차</div>
                                </div>""" if week >= 2 else "<div class='hidden'></div>"}
                                <!-- 4주차 -->
                                {f"""<div class="flex flex-col items-center w-full">
                                    <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["4주차"]["category_averages"]["stress"] <= cutoff_stress[0] else "yellow" if participant["analysis"]["4주차"]["category_averages"]["stress"] <= cutoff_stress[1] else "orange" if participant["analysis"]["4주차"]["category_averages"]["stress"] <= cutoff_stress[2] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                    <div class="text-xs">4주차</div>
                                </div>""" if week >= 4 else "<div class='hidden'></div>"}
                                <!-- 6주차 -->
                                {f"""<div class="flex flex-col items-center w-full">
                                    <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["6주차"]["category_averages"]["stress"] <= cutoff_stress[0] else "yellow" if participant["analysis"]["6주차"]["category_averages"]["stress"] <= cutoff_stress[1] else "orange" if participant["analysis"]["6주차"]["category_averages"]["stress"] <= cutoff_stress[2] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                    <div class="text-xs">6주차</div>
                                </div>""" if week >= 6 else "<div class='hidden'></div>"}
                                <!-- 8주차 -->
                                {f"""<div class="flex flex-col items-center w-full">
                                    <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["8주차"]["category_averages"]["stress"] <= cutoff_stress[0] else "yellow" if participant["analysis"]["8주차"]["category_averages"]["stress"] <= cutoff_stress[1] else "orange" if participant["analysis"]["8주차"]["category_averages"]["stress"] <= cutoff_stress[2] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                    <div class="text-xs">8주차</div>
                                </div>""" if week >= 8 else "<div class='hidden'></div>"}
                                <!-- 10주차 -->
                                {f"""<div class="flex flex-col items-center w-full">
                                    <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["10주차"]["category_averages"]["stress"] <= cutoff_stress[0] else "yellow" if participant["analysis"]["10주차"]["category_averages"]["stress"] <= cutoff_stress[1] else "orange" if participant["analysis"]["10주차"]["category_averages"]["stress"] <= cutoff_stress[2] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                    <div class="text-xs">10주차</div>
                                </div>""" if week >= 10 else "<div class='hidden'></div>"}
                                <!-- 12주차 -->
                                {f"""<div class="flex flex-col items-center w-full">
                                    <div class="w-full rounded-lg bg-{"green" if participant["analysis"]["12주차"]["category_averages"]["stress"] <= cutoff_stress[0] else "yellow" if participant["analysis"]["12주차"]["category_averages"]["stress"] <= cutoff_stress[1] else "orange" if participant["analysis"]["12주차"]["category_averages"]["stress"] <= cutoff_stress[2] else "red"}-400 h-5 mb-1">&nbsp;</div>
                                    <div class="text-xs">12주차</div>
                                </div>""" if week >= 12 else "<div class='hidden'></div>"}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 감정 노동 정도 -->
            <div class="flex flex-col items-start w-full px-5">
                <div class="flex w-full justify-between items-center">
                    <h3 class="text-2xl font-semibold">감정 노동 정도</h3>

                    <!-- 범례 -->
                    <div class="flex items-center space-x-4">
                        <div class="flex items-center">
                            <div class="w-4 h-4 border-2 border-gray-600 rounded-full bg-white mr-2"></div>
                            <span class="text-xs">사용자 점수</span>
                        </div>
                        <div class="flex items-center">
                            <div class="w-4 h-4 border-2 border-black bg-white mr-2"></div>
                            <span class="text-xs">회사 평균</span>
                        </div>
                    </div>
                </div>
                <hr class="w-full border-t border-black my-2">

                <div class="grid grid-cols-5 w-full gap-4 mb-4">
                    <!-- 첫번째 컬럼 -->
                    <div class="flex flex-col items-center">
                        <div class="flex justify-center w-full h-52">
                            <div class="border border-black rounded-lg p-3 flex justify-center h-full w-20">
                                <div class="relative h-full w-1 mx-auto">
                                    <!-- 위험 구간 - 위쪽 상단 -->
                                    <div class="absolute w-full bg-red-400" style="height: {100 - cutoff_emotional_labor[0]}%; top: 0;"></div>

                                    <!-- 정상 구간  - 아래쪽 -->
                                    <div class="absolute w-full bg-green-400" style="height: {cutoff_emotional_labor[0]}%; top: {100 - cutoff_emotional_labor[0]}%;">
                                    </div>

                                    <!-- 사용자 점수 마커 - 원 -->
                                    <div class="absolute w-4 h-4 border-2 border-{'green' if emotional_labor_this_week["감정조절의 노력 및 다양성"] <= cutoff_emotional_labor[0] else 'red'}-600 rounded-full bg-white transform -translate-x-1/2 left-1/2 z-10"
                                        style="top: {100 - emotional_labor_this_week["감정조절의 노력 및 다양성"]}%;"></div>
                                    <!-- 회사 평균 마커 - 사각형 -->
                                    <div class="absolute w-4 h-4 border-1 border-black bg-white transform -translate-x-1/2 left-1/2"
                                        style="top: {100 - company_emotional_labor_this_week["감정조절의 노력 및 다양성"]}%;"></div>
                                </div>
                            </div>
                        </div>
                        <div class="text-xs text-center mt-2 h-8">감정조절의 노력 및 다양성</div>
                    </div>

                    <!-- 두번째 컬럼 -->
                    <div class="flex flex-col items-center">
                        <div class="flex justify-center w-full h-52">
                            <div class="border border-black rounded-lg p-3 flex justify-center h-full w-20">
                                <div class="relative h-full w-1 mx-auto">
                                    <!-- 위험 구간  - 위쪽 상단 -->
                                    <div class="absolute w-full bg-red-400" style="height: {100 - cutoff_emotional_labor[1]}%; top: 0;"></div>

                                    <!-- 정상 구간  - 아래쪽 -->
                                    <div class="absolute w-full bg-green-400" style="height: {cutoff_emotional_labor[1]}%; top: {100 - cutoff_emotional_labor[1]}%;">
                                    </div>

                                    <!-- 사용자 점수 마커 - 원 -->
                                    <div class="absolute w-4 h-4 border-2 border-{'green' if emotional_labor_this_week["고객응대의 과부하 및 갈등"] <= cutoff_emotional_labor[1] else 'red'}-600 rounded-full bg-white transform -translate-x-1/2 left-1/2 z-10"
                                        style="top: {100 - emotional_labor_this_week["고객응대의 과부하 및 갈등"]}%;"></div>
                                    <!-- 회사 평균 마커 - 사각형 -->
                                    <div class="absolute w-4 h-4 border-1 border-black bg-white transform -translate-x-1/2 left-1/2"
                                        style="top: {100 - company_emotional_labor_this_week["고객응대의 과부하 및 갈등"]}%;"></div>
                                </div>
                            </div>
                        </div>
                        <div class="text-xs text-center mt-2 h-8">고객응대의 과부하 및 갈등</div>
                    </div>

                    <!-- 세번째 컬럼 -->
                    <div class="flex flex-col items-center">
                        <div class="flex justify-center w-full h-52">
                            <div class="border border-black rounded-lg p-3 flex justify-center h-full w-20">
                                <div class="relative h-full w-1 mx-auto">
                                    <!-- 위험 구간  - 위쪽 상단 -->
                                    <div class="absolute w-full bg-red-400" style="height: {100 - cutoff_emotional_labor[2]}%; top: 0;"></div>

                                    <!-- 정상 구간  - 아래쪽 -->
                                    <div class="absolute w-full bg-green-400" style="height: {cutoff_emotional_labor[2]}%; top: {100 - cutoff_emotional_labor[2]}%;">
                                    </div>

                                    <!-- 사용자 점수 마커 - 원 -->
                                    <div class="absolute w-4 h-4 border-2 border-{'green' if emotional_labor_this_week["감정부조화 및 손상"] <= cutoff_emotional_labor[2] else 'red'}-600 rounded-full bg-white transform -translate-x-1/2 left-1/2 z-10"
                                        style="top: {100 - emotional_labor_this_week["감정부조화 및 손상"]}%;"></div>
                                    <!-- 회사 평균 마커 - 사각형 -->
                                    <div class="absolute w-4 h-4 border-1 border-black bg-white transform -translate-x-1/2 left-1/2"
                                        style="top: {100 - company_emotional_labor_this_week["감정부조화 및 손상"]}%;"></div>
                                </div>
                            </div>
                        </div>
                        <div class="text-xs text-center mt-2 h-8">감정부조화 및 손상</div>
                    </div>

                    <!-- 네번째 컬럼 -->
                    <div class="flex flex-col items-center">
                        <div class="flex justify-center w-full h-52">
                            <div class="border border-black rounded-lg p-3 flex justify-center h-full w-20">
                                <div class="relative h-full w-1 mx-auto">
                                    <!-- 위험 구간  - 위쪽 상단 -->
                                    <div class="absolute w-full bg-red-400" style="height: {100 - cutoff_emotional_labor[3]}%; top: 0;"></div>

                                    <!-- 정상 구간  - 아래쪽 -->
                                    <div class="absolute w-full bg-green-400" style="height: {cutoff_emotional_labor[3]}%; top: {100 - cutoff_emotional_labor[3]}%;">
                                    </div>

                                    <!-- 사용자 점수 마커 - 원 -->
                                    <div class="absolute w-4 h-4 border-2 border-{'green' if emotional_labor_this_week["조직의 감시 및 모니터링"] <= cutoff_emotional_labor[3] else 'red'}-600 rounded-full bg-white transform -translate-x-1/2 left-1/2 z-10"
                                        style="top: {100 - emotional_labor_this_week["조직의 감시 및 모니터링"]}%;"></div>
                                    <!-- 회사 평균 마커 - 사각형 -->
                                    <div class="absolute w-4 h-4 border-1 border-black bg-white transform -translate-x-1/2 left-1/2"
                                        style="top: {100 - company_emotional_labor_this_week["조직의 감시 및 모니터링"]}%;"></div>
                                </div>
                            </div>
                        </div>
                        <div class="text-xs text-center mt-2 h-8">조직의 감시 및 모니터링</div>
                    </div>

                    <!-- 다섯번째 컬럼 -->
                    <div class="flex flex-col items-center">
                        <div class="flex justify-center w-full h-52">
                            <div class="border border-black rounded-lg p-3 flex justify-center h-full w-20">
                                <div class="relative h-full w-1 mx-auto">
                                    <!-- 위험 구간  - 위쪽 상단 -->
                                    <div class="absolute w-full bg-red-400" style="height: {100 - cutoff_emotional_labor[4]}%; top: 0;"></div>

                                    <!-- 정상 구간  - 아래쪽 -->
                                    <div class="absolute w-full bg-green-400" style="height: {cutoff_emotional_labor[4]}%; top: {100 - cutoff_emotional_labor[4]}%;">
                                    </div>

                                    <!-- 사용자 점수 마커 - 원 -->
                                    <div class="absolute w-4 h-4 border-2 border-{'green' if emotional_labor_this_week["조직의 지지 및 보호체계"] <= cutoff_emotional_labor[4] else 'red'}-600 rounded-full bg-white transform -translate-x-1/2 left-1/2 z-10"
                                        style="top: {100 - emotional_labor_this_week["조직의 지지 및 보호체계"]}%;"></div>
                                    <!-- 회사 평균 마커 - 사각형 -->
                                    <div class="absolute w-4 h-4 border-1 border-black bg-white transform -translate-x-1/2 left-1/2"
                                        style="top: {100 - company_emotional_labor_this_week["조직의 지지 및 보호체계"]}%;"></div>
                                </div>
                            </div>
                        </div>
                        <div class="text-xs text-center mt-2 h-8">조직의 지지 및 보호체계</div>
                    </div>
                </div>
            </div>

        </div>
</body>

</html>
    """

    # 이제 안전하게 파일 열기 가능
    with open(
        f"data/reports/html/{name}_{week}주차.html", "w", encoding="utf-8"
    ) as file:
        # 파일 쓰기 작업 계속 진행
        file.write(html)

    # PDF 파일 생성
