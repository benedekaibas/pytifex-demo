# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "typeguard",
#     "beartype",
# ]
# ///

"""
Compare comprehensive_eval (old) vs comprehensive_eval_v2 (new) side by side.

Usage:
    python compare_eval.py generated_examples/2026-01-27_19-33-16/results.json
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass

from comprehensive_eval import evaluate_comprehensive as eval_old
from comprehensive_eval_v2 import evaluate_comprehensive as eval_new


@dataclass
class FileComparison:
    filename: str
    old_tier1_count: int
    new_tier1_count: int
    old_verdicts: dict[str, dict]
    new_verdicts: dict[str, dict]
    new_found_extra_bugs: bool


def compare_file(
    source_code: str,
    checker_outputs: dict[str, str],
    filename: str,
) -> FileComparison:
    old_result = eval_old(source_code, checker_outputs, filename)
    new_result = eval_new(source_code, checker_outputs, filename)

    new_found_extra = len(new_result.tier1_bugs) > len(old_result.tier1_bugs)

    return FileComparison(
        filename=filename,
        old_tier1_count=len(old_result.tier1_bugs),
        new_tier1_count=len(new_result.tier1_bugs),
        old_verdicts=old_result.checker_verdicts,
        new_verdicts=new_result.checker_verdicts,
        new_found_extra_bugs=new_found_extra,
    )


def print_comparison_table(
    comparisons: list[FileComparison],
    checkers: list[str],
) -> None:
    checker_col_width = max(len(c) for c in checkers) + 2
    file_col_width = max(len(c.filename) for c in comparisons) + 2
    file_col_width = max(file_col_width, 10)

    header = (
        f"{'File':<{file_col_width}}"
        f"{'T1 Old':>8}"
        f"{'T1 New':>8}"
        f"  "
    )
    for checker in checkers:
        header += f"{'Old ' + checker:>{checker_col_width + 4}}"
        header += f"{'New ' + checker:>{checker_col_width + 4}}"
    print(header)
    print("-" * len(header))

    for comp in comparisons:
        row = (
            f"{comp.filename:<{file_col_width}}"
            f"{comp.old_tier1_count:>8}"
            f"{comp.new_tier1_count:>8}"
            f"  "
        )
        for checker in checkers:
            old_v = comp.old_verdicts.get(checker, {}).get("verdict", "N/A")
            new_v = comp.new_verdicts.get(checker, {}).get("verdict", "N/A")
            old_short = old_v[:3] if old_v != "N/A" else "N/A"
            new_short = new_v[:3] if new_v != "N/A" else "N/A"
            row += f"{old_short:>{checker_col_width + 4}}"
            row += f"{new_short:>{checker_col_width + 4}}"
        print(row)


def print_verdict_diffs(
    comparisons: list[FileComparison],
    checkers: list[str],
) -> None:
    print("\n" + "=" * 70)
    print("VERDICT DIFFERENCES (per checker)")
    print("=" * 70)

    any_diff = False
    for comp in comparisons:
        diffs = []
        for checker in checkers:
            old_v = comp.old_verdicts.get(checker, {}).get("verdict", "N/A")
            new_v = comp.new_verdicts.get(checker, {}).get("verdict", "N/A")
            if old_v != new_v:
                diffs.append((checker, old_v, new_v))
        if diffs:
            any_diff = True
            print(f"\n  {comp.filename}:")
            for checker, old_v, new_v in diffs:
                print(f"    {checker}: {old_v} -> {new_v}")

    if not any_diff:
        print("\n  No verdict differences found.")


def determine_recommendation(comparisons: list[FileComparison], checkers: list[str]) -> str:
    total_old_t1 = sum(c.old_tier1_count for c in comparisons)
    total_new_t1 = sum(c.new_tier1_count for c in comparisons)

    old_incorrect = 0
    new_incorrect = 0
    old_correct = 0
    new_correct = 0
    new_false_positives = 0

    for comp in comparisons:
        for checker in checkers:
            old_v = comp.old_verdicts.get(checker, {}).get("verdict", "UNCERTAIN")
            new_v = comp.new_verdicts.get(checker, {}).get("verdict", "UNCERTAIN")
            if old_v == "INCORRECT":
                old_incorrect += 1
            if new_v == "INCORRECT":
                new_incorrect += 1
            if old_v == "CORRECT":
                old_correct += 1
            if new_v == "CORRECT":
                new_correct += 1
            if old_v == "CORRECT" and new_v == "INCORRECT":
                new_false_positives += 1

    improved = (
        total_new_t1 > total_old_t1
        or new_incorrect > old_incorrect
        or new_correct > old_correct
    )

    if new_false_positives > 0:
        return "KEEP OLD"
    if improved:
        return "APPROVE"
    return "KEEP OLD"


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python compare_eval.py <results.json>")
        sys.exit(1)

    results_arg = sys.argv[1]
    tc_dir = Path(__file__).resolve().parent
    results_path = (tc_dir / results_arg).resolve()

    if not results_path.exists():
        results_path = Path(results_arg).resolve()
    if not results_path.exists():
        print(f"Error: {results_arg} not found")
        sys.exit(1)

    with open(results_path) as f:
        data = json.load(f)

    results = data.get("results", [])
    checkers = data.get("checkers_used", ["mypy", "pyrefly", "zuban", "ty"])

    print("=" * 70)
    print("COMPARISON: comprehensive_eval (old) vs comprehensive_eval_v2 (new)")
    print("=" * 70)
    print(f"Results file: {results_path}")
    print(f"Files to evaluate: {len(results)}")
    print()

    comparisons: list[FileComparison] = []

    for i, file_entry in enumerate(results, 1):
        filepath = file_entry.get("filepath", "")
        filename = file_entry.get("filename", "")
        outputs = file_entry.get("outputs", {})

        resolved = (tc_dir / filepath).resolve()
        if not resolved.exists():
            print(f"[{i}/{len(results)}] {filename} - SKIPPED (file not found: {resolved})")
            continue

        source_code = resolved.read_text()
        print(f"[{i}/{len(results)}] {filename} ... ", end="", flush=True)

        comp = compare_file(source_code, outputs, filename)
        comparisons.append(comp)

        t1_change = ""
        if comp.new_tier1_count > comp.old_tier1_count:
            t1_change = " [NEW BUGS FOUND]"
        elif comp.new_tier1_count < comp.old_tier1_count:
            t1_change = " [BUGS LOST]"
        print(f"T1: {comp.old_tier1_count}->{comp.new_tier1_count}{t1_change}")

    if not comparisons:
        print("\nNo files could be evaluated.")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("COMPARISON TABLE")
    print("=" * 70 + "\n")
    print_comparison_table(comparisons, checkers)

    print_verdict_diffs(comparisons, checkers)

    total_old_t1 = sum(c.old_tier1_count for c in comparisons)
    total_new_t1 = sum(c.new_tier1_count for c in comparisons)
    files_with_extra = sum(1 for c in comparisons if c.new_found_extra_bugs)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Total Tier 1 bugs (old): {total_old_t1}")
    print(f"  Total Tier 1 bugs (new): {total_new_t1}")
    print(f"  Files where v2 found more bugs: {files_with_extra}")

    recommendation = determine_recommendation(comparisons, checkers)
    print("\n" + "=" * 70)
    print(f"  RECOMMENDATION: {recommendation}")
    print("=" * 70)


if __name__ == "__main__":
    main()
