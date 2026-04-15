"""
Generate research tables for Pytifex paper from 2026 experimental runs.

Produces a spreadsheet (research_tables.xlsx) with 7 tabs:
  Table 1: Generation Effectiveness (RQ1)
  Table 2: Disagreement Category Distribution (RQ2)
  Table 3: Pairwise Checker Disagreement Matrix (RQ2)
  Table 4: Checker Correctness by Tier (RQ3)
  Table 5: Precision / Recall / F1 / Weighted Score (RQ3)
  Table 6: Code Metrics Summary (RQ4)
  Table 7: Seed Source Effectiveness (RQ5)

Usage:
    python generate_research_tables.py
"""

import json
import os
import re
import glob
import statistics
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

from code_metrics import compute_metrics, metrics_to_dict

BASE_DIR = Path(__file__).resolve().parent / "generated_examples"
OUTPUT_DIR = Path(__file__).resolve().parent / "research_tables"
CHECKERS = ["mypy", "pyrefly", "zuban", "ty"]

# Only include 2026 runs
YEAR_PREFIX = "2026-"

# Exclude yesterday's runs (today is 2026-04-01, so exclude 2026-03-31)
EXCLUDE_PREFIXES = ["2026-03-31"]


def load_all_runs() -> list[dict]:
    """Load all 2026 results.json files (excluding yesterday)."""
    runs = []
    for results_path in sorted(glob.glob(str(BASE_DIR / "2026-*" / "results.json"))):
        run_dir = os.path.dirname(results_path)
        run_name = os.path.basename(run_dir)

        if any(run_name.startswith(p) for p in EXCLUDE_PREFIXES):
            continue

        with open(results_path) as f:
            data = json.load(f)

        eval_path = os.path.join(run_dir, "evaluation_comprehensive.json")
        eval_data = None
        if os.path.exists(eval_path):
            with open(eval_path) as f:
                eval_data = json.load(f)

        runs.append({
            "name": run_name,
            "dir": run_dir,
            "data": data,
            "eval": eval_data,
        })

    return runs


def table1_generation_effectiveness(runs: list[dict]) -> list[list]:
    """Table 1: Generation effectiveness per run."""
    headers = ["Run", "Model", "Total Generated", "Disagreements", "Success Rate (%)"]
    rows = [headers]

    for run in runs:
        data = run["data"]
        model = data.get("model_used", "N/A")
        total = data.get("total_generated", "N/A")
        disagree = data.get("disagreements_found", len(data.get("results", [])))
        rate = data.get("success_rate", "N/A")

        if total != "N/A" and isinstance(total, int) and total > 0:
            rate_val = f"{disagree / total * 100:.1f}"
        elif isinstance(rate, str) and rate != "N/A":
            rate_val = rate.rstrip("%")
        else:
            rate_val = "N/A"

        rows.append([run["name"], model, total, disagree, rate_val])

    # Summary row
    valid_rates = [float(r[4]) for r in rows[1:] if r[4] != "N/A"]
    valid_totals = [r[2] for r in rows[1:] if isinstance(r[2], int)]
    valid_disagree = [r[3] for r in rows[1:] if isinstance(r[3], int)]

    if valid_rates:
        rows.append([
            "SUMMARY",
            "",
            sum(valid_totals) if valid_totals else "N/A",
            sum(valid_disagree) if valid_disagree else "N/A",
            f"{statistics.mean(valid_rates):.1f} (mean)",
        ])

    return rows


def table2_disagreement_categories(runs: list[dict]) -> list[list]:
    """Table 2: Disagreement categories based on filename patterns and seed issues."""
    category_count = Counter()
    category_examples = defaultdict(list)

    CATEGORY_PATTERNS = {
        "Protocol": r"protocol",
        "TypedDict": r"typed.?dict",
        "ParamSpec": r"param.?spec|concatenate",
        "TypeGuard / TypeIs": r"type.?guard|type.?is|narrowing",
        "Generics": r"generic|typevar|bounded",
        "NewType": r"new.?type",
        "Overloads": r"overload",
        "Final": r"final",
        "Decorators": r"decorator|wrapper",
        "Inheritance / Override": r"inherit|override|subclass|super|lsp",
        "Callable": r"callable|callback",
        "Variance": r"covarian|contravarian|variance",
    }

    for run in runs:
        for result in run["data"].get("results", []):
            filename = result.get("filename", "").lower()
            seed = (result.get("seed_issue") or "").lower()
            combined = f"{filename} {seed}"

            matched = False
            for category, pattern in CATEGORY_PATTERNS.items():
                if re.search(pattern, combined):
                    category_count[category] += 1
                    category_examples[category].append(filename)
                    matched = True
                    break
            if not matched:
                category_count["Other"] += 1
                category_examples["Other"].append(filename)

    total = sum(category_count.values())
    headers = ["Category", "Count", "Percentage (%)", "Example Files"]
    rows = [headers]

    for category, count in category_count.most_common():
        pct = f"{count / total * 100:.1f}" if total > 0 else "0"
        examples = ", ".join(category_examples[category][:3])
        rows.append([category, count, pct, examples])

    rows.append(["TOTAL", total, "100.0", ""])
    return rows


def table3_pairwise_disagreement(runs: list[dict]) -> list[list]:
    """Table 3: Pairwise checker disagreement matrix."""
    pair_disagree = Counter()
    pair_total = Counter()

    for run in runs:
        for result in run["data"].get("results", []):
            statuses = result.get("statuses", {})
            if not statuses:
                continue

            for c1, c2 in combinations(CHECKERS, 2):
                s1 = statuses.get(c1)
                s2 = statuses.get(c2)
                if s1 is None or s2 is None:
                    continue
                pair_total[(c1, c2)] += 1
                if s1 != s2:
                    pair_disagree[(c1, c2)] += 1

    # Build matrix
    headers = ["Checker"] + CHECKERS
    rows = [headers]

    for c1 in CHECKERS:
        row = [c1]
        for c2 in CHECKERS:
            if c1 == c2:
                row.append("—")
            else:
                key = (c1, c2) if (c1, c2) in pair_total else (c2, c1)
                total = pair_total.get(key, 0)
                disagree = pair_disagree.get(key, 0)
                if total > 0:
                    row.append(f"{disagree}/{total} ({disagree/total*100:.0f}%)")
                else:
                    row.append("0/0")
        rows.append(row)

    return rows


def table4_checker_correctness_by_tier(runs: list[dict]) -> list[list]:
    """Table 4: Checker correctness by evaluation tier."""
    # tier -> checker -> verdict -> count
    tier_stats = defaultdict(lambda: defaultdict(lambda: Counter()))

    for run in runs:
        eval_data = run["eval"]
        if not eval_data:
            continue

        verdicts_list = eval_data.get("oracle_verdicts", eval_data.get("results", []))
        for entry in verdicts_list:
            verdicts = entry.get("verdicts", {})
            for checker, v in verdicts.items():
                if isinstance(v, dict):
                    verdict = v.get("verdict", "UNCERTAIN")
                    tier = v.get("tier", 4)
                else:
                    verdict = str(v)
                    tier = 4
                tier_stats[tier][checker][verdict] += 1

    headers = ["Tier", "Checker", "CORRECT", "INCORRECT", "UNCERTAIN", "Total"]
    rows = [headers]

    for tier in sorted(tier_stats.keys()):
        for checker in CHECKERS:
            stats = tier_stats[tier].get(checker, Counter())
            correct = stats.get("CORRECT", 0)
            incorrect = stats.get("INCORRECT", 0)
            uncertain = stats.get("UNCERTAIN", 0)
            total = correct + incorrect + uncertain
            if total > 0:
                rows.append([tier, checker, correct, incorrect, uncertain, total])

    return rows


def table5_precision_recall_f1(runs: list[dict]) -> list[list]:
    """Table 5: Precision / Recall / F1 across all evaluated files."""
    checker_stats = {c: {"tp": 0, "fp": 0, "fn": 0, "correct": 0, "incorrect": 0, "uncertain": 0} for c in CHECKERS}

    for run in runs:
        eval_data = run["eval"]
        if not eval_data:
            continue

        verdicts_list = eval_data.get("oracle_verdicts", eval_data.get("results", []))
        for entry in verdicts_list:
            verdicts = entry.get("verdicts", {})
            has_bug = (
                len(entry.get("tier1_bugs", [])) > 0
                or len(entry.get("tier2_bugs", [])) > 0
                or len(entry.get("tier3_findings", [])) > 0
            )

            for checker in CHECKERS:
                v = verdicts.get(checker, {})
                verdict = v.get("verdict", "UNCERTAIN") if isinstance(v, dict) else str(v)
                checker_stats[checker][verdict.lower()] = checker_stats[checker].get(verdict.lower(), 0)

                if verdict == "CORRECT":
                    checker_stats[checker]["correct"] += 1
                    if has_bug:
                        checker_stats[checker]["tp"] += 1
                elif verdict == "INCORRECT":
                    checker_stats[checker]["incorrect"] += 1
                    if has_bug:
                        checker_stats[checker]["fn"] += 1
                    else:
                        checker_stats[checker]["fp"] += 1
                else:
                    checker_stats[checker]["uncertain"] += 1

    headers = ["Checker", "CORRECT", "INCORRECT", "UNCERTAIN", "TP", "FP", "FN", "Precision", "Recall", "F1"]
    rows = [headers]

    for checker in CHECKERS:
        s = checker_stats[checker]
        tp, fp, fn = s["tp"], s["fp"], s["fn"]
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        rows.append([
            checker,
            s["correct"], s["incorrect"], s["uncertain"],
            tp, fp, fn,
            f"{precision:.3f}", f"{recall:.3f}", f"{f1:.3f}",
        ])

    return rows


def table6_code_metrics(runs: list[dict]) -> list[list]:
    """Table 6: Code metrics summary across all generated files."""
    all_metrics = {"loc": [], "num_functions": [], "type_imports": [], "type_density": [], "internal_calls": []}

    for run in runs:
        for result in run["data"].get("results", []):
            filepath = result.get("filepath", "")
            if not filepath or not os.path.exists(filepath):
                continue

            with open(filepath) as f:
                source = f.read()

            m = compute_metrics(source)
            all_metrics["loc"].append(m.loc)
            all_metrics["num_functions"].append(m.num_functions)
            all_metrics["type_imports"].append(m.type_imports)
            all_metrics["type_density"].append(m.type_density)
            all_metrics["internal_calls"].append(m.internal_calls)

    headers = ["Metric", "Mean", "Median", "Std Dev", "Min", "Max", "N"]
    rows = [headers]

    labels = {
        "loc": "Lines of Code",
        "num_functions": "Functions",
        "type_imports": "Type Imports",
        "type_density": "Type Density",
        "internal_calls": "Internal Calls",
    }

    for key, label in labels.items():
        values = all_metrics[key]
        if not values:
            continue
        rows.append([
            label,
            f"{statistics.mean(values):.2f}",
            f"{statistics.median(values):.2f}",
            f"{statistics.stdev(values):.2f}" if len(values) > 1 else "0.00",
            f"{min(values):.2f}",
            f"{max(values):.2f}",
            len(values),
        ])

    return rows


def table7_seed_effectiveness(runs: list[dict]) -> list[list]:
    """Table 7: GitHub seed vs pattern-only generation effectiveness."""
    seed_stats = {"with_seed": {"total": 0, "disagree": 0}, "no_seed": {"total": 0, "disagree": 0}}
    seed_repo_stats = Counter()

    for run in runs:
        data = run["data"]
        total = data.get("total_generated")
        disagree = data.get("disagreements_found", len(data.get("results", [])))

        if total is None or not isinstance(total, int):
            continue

        # Check if run used seeds (look at seed_issue fields)
        has_seeds = any(
            r.get("seed_issue") for r in data.get("results", [])
        )

        if has_seeds:
            seed_stats["with_seed"]["total"] += total
            seed_stats["with_seed"]["disagree"] += disagree
        else:
            seed_stats["no_seed"]["total"] += total
            seed_stats["no_seed"]["disagree"] += disagree

        for result in data.get("results", []):
            seed = result.get("seed_issue", "")
            if seed:
                # Extract repo name
                match = re.search(r"(?:github\.com/)?(\w+/\w+)", seed)
                if match:
                    seed_repo_stats[match.group(1)] += 1

    headers = ["Strategy", "Total Generated", "Disagreements", "Success Rate (%)"]
    rows = [headers]

    for strategy, label in [("with_seed", "GitHub Seeds"), ("no_seed", "Pattern-Only")]:
        s = seed_stats[strategy]
        rate = f"{s['disagree'] / s['total'] * 100:.1f}" if s["total"] > 0 else "N/A"
        rows.append([label, s["total"], s["disagree"], rate])

    # Add seed source breakdown
    rows.append([])
    rows.append(["Seed Source Repo", "Files Seeded", "", ""])
    for repo, count in seed_repo_stats.most_common():
        rows.append([repo, count, "", ""])

    return rows


def save_csv(rows: list[list], filepath: str):
    """Save table rows as CSV."""
    import csv
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def save_xlsx(all_tables: dict[str, list[list]], filepath: str):
    """Save all tables as sheets in an xlsx workbook."""
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    except ImportError:
        print("[WARNING] openpyxl not installed, saving as CSV instead")
        for name, rows in all_tables.items():
            safe_name = re.sub(r"[^\w]", "_", name)
            save_csv(rows, os.path.join(OUTPUT_DIR, f"{safe_name}.csv"))
        return

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    header_font = Font(bold=True, size=11)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font_white = Font(bold=True, size=11, color="FFFFFF")
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    for sheet_name, rows in all_tables.items():
        ws = wb.create_sheet(title=sheet_name[:31])

        for r_idx, row in enumerate(rows):
            for c_idx, val in enumerate(row):
                cell = ws.cell(row=r_idx + 1, column=c_idx + 1, value=val)
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="center", vertical="center")

                if r_idx == 0:
                    cell.font = header_font_white
                    cell.fill = header_fill

        for col in ws.columns:
            max_len = 0
            for cell in col:
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

    wb.save(filepath)
    print(f"[SUCCESS] Spreadsheet saved: {filepath}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading 2026 experimental runs...")
    runs = load_all_runs()
    print(f"Found {len(runs)} runs\n")

    if not runs:
        print("[ERROR] No runs found")
        return

    print("Generating tables...")
    all_tables = {}

    print("  Table 1: Generation Effectiveness")
    all_tables["T1 Generation"] = table1_generation_effectiveness(runs)

    print("  Table 2: Disagreement Categories")
    all_tables["T2 Categories"] = table2_disagreement_categories(runs)

    print("  Table 3: Pairwise Disagreements")
    all_tables["T3 Pairwise"] = table3_pairwise_disagreement(runs)

    print("  Table 4: Correctness by Tier")
    all_tables["T4 Tier Correctness"] = table4_checker_correctness_by_tier(runs)

    print("  Table 5: Precision Recall F1")
    all_tables["T5 PRF1"] = table5_precision_recall_f1(runs)

    print("  Table 6: Code Metrics")
    all_tables["T6 Code Metrics"] = table6_code_metrics(runs)

    print("  Table 7: Seed Effectiveness")
    all_tables["T7 Seeds"] = table7_seed_effectiveness(runs)

    # Save as xlsx
    xlsx_path = os.path.join(OUTPUT_DIR, "research_tables.xlsx")
    save_xlsx(all_tables, xlsx_path)

    # Also save individual CSVs as backup
    for name, rows in all_tables.items():
        safe_name = re.sub(r"[^\w]", "_", name)
        csv_path = os.path.join(OUTPUT_DIR, f"{safe_name}.csv")
        save_csv(rows, csv_path)
        print(f"  CSV: {csv_path}")

    # Print preview
    print("\n" + "=" * 70)
    print("TABLE PREVIEWS")
    print("=" * 70)
    for name, rows in all_tables.items():
        print(f"\n--- {name} ---")
        for row in rows[:8]:
            print("  " + " | ".join(str(v) for v in row))
        if len(rows) > 8:
            print(f"  ... ({len(rows) - 1} data rows total)")


if __name__ == "__main__":
    main()
