#!/usr/bin/env python3
"""
Research Table Generator for Pytifex
Generates LaTeX tables with booktabs style for academic papers.
"""

import json
import os
import sys
import subprocess
from dataclasses import dataclass, field
from typing import Optional

import csv


@dataclass
class ExampleResult:
    filename: str
    filepath: str
    seed_issue: str
    metrics: dict
    outputs: dict
    statuses: dict
    verdicts: dict = field(default_factory=dict)
    has_disagreement: bool = False
    minority_checkers: list = field(default_factory=list)
    majority_checkers: list = field(default_factory=list)
    tier3_findings: list = field(default_factory=list)


def load_examples(folders: list, base_dir: str) -> list[ExampleResult]:
    """Load examples from specified folders."""
    examples = []
    seen = set()

    for folder in folders:
        results_path = os.path.join(base_dir, folder, "results.json")
        eval_path = os.path.join(base_dir, folder, "evaluation_comprehensive.json")

        if not os.path.exists(results_path):
            continue

        with open(results_path) as f:
            results_data = json.load(f)

        verdicts = {}
        findings = {}
        if os.path.exists(eval_path):
            with open(eval_path) as f:
                eval_data = json.load(f)
                for ov in eval_data.get("oracle_verdicts", []):
                    verdicts[ov["filename"]] = ov.get("verdicts", {})
                    findings[ov["filename"]] = ov.get("tier3_findings", [])

        for r in results_data.get("results", []):
            if r["filename"] in seen:
                continue
            seen.add(r["filename"])

            statuses = r.get("statuses", {})
            has_disagreement = len(set(statuses.values())) > 1

            error_checkers = [c for c, s in statuses.items() if s == "error"]
            ok_checkers = [c for c, s in statuses.items() if s == "ok"]

            # Minority = the ones that are in the LOWER count group
            minority = (
                error_checkers
                if len(error_checkers) < len(ok_checkers)
                else ok_checkers
            )
            majority = (
                ok_checkers
                if len(error_checkers) < len(ok_checkers)
                else error_checkers
            )

            ex = ExampleResult(
                filename=r["filename"],
                filepath=r.get("filepath", ""),
                seed_issue=r.get("seed_issue", ""),
                metrics=r.get("metrics", {}),
                outputs=r.get("outputs", {}),
                statuses=statuses,
                verdicts=verdicts.get(r["filename"], {}),
                has_disagreement=has_disagreement,
                minority_checkers=minority,
                majority_checkers=majority,
                tier3_findings=findings.get(r["filename"], []),
            )
            examples.append(ex)

    return examples


def check_runtime_error(filepath: str, base_dir: str) -> tuple[bool, str]:
    """Check if code causes runtime error."""
    if not os.path.isabs(filepath):
        filepath = os.path.join(base_dir, filepath)

    if not os.path.exists(filepath):
        return False, "File not found"

    try:
        result = subprocess.run(
            [sys.executable, filepath], capture_output=True, text=True, timeout=10
        )
        return result.returncode != 0, result.stderr[:200] if result.stderr else ""
    except Exception as e:
        return True, str(e)


def get_verdict_correct(ex: ExampleResult, checker: str) -> Optional[bool]:
    """Get whether a checker's verdict was correct. Returns True/False/None."""
    verdict = ex.verdicts.get(checker, {}).get("verdict", "").upper()
    if verdict == "CORRECT":
        return True
    elif verdict == "INCORRECT":
        return False
    return None


def latex_escape(s: str) -> str:
    """Escape special LaTeX characters."""
    return s.replace("_", r"\_").replace("%", r"\%").replace("&", r"\&")


def generate_latex_document(examples: list, base_dir: str) -> str:
    """Generate complete LaTeX document."""

    disagreement_exs = [e for e in examples if e.has_disagreement]

    checker_stats = {
        c: {"correct": 0, "incorrect": 0, "uncertain": 0}
        for c in ["mypy", "pyrefly", "ty", "zuban"]
    }
    for ex in examples:
        for checker in ["mypy", "pyrefly", "ty", "zuban"]:
            verdict = ex.verdicts.get(checker, {}).get("verdict", "").upper()
            if verdict == "CORRECT":
                checker_stats[checker]["correct"] += 1
            elif verdict == "INCORRECT":
                checker_stats[checker]["incorrect"] += 1
            elif verdict == "UNCERTAIN":
                checker_stats[checker]["uncertain"] += 1

    checker_errors = {
        c: sum(1 for e in examples if e.statuses.get(c) == "error")
        for c in ["mypy", "pyrefly", "ty", "zuban"]
    }

    lines = [
        r"\documentclass{article}",
        r"\usepackage[margin=1in]{geometry}",
        r"\usepackage{booktabs}",
        r"\usepackage{longtable}",
        r"\usepackage{amssymb}",
        r"\usepackage{array}",
        r"\usepackage{hyperref}",
        r"\hypersetup{colorlinks=true, linkcolor=blue}",
        r"",
        r"\title{Type Checker Disagreement Analysis}",
        r"\author{Pytifex Research}",
        r"\date{\today}",
        r"",
        r"\begin{document}",
        r"\maketitle",
        r"\thispagestyle{empty}",
        r"\newpage",
        r"",
    ]

    # TABLE 1: Code Metrics
    lines.extend(
        [
            r"\section{Code Metrics}",
            r"\begin{table}[htbp]",
            r"\centering",
            r"\begin{tabular}{lrrrrr}",
            r"\toprule",
            r"File & LOC & Func. & Type Imports & Type Density & Interactions \\",
            r"\midrule",
        ]
    )

    for ex in examples:
        m = ex.metrics
        name = latex_escape(ex.filename[:45])
        lines.append(
            f"{name} & {m.get('loc', 0)} & {m.get('num_functions', 0)} & "
            f"{m.get('type_imports', 0)} & {m.get('type_density', 0):.3f} & {m.get('internal_calls', 0)} \\\\"
        )

    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption{Code Metrics for Type Checker Disagreement Examples}",
            r"\label{tab:metrics}",
            r"\end{table}",
            r"",
        ]
    )

    # TABLE 2: TRREC
    lines.extend(
        [
            r"\section{Type Related Runtime Error Caught (TRREC)}",
            r"\begin{longtable}{p{5cm}rrrrr}",
            r"\caption{TRREC - Checker Error Detection}\label{tab:trrec}\\",
            r"\toprule",
            r"File & Runtime & Mypy & Pyrefly & Ty & Zuban \\",
            r"\midrule",
            r"\endfirsthead",
            r"\toprule",
            r"File & Runtime & Mypy & Pyrefly & Ty & Zuban \\",
            r"\midrule",
            r"\endhead",
            r"\bottomrule",
            r"\endlastfoot",
        ]
    )

    runtime_error_count = 0
    for ex in examples:
        has_error, _ = check_runtime_error(ex.filepath, base_dir)
        if has_error:
            runtime_error_count += 1

        runtime_mark = r"\checkmark" if has_error else ""
        name = latex_escape(ex.filename[:45])

        row = [name, runtime_mark]
        for checker in ["mypy", "pyrefly", "ty", "zuban"]:
            mark = r"\checkmark" if ex.statuses.get(checker) == "error" else ""
            row.append(mark)

        lines.append(" & ".join(row) + " \\\\")

    lines.extend(
        [
            r"\bottomrule",
            r"\end{longtable}",
            r"",
            f"\\textit{{Summary:}} {runtime_error_count} files cause runtime errors. "
            f"Mypy detected errors in {checker_errors['mypy']} files, "
            f"Pyrefly in {checker_errors['pyrefly']}, "
            f"Ty in {checker_errors['ty']}, "
            f"Zuban in {checker_errors['zuban']}.",
            r"",
        ]
    )

    # TABLE 3: Disagreements with verdicts
    lines.extend(
        [
            r"\section{Disagreement Analysis}",
            r"\begin{longtable}{p{5cm}lc}",
            r"\caption{Disagreement Analysis - Minority Checkers and Verdicts}\label{tab:disagreements}\\",
            r"\toprule",
            r"File & Minority Checkers & Verdict \\",
            r"\midrule",
            r"\endfirsthead",
            r"\toprule",
            r"File & Minority Checkers & Verdict \\",
            r"\midrule",
            r"\endhead",
            r"\bottomrule",
            r"\endlastfoot",
        ]
    )

    for ex in disagreement_exs:
        name = latex_escape(ex.filename[:45])
        minority_str = (
            ", ".join(c.upper() for c in ex.minority_checkers)
            if ex.minority_checkers
            else "None"
        )

        minority_results = []
        for c in ex.minority_checkers:
            v = get_verdict_correct(ex, c)
            if v is True:
                minority_results.append(f"{c.upper()}: Correct")
            elif v is False:
                minority_results.append(f"{c.upper()}: Incorrect")
            else:
                minority_results.append(f"{c.upper()}: Uncertain")

        verdict_str = "; ".join(minority_results) if minority_results else "N/A"
        lines.append(f"{name} & {minority_str} & {verdict_str} \\\\")

    lines.extend(
        [
            r"\bottomrule",
            r"\end{longtable}",
            r"",
            f"\\textit{{Summary:}} {len(disagreement_exs)} out of {len(examples)} files "
            f"({len(disagreement_exs) / len(examples) * 100:.0f}\%) show disagreement among type checkers.",
            r"",
        ]
    )

    # TABLE 4: Minority vs Majority Correctness
    lines.extend(
        [
            r"\section{Minority vs Majority Correctness}",
            r"\begin{longtable}{p{5cm}cc}",
            r"\caption{Minority vs Majority Checker Correctness}\label{tab:minority}\\",
            r"\toprule",
            r"File & Minority (C/I/U) & Majority (C/I/U) \\",
            r"\midrule",
            r"\endfirsthead",
            r"\toprule",
            r"File & Minority (C/I/U) & Majority (C/I/U) \\",
            r"\midrule",
            r"\endhead",
            r"\bottomrule",
            r"\endlastfoot",
            r"\multicolumn{3}{l}{\textit{Note: C=Correct, I=Incorrect, U=Uncertain}} \\",
        ]
    )

    for ex in disagreement_exs:
        name = latex_escape(ex.filename[:45])

        minority_c = sum(
            1 for c in ex.minority_checkers if get_verdict_correct(ex, c) is True
        )
        minority_i = sum(
            1 for c in ex.minority_checkers if get_verdict_correct(ex, c) is False
        )
        minority_u = len(ex.minority_checkers) - minority_c - minority_i

        majority_c = sum(
            1 for c in ex.majority_checkers if get_verdict_correct(ex, c) is True
        )
        majority_i = sum(
            1 for c in ex.majority_checkers if get_verdict_correct(ex, c) is False
        )
        majority_u = len(ex.majority_checkers) - majority_c - majority_i

        minority_str = f"{minority_c}/{minority_i}/{minority_u}"
        majority_str = f"{majority_c}/{majority_i}/{majority_u}"

        lines.append(f"{name} & {minority_str} & {majority_str} \\\\")

    lines.extend(
        [
            r"\bottomrule",
            r"\end{longtable}",
            r"",
        ]
    )

    # TABLE 5: Verdicts Summary
    lines.extend(
        [
            r"\section{Per-Checker Evaluation Summary}",
            r"\begin{table}[htbp]",
            r"\centering",
            r"\begin{tabular}{lrrrrr}",
            r"\toprule",
            r"Checker & Correct & Incorrect & Uncertain & Total & Accuracy \\",
            r"\midrule",
        ]
    )

    for checker in ["mypy", "pyrefly", "ty", "zuban"]:
        stats = checker_stats[checker]
        total = sum(stats.values())
        acc = f"{stats['correct'] / total * 100:.0f}\%" if total > 0 else "N/A"
        lines.append(
            f"{checker.upper()} & {stats['correct']} & {stats['incorrect']} & "
            f"{stats['uncertain']} & {total} & {acc} \\\\"
        )

    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption{Per-Checker Evaluation Verdicts}",
            r"\label{tab:verdicts}",
            r"\end{table}",
            r"",
        ]
    )

    # TABLE 6: PEP Compliance
    pep_findings = []
    for ex in examples:
        for finding in ex.tier3_findings:
            pep_findings.append((ex.filename, finding))

    if pep_findings:
        lines.extend(
            [
                r"\section{PEP Compliance Analysis}",
                r"\begin{longtable}{p{4cm}lc}",
                r"\caption{PEP Compliance Analysis}\label{tab:pep}\\",
                r"\toprule",
                r"File & PEP & Correct? \\",
                r"\midrule",
                r"\endfirsthead",
                r"\toprule",
                r"File & PEP & Correct? \\",
                r"\midrule",
                r"\endhead",
                r"\bottomrule",
                r"\endlastfoot",
            ]
        )

        for filename, finding in pep_findings:
            name = latex_escape(filename[:40])
            pep = finding.get("pep", "N/A")
            checker = finding.get("checker", "").upper()
            is_correct = r"\checkmark" if finding.get("is_correct") else r"\texttimes"
            lines.append(f"{name} & PEP {pep} ({checker}) & {is_correct} \\\\")

        lines.extend(
            [
                r"\bottomrule",
                r"\end{longtable}",
                r"",
            ]
        )

    lines.append(r"\end{document}")

    return "\n".join(lines)


def save_csv_tables(examples: list, base_dir: str, output_dir: str):
    """Save tables as CSV files."""

    with open(os.path.join(output_dir, "table1_metrics.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["File", "LOC", "Functions", "Type Imports", "Type Density", "Interactions"]
        )
        for ex in examples:
            m = ex.metrics
            writer.writerow(
                [
                    ex.filename,
                    m.get("loc", 0),
                    m.get("num_functions", 0),
                    m.get("type_imports", 0),
                    m.get("type_density", 0),
                    m.get("internal_calls", 0),
                ]
            )

    with open(os.path.join(output_dir, "table2_trrec.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["File", "RuntimeError", "Mypy", "Pyrefly", "Ty", "Zuban"])
        for ex in examples:
            has_error, _ = check_runtime_error(ex.filepath, base_dir)
            row = [ex.filename, "Yes" if has_error else "No"]
            for checker in ["mypy", "pyrefly", "ty", "zuban"]:
                row.append("Error" if ex.statuses.get(checker) == "error" else "OK")
            writer.writerow(row)

    with open(
        os.path.join(output_dir, "table3_disagreements.csv"), "w", newline=""
    ) as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "File",
                "HasDisagreement",
                "MinorityCheckers",
                "MinorityVerdicts",
                "Mypy",
                "Pyrefly",
                "Ty",
                "Zuban",
            ]
        )
        for ex in examples:
            minority_str = (
                ",".join(ex.minority_checkers).upper() if ex.minority_checkers else ""
            )
            minority_verdicts = []
            for c in ex.minority_checkers:
                v = ex.verdicts.get(c, {}).get("verdict", "N/A")
                minority_verdicts.append(f"{c.upper()}:{v}")
            writer.writerow(
                [
                    ex.filename,
                    "Yes" if ex.has_disagreement else "No",
                    minority_str,
                    ";".join(minority_verdicts),
                    ex.statuses.get("mypy", ""),
                    ex.statuses.get("pyrefly", ""),
                    ex.statuses.get("ty", ""),
                    ex.statuses.get("zuban", ""),
                ]
            )

    with open(os.path.join(output_dir, "table4_minority.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "File",
                "MinorityCheckers",
                "MinorityC",
                "MinorityI",
                "MinorityU",
                "MajorityC",
                "MajorityI",
                "MajorityU",
            ]
        )
        for ex in examples:
            if not ex.has_disagreement:
                continue

            def count_verdicts(checkers):
                c = sum(1 for x in checkers if get_verdict_correct(ex, x) is True)
                i = sum(1 for x in checkers if get_verdict_correct(ex, x) is False)
                u = len(checkers) - c - i
                return c, i, u

            mc, mi, mu = count_verdicts(ex.minority_checkers)
            Mac, Mai, Mau = count_verdicts(ex.majority_checkers)

            writer.writerow(
                [
                    ex.filename,
                    ",".join(ex.minority_checkers).upper(),
                    mc,
                    mi,
                    mu,
                    Mac,
                    Mai,
                    Mau,
                ]
            )


def main():
    base_dir = "/home/benedek-kaibas/Documents/pytifex-demo/src/tc_disagreement"

    folders = [
        "generated_examples/2026-03-04_21-27-35",
        "generated_examples/2026-03-25_12-52-32",
        "generated_examples/2026-03-25_13-30-00",
    ]

    output_dir = os.path.join(base_dir, "research_tables")
    os.makedirs(output_dir, exist_ok=True)

    print("Loading examples...")
    examples = load_examples(folders, base_dir)
    print(f"Loaded {len(examples)} unique examples")

    print("Generating LaTeX document...")
    latex_doc = generate_latex_document(examples, base_dir)

    with open(os.path.join(output_dir, "research_tables.tex"), "w") as f:
        f.write(latex_doc)
    print(f"Saved: research_tables.tex")

    print("Saving CSV files...")
    save_csv_tables(examples, base_dir, output_dir)
    print(f"Saved CSV files to: {output_dir}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total examples: {len(examples)}")
    print(f"With disagreements: {sum(1 for e in examples if e.has_disagreement)}")


if __name__ == "__main__":
    main()
