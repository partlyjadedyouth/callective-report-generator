import json
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from typing import List, Dict, Optional
import sys
import os

# 절단점 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from cutoff_values import CUTOFF_BURNOUT_PRIMARY


def load_analysis_data(file_path: str = "data/analysis/analysis.json") -> Dict:
    """
    분석 데이터를 JSON 파일에서 로드합니다.

    Args:
        file_path (str): JSON 파일 경로

    Returns:
        Dict: 로드된 분석 데이터
    """
    try:
        # JSON 파일을 열고 데이터를 로드합니다
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        # 파일이 존재하지 않는 경우 에러를 발생시킵니다
        raise FileNotFoundError(f"분석 데이터 파일을 찾을 수 없습니다: {file_path}")
    except json.JSONDecodeError:
        # JSON 파싱 에러가 발생한 경우 에러를 발생시킵니다
        raise ValueError(f"JSON 파일 파싱 중 오류가 발생했습니다: {file_path}")


def get_team2_participants(data: Dict) -> List[Dict]:
    """
    상담 2팀에 속한 팀원들의 데이터를 필터링합니다.

    Args:
        data (Dict): 전체 분석 데이터

    Returns:
        List[Dict]: 상담 2팀 팀원들의 데이터 리스트
    """
    # participants 리스트에서 상담 2팀 소속 팀원들만 필터링합니다
    team2_participants = [
        participant
        for participant in data.get("participants", [])
        if participant.get("team") == "상담 2팀"
    ]
    return team2_participants


def extract_bat_primary_scores(
    participants: List[Dict], week: str
) -> Dict[str, Optional[float]]:
    """
    지정된 주차의 BAT_primary 점수를 추출합니다.

    Args:
        participants (List[Dict]): 팀원 데이터 리스트
        week (str): 주차 (예: "0주차", "2주차")

    Returns:
        Dict[str, Optional[float]]: 팀원 이름을 키로 하고 BAT_primary 점수를 값으로 하는 딕셔너리
    """
    scores = {}

    # 각 팀원의 데이터를 순회합니다
    for participant in participants:
        name = participant.get("name", "Unknown")  # 팀원 이름을 가져옵니다
        analysis = participant.get("analysis", {})  # 분석 데이터를 가져옵니다

        # 지정된 주차의 데이터가 있는지 확인합니다
        if week in analysis:
            week_data = analysis[week]
            # BAT_primary 점수를 추출합니다
            bat_primary = week_data.get("category_averages", {}).get("BAT_primary")
            scores[name] = bat_primary
        else:
            # 해당 주차 데이터가 없는 경우 None으로 설정합니다
            scores[name] = None

    return scores


def setup_korean_font():
    """
    한글 폰트를 설정합니다.
    """
    try:
        # 시스템에서 사용 가능한 한글 폰트를 찾습니다
        font_candidates = [
            "AppleGothic",  # macOS
            "Malgun Gothic",  # Windows
            "NanumGothic",  # Linux
            "DejaVu Sans",  # Fallback
        ]

        # 사용 가능한 첫 번째 폰트를 설정합니다
        for font_name in font_candidates:
            try:
                plt.rcParams["font.family"] = font_name
                break
            except:
                continue

        # 마이너스 기호가 깨지지 않도록 설정합니다
        plt.rcParams["axes.unicode_minus"] = False

    except Exception as e:
        # 폰트 설정에 실패한 경우 기본 설정을 사용합니다
        print(f"폰트 설정 중 오류 발생: {e}")
        print("기본 폰트를 사용합니다.")


def create_bar_chart(
    scores: Dict[str, Optional[float]], week: str, save_path: Optional[str] = None
):
    """
    BAT_primary 점수의 가로 막대 그래프를 생성합니다.

    Args:
        scores (Dict[str, Optional[float]]): 팀원별 점수 데이터
        week (str): 주차 정보
        save_path (Optional[str]): 그래프 저장 경로 (None이면 화면에 표시)
    """
    # 한글 폰트를 설정합니다
    setup_korean_font()

    # None이 아닌 점수만 필터링합니다
    valid_scores = {name: score for name, score in scores.items() if score is not None}

    # 데이터가 없는 경우 처리합니다
    if not valid_scores:
        print(f"상담 2팀의 {week} BAT_primary 데이터가 없습니다.")
        return

    # 참가자 구분을 위한 색상 팔레트를 정의합니다
    color_palette = [
        "#E41A1C",  # Red
        "#377EB8",  # Blue
        "#4DAF4A",  # Green
        "#984EA3",  # Purple
        "#FF7F00",  # Orange
        "#FFFF33",  # Yellow
        "#F781BF",  # Pink
        "#00CED1",  # Cyan
        "#A65628",  # Brown
        "#999999",  # Gray
        "#6A5ACD",  # Dark Slate Blue
        "#66C2A5",  # Teal
    ]

    # 데이터를 분리합니다
    names = list(valid_scores.keys())  # 팀원 이름 리스트 (내부적으로만 사용)
    values = list(valid_scores.values())  # BAT_primary 점수 리스트

    # 참가자 수만큼 색상을 할당합니다 (색상이 부족하면 반복)
    colors = [color_palette[i % len(color_palette)] for i in range(len(values))]

    # 그래프 크기를 설정합니다
    plt.figure(figsize=(10, 8))

    # 가로 막대 그래프를 생성합니다
    bars = plt.barh(
        range(len(values)),
        values,
        color=colors,
        alpha=0.8,
        edgecolor="black",
        linewidth=1,
    )

    # 각 막대 끝에 점수 값을 표시합니다
    for i, (bar, value) in enumerate(zip(bars, values)):
        plt.text(
            bar.get_width() + 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.2f}",
            ha="left",
            va="center",
            fontsize=10,
            fontweight="bold",
        )

    # 그래프 제목과 축 라벨을 설정합니다
    plt.title(
        f"상담 2팀 {week} BAT_primary 점수", fontsize=16, fontweight="bold", pad=20
    )
    plt.xlabel("BAT_primary 점수", fontsize=12, fontweight="bold")
    plt.ylabel("참가자", fontsize=12, fontweight="bold")

    # y축 라벨을 참가자 번호로 설정합니다 (이름 대신 번호 사용)
    participant_labels = [f"참가자 {i+1}" for i in range(len(values))]
    plt.yticks(range(len(values)), participant_labels)

    # x축 범위를 설정합니다 (0부터 5까지, BAT 척도 범위)
    plt.xlim(0, 5.5)

    # 절단점을 수직선으로 표시합니다
    # 정상-준위험 경계선 (2.58)
    plt.axvline(
        x=CUTOFF_BURNOUT_PRIMARY[0],
        color="orange",
        linestyle="--",
        linewidth=2,
        alpha=0.8,
        label=f"정상-준위험 경계 ({CUTOFF_BURNOUT_PRIMARY[0]})",
    )

    # 준위험-위험 경계선 (3.01)
    plt.axvline(
        x=CUTOFF_BURNOUT_PRIMARY[1],
        color="red",
        linestyle="--",
        linewidth=2,
        alpha=0.8,
        label=f"준위험-위험 경계 ({CUTOFF_BURNOUT_PRIMARY[1]})",
    )

    # 위험도 구간을 배경색으로 표시합니다
    plt.axvspan(
        0, CUTOFF_BURNOUT_PRIMARY[0], alpha=0.1, color="green", label="정상 구간"
    )
    plt.axvspan(
        CUTOFF_BURNOUT_PRIMARY[0],
        CUTOFF_BURNOUT_PRIMARY[1],
        alpha=0.1,
        color="orange",
        label="준위험 구간",
    )
    plt.axvspan(
        CUTOFF_BURNOUT_PRIMARY[1], 5.5, alpha=0.1, color="red", label="위험 구간"
    )

    # 범례를 추가합니다
    plt.legend(loc="upper right", fontsize=9)

    # 격자를 추가합니다
    plt.grid(True, alpha=0.3, linestyle="--", axis="x")

    # 레이아웃을 조정합니다
    plt.tight_layout()

    # 그래프를 저장하거나 표시합니다
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"그래프가 저장되었습니다: {save_path}")
    else:
        plt.show()


def visualize_team2_bat_primary(
    week: str,
    data_path: str = "data/analysis/analysis.json",
    save_path: Optional[str] = None,
):
    """
    상담 2팀의 지정된 주차 BAT_primary 점수를 시각화합니다.

    Args:
        week (str): 시각화할 주차 (예: "0주차", "2주차")
        data_path (str): 분석 데이터 파일 경로
        save_path (Optional[str]): 그래프 저장 경로 (None이면 화면에 표시)
    """
    try:
        # 분석 데이터를 로드합니다
        print("분석 데이터를 로드하는 중...")
        data = load_analysis_data(data_path)

        # 상담 2팀 팀원들을 필터링합니다
        print("상담 2팀 팀원들을 필터링하는 중...")
        team2_participants = get_team2_participants(data)

        # 팀원 수를 출력합니다
        print(f"상담 2팀 팀원 수: {len(team2_participants)}명")

        # BAT_primary 점수를 추출합니다
        print(f"{week} BAT_primary 점수를 추출하는 중...")
        scores = extract_bat_primary_scores(team2_participants, week)

        # 추출된 점수 정보를 출력합니다
        valid_count = sum(1 for score in scores.values() if score is not None)
        print(f"유효한 {week} 데이터: {valid_count}/{len(scores)}명")

        # 막대 그래프를 생성합니다
        print("막대 그래프를 생성하는 중...")
        create_bar_chart(scores, week, save_path)

        print("시각화가 완료되었습니다!")

    except Exception as e:
        # 오류가 발생한 경우 에러 메시지를 출력합니다
        print(f"시각화 중 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    # 스크립트가 직접 실행될 때의 예시 코드입니다

    # 2주차 데이터 시각화 예시
    print("\n=== 상담 2팀 2주차 BAT_primary 시각화 ===")
    visualize_team2_bat_primary("2주차")
