import os
import sys
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_pipeline_for_file(input_file_path):
    data_dir = os.path.join(BASE_DIR, "data")
    os.makedirs(data_dir, exist_ok=True)
    target_path = os.path.join(data_dir, "raw_reviews.csv")

    if input_file_path and os.path.abspath(input_file_path) != os.path.abspath(target_path):
        shutil.copy(input_file_path, target_path)

    steps = [
        ("Module 1: Preprocessing", "preprocess.py"),
        ("Module 2: Demand Detection", "demand_detection.py"),
        ("Module 3: Supply Analysis", "supply_analysis.py"),
        ("Module 4: Gap Score Computation", "gap_score.py"),
    ]

    for label, script in steps:
        script_path = os.path.join(BASE_DIR, script)
        print(f"\nRunning {label} ({script_path})...")
        res = subprocess.run([sys.executable, script_path], cwd=BASE_DIR, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Error in {script}:\n{res.stderr}")

if __name__ == "__main__":
    run_pipeline_for_file(None)