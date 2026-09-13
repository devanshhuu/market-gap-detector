"""
supply_analysis.py
-------------------
MODULE 3: Supply-Side Analysis

What this does:
  For each category, estimates how well existing products already satisfy
  customers — i.e. how much "supply" already exists — using two signals:
    1. The proportion of positive reviews (rating >= 4) in that category
    2. How often positive reviews use satisfaction language
       ("love", "perfect", "great", "excellent", "satisfied")

  A category where most reviews are glowing has high supply (little gap
  left to fill). A category with few positive reviews has low supply
  (more room for a new/better product).

Run this after preprocess.py (it does not depend on demand_detection.py).
"""

import os
import pandas as pd

INPUT_PATH = os.path.join("data", "processed_reviews.csv")
OUTPUT_PATH = os.path.join("data", "supply_by_category.csv")

SATISFACTION_WORDS = ["love", "perfect", "great", "excellent", "satisfied", "amazing"]


def main():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"Could not find {INPUT_PATH}. Run preprocess.py first.")

    df = pd.read_csv(INPUT_PATH)

    def has_satisfaction_word(text):
        text = str(text)
        return any(word in text for word in SATISFACTION_WORDS)

    df["is_positive"] = df["rating"] >= 4
    df["has_satisfaction_language"] = df["clean_text"].apply(has_satisfaction_word)

    grouped = df.groupby("category").agg(
        total_reviews=("review_id", "count"),
        positive_reviews=("is_positive", "sum"),
        satisfaction_mentions=("has_satisfaction_language", "sum"),
    ).reset_index()

    grouped["positive_ratio"] = grouped["positive_reviews"] / grouped["total_reviews"]
    grouped["satisfaction_ratio"] = grouped["satisfaction_mentions"] / grouped["total_reviews"]

    # Supply Score = average of the two ratios (simple, explainable blend)
    grouped["supply_score"] = (grouped["positive_ratio"] + grouped["satisfaction_ratio"]) / 2

    result = grouped[["category", "supply_score"]].sort_values("supply_score", ascending=False)
    result.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved per-category supply scores to: {OUTPUT_PATH}")
    print("\nSupply scores by category:")
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
