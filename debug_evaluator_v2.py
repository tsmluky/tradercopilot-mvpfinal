
import sys
import os
import time

# Ensure backend dir is in pythonpath
sys.path.append(os.path.abspath("backend"))

try:
    from evaluated_logger import evaluate_all_tokens, LITE_DIR, EVAL_DIR
    
    log_file = os.path.abspath("debug_evaluator_v2.log")
    
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("=== STARTING EVALUATOR DEBUG V2 ===\n")
        f.write(f"LITE_DIR: {LITE_DIR}\n")
        f.write(f"EVAL_DIR: {EVAL_DIR}\n")
        
        if not LITE_DIR.exists():
            f.write("LITE_DIR does not exist!\n")
        else:
            files = list(LITE_DIR.glob("*.csv"))
            f.write(f"Found {len(files)} CSV files in LITE_DIR: {[fo.name for fo in files]}\n")
            
        sys.stdout = f
        sys.stderr = f
        
        try:
            count, new_evals = evaluate_all_tokens()
            print(f"\n=== FINISHED: Processed {count} tokens, {new_evals} new evaluations ===")
        except Exception as e:
            print(f"\nCRASH DURING EVALUATION: {e}")
            import traceback
            traceback.print_exc()

    print(f"Debug finished. Check {log_file}")

except Exception as main_e:
    print(f"Failed to setup debug: {main_e}")
