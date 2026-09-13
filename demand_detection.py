"""
demand_detection.py
--------------------
MODULE 2: Demand-Language Detection (NLP)

What this does:
  1. Loads the cleaned reviews (data/processed_reviews.csv)
  2. Builds a TF-IDF model over all review text, so we know which words are
     unusually important in a given review vs the whole dataset
  3. Checks each review against a lexicon of "need phrases" (things people
     say when something is missing, e.g. "wish it had", "still waiting for")
  4. Scores each review's demand strength, then averages this per category
  5. Saves per-review results and per-category Demand Scores

Run this after preprocess.py.
"""

import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

INPUT_PATH = os.path.join("data", "processed_reviews.csv")
REVIEW_OUTPUT_PATH = os.path.join("data", "demand_by_review.csv")
CATEGORY_OUTPUT_PATH = os.path.join("data", "demand_by_category.csv")

# Phrases that typically signal an unmet need. Feel free to add your own.
NEED_PHRASES = [
    "wish it had", "wish it came with", "needs a", "need a",
    "no option for", "missing a", "missing an", "still waiting for",
    "would be great if", "doesn't have", "does not have", "lacks a",
    "should include", "there's no", "there is no",
]


def main():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"Could not find {INPUT_PATH}. Run preprocess.py first.")

    # Speed limit added (nrows=5000) for instant execution
    df = pd.read_csv(INPUT_PATH, nrows=5000)
    texts = df["clean_text"].astype(str).tolist()

    # Build TF-IDF over the dataset (1-word and 2-word phrases)
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    vectorizer.fit(texts)
    vocab = vectorizer.vocabulary_
    idf = vectorizer.idf_  # higher idf = rarer / more distinctive word

    def phrase_weight(phrase):
        """Average IDF weight of the words in a matched phrase (fallback 1.0)."""
        words = [w for w in phrase.split() if w in vocab]
        if not words:
            return 1.0
        return sum(idf[vocab[w]] for w in words) / len(words)

    def score_review(text):
        matched_phrase = None
        weight = 0.0
        for phrase in NEED_PHRASES:
            if phrase in text:
                w = phrase_weight(phrase)
                if w > weight:
                    weight = w
                    matched_phrase = phrase
        return pd.Series([matched_phrase, weight])

    df[["matched_phrase", "demand_weight"]] = df["clean_text"].apply(score_review)

    # Normalise weights to a clean 0-1 "Demand Score" for readability
    max_weight = df["demand_weight"].max()
    df["demand_score"] = df["demand_weight"] / max_weight if max_weight > 0 else 0.0

    df.to_csv(REVIEW_OUTPUT_PATH, index=False)
    print(f"Saved per-review demand scores to: {REVIEW_OUTPUT_PATH}")

    # Aggregate to per-category Demand Score (mean demand_score per category)
    category_scores = (
        df.groupby("category")["demand_score"]
        .mean()
        .reset_index()
        .rename(columns={"demand_score": "demand_score"})
        .sort_values("demand_score", ascending=False)
    )
    category_scores.to_csv(CATEGORY_OUTPUT_PATH, index=False)
    print(f"Saved per-category demand scores to: {CATEGORY_OUTPUT_PATH}")
    print("\nTop categories by demand:")
    print(category_scores.to_string(index=False))


if __name__ == "__main__":
    main()