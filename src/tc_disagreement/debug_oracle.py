#!/usr/bin/env python3
"""Debug script: run the oracle against source files and report findings."""

import json
import sys
import os

from oracle import run_oracle, evaluate_checker, parse_checker_diagnostics


def main():
    results_path = sys.argv[1] if len(sys.argv) > 1 else (
        "generated_examples/2026-03-04_21-27-35/results.json"
    )

    with open(results_path) as f:
        data = json.load(f)

    base_dir = os.path.dirname(results_path)
    files_with_findings = 0
    total_files = 0

    for entry in data["results"]:
        filename = entry["filename"]
        filepath = os.path.join(base_dir, "source_files", filename)
        if not os.path.exists(filepath):
            filepath = entry.get("filepath", filepath)

        with open(filepath) as f:
            source = f.read()

        findings = run_oracle(source)
        total_files += 1

        print(f"\n{'='*60}")
        print(f"FILE: {filename}")
        print(f"  Oracle findings: {len(findings)}")

        if findings:
            files_with_findings += 1
            for finding in findings:
                print(f"    [{finding.rule_id}] L{finding.line} ({finding.confidence:.2f}): {finding.message}")

            for checker, output in entry["outputs"].items():
                verdict = evaluate_checker(findings, output, checker)
                print(f"  {checker}: {verdict.verdict} (hit={len(verdict.findings_hit)}, missed={len(verdict.findings_missed)})")
        else:
            print(f"  (no findings)")

    print(f"\n{'='*60}")
    print(f"FILES WITH ORACLE FINDINGS: {files_with_findings}/{total_files}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
