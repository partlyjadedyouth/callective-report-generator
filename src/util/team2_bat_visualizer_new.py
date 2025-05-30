import json
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from scipy import stats
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


def extract_bat_primary_scores(participants: List[Dict], week: str) -> List[float]:
    """
    지정된 주차의 BAT_primary 점수를 추출합니다.

    Args:
        participants (List[Dict]): 팀원 데이터 리스트
        week (str): 주차 (예: "0주차", "2주차")

    Returns:
        List[float]: 유효한 BAT_primary 점수들의 리스트
    """
    scores = []

    # 디버깅을 위한 정보를 출력합니다
    print(f"\n=== {week} BAT_primary 점수 추출 과정 ===")
    print(f"총 참가자 수: {len(participants)}명")

    # 각 팀원의 데이터를 순회합니다
    for i, participant in enumerate(participants):
        name = participant.get("name", f"참가자_{i+1}")  # 참가자 이름을 가져옵니다
        analysis = participant.get("analysis", {})  # 분석 데이터를 가져옵니다

        # 지정된 주차의 데이터가 있는지 확인합니다
        if week in analysis:
            week_data = analysis[week]
            # BAT_primary 점수를 추출합니다
            bat_primary = week_data.get("category_averages", {}).get("BAT_primary")

            # 유효한 점수만 리스트에 추가합니다
            if bat_primary is not None:
                scores.append(bat_primary)
                print(f"  ✓ {name}: {bat_primary:.2f}")
            else:
                print(f"  ✗ {name}: BAT_primary 데이터 없음 (category_averages 문제)")
        else:
            print(f"  ✗ {name}: {week} 데이터 없음")

    print(f"유효한 점수 개수: {len(scores)}개")
    print("=" * 50)

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


def create_distribution_with_bars(
    scores: List[float], week: str, save_path: Optional[str] = None
):
    """
    BAT_primary 점수의 정규분포 그래프와 개별 참여자 점수를 막대로 표시합니다.

    Args:
        scores (List[float]): BAT_primary 점수 리스트
        week (str): 주차 정보
        save_path (Optional[str]): 그래프 저장 경로 (None이면 화면에 표시)
    """
    # 한글 폰트를 설정합니다
    setup_korean_font()

    # 데이터가 없는 경우 처리합니다
    if not scores:
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

    # 그래프 크기를 설정합니다
    plt.figure(figsize=(12, 8))

    # x축 범위를 설정합니다 (BAT 척도 범위: 0-5)
    x_range = np.linspace(0, 5, 100)

    # 점수들의 정규분포를 계산합니다
    if len(scores) > 1:
        # 점수가 2개 이상일 때 정규분포를 계산합니다
        mean_score = np.mean(scores)  # 평균을 계산합니다
        std_score = np.std(scores, ddof=1)  # 표준편차를 계산합니다 (표본 표준편차)

        # 정규분포 확률밀도함수를 계산합니다
        normal_density = stats.norm.pdf(x_range, mean_score, std_score)

        # 정규분포 곡선을 그립니다
        plt.plot(
            x_range,
            normal_density,
            "b-",
            linewidth=2,
            alpha=0.7,
            label=f"정규분포 (μ={mean_score:.2f}, σ={std_score:.2f})",
        )

        # 정규분포 곡선 아래 영역을 채웁니다
        plt.fill_between(x_range, normal_density, alpha=0.3, color="lightblue")
    else:
        # 점수가 1개만 있을 때는 수직선으로 표시합니다
        plt.axvline(
            x=scores[0], color="blue", linewidth=2, alpha=0.7, label="단일 점수"
        )

    # 각 참여자의 점수를 높이 0.2인 막대로 표시합니다
    bar_height = 0.2
    bar_width = 0.05  # 막대의 너비를 설정합니다

    # 겹치는 막대를 방지하기 위해 점수별로 정렬하고 오프셋을 적용합니다
    score_positions = []  # 각 점수의 실제 x 위치를 저장할 리스트

    # 각 점수에 대해 막대를 그립니다
    for i, score in enumerate(scores):
        # 색상을 순환하여 할당합니다
        color = color_palette[i % len(color_palette)]

        # 같은 점수 근처에 있는 다른 막대들과의 겹침을 방지하기 위한 오프셋 계산
        x_position = score
        offset_applied = False

        # 기존에 그려진 막대들과 너무 가까운지 확인합니다
        for existing_pos in score_positions:
            if (
                abs(x_position - existing_pos) < bar_width * 1.2
            ):  # 막대 너비의 1.2배 이내이면 겹침으로 판단
                # 작은 랜덤 오프셋을 적용합니다 (최대 ±0.02)
                offset = (i % 3 - 1) * 0.015  # -0.015, 0, +0.015 중 하나
                x_position = score + offset
                offset_applied = True
                break

        # 계산된 위치를 저장합니다
        score_positions.append(x_position)

        # 개별 참여자 점수를 막대로 표시합니다
        plt.bar(
            x_position,
            bar_height,
            width=bar_width,
            color=color,
            alpha=0.8,
            edgecolor="black",
            linewidth=1,
            label=f"참가자 {i+1}",  # 모든 참가자를 범례에 표시합니다
        )

        # 막대 위에 점수 값을 표시합니다 (오프셋 적용시 원래 점수 표시)
        plt.text(
            x_position,
            bar_height + 0.02,
            f"{score:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

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

    # 그래프 제목과 축 라벨을 설정합니다
    plt.title(
        f"상담 2팀 {week} BAT_primary 점수 정규분포 및 개별 점수",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    plt.xlabel("BAT_primary 점수", fontsize=12, fontweight="bold")
    plt.ylabel("확률밀도 / 개별 점수", fontsize=12, fontweight="bold")

    # x축 범위를 설정합니다 (0부터 5까지, BAT 척도 범위)
    plt.xlim(0, 5)

    # y축 범위를 0부터 1.0으로 고정합니다
    plt.ylim(0, 1.0)

    # 범례를 추가합니다 (모든 참가자를 표시하기 위해 조정)
    plt.legend(loc="upper right", fontsize=8, ncol=3, bbox_to_anchor=(1.0, 1.0))

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


def visualize_team2_bat_distribution(
    week: str,
    data_path: str = "data/analysis/analysis.json",
    save_path: Optional[str] = None,
):
    """
    상담 2팀의 지정된 주차 BAT_primary 점수 분포와 개별 점수를 시각화합니다.

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
        print(f"유효한 {week} 데이터: {len(scores)}개")
        print(
            f"점수 범위: {min(scores):.2f} - {max(scores):.2f}"
            if scores
            else "데이터 없음"
        )

        # 분포 그래프와 개별 점수 막대를 생성합니다
        print("분포 그래프와 개별 점수 막대를 생성하는 중...")
        create_distribution_with_bars(scores, week, save_path)

        print("시각화가 완료되었습니다!")

    except Exception as e:
        # 오류가 발생한 경우 에러 메시지를 출력합니다
        print(f"시각화 중 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    # 스크립트가 직접 실행될 때의 예시 코드입니다

    # 2주차 데이터 시각화 예시
    print("\n=== 상담 2팀 2주차 BAT_primary 분포 및 개별 점수 시각화 ===")
    visualize_team2_bat_distribution("2주차")
