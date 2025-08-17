import json
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os

# Set up Korean font support for matplotlib
plt.rcParams["font.family"] = ["DejaVu Sans", "Arial Unicode MS", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False


def load_factor_data(file_path):
    """Load positive and negative factors from JSON file"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    positive_factors = data["emotion_categories"]["positive"]["factors"]
    negative_factors = data["emotion_categories"]["negative"]["factors"]

    return positive_factors, negative_factors


def create_factor_comparison_chart(positive_factors, negative_factors, output_path):
    """Create a side-by-side comparison chart of positive vs negative factors"""

    # Get all unique factors and sort them by total count (descending)
    all_factors = set(positive_factors.keys()) | set(negative_factors.keys())
    factor_totals = {}
    for factor in all_factors:
        pos_count = positive_factors.get(factor, 0)
        neg_count = negative_factors.get(factor, 0)
        factor_totals[factor] = pos_count + neg_count

    # Sort factors by total count (descending)
    sorted_factors = sorted(all_factors, key=lambda x: factor_totals[x], reverse=True)

    # Prepare data for plotting
    pos_counts = [positive_factors.get(factor, 0) for factor in sorted_factors]
    neg_counts = [negative_factors.get(factor, 0) for factor in sorted_factors]

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(14, 10))

    # Set up bar positions
    x = np.arange(len(sorted_factors))
    width = 0.35

    # Create bars
    bars_pos = ax.bar(
        x - width / 2,
        pos_counts,
        width,
        label="긍정적 감정",
        color="cornflowerblue",
        alpha=0.8,
    )
    bars_neg = ax.bar(
        x + width / 2,
        neg_counts,
        width,
        label="부정적 감정",
        color="indianred",
        alpha=0.8,
    )

    # Add value labels on bars
    for i, (pos_count, neg_count) in enumerate(zip(pos_counts, neg_counts)):
        if pos_count > 0:
            ax.text(
                i - width / 2,
                pos_count + max(pos_counts + neg_counts) * 0.01,
                f"{pos_count:,}",
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=10,
            )
        if neg_count > 0:
            ax.text(
                i + width / 2,
                neg_count + max(pos_counts + neg_counts) * 0.01,
                f"{neg_count:,}",
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=10,
            )

    # Customize the chart
    ax.set_xlabel("감정 영향 요인", fontsize=14, fontweight="bold")
    ax.set_ylabel("요인 수", fontsize=14, fontweight="bold")
    ax.set_title(
        "감정별 영향 요인 분석\n(긍정적 감정 vs 부정적 감정)",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(sorted_factors, rotation=45, ha="right", fontsize=12)
    ax.legend(fontsize=12, loc="upper right")
    ax.grid(axis="y", alpha=0.3)

    # Add summary statistics
    total_pos = sum(pos_counts)
    total_neg = sum(neg_counts)
    total_all = total_pos + total_neg

    summary_text = f"총 긍정 요인 수: {total_pos:,} ({total_pos/total_all*100:.1f}%)\n"
    summary_text += f"총 부정 요인 수: {total_neg:,} ({total_neg/total_all*100:.1f}%)\n"
    summary_text += f"전체 요인 수: {total_all:,}"

    ax.text(
        0.7,
        0.6,
        summary_text,
        transform=ax.transAxes,
        fontsize=11,
        verticalalignment="top",
    )

    # Adjust layout
    plt.tight_layout()

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the chart
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Factor comparison chart saved to: {output_path}")


def create_stacked_percentage_chart(positive_factors, negative_factors, output_path):
    """Create a stacked percentage chart showing factor distribution"""

    # Get all unique factors
    all_factors = set(positive_factors.keys()) | set(negative_factors.keys())
    factor_totals = {}
    for factor in all_factors:
        pos_count = positive_factors.get(factor, 0)
        neg_count = negative_factors.get(factor, 0)
        factor_totals[factor] = pos_count + neg_count

    # Sort factors by total count (descending)
    sorted_factors = sorted(all_factors, key=lambda x: factor_totals[x], reverse=True)

    # Calculate percentages
    pos_percentages = []
    neg_percentages = []

    for factor in sorted_factors:
        pos_count = positive_factors.get(factor, 0)
        neg_count = negative_factors.get(factor, 0)
        total = pos_count + neg_count

        if total > 0:
            pos_percentages.append(pos_count / total * 100)
            neg_percentages.append(neg_count / total * 100)
        else:
            pos_percentages.append(0)
            neg_percentages.append(0)

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(14, 8))

    # Create stacked bar chart
    x = np.arange(len(sorted_factors))
    bars_pos = ax.bar(
        x, pos_percentages, label="긍정적 감정", color="cornflowerblue", alpha=0.8
    )
    bars_neg = ax.bar(
        x,
        neg_percentages,
        bottom=pos_percentages,
        label="부정적 감정",
        color="indianred",
        alpha=0.8,
    )

    # Add percentage labels
    for i, (pos_pct, neg_pct) in enumerate(zip(pos_percentages, neg_percentages)):
        if pos_pct > 5:  # Only show label if percentage is > 5%
            ax.text(
                i,
                pos_pct / 2,
                f"{pos_pct:.1f}%",
                ha="center",
                va="center",
                fontweight="bold",
                color="white",
                fontsize=10,
            )
        if neg_pct > 5:  # Only show label if percentage is > 5%
            ax.text(
                i,
                pos_pct + neg_pct / 2,
                f"{neg_pct:.1f}%",
                ha="center",
                va="center",
                fontweight="bold",
                color="white",
                fontsize=10,
            )

    # Customize the chart
    ax.set_xlabel("감정 영향 요인", fontsize=14, fontweight="bold")
    ax.set_ylabel("비율 (%)", fontsize=14, fontweight="bold")
    ax.set_title(
        "요인별 긍정/부정 감정 비율 분포", fontsize=16, fontweight="bold", pad=20
    )
    ax.set_xticks(x)
    ax.set_xticklabels(sorted_factors, rotation=45, ha="right", fontsize=12)
    ax.legend(fontsize=12, loc="upper right")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", alpha=0.3)

    # Adjust layout
    plt.tight_layout()

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the chart
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Percentage chart saved to: {output_path}")


def main():
    """Main function to create factor visualizations"""

    # File paths
    input_file = "data/figures/final/app_analysis_final.json"
    output_file_1 = "data/figures/final/5-감정별_영향요인_비교.png"
    output_file_2 = "data/figures/final/5-요인별_감정비율_분포.png"

    try:
        # Load factor data
        print("Loading factor data...")
        positive_factors, negative_factors = load_factor_data(input_file)

        print("Positive factors:")
        for factor, count in sorted(
            positive_factors.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {factor}: {count:,}")

        print("\nNegative factors:")
        for factor, count in sorted(
            negative_factors.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {factor}: {count:,}")

        # Create comparison chart
        print(f"\nCreating factor comparison chart...")
        create_factor_comparison_chart(
            positive_factors, negative_factors, output_file_1
        )

        # Create percentage chart
        print(f"Creating percentage distribution chart...")
        create_stacked_percentage_chart(
            positive_factors, negative_factors, output_file_2
        )

        print("Factor analysis completed successfully!")

    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file}")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")


if __name__ == "__main__":
    main()
