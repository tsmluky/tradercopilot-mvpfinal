
import sys
import os

# Ensure backend dir is in pythonpath
sys.path.append(os.path.abspath("backend"))

from evaluated_logger import evaluate_all_tokens, _eligible_signals_for_token, LITE_DIR

print("=== STARTING EVALUATOR DEBUG ===")
print(f"LITE_DIR: {LITE_DIR}")

if not LITE_DIR.exists():
    print("LITE_DIR does not exist!")
else:
    files = list(LITE_DIR.glob("*.csv"))
    print(f"Found {len(files)} CSV files in LITE_DIR: {[f.name for f in files]}")

count, new_evals = evaluate_all_tokens()
print(f"=== FINISHED: Processed {count} tokens, {new_evals} new evaluations ===")
