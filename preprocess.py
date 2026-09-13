"""
preprocess.py
-------------
MODULE 1: Data Acquisition & Preprocessing

What this does:
  1. Loads the raw review CSV (data/raw_reviews.csv)
  2. Removes duplicate reviews
  3. Removes very short, low-value reviews (fewer than MIN_WORDS words)
  4. Cleans the text (lowercase, strips extra punctuation/whitespace)
  5. Saves the result to data/processed_reviews.csv

Run this after generate_sample_data.py (or after you've placed a real
Kaggle CSV at data/raw_reviews.csv).
"""

import os
import re
import pandas as pd

INPUT_PATH = os.path.join("data", "raw_reviews.csv")
OUTPUT_PATH = os.path.join("data", "processed_reviews.csv")
MIN_WORDS = 5  # reviews shorter than this are considered "low signal"


def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s']", " ", text)   # strip punctuation except apostrophes
    text = re.sub(r"\s+", " ", text).strip()     # collapse extra whitespace
    return text


def main():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(
            f"Could not find {INPUT_PATH}. Run generate_sample_data.py first, "
            "or place your own CSV there with columns: review_id, category, review_text, rating."
        )

    df = pd.read_csv(INPUT_PATH)
    start_count = len(df)
    print(f"Loaded {start_count} raw reviews.")

    # 1. Remove exact duplicate review texts
    df = df.drop_duplicates(subset="review_text")
    print(f"Removed {start_count - len(df)} duplicate reviews.")

    # 2. Clean the text
    df["clean_text"] = df["review_text"].apply(clean_text)

    # 3. Remove short / low-signal reviews
    before_filter = len(df)
    df["word_count"] = df["clean_text"].apply(lambda t: len(t.split()))
    df = df[df["word_count"] >= MIN_WORDS]
    print(f"Removed {before_filter - len(df)} short/low-signal reviews (< {MIN_WORDS} words).")

    df = df.drop(columns=["word_count"])

    os.makedirs("data", exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} cleaned reviews to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
