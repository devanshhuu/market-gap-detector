import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DATA_PATH = os.path.join("data", "gap_results.csv")
OUTPUT_DIR = "output"

def generate_dashboard():
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} not found. Please run gap_score.py first.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_csv(DATA_PATH)

    # Top 10 categories for plotting
    top_10 = df.head(10)

    # Styling
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))

    # Barplot
    bar_chart = sns.barplot(
        data=top_10,
        x="gap_score",
        y="category",
        palette="Blues_r"
    )

    plt.title("Top 10 Market Opportunities (Gap Scores)", fontsize=14, fontweight="bold")
    plt.xlabel("Market Gap Score (Higher = Bigger Opportunity)", fontsize=11)
    plt.ylabel("Category / Product", fontsize=11)
    plt.xlim(0, 1.0)

    for p in bar_chart.patches:
        width = p.get_width()
        bar_chart.annotate(
            f"{width:.2f}",
            (width, p.get_y() + p.get_height() / 2.),
            ha='left', va='center',
            xytext=(5, 0),
            textcoords='offset points',
            fontsize=9
        )

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, "market_gap_dashboard.png")
    plt.savefig(output_path, dpi=300)
    print(f"Dashboard saved successfully at: {output_path}")
    plt.show()

if __name__ == "__main__":
    generate_dashboard()