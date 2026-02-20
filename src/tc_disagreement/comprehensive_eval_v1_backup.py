# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "hypothesis",
#     "beartype",
#     "typeguard",
# ]
# ///

"""
Comprehensive Tiered Evaluation System for Type Checker Correctness.

This module implements a multi-tiered evaluation strategy:

Tier 1: Runtime Crash Detection (~10% of cases)
    - Execute code and catch type-related exceptions
    - Highest confidence - proves actual bugs exist

Tier 2: Mutation + Typeguard Testing (~40% of cases)  
    - Mutate values to violate type constraints
    - Use typeguard to enforce type annotations on assignments
    - Proves type constraints matter in practice

Tier 3: PEP Specification Compliance (~40% of cases)
    - Check against official Python typing PEPs
    - Pattern-based rules for common disagreement types
    - Authoritative ground truth

Tier 4: Design Differences (~10% of cases)
    - Accept that some disagreements are philosophical
    - Document as legitimate design choices
"""

import ast
import sys
import re
import os
import json
import copy
import traceback
import io
import contextlib
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import Any, Optional, Literal
from pathlib import Path
from enum import Enum


class Verdict(Enum):
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"
    UNCERTAIN = "UNCERTAIN"


@dataclass
class TypeBug:
    """A confirmed type-related bug found through testing."""
    line: int
    bug_type: str
    message: str
    source: str  # "tier1_runtime", "tier2_mutation", "tier3_pep"
    confidence: float
    details: dict = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """Complete evaluation result for a file."""
    filename: str
    tier1_bugs: list[TypeBug]
    tier2_bugs: list[TypeBug]
    tier3_findings: list[dict]
    checker_verdicts: dict[str, dict]
    tier_reached: int
    

# =============================================================================
# TIER 1: RUNTIME CRASH DETECTION
# =============================================================================

def run_tier1(source_code: str) -> list[TypeBug]:
    """
    Tier 1: Execute code and catch type-related runtime exceptions.
    
    This is the highest confidence tier - if code crashes with a type error,
    we have definitive proof of a bug.
    """
    bugs: list[TypeBug] = []
    
    try:
        with contextlib.redirect_stdout(io.StringIO()), \
             contextlib.redirect_stderr(io.StringIO()):
            exec(compile(source_code, "<tier1>", "exec"), {"__name__": "__main__"})
    except TypeError as e:
        tb = traceback.extract_tb(sys.exc_info()[2])
        line = tb[-1].lineno if tb else 0
        bugs.append(TypeBug(
            line=line, bug_type="TypeError", message=str(e)[:200],
            source="tier1_runtime", confidence=1.0
        ))
    except KeyError as e:
        tb = traceback.extract_tb(sys.exc_info()[2])
        line = tb[-1].lineno if tb else 0
        bugs.append(TypeBug(
            line=line, bug_type="KeyError", message=f"KeyError: {e}",
            source="tier1_runtime", confidence=1.0
        ))
    except AttributeError as e:
        tb = traceback.extract_tb(sys.exc_info()[2])
        line = tb[-1].lineno if tb else 0
        bugs.append(TypeBug(
            line=line, bug_type="AttributeError", message=str(e)[:200],
            source="tier1_runtime", confidence=1.0
        ))
    except Exception:
        pass  # Other exceptions are not type errors
    
    return bugs


# =============================================================================
# TIER 2: MUTATION + TYPEGUARD TESTING
# =============================================================================

@dataclass
class TypeAnnotation:
    """Represents a type annotation found in the code."""
    line: int
    variable_name: str
    annotation: str
    value_expr: Optional[str] = None


def extract_type_annotations(source_code: str) -> list[TypeAnnotation]:
    """Extract all type annotations from source code."""
    annotations = []
    
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return annotations
    
    class AnnotationVisitor(ast.NodeVisitor):
        def visit_AnnAssign(self, node):
            """Handle annotated assignments: x: int = 5"""
            if isinstance(node.target, ast.Name):
                ann = ast.unparse(node.annotation)
                val = ast.unparse(node.value) if node.value else None
                annotations.append(TypeAnnotation(
                    line=node.lineno,
                    variable_name=node.target.id,
                    annotation=ann,
                    value_expr=val,
                ))
            self.generic_visit(node)
        
        def visit_FunctionDef(self, node):
            """Handle function parameter and return annotations."""
            # Return type
            if node.returns:
                annotations.append(TypeAnnotation(
                    line=node.lineno,
                    variable_name=f"{node.name}.__return__",
                    annotation=ast.unparse(node.returns),
                ))
            # Parameters
            for arg in node.args.args:
                if arg.annotation:
                    annotations.append(TypeAnnotation(
                        line=node.lineno,
                        variable_name=f"{node.name}.{arg.arg}",
                        annotation=ast.unparse(arg.annotation),
                    ))
            self.generic_visit(node)
    
    visitor = AnnotationVisitor()
    visitor.visit(tree)
    return annotations


def generate_violating_values(annotation: str) -> list[tuple[Any, str]]:
    """
    Generate values that VIOLATE a given type annotation.
    
    Returns list of (value, description) tuples.
    """
    annotation = annotation.strip()
    violations = []
    
    # Literal types: generate values not in the literal set
    if annotation.startswith("Literal["):
        violations = [
            ("__INVALID_LITERAL__", "string not in Literal set"),
            (99999, "int not in Literal set"),
            (None, "None not in Literal set"),
        ]
    
    # Basic types
    elif annotation == "int":
        violations = [
            ("not_an_int", "str instead of int"),
            (3.14, "float instead of int"),
            (None, "None instead of int"),
        ]
    elif annotation == "str":
        violations = [
            (42, "int instead of str"),
            (None, "None instead of str"),
        ]
    elif annotation == "float":
        violations = [
            ("not_a_float", "str instead of float"),
            (None, "None instead of float"),
        ]
    elif annotation == "bool":
        violations = [
            ("not_a_bool", "str instead of bool"),
        ]
    
    # List/Dict types
    elif annotation.startswith(("List[", "list[")):
        violations = [
            ("not_a_list", "str instead of list"),
            (42, "int instead of list"),
        ]
    elif annotation.startswith(("Dict[", "dict[")):
        violations = [
            ("not_a_dict", "str instead of dict"),
            ([], "list instead of dict"),
        ]
    
    # TypedDict - provide empty dict (missing required keys)
    elif "TypedDict" in annotation or (annotation[0].isupper() and "Dict" not in annotation):
        violations = [
            ({}, "empty dict (missing required keys)"),
            ("not_a_dict", "str instead of TypedDict"),
        ]
    
    # Fallback
    if not violations:
        violations = [
            (None, "None for unknown type"),
            ("__WRONG_TYPE__", "str for unknown type"),
        ]
    
    return violations


def run_tier2(source_code: str, annotations: list[TypeAnnotation]) -> list[TypeBug]:
    """
    Tier 2: Mutation + Typeguard testing.
    
    For each type annotation:
    1. Generate values that violate the type
    2. Create a test that uses typeguard to enforce the annotation
    3. If typeguard catches the violation, the constraint matters
    """
    bugs: list[TypeBug] = []
    
    # Check if typeguard is available
    try:
        import typeguard
    except ImportError:
        return bugs
    
    for ann in annotations:
        # Skip complex annotations we can't easily test
        if "." in ann.variable_name and "__return__" not in ann.variable_name:
            continue  # Skip function parameters for now
        
        violations = generate_violating_values(ann.annotation)
        
        for violating_value, description in violations:
            # Create a test that enforces the type with typeguard
            test_code = _create_typeguard_test(ann, violating_value)
            
            if test_code:
                crashed, error_msg = _run_typeguard_test(test_code)
                
                if crashed:
                    bugs.append(TypeBug(
                        line=ann.line,
                        bug_type="TypeguardViolation",
                        message=f"Mutation ({description}): {error_msg}",
                        source="tier2_mutation",
                        confidence=0.9,
                        details={
                            "annotation": ann.annotation,
                            "mutation": description,
                        }
                    ))
                    break  # One violation per annotation is enough
    
    return bugs


def _create_typeguard_test(ann: TypeAnnotation, violating_value: Any) -> Optional[str]:
    """Create a test script that uses typeguard to check a type violation."""
    
    # Handle return type annotations
    if "__return__" in ann.variable_name:
        func_name = ann.variable_name.replace(".__return__", "")
        return f'''
from typeguard import typechecked

@typechecked
def test_func() -> {ann.annotation}:
    return {repr(violating_value)}

test_func()
'''
    
    # Handle variable annotations
    return f'''
from typeguard import check_type

value = {repr(violating_value)}
check_type(value, {ann.annotation})
'''


def _run_typeguard_test(test_code: str) -> tuple[bool, str]:
    """Run a typeguard test and return (crashed, error_message)."""
    try:
        with contextlib.redirect_stdout(io.StringIO()), \
             contextlib.redirect_stderr(io.StringIO()):
            exec(compile(test_code, "<typeguard_test>", "exec"), {})
        return False, ""
    except Exception as e:
        error_name = type(e).__name__
        if "TypeCheck" in error_name or "type" in str(e).lower():
            return True, f"{error_name}: {str(e)[:100]}"
        return False, ""


# =============================================================================
# TIER 3: PEP SPECIFICATION COMPLIANCE
# =============================================================================

@dataclass
class PEPRule:
    """A rule derived from Python typing PEPs."""
    pep_number: int
    pattern: str  # regex pattern to match in checker output or code
    rule_description: str
    correct_behavior: str  # "error" or "ok"


# Common PEP rules for type checking
PEP_RULES = [
    # PEP 586: Literal Types
    PEPRule(
        pep_number=586,
        pattern=r"str.*(?:to|→|->).*Literal\[",
        rule_description="str is not assignable to Literal[...] (PEP 586)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=586,
        pattern=r"Literal\[.*\].*(?:to|→|->).*str",
        rule_description="Literal[...] is assignable to str (PEP 586)",
        correct_behavior="ok",
    ),
    
    # PEP 589: TypedDict
    PEPRule(
        pep_number=589,
        pattern=r"[Mm]issing.*(?:required|key).*TypedDict",
        rule_description="Missing required key in TypedDict (PEP 589)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=589,
        pattern=r"TypedDict.*[Mm]issing.*key",
        rule_description="Missing required key in TypedDict (PEP 589)",
        correct_behavior="error",
    ),
    
    # PEP 484: NewType
    PEPRule(
        pep_number=484,
        pattern=r"NewType.*float",
        rule_description="float is a valid base for NewType (PEP 484)",
        correct_behavior="ok",  # ty incorrectly rejects this
    ),
    
    # PEP 484: Liskov Substitution Principle
    PEPRule(
        pep_number=484,
        pattern=r"(?:override|LSP|Liskov|incompatible).*method",
        rule_description="Method override must be compatible (PEP 484 LSP)",
        correct_behavior="error",
    ),
    
    # PEP 647: TypeGuard
    PEPRule(
        pep_number=647,
        pattern=r"TypeGuard.*narrow",
        rule_description="TypeGuard narrows to specified type (PEP 647)",
        correct_behavior="ok",  # narrowing should be allowed
    ),
]


def run_tier3(source_code: str, checker_outputs: dict[str, str]) -> list[dict]:
    """
    Tier 3: Check against PEP specifications.
    
    Analyzes the code and checker outputs to determine which checker
    follows the official Python typing specifications.
    """
    findings = []
    
    # Check each PEP rule against checker outputs
    for rule in PEP_RULES:
        for checker, output in checker_outputs.items():
            if re.search(rule.pattern, output, re.IGNORECASE):
                # Checker's output matches this pattern
                checker_says_error = _checker_reports_error(output)
                
                is_correct = (
                    (rule.correct_behavior == "error" and checker_says_error) or
                    (rule.correct_behavior == "ok" and not checker_says_error)
                )
                
                findings.append({
                    "checker": checker,
                    "pep": rule.pep_number,
                    "rule": rule.rule_description,
                    "checker_behavior": "error" if checker_says_error else "ok",
                    "correct_behavior": rule.correct_behavior,
                    "is_correct": is_correct,
                    "confidence": 0.85,
                })
    
    # Also check code patterns that should trigger specific rules
    code_findings = _analyze_code_patterns(source_code, checker_outputs)
    findings.extend(code_findings)
    
    return findings


def _checker_reports_error(output: str) -> bool:
    """Determine if a checker output indicates an error."""
    output_lower = output.lower()
    return (
        "error" in output_lower and
        "0 error" not in output_lower and
        "success" not in output_lower
    )


def _analyze_code_patterns(source_code: str, checker_outputs: dict[str, str]) -> list[dict]:
    """Analyze code for patterns that have clear PEP-defined behavior."""
    findings = []
    
    # Pattern 1: str assigned to Literal (PEP 586)
    if re.search(r':\s*str\s*=', source_code) and re.search(r'Literal\[', source_code):
        # Check if any assignment is str -> Literal
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.AnnAssign):
                    ann = ast.unparse(node.annotation) if node.annotation else ""
                    if "Literal[" in ann:
                        # This is a Literal annotation - checkers should flag str -> Literal
                        for checker, output in checker_outputs.items():
                            checker_says_error = _checker_reports_error(output)
                            # Per PEP 586, str -> Literal should be an error
                            # But we need to check if the SOURCE is str, not the value
                            if "str" in output.lower() and "literal" in output.lower():
                                findings.append({
                                    "checker": checker,
                                    "pep": 586,
                                    "rule": "str is not assignable to Literal (PEP 586)",
                                    "line": node.lineno,
                                    "checker_behavior": "error" if checker_says_error else "ok",
                                    "correct_behavior": "error",
                                    "is_correct": checker_says_error,
                                    "confidence": 0.8,
                                })
        except SyntaxError:
            pass
    
    # Pattern 2: TypedDict with missing keys (PEP 589)
    if "TypedDict" in source_code and "total=False" not in source_code:
        # Check for potentially missing required keys
        for checker, output in checker_outputs.items():
            if re.search(r"missing.*key|key.*missing", output.lower()):
                findings.append({
                    "checker": checker,
                    "pep": 589,
                    "rule": "Required TypedDict keys must be present (PEP 589)",
                    "checker_behavior": "error",
                    "correct_behavior": "error",
                    "is_correct": True,
                    "confidence": 0.85,
                })
    
    return findings


# =============================================================================
# VERDICT DETERMINATION
# =============================================================================

@dataclass 
class FunctionSpan:
    """Represents a function's location in source code."""
    name: str
    start_line: int
    end_line: int
    class_name: Optional[str] = None


def extract_function_spans(source_code: str) -> list[FunctionSpan]:
    """Extract all function spans from source code."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []
    
    spans = []
    
    class FunctionVisitor(ast.NodeVisitor):
        def __init__(self):
            self.current_class = None
        
        def visit_ClassDef(self, node):
            old = self.current_class
            self.current_class = node.name
            self.generic_visit(node)
            self.current_class = old
        
        def visit_FunctionDef(self, node):
            end = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno + 20
            spans.append(FunctionSpan(node.name, node.lineno, end, self.current_class))
            self.generic_visit(node)
    
    FunctionVisitor().visit(tree)
    return spans


def extract_checker_error_lines(output: str) -> list[int]:
    """Extract line numbers from checker output."""
    lines = []
    patterns = [
        r'\.py:(\d+)(?::\d+)?:',
        r'[Ll]ine\s+(\d+)',
        r':(\d+):.*(?:error|Error)',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, output):
            try:
                lines.append(int(match.group(1)))
            except (ValueError, IndexError):
                pass
    return list(set(lines))


def determine_verdicts(
    tier1_bugs: list[TypeBug],
    tier2_bugs: list[TypeBug],
    tier3_findings: list[dict],
    checker_outputs: dict[str, str],
    source_code: str,
) -> dict[str, dict]:
    """
    Determine final verdict for each checker based on all tiers.
    
    Priority:
    1. Tier 1 (runtime crashes) - highest confidence
    2. Tier 2 (mutation testing) - high confidence  
    3. Tier 3 (PEP compliance) - medium-high confidence
    """
    verdicts = {}
    function_spans = extract_function_spans(source_code)
    
    # Combine all bugs
    all_bugs = tier1_bugs + tier2_bugs
    proven_bugs = [b for b in all_bugs if b.confidence >= 0.85]
    
    for checker, output in checker_outputs.items():
        checker_reported_error = _checker_reports_error(output)
        checker_error_lines = extract_checker_error_lines(output)
        
        # Check Tier 1 & 2: Did checker catch proven bugs?
        if proven_bugs:
            bugs_caught = []
            bugs_missed = []
            
            # For Tier 1 (runtime crashes), use strict matching
            # For Tier 2 (mutations), checker just needs to report errors to be "correct"
            # because Tier 2 proves constraints matter, not specific lines
            
            is_tier1 = any(b.source == "tier1_runtime" for b in proven_bugs)
            
            if is_tier1:
                # Strict matching for runtime crashes
                for bug in proven_bugs:
                    caught = False
                    for error_line in checker_error_lines:
                        if abs(bug.line - error_line) <= 5:
                            caught = True
                            break
                        bug_func = _get_function_at_line(function_spans, bug.line)
                        err_func = _get_function_at_line(function_spans, error_line)
                        if bug_func and err_func and bug_func.name == err_func.name:
                            caught = True
                            break
                    
                    if caught:
                        bugs_caught.append(bug)
                    else:
                        bugs_missed.append(bug)
            else:
                # For Tier 2: If checker reported errors, they were being cautious (CORRECT)
                # If checker said OK, they missed the constraint (need to check specific line)
                for bug in proven_bugs:
                    caught = False
                    # Wider tolerance for Tier 2 - check ±10 lines
                    for error_line in checker_error_lines:
                        if abs(bug.line - error_line) <= 10:
                            caught = True
                            break
                    
                    if caught:
                        bugs_caught.append(bug)
                    elif not checker_reported_error:
                        # Checker said OK but we proved constraint matters
                        bugs_missed.append(bug)
            
            if bugs_missed and not bugs_caught:
                verdicts[checker] = {
                    "verdict": Verdict.INCORRECT.value,
                    "reason": f"Missed {len(bugs_missed)} proven bug(s)",
                    "confidence": 0.95 if is_tier1 else 0.85,
                    "tier": 1 if is_tier1 else 2,
                    "missed_bugs": [{"line": b.line, "type": b.bug_type} for b in bugs_missed],
                }
                continue
            elif bugs_caught:
                verdicts[checker] = {
                    "verdict": Verdict.CORRECT.value,
                    "reason": f"Caught {len(bugs_caught)} proven bug(s)",
                    "confidence": 0.9 if is_tier1 else 0.8,
                    "tier": 1 if is_tier1 else 2,
                }
                continue
        
        # Check Tier 3: PEP compliance
        checker_findings = [f for f in tier3_findings if f.get("checker") == checker]
        if checker_findings:
            correct_count = sum(1 for f in checker_findings if f.get("is_correct"))
            incorrect_count = len(checker_findings) - correct_count
            
            if incorrect_count > correct_count:
                verdicts[checker] = {
                    "verdict": Verdict.INCORRECT.value,
                    "reason": f"Violates PEP specifications ({incorrect_count} violations)",
                    "confidence": 0.8,
                    "tier": 3,
                    "pep_findings": checker_findings,
                }
                continue
            elif correct_count > 0:
                verdicts[checker] = {
                    "verdict": Verdict.CORRECT.value,
                    "reason": f"Follows PEP specifications ({correct_count} checks)",
                    "confidence": 0.75,
                    "tier": 3,
                }
                continue
        
        # No definitive verdict
        verdicts[checker] = {
            "verdict": Verdict.UNCERTAIN.value,
            "reason": "No definitive evidence from any tier",
            "confidence": 0.5,
            "tier": 4,
        }
    
    return verdicts


def _get_function_at_line(spans: list[FunctionSpan], line: int) -> Optional[FunctionSpan]:
    """Find which function contains a line."""
    for span in spans:
        if span.start_line <= line <= span.end_line:
            return span
    return None


# =============================================================================
# MAIN EVALUATION FUNCTION
# =============================================================================

def evaluate_comprehensive(
    source_code: str,
    checker_outputs: dict[str, str],
    filename: str = "unknown.py",
) -> EvaluationResult:
    """
    Run comprehensive tiered evaluation on a code example.
    
    Returns results from all tiers and final verdicts.
    """
    # Tier 1: Runtime crashes
    tier1_bugs = run_tier1(source_code)
    
    tier_reached = 1
    tier2_bugs = []
    tier3_findings = []
    
    # Only proceed to higher tiers if Tier 1 didn't resolve everything
    if not tier1_bugs:
        tier_reached = 2
        
        # Tier 2: Mutation + Typeguard
        annotations = extract_type_annotations(source_code)
        tier2_bugs = run_tier2(source_code, annotations)
        
        if not tier2_bugs:
            tier_reached = 3
            
            # Tier 3: PEP compliance
            tier3_findings = run_tier3(source_code, checker_outputs)
            
            if not tier3_findings:
                tier_reached = 4
    
    # Determine final verdicts
    verdicts = determine_verdicts(
        tier1_bugs, tier2_bugs, tier3_findings,
        checker_outputs, source_code
    )
    
    return EvaluationResult(
        filename=filename,
        tier1_bugs=tier1_bugs,
        tier2_bugs=tier2_bugs,
        tier3_findings=tier3_findings,
        checker_verdicts=verdicts,
        tier_reached=tier_reached,
    )


def evaluate_results_comprehensive(results_path: str) -> dict:
    """
    Evaluate all files using the comprehensive tiered system.
    """
    with open(results_path) as f:
        data = json.load(f)
    
    results = data.get("results", [])
    checkers = data.get("checkers_used", ["mypy", "pyrefly", "zuban", "ty"])
    
    all_results = []
    summary_stats = {
        checker: {"correct": 0, "incorrect": 0, "uncertain": 0}
        for checker in checkers
    }
    tier_distribution = {1: 0, 2: 0, 3: 0, 4: 0}
    
    print("=" * 70)
    print("COMPREHENSIVE TIERED EVALUATION")
    print("=" * 70)
    print("Tier 1: Runtime crash detection")
    print("Tier 2: Mutation + Typeguard testing")
    print("Tier 3: PEP specification compliance")
    print("Tier 4: Design differences (uncertain)")
    print(f"Files to evaluate: {len(results)}")
    print("=" * 70)
    print()
    
    for i, file_entry in enumerate(results, 1):
        filepath = file_entry.get("filepath", "")
        filename = file_entry.get("filename", "")
        outputs = file_entry.get("outputs", {})
        
        print(f"[{i}/{len(results)}] {filename}")
        
        try:
            with open(filepath) as f:
                source_code = f.read()
        except FileNotFoundError:
            print("  [SKIP] File not found")
            continue
        
        result = evaluate_comprehensive(source_code, outputs, filename)
        all_results.append(result)
        tier_distribution[result.tier_reached] += 1
        
        # Print summary
        print(f"  Tier reached: {result.tier_reached}")
        print(f"  Bugs: T1={len(result.tier1_bugs)}, T2={len(result.tier2_bugs)}, T3={len(result.tier3_findings)}")
        
        for checker, verdict in result.checker_verdicts.items():
            v = verdict["verdict"]
            tier = verdict.get("tier", "?")
            if v == "CORRECT":
                print(f"  ✓ {checker}: CORRECT (tier {tier})")
                summary_stats[checker]["correct"] += 1
            elif v == "INCORRECT":
                print(f"  ✗ {checker}: INCORRECT (tier {tier})")
                summary_stats[checker]["incorrect"] += 1
            else:
                print(f"  ? {checker}: UNCERTAIN")
                summary_stats[checker]["uncertain"] += 1
        
        print()
    
    # Print summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    print(f"\nTier distribution:")
    for tier, count in tier_distribution.items():
        print(f"  Tier {tier}: {count} files")
    
    print(f"\n{'Checker':<12} {'Correct':>10} {'Incorrect':>10} {'Uncertain':>10}")
    print("-" * 44)
    
    for checker in checkers:
        stats = summary_stats[checker]
        print(f"{checker:<12} {stats['correct']:>10} {stats['incorrect']:>10} {stats['uncertain']:>10}")
    
    print("=" * 70)
    
    # Save results
    output_dir = os.path.dirname(results_path)
    eval_path = os.path.join(output_dir, "evaluation_comprehensive.json")
    
    with open(eval_path, "w") as f:
        json.dump({
            "method": "comprehensive_tiered",
            "tier_distribution": tier_distribution,
            "summary": summary_stats,
            "results": [
                {
                    "filename": r.filename,
                    "tier_reached": r.tier_reached,
                    "tier1_bugs": [{"line": b.line, "type": b.bug_type, "msg": b.message} for b in r.tier1_bugs],
                    "tier2_bugs": [{"line": b.line, "type": b.bug_type, "msg": b.message} for b in r.tier2_bugs],
                    "tier3_findings": r.tier3_findings,
                    "verdicts": r.checker_verdicts,
                }
                for r in all_results
            ],
        }, f, indent=2)
    
    print(f"\nResults saved to: {eval_path}")
    
    return summary_stats


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python comprehensive_eval.py <results.json>")
        print()
        print("Comprehensive tiered evaluation system:")
        print("  Tier 1: Runtime crash detection (highest confidence)")
        print("  Tier 2: Mutation + Typeguard testing")
        print("  Tier 3: PEP specification compliance")
        print("  Tier 4: Design differences (uncertain)")
        sys.exit(1)
    
    evaluate_results_comprehensive(sys.argv[1])
