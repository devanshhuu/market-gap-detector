"""
generate_sample_data.py
------------------------
Creates a synthetic (fake but realistic) product review dataset so you can
run the whole IntelliNiche pipeline immediately, without needing a Kaggle
account or an internet connection.

Once this works, Step 9 of the README shows you how to swap this file out
for a real dataset downloaded from Kaggle.

Run this file first, before anything else.
"""

import csv
import random
import os

random.seed(42)  # keeps the "random" data the same every time you run this

OUTPUT_PATH = os.path.join("data", "raw_reviews.csv")

# Each category has its own list of features that reviewers might be happy
# about (supply) or wishing for (demand).
CATEGORY_FEATURES = {
    "Home & Kitchen - Storage": [
        "stackable design", "airtight lids", "a larger size option",
        "dishwasher-safe material", "clear labels",
    ],
    "Electronics - Wearables": [
        "a longer battery life", "a heart rate sensor", "GPS tracking",
        "a bigger display", "water resistance",
    ],
    "Electronics - Audio": [
        "noise cancellation", "a carrying case", "Bluetooth 5.0",
        "better bass", "a mute button",
    ],
    "Home & Kitchen - Cookware": [
        "an induction-safe base", "a non-stick coating", "a matching lid",
        "oven-safe handles", "even heat distribution",
    ],
    "Electronics - Accessories": [
        "a charging cable included", "multiple color options",
        "a protective case", "compatibility with older models", "a warranty card",
    ],
}

# How often each category gets a "wish it had X" review vs a happy review vs
# a plain neutral review. This is what makes some categories end up with a
# bigger demand-supply GAP than others once you run the pipeline.
CATEGORY_MIX = {
    "Home & Kitchen - Storage":  {"need": 0.60, "positive": 0.20, "neutral": 0.20},
    "Electronics - Wearables":   {"need": 0.50, "positive": 0.30, "neutral": 0.20},
    "Electronics - Audio":       {"need": 0.40, "positive": 0.40, "neutral": 0.20},
    "Home & Kitchen - Cookware": {"need": 0.30, "positive": 0.50, "neutral": 0.20},
    "Electronics - Accessories": {"need": 0.20, "positive": 0.60, "neutral": 0.20},
}

NEED_TEMPLATES = [
    "I really wish it had {feature}.",
    "This product is missing {feature}, which is disappointing.",
    "Still waiting for a version with {feature}.",
    "Would be great if it came with {feature}.",
    "There's no option for {feature}, which is frustrating.",
    "It doesn't have {feature}, otherwise it would be perfect.",
    "Needs {feature} in the next update.",
]

POSITIVE_TEMPLATES = [
    "Absolutely love this, {feature} works perfectly.",
    "Great quality and {feature} is exactly what I needed.",
    "Perfect purchase, it even has {feature}.",
    "Very satisfied, {feature} exceeded my expectations.",
    "Excellent product, {feature} is really well designed.",
]

NEUTRAL_TEMPLATES = [
    "It's okay, does the job.",
    "Average product for the price.",
    "Works as expected, nothing special.",
    "Decent, but not amazing.",
]


def make_review(category, kind):
    features = CATEGORY_FEATURES[category]
    feature = random.choice(features)
    if kind == "need":
        text = random.choice(NEED_TEMPLATES).format(feature=feature)
        rating = random.choice([2, 2, 3])
    elif kind == "positive":
        text = random.choice(POSITIVE_TEMPLATES).format(feature=feature)
        rating = random.choice([4, 5, 5])
    else:
        text = random.choice(NEUTRAL_TEMPLATES)
        rating = random.choice([3, 4])
    return text, rating


def main():
    os.makedirs("data", exist_ok=True)
    rows = []
    review_id = 10000

    for category, mix in CATEGORY_MIX.items():
        n_reviews = 120
        for _ in range(n_reviews):
            roll = random.random()
            if roll < mix["need"]:
                kind = "need"
            elif roll < mix["need"] + mix["positive"]:
                kind = "positive"
            else:
                kind = "neutral"

            text, rating = make_review(category, kind)
            review_id += 1
            rows.append([review_id, category, text, rating])

    # Add a handful of very short, low-value reviews on purpose, so the
    # preprocessing step in Module 1 has something real to filter out.
    for _ in range(40):
        category = random.choice(list(CATEGORY_FEATURES.keys()))
        review_id += 1
        rows.append([review_id, category, random.choice(["Good", "Nice", "Ok", "Fine"]), 4])

    random.shuffle(rows)

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["review_id", "category", "review_text", "rating"])
        writer.writerows(rows)

    print(f"Created {len(rows)} sample reviews at: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
