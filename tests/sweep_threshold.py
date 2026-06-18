# tests/sweep_threshold.py
"""Threshold sweep: run the test set across multiple thresholds.

Reveals which thresholds maximize correct behavior, and which test cases
are threshold-fixable vs blocked regardless (corpus gaps / Layer 2 refusals).

Run with: python -m tests.sweep_threshold
"""
from tests.test_eval import TEST_CASES, evaluate_case

THRESHOLDS = [0.35, 0.40, 0.45, 0.50, 0.55, 0.60]

def confusion_matrix(results):
    tp = fp = tn = fn = 0
    for r in results:
        should_answer = not r["expected_blocked"]
        answered = not r["blocked"]
        if should_answer and answered:
            tp += 1     
        elif should_answer and not answered:
            fn += 1 
        elif not should_answer and answered:
            fp += 1
        else:
            tn += 1
    return {"TP": tp, "FP": fp, "TN": tn, "FN": fn}

def run_sweep():
    print("\n" + "=" * 70)
    print("THRESHOLD SWEEP")
    print("=" * 70 + "\n")

    all_results = {}

    for threshold in THRESHOLDS:
        results = [evaluate_case(case, threshold=threshold) for case in TEST_CASES]
        all_results[threshold] = results
        passed = sum(1 for r in results if r["passed"])
        total = len(results)

        cm = confusion_matrix(results)
        print(f"Threshold {threshold:.2f}: {passed}/{total} passed  "
              f"| TP {cm['TP']} FN {cm['FN']} FP {cm['FP']} TN {cm['TN']}")

    print("\n" + "=" * 70)
    print("PER-CASE BREAKDOWN (✅ = passed at that threshold)")
    print("=" * 70 + "\n")

    header = "Case                          " + "  ".join(f"{t:.2f}" for t in THRESHOLDS)
    print(header)
    print("-" * len(header))

    for i, case in enumerate(TEST_CASES):
        label = f"{case['id']:>2} {case['type']:<12} "
        marks = []
        for threshold in THRESHOLDS:
            r = all_results[threshold][i]
            marks.append(" ✅ " if r["passed"] else " ❌ ")
        print(label + " ".join(marks))

    print("\n" + "=" * 70)
    return all_results




if __name__ == "__main__":
    run_sweep()