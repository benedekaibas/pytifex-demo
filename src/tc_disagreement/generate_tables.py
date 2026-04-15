"""
Generate research paper tables from evaluation JSON files.

Produces:
  Table 1: Code Metrics (LOC, functions, type imports, type density, internal calls)
  Table 2: Type Related Runtime Error Caught (TRREC)
  Table 2a: Non-Crash Construct Category Summary (per-construct checker error rates)
  Table 2b: Non-Crash Per-File Detail (construct, statuses, verdicts)
  Table 3: Checker Disagreement Summary (error/ok per checker per file)
  Table 4: Minority Checker Analysis (when one checker disagrees with the majority)
  Table 5: Per-Checker Accuracy Summary (correct/incorrect/uncertain counts)
  Table 6: Disagreement Pattern Distribution (4-0, 3-1, 2-2 splits)

Outputs: CSV files + combined XLSX workbook.

Usage:
    python generate_tables.py [--batches 2026-02-20_13-08-02 2026-03-04_21-27-35 ...]
    python generate_tables.py   # uses all Feb+March batches
"""

import json
import csv
import os
import sys
from pathlib import Path
from dataclasses import dataclass

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

try:
    from code_metrics import compute_metrics
except ImportError:
    from .code_metrics import compute_metrics

ROOT = Path(__file__).resolve().parent
GEN_DIR = ROOT / "generated_examples"
CHECKERS = ["mypy", "pyrefly", "zuban", "ty"]

DEFAULT_BATCHES = [
    "2026-02-15_15-56-33",
    "2026-02-18_23-27-53",
    "2026-02-20_13-08-02",
    "2026-03-02_20-17-37",
    "2026-03-04_21-27-35",
    "2026-03-25_12-52-32",
]


@dataclass
class FileRecord:
    filename: str
    batch: str
    filepath: str
    source_code: str
    statuses: dict[str, str]       # checker -> "ok"/"error"
    verdicts: dict[str, dict]      # checker -> {"verdict": ..., "reason": ...}
    agent_verdicts: dict[str, str] # checker -> final agent verdict (if any)
    tier1_bugs: list[dict]
    tier_reached: int
    metrics: dict


def load_all_records(batches: list[str]) -> list[FileRecord]:
    """Load and deduplicate records from all batches."""
    records: list[FileRecord] = []
    seen_filenames: set[str] = set()

    for batch in batches:
        rpath = GEN_DIR / batch / "results.json"
        epath = GEN_DIR / batch / "evaluation_comprehensive.json"
        if not rpath.exists() or not epath.exists():
            print(f"WARNING: skipping {batch} (missing files)")
            continue

        with open(rpath) as f:
            rdata = json.load(f)
        with open(epath) as f:
            edata = json.load(f)

        results = rdata.get("results", [])
        eval_results = edata.get("results", edata.get("oracle_verdicts", []))
        agent_list = edata.get("agent_verdicts", [])

        # Index eval results by filename
        eval_by_name = {e["filename"]: e for e in eval_results}
        # Index agent verdicts
        agent_by_file: dict[str, dict[str, str]] = {}
        for av in agent_list:
            fn = av.get("filename", "")
            c = av.get("checker", "")
            v = av.get("verdict", "UNCERTAIN")
            agent_by_file.setdefault(fn, {})[c] = v

        for r in results:
            fn = r["filename"]
            if fn in seen_filenames:
                continue
            seen_filenames.add(fn)

            filepath = r.get("filepath", "")
            source_code = ""
            if os.path.exists(filepath):
                with open(filepath) as f:
                    source_code = f.read()

            # Compute metrics from source
            if source_code:
                m = compute_metrics(source_code)
                metrics = {
                    "loc": m.loc,
                    "num_functions": m.num_functions,
                    "type_imports": m.type_imports,
                    "type_density": m.type_density,
                    "internal_calls": m.internal_calls,
                }
            else:
                metrics = r.get("metrics", {})

            ev = eval_by_name.get(fn, {})
            verdicts = ev.get("verdicts", {})
            tier1_bugs = ev.get("tier1_bugs", [])
            tier_reached = ev.get("tier_reached", -1)

            records.append(FileRecord(
                filename=fn,
                batch=batch,
                filepath=filepath,
                source_code=source_code,
                statuses=r.get("statuses", {}),
                verdicts=verdicts,
                agent_verdicts=agent_by_file.get(fn, {}),
                tier1_bugs=tier1_bugs,
                tier_reached=tier_reached,
                metrics=metrics,
            ))

    return records


def get_final_verdict(rec: FileRecord, checker: str) -> str:
    """Get the final verdict for a checker, preferring agent override."""
    if checker in rec.agent_verdicts:
        return rec.agent_verdicts[checker]
    v = rec.verdicts.get(checker, {})
    return v.get("verdict", "UNCERTAIN")


def get_verdict_reason(rec: FileRecord, checker: str) -> str:
    """Get the reason string for a verdict."""
    v = rec.verdicts.get(checker, {})
    return v.get("reason", "")


# =============================================================================
# TABLE 1: Code Metrics
# =============================================================================

def generate_table1(records: list[FileRecord]) -> list[list[str]]:
    headers = [
        "File",
        "LOC (NCSS)",
        "# Functions",
        "# Type Imports",
        "Type Density",
        "# Internal Calls",
    ]
    rows = [headers]
    for rec in records:
        m = rec.metrics
        rows.append([
            rec.filename,
            str(m.get("loc", 0)),
            str(m.get("num_functions", 0)),
            str(m.get("type_imports", 0)),
            str(m.get("type_density", 0.0)),
            str(m.get("internal_calls", 0)),
        ])
    return rows


# =============================================================================
# TABLE 2: Type Related Runtime Error Caught (TRREC)
# =============================================================================

def generate_table2(records: list[FileRecord]) -> list[list[str]]:
    headers = [
        "File",
        "Runtime Error (Yes/No)",
        "Error Type",
    ] + [f"{c} Caught" for c in CHECKERS]
    rows = [headers]

    for rec in records:
        has_crash = len(rec.tier1_bugs) > 0
        error_type = rec.tier1_bugs[0]["type"] if has_crash else ""

        checker_caught = []
        for c in CHECKERS:
            if not has_crash:
                checker_caught.append("")
            else:
                v = get_final_verdict(rec, c)
                reason = get_verdict_reason(rec, c)
                if v == "CORRECT" and "Caught" in reason:
                    checker_caught.append("✓")
                elif v == "INCORRECT" and "Missed" in reason:
                    checker_caught.append("✗")
                elif v == "INCORRECT" and "Caught" in reason and "missed" in reason.lower():
                    checker_caught.append("Partial")
                else:
                    checker_caught.append("?")

        rows.append([
            rec.filename,
            "Yes" if has_crash else "No",
            error_type,
        ] + checker_caught)

    return rows


# =============================================================================
# CONSTRUCT CATEGORIZATION
# =============================================================================

_CONSTRUCT_PREFIXES = [
    ("paramspec-", "ParamSpec"),
    ("typeguard-", "TypeGuard"),
    ("typeis-", "TypeIs"),
    ("typeddict-", "TypedDict"),
    ("typed-dict-", "TypedDict"),
    ("newtype-", "NewType"),
    ("self-", "Self"),
    ("dataclass-", "dataclass_transform"),
    ("protocol-", "Protocol"),
    ("overload-", "Overload"),
    ("callable-", "Callable"),
    ("match-", "Pattern Matching"),
    ("generic-", "Generic"),
    ("typealiastype-", "TypeAliasType"),
    ("typealias-", "TypeAliasType"),
    ("type-alias-", "TypeAliasType"),
    ("decorator-", "Decorator"),
    ("classvar-", "ClassVar"),
    ("literal-", "Literal"),
    ("literal_", "Literal"),
    ("walrus-", "Walrus/Comprehension"),
    ("walrus_", "Walrus/Comprehension"),
    ("asyncio-", "asyncio"),
    ("isinstance-", "isinstance/Protocol"),
    ("inherited-", "Inheritance"),
    ("mixed-tuple-", "Tuple/NewType"),
    ("tuple-", "Tuple"),
    ("typevartuple-", "TypeVarTuple"),
    ("pydantic-", "dataclass_transform"),
    ("getattr-", "ClassVar"),
    ("dictionary-", "TypedDict"),
]


def _categorize_file(filename: str) -> str:
    """Determine the primary typing construct category from the filename."""
    lower = filename.lower()
    for prefix, category in _CONSTRUCT_PREFIXES:
        if lower.startswith(prefix):
            return category
    return "Other"


# =============================================================================
# TABLE 2a: Non-Crash Construct Category Summary
# =============================================================================

def generate_table2a(records: list[FileRecord]) -> list[list[str]]:
    """Non-crash files grouped by typing construct category with per-checker error rates."""
    non_crash = [r for r in records if len(r.tier1_bugs) == 0]

    # Group by category
    categories: dict[str, list[FileRecord]] = {}
    for rec in non_crash:
        cat = _categorize_file(rec.filename)
        categories.setdefault(cat, []).append(rec)

    headers = [
        "Construct Category",
        "# Files",
        "Dominant Split",
    ] + [f"{c} Error Rate" for c in CHECKERS] + [
        "Avg Checkers Flagging",
    ]
    rows = [headers]

    for cat in sorted(categories.keys()):
        recs = categories[cat]
        n = len(recs)

        # Per-checker error rate
        checker_error_counts = {c: 0 for c in CHECKERS}
        split_counts: dict[str, int] = {}
        total_flagging = 0

        for rec in recs:
            flagging = 0
            for c in CHECKERS:
                if rec.statuses.get(c) == "error":
                    checker_error_counts[c] += 1
                    flagging += 1
            total_flagging += flagging

            # Compute split pattern
            error_count = sum(1 for c in CHECKERS if rec.statuses.get(c) == "error")
            ok_count = sum(1 for c in CHECKERS if rec.statuses.get(c) == "ok")
            if error_count == 0:
                pat = "4-0 (all ok)"
            elif ok_count == 0:
                pat = "0-4 (all error)"
            else:
                pat = f"{error_count}-{ok_count}"
            split_counts[pat] = split_counts.get(pat, 0) + 1

        dominant_split = max(split_counts, key=split_counts.get)
        dominant_pct = split_counts[dominant_split] / n * 100

        rows.append([
            cat,
            str(n),
            f"{dominant_split} ({dominant_pct:.0f}%)",
        ] + [
            f"{checker_error_counts[c]}/{n} ({checker_error_counts[c]/n*100:.0f}%)"
            for c in CHECKERS
        ] + [
            f"{total_flagging / n:.1f}",
        ])

    return rows


# =============================================================================
# TABLE 2b: Non-Crash Per-File Detail
# =============================================================================

def generate_table2b(records: list[FileRecord]) -> list[list[str]]:
    """Per-file detail for non-crash files: construct category, checker statuses, verdicts."""
    non_crash = [r for r in records if len(r.tier1_bugs) == 0]

    headers = [
        "File",
        "Construct",
    ] + [f"{c} Status" for c in CHECKERS] + [
        "Split",
    ] + [f"{c} Verdict" for c in CHECKERS]
    rows = [headers]

    for rec in sorted(non_crash, key=lambda r: _categorize_file(r.filename)):
        cat = _categorize_file(rec.filename)
        statuses = [rec.statuses.get(c, "?") for c in CHECKERS]
        error_count = sum(1 for s in statuses if s == "error")
        ok_count = sum(1 for s in statuses if s == "ok")
        if error_count == 0:
            split = "4-0"
        elif ok_count == 0:
            split = "0-4"
        else:
            split = f"{error_count}-{ok_count}"

        verdicts = [get_final_verdict(rec, c) for c in CHECKERS]

        rows.append([
            rec.filename,
            cat,
        ] + statuses + [
            split,
        ] + verdicts)

    return rows


# =============================================================================
# TABLE 3: Checker Disagreement Summary
# =============================================================================

def generate_table3(records: list[FileRecord]) -> list[list[str]]:
    headers = ["File"] + [f"{c} Status" for c in CHECKERS] + ["Split Pattern"]
    rows = [headers]

    for rec in records:
        statuses = [rec.statuses.get(c, "?") for c in CHECKERS]
        error_count = sum(1 for s in statuses if s == "error")
        ok_count = sum(1 for s in statuses if s == "ok")
        if error_count == 0:
            pattern = "4-0 (all ok)"
        elif ok_count == 0:
            pattern = "0-4 (all error)"
        else:
            pattern = f"{error_count}-{ok_count}"

        rows.append([rec.filename] + statuses + [pattern])

    return rows


# =============================================================================
# TABLE 4: Minority Checker Analysis
# =============================================================================

def generate_table4(records: list[FileRecord]) -> list[list[str]]:
    """For each file with a 3-1 split, identify the minority checker
    and whether the minority was correct or not."""
    headers = [
        "File",
        "Minority Checker",
        "Minority Position",
        "Majority Position",
        "Minority Verdict",
        "Minority Was Correct",
    ]
    rows = [headers]

    for rec in records:
        statuses = {c: rec.statuses.get(c, "?") for c in CHECKERS}
        error_checkers = [c for c in CHECKERS if statuses[c] == "error"]
        ok_checkers = [c for c in CHECKERS if statuses[c] == "ok"]

        # Only 3-1 splits
        if len(error_checkers) == 1:
            minority = error_checkers[0]
            minority_pos = "error"
            majority_pos = "ok"
        elif len(ok_checkers) == 1:
            minority = ok_checkers[0]
            minority_pos = "ok"
            majority_pos = "error"
        else:
            continue

        final_v = get_final_verdict(rec, minority)
        # Determine if minority was correct:
        # If minority says error and verdict is CORRECT -> minority was right
        # If minority says ok and verdict is CORRECT -> minority was right
        # If verdict is INCORRECT -> minority was wrong
        # If verdict is UNCERTAIN -> we can't tell
        if final_v == "CORRECT":
            was_correct = "Yes"
        elif final_v == "INCORRECT":
            was_correct = "No"
        else:
            was_correct = "Uncertain"

        rows.append([
            rec.filename,
            minority,
            minority_pos,
            majority_pos,
            final_v,
            was_correct,
        ])

    return rows


# =============================================================================
# TABLE 5: Per-Checker Accuracy Summary
# =============================================================================

def generate_table5(records: list[FileRecord]) -> list[list[str]]:
    headers = ["Checker", "CORRECT", "INCORRECT", "UNCERTAIN", "Total", "Accuracy (%)"]
    rows = [headers]

    for c in CHECKERS:
        correct = 0
        incorrect = 0
        uncertain = 0
        for rec in records:
            v = get_final_verdict(rec, c)
            if v == "CORRECT":
                correct += 1
            elif v == "INCORRECT":
                incorrect += 1
            else:
                uncertain += 1
        total = correct + incorrect + uncertain
        determined = correct + incorrect
        accuracy = f"{correct / determined * 100:.1f}" if determined > 0 else "N/A"
        rows.append([c, str(correct), str(incorrect), str(uncertain), str(total), accuracy])

    return rows


# =============================================================================
# TABLE 6: Disagreement Pattern Distribution
# =============================================================================

def generate_table6(records: list[FileRecord]) -> list[list[str]]:
    headers = ["Pattern", "Count", "Percentage", "Example Files"]
    patterns: dict[str, list[str]] = {}

    for rec in records:
        statuses = [rec.statuses.get(c, "?") for c in CHECKERS]
        error_count = sum(1 for s in statuses if s == "error")
        ok_count = sum(1 for s in statuses if s == "ok")

        if error_count == 0:
            key = "0 error / 4 ok (consensus ok)"
        elif ok_count == 0:
            key = "4 error / 0 ok (consensus error)"
        elif error_count == 1:
            key = "1 error / 3 ok"
        elif error_count == 3:
            key = "3 error / 1 ok"
        else:
            key = "2 error / 2 ok"

        patterns.setdefault(key, []).append(rec.filename)

    rows = [headers]
    total = len(records)
    for key in sorted(patterns.keys()):
        files = patterns[key]
        pct = f"{len(files) / total * 100:.1f}%"
        examples = ", ".join(files[:3])
        if len(files) > 3:
            examples += f" (+{len(files) - 3} more)"
        rows.append([key, str(len(files)), pct, examples])

    return rows


# =============================================================================
# TABLE 7: Per-Checker Minority Frequency
# =============================================================================

def generate_table7(records: list[FileRecord]) -> list[list[str]]:
    """How often each checker is the sole dissenter in 3-1 splits."""
    headers = [
        "Checker",
        "Times in Minority",
        "Minority as Error",
        "Minority as OK",
        "Correct When Minority",
        "Incorrect When Minority",
        "Uncertain When Minority",
    ]

    stats: dict[str, dict[str, int]] = {
        c: {"total": 0, "as_error": 0, "as_ok": 0, "correct": 0, "incorrect": 0, "uncertain": 0}
        for c in CHECKERS
    }

    for rec in records:
        statuses = {c: rec.statuses.get(c, "?") for c in CHECKERS}
        error_checkers = [c for c in CHECKERS if statuses[c] == "error"]
        ok_checkers = [c for c in CHECKERS if statuses[c] == "ok"]

        if len(error_checkers) == 1:
            minority = error_checkers[0]
            stats[minority]["total"] += 1
            stats[minority]["as_error"] += 1
        elif len(ok_checkers) == 1:
            minority = ok_checkers[0]
            stats[minority]["total"] += 1
            stats[minority]["as_ok"] += 1
        else:
            continue

        v = get_final_verdict(rec, minority)
        if v == "CORRECT":
            stats[minority]["correct"] += 1
        elif v == "INCORRECT":
            stats[minority]["incorrect"] += 1
        else:
            stats[minority]["uncertain"] += 1

    rows = [headers]
    for c in CHECKERS:
        s = stats[c]
        rows.append([
            c,
            str(s["total"]),
            str(s["as_error"]),
            str(s["as_ok"]),
            str(s["correct"]),
            str(s["incorrect"]),
            str(s["uncertain"]),
        ])

    return rows


# =============================================================================
# OUTPUT
# =============================================================================

def write_csv(rows: list[list[str]], path: str) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"  CSV: {path}")


def write_xlsx(all_tables: dict[str, list[list[str]]], path: str) -> None:
    if not HAS_OPENPYXL:
        print("  XLSX: skipped (openpyxl not installed)")
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
    correct_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    incorrect_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    uncertain_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")

    for sheet_name, rows in all_tables.items():
        ws = wb.create_sheet(title=sheet_name[:31])  # Excel 31 char limit

        for r_idx, row in enumerate(rows, 1):
            for c_idx, value in enumerate(row, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=value)
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

                if r_idx == 1:
                    cell.font = header_font_white
                    cell.fill = header_fill
                else:
                    if value == "CORRECT" or value == "✓" or value == "Yes":
                        cell.fill = correct_fill
                    elif value == "INCORRECT" or value == "✗" or value == "No":
                        cell.fill = incorrect_fill
                    elif value == "UNCERTAIN" or value == "?" or value == "Uncertain":
                        cell.fill = uncertain_fill

        # Auto-width columns
        for col in ws.columns:
            max_len = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    if cell.value:
                        max_len = max(max_len, len(str(cell.value)))
                except Exception:
                    pass
            ws.column_dimensions[col_letter].width = min(max_len + 4, 50)

    wb.save(path)
    print(f"  XLSX: {path}")


def main() -> int:
    batches = DEFAULT_BATCHES
    if "--batches" in sys.argv:
        idx = sys.argv.index("--batches")
        batches = sys.argv[idx + 1:]

    print("Loading records...")
    records = load_all_records(batches)
    print(f"Loaded {len(records)} unique files from {len(batches)} batches\n")

    if not records:
        print("ERROR: No records found")
        return 1

    out_dir = str(GEN_DIR)

    print("Generating tables...")
    tables = {
        "T1 Code Metrics": generate_table1(records),
        "T2 Runtime Errors": generate_table2(records),
        "T2a Construct Summary": generate_table2a(records),
        "T2b Non-Crash Detail": generate_table2b(records),
        "T3 Checker Statuses": generate_table3(records),
        "T4 Minority Analysis": generate_table4(records),
        "T5 Accuracy Summary": generate_table5(records),
        "T6 Split Distribution": generate_table6(records),
        "T7 Minority Frequency": generate_table7(records),
    }

    # Write individual CSVs
    csv_paths = {
        "T1 Code Metrics": os.path.join(out_dir, "table1_code_metrics.csv"),
        "T2 Runtime Errors": os.path.join(out_dir, "table2_runtime_errors.csv"),
        "T2a Construct Summary": os.path.join(out_dir, "table2a_construct_summary.csv"),
        "T2b Non-Crash Detail": os.path.join(out_dir, "table2b_non_crash_detail.csv"),
        "T3 Checker Statuses": os.path.join(out_dir, "table3_checker_statuses.csv"),
        "T4 Minority Analysis": os.path.join(out_dir, "table4_minority_analysis.csv"),
        "T5 Accuracy Summary": os.path.join(out_dir, "table5_accuracy_summary.csv"),
        "T6 Split Distribution": os.path.join(out_dir, "table6_split_distribution.csv"),
        "T7 Minority Frequency": os.path.join(out_dir, "table7_minority_frequency.csv"),
    }

    for name, rows in tables.items():
        write_csv(rows, csv_paths[name])

    # Write combined XLSX
    xlsx_path = os.path.join(out_dir, "paper_tables.xlsx")
    write_xlsx(tables, xlsx_path)

    # Print summary tables to stdout
    print("\n" + "=" * 80)
    for name, rows in tables.items():
        print(f"\n{'─' * 80}")
        print(f"  {name}")
        print(f"{'─' * 80}")
        # Calculate column widths
        widths = [0] * len(rows[0])
        for row in rows:
            for i, val in enumerate(row):
                widths[i] = max(widths[i], len(str(val)))
        widths = [min(w + 2, 45) for w in widths]

        for r_idx, row in enumerate(rows):
            line = "  ".join(str(v).ljust(widths[i]) for i, v in enumerate(row))
            print(f"  {line}")
            if r_idx == 0:
                print("  " + "─" * sum(widths))

    print(f"\n{'=' * 80}")
    print(f"Files saved to: {out_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
