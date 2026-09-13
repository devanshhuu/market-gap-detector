"""
gap_score.py
------------
MODULE 4: Gap Score Computation

What this does:
  1. Loads the per-category Demand Scores (Module 2) and Supply Scores (Module 3)
  2. Computes Gap Score = Demand Score - Supply Score for each category
  3. Uses a max-heap (Python's heapq) to rank categories from most to least
     underserved
  4. Attaches 2 supporting review quotes (evidence) to each category, taken
     from the highest-demand-weight reviews in that category
  5. Saves the final ranked report

Run this after demand_detection.py and supply_analysis.py.
"""

import os
import heapq
import pandas as pd

DEMAND_CATEGORY_PATH = os.path.join("data", "demand_by_category.csv")
DEMAND_REVIEW_PATH = os.path.join("data", "demand_by_review.csv")
SUPPLY_PATH = os.path.join("data", "supply_by_category.csv")
OUTPUT_PATH = os.path.join("data", "gap_results.csv")


def main():
    for path in (DEMAND_CATEGORY_PATH, DEMAND_REVIEW_PATH, SUPPLY_PATH):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Could not find {path}. Run demand_detection.py and supply_analysis.py first.")

    demand_df = pd.read_csv(DEMAND_CATEGORY_PATH)
    supply_df = pd.read_csv(SUPPLY_PATH)
    reviews_df = pd.read_csv(DEMAND_REVIEW_PATH)

    merged = pd.merge(demand_df, supply_df, on="category", how="inner")

    # Normalise both scores to the same 0-1 scale (min-max) before comparing
    # them, so a "high demand, low supply" category clearly comes out with
    # a positive Gap Score, and vice versa.
    def min_max(series):
        lo, hi = series.min(), series.max()
        if hi == lo:
            return series * 0
        return (series - lo) / (hi - lo)

    merged["demand_norm"] = min_max(merged["demand_score"])
    merged["supply_norm"] = min_max(merged["supply_score"])
    merged["gap_score"] = merged["demand_norm"] - merged["supply_norm"]

    # --- Rank using a max-heap (Data Structures requirement) ---
    heap = []
    for _, row in merged.iterrows():
        # heapq is a MIN-heap in Python, so we push the negative gap score
        # to effectively get max-heap behaviour.
        heapq.heappush(heap, (-row["gap_score"], row["category"], row["demand_score"], row["supply_score"]))

    ranked_rows = []
    rank = 1
    while heap:
        neg_gap, category, demand_score, supply_score = heapq.heappop(heap)
        gap_score = -neg_gap

        # Grab up to 2 supporting review quotes with the strongest demand weight
        evidence = (
            reviews_df[reviews_df["category"] == category]
            .sort_values("demand_weight", ascending=False)
            .head(2)["review_text"]
            .tolist()
        )

        ranked_rows.append({
            "rank": rank,
            "category": category,
            "demand_score": round(demand_score, 3),
            "supply_score": round(supply_score, 3),
            "gap_score": round(gap_score, 3),
            "evidence_1": evidence[0] if len(evidence) > 0 else "",
            "evidence_2": evidence[1] if len(evidence) > 1 else "",
        })
        rank += 1

    result_df = pd.DataFrame(ranked_rows)
    result_df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved ranked gap report to: {OUTPUT_PATH}\n")
    print("=" * 70)
    print("INTELLINICHE — RANKED MARKET GAP REPORT")
    print("=" * 70)
    for row in ranked_rows:
        print(f"\n#{row['rank']}  {row['category']}")
        print(f"    Demand: {row['demand_score']}   Supply: {row['supply_score']}   Gap: {row['gap_score']}")
        if row["evidence_1"]:
            print(f"    Evidence: \"{row['evidence_1']}\"")


if __name__ == "__main__":
    main()
