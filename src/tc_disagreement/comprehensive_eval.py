# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "hypothesis",
#     "beartype",
#     "typeguard",
# ]
# ///

"""
Comprehensive Tiered Evaluation System for Type Checker Correctness (V2).

Improvements over V1:
- Full traceback walking (not just last frame)
- Exception chain inspection (__cause__ / __context__)
- AST-based try/except isolation to surface swallowed type errors

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


class DebugArtifactCollector:
    """Collects ephemeral test snippets generated during evaluation for later inspection."""

    def __init__(self) -> None:
        self.tier1_snippets: list[dict[str, str]] = []
        self.tier2_snippets: list[dict[str, str]] = []

    def add_tier1(self, label: str, code: str) -> None:
        self.tier1_snippets.append({"label": label, "code": code})

    def add_tier2(self, annotation: str, violation: str, code: str) -> None:
        self.tier2_snippets.append({
            "annotation": annotation,
            "violation": violation,
            "code": code,
        })

    def save(self, directory: str, filename: str) -> None:
        stem = filename.removesuffix(".py")
        base = os.path.join(directory, stem)
        os.makedirs(base, exist_ok=True)

        for i, s in enumerate(self.tier1_snippets):
            path = os.path.join(base, f"tier1_{i}_{s['label']}.py")
            with open(path, "w") as f:
                f.write(s["code"])

        for i, s in enumerate(self.tier2_snippets):
            safe_ann = re.sub(r"[^\w]", "_", s["annotation"])[:40]
            path = os.path.join(base, f"tier2_{i}_{safe_ann}.py")
            with open(path, "w") as f:
                f.write(f"# annotation: {s['annotation']}\n")
                f.write(f"# violation:  {s['violation']}\n\n")
                f.write(s["code"])


# =============================================================================
# TIER 1: RUNTIME CRASH DETECTION
# =============================================================================

TYPE_ERROR_EXCEPTIONS = (TypeError, KeyError, AttributeError)


def _extract_all_source_lines(tb_list: list, source_tag: str = "<tier1>") -> list[int]:
    """Extract all line numbers from traceback frames that belong to our source."""
    return [frame.lineno for frame in tb_list if frame.filename == source_tag]


def _collect_chained_exceptions(exc: BaseException) -> list[BaseException]:
    """Walk __cause__ and __context__ chains to find all related exceptions."""
    seen: set[int] = set()
    chain: list[BaseException] = []
    current: BaseException | None = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        chain.append(current)
        current = current.__cause__ or current.__context__
    return chain


def _extract_try_bodies(source_code: str) -> list[tuple[int, int, str]]:
    """AST-scan for try/except blocks and return (start_line, end_line, body_source)."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []

    source_lines = source_code.splitlines()
    bodies: list[tuple[int, int, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            body_start = node.body[0].lineno
            body_end = node.body[-1].end_lineno or node.body[-1].lineno
            body_source = "\n".join(source_lines[body_start - 1 : body_end])
            bodies.append((body_start, body_end, body_source))

    return bodies


def _run_isolated_code(code: str, source_tag: str = "<tier1_isolated>") -> list[TypeBug]:
    """Execute code and collect type-related bugs with full traceback info."""
    bugs: list[TypeBug] = []
    try:
        with contextlib.redirect_stdout(io.StringIO()), \
             contextlib.redirect_stderr(io.StringIO()):
            exec(compile(code, source_tag, "exec"), {"__name__": "__main__"})
    except TYPE_ERROR_EXCEPTIONS as e:
        bugs.extend(_bugs_from_exception(e, source_tag))
    except Exception:
        pass
    return bugs


def _bugs_from_exception(exc: BaseException, source_tag: str) -> list[TypeBug]:
    """Create TypeBug entries from an exception and its chain."""
    bugs: list[TypeBug] = []
    seen_lines: set[int] = set()

    for chained_exc in _collect_chained_exceptions(exc):
        if not isinstance(chained_exc, TYPE_ERROR_EXCEPTIONS):
            continue

        bug_type = type(chained_exc).__name__
        message = str(chained_exc)[:200]
        if isinstance(chained_exc, KeyError):
            message = f"KeyError: {chained_exc}"

        tb_info = traceback.extract_tb(chained_exc.__traceback__)
        all_source_lines = _extract_all_source_lines(tb_info, source_tag)

        if not all_source_lines:
            all_source_lines = [tb_info[-1].lineno] if tb_info else [0]

        primary_line = all_source_lines[0]

        if primary_line in seen_lines:
            continue
        seen_lines.add(primary_line)

        bugs.append(TypeBug(
            line=primary_line,
            bug_type=bug_type,
            message=message,
            source="tier1_runtime",
            confidence=1.0,
            details={"all_traceback_lines": all_source_lines},
        ))

    return bugs


def run_tier1(
    source_code: str,
    debug: DebugArtifactCollector | None = None,
) -> list[TypeBug]:
    """
    Tier 1: Execute code and catch type-related runtime exceptions.
    
    V2 improvements:
    - Walks the full traceback to find the root cause line
    - Inspects exception chains (__cause__ / __context__)
    - Isolates try/except bodies to surface swallowed type errors
    """
    bugs = _run_isolated_code(source_code, "<tier1>")
    if debug:
        debug.add_tier1("full_source", source_code)

    try_bodies = _extract_try_bodies(source_code)
    seen_lines = {b.line for b in bugs}

    for idx, (start_line, end_line, body_source) in enumerate(try_bodies):
        if debug:
            debug.add_tier1(f"try_body_{idx}_L{start_line}", body_source)
        isolated_bugs = _run_isolated_code(body_source, "<tier1_isolated>")
        for bug in isolated_bugs:
            adjusted_line = bug.line + start_line - 1
            if adjusted_line not in seen_lines:
                seen_lines.add(adjusted_line)
                bug.line = adjusted_line
                bug.details["isolated_from_try"] = True
                bug.details["all_traceback_lines"] = [
                    ln + start_line - 1 for ln in bug.details.get("all_traceback_lines", [])
                ]
                bug.confidence = 0.95
                bugs.append(bug)

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


def _extract_disagreement_lines(
    checker_outputs: dict[str, str],
) -> set[int]:
    """Extract lines where checkers disagree (some report errors, some don't)."""
    per_checker_lines: dict[str, set[int]] = {}
    for checker, output in checker_outputs.items():
        per_checker_lines[checker] = set(extract_checker_error_lines(output))

    all_error_lines: set[int] = set()
    for lines in per_checker_lines.values():
        all_error_lines |= lines

    has_error = {c for c, o in checker_outputs.items() if _checker_reports_error(o)}
    has_ok = set(checker_outputs.keys()) - has_error

    if has_error and has_ok:
        return all_error_lines

    return all_error_lines


def _annotation_near_disagreement(
    ann: TypeAnnotation,
    disagreement_lines: set[int],
    tolerance: int = 15,
) -> bool:
    """Check if an annotation is near any disagreement line."""
    if not disagreement_lines:
        return True
    return any(abs(ann.line - dl) <= tolerance for dl in disagreement_lines)


def run_tier2(
    source_code: str,
    annotations: list[TypeAnnotation],
    checker_outputs: dict[str, str] | None = None,
    debug: DebugArtifactCollector | None = None,
) -> list[TypeBug]:
    """
    Tier 2: Mutation + Typeguard testing.
    
    Only tests annotations near actual checker disagreement points.
    For each relevant type annotation:
    1. Generate values that violate the type
    2. Create a test that uses typeguard to enforce the annotation
    3. If typeguard catches the violation, the constraint matters
    """
    bugs: list[TypeBug] = []
    
    try:
        import typeguard
    except ImportError:
        return bugs
    
    disagreement_lines: set[int] = set()
    if checker_outputs:
        disagreement_lines = _extract_disagreement_lines(checker_outputs)
    
    source_imports = _extract_imports(source_code)
    
    for ann in annotations:
        if "." in ann.variable_name and "__return__" not in ann.variable_name:
            continue

        if disagreement_lines and not _annotation_near_disagreement(ann, disagreement_lines):
            continue
        
        violations = generate_violating_values(ann.annotation)
        
        for violating_value, description in violations:
            test_code = _create_typeguard_test(ann, violating_value, source_imports)
            
            if test_code:
                if debug:
                    debug.add_tier2(ann.annotation, description, test_code)
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
                    break
    
    return bugs


def _extract_imports(source_code: str) -> str:
    """Extract all import statements from source code."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return ""
    lines = source_code.splitlines()
    import_lines: list[str] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            start = node.lineno - 1
            end = (node.end_lineno or node.lineno)
            import_lines.extend(lines[start:end])
    return "\n".join(import_lines)


def _create_typeguard_test(
    ann: TypeAnnotation, violating_value: Any, source_imports: str = "",
) -> Optional[str]:
    """Create a test script that uses typeguard to check a type violation."""
    
    if "__return__" in ann.variable_name:
        func_name = ann.variable_name.replace(".__return__", "")
        return f'''
{source_imports}
from typeguard import typechecked

@typechecked
def test_func() -> {ann.annotation}:
    return {repr(violating_value)}

test_func()
'''
    
    return f'''
{source_imports}
from typeguard import check_type

value = {repr(violating_value)}
check_type(value, {ann.annotation})
'''


HARNESS_ERRORS = (NameError, SyntaxError, ImportError, ModuleNotFoundError)

TYPEGUARD_ERROR_NAMES = {"TypeCheckError", "TypeHintError", "BeartypeCallHintViolation"}


def _run_typeguard_test(test_code: str) -> tuple[bool, str]:
    """Run a typeguard test and return (crashed, error_message)."""
    try:
        with contextlib.redirect_stdout(io.StringIO()), \
             contextlib.redirect_stderr(io.StringIO()):
            exec(compile(test_code, "<typeguard_test>", "exec"), {})
        return False, ""
    except HARNESS_ERRORS:
        return False, ""
    except Exception as e:
        error_name = type(e).__name__
        if error_name in TYPEGUARD_ERROR_NAMES:
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


PEP_RULES = [
    # ── PEP 484: Type Hints (core) ──────────────────────────────────────
    PEPRule(
        pep_number=484,
        pattern=r"(?:override|LSP|Liskov|incompatible).*method",
        rule_description="Method override must be compatible (PEP 484 LSP)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=484,
        pattern=r"NewType.*float",
        rule_description="float is a valid base for NewType (PEP 484)",
        correct_behavior="ok",
    ),
    PEPRule(
        pep_number=484,
        pattern=r"not assignable to.*NewType|NewType.*not assignable",
        rule_description="NewType creates a distinct nominal type (PEP 484)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=484,
        pattern=r"invalid.argument.type|incompatible type.*expected",
        rule_description="Argument type must match parameter annotation (PEP 484)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=484,
        pattern=r"invalid.assignment|not assignable to declared type",
        rule_description="Assigned value must be compatible with declared type (PEP 484)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=484,
        pattern=r"return type.*incompatible|incompatible return",
        rule_description="Return value must match return type annotation (PEP 484)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=484,
        pattern=r"not subscriptable|not (?:a )?generic|cannot subscript",
        rule_description="Only generic classes can be subscripted (PEP 484)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=484,
        pattern=r"type application.*only supported for generic",
        rule_description="Type application is only supported for generic classes (PEP 484)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=484,
        pattern=r"has no attribute|unresolved.reference",
        rule_description="Attribute access must resolve on the declared type (PEP 484)",
        correct_behavior="error",
    ),

    # ── PEP 526: Variable Annotations ───────────────────────────────────
    PEPRule(
        pep_number=526,
        pattern=r"ClassVar.*(?:instance|self)|instance.*ClassVar",
        rule_description="ClassVar cannot be set on instances (PEP 526)",
        correct_behavior="error",
    ),

    # ── PEP 544: Protocols ──────────────────────────────────────────────
    PEPRule(
        pep_number=544,
        pattern=r"[Pp]rotocol.*cannot be instantiated|instantiate.*[Pp]rotocol",
        rule_description="Protocol classes cannot be instantiated directly (PEP 544)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=544,
        pattern=r"does not (?:implement|satisfy|conform).*[Pp]rotocol",
        rule_description="Type must implement all Protocol members (PEP 544)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=544,
        pattern=r"incompatible.*[Pp]rotocol|not compatible with.*[Pp]rotocol",
        rule_description="Type is incompatible with Protocol (PEP 544)",
        correct_behavior="error",
    ),

    # ── PEP 586: Literal Types ──────────────────────────────────────────
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
    PEPRule(
        pep_number=586,
        pattern=r"invalid.*Literal|Literal.*invalid",
        rule_description="Literal parameters must be valid literal values (PEP 586)",
        correct_behavior="error",
    ),

    # ── PEP 589: TypedDict ──────────────────────────────────────────────
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
    PEPRule(
        pep_number=589,
        pattern=r"TypedDict.*(?:extra|unexpected).*key|(?:extra|unexpected).*key.*TypedDict",
        rule_description="Extra keys not allowed in TypedDict (PEP 589)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=589,
        pattern=r"[Oo]verwriting TypedDict field",
        rule_description="Overwriting TypedDict field while extending (PEP 589)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=589,
        pattern=r"does not have key|not (?:a )?valid.*key.*TypedDict|bad.typed.dict.key",
        rule_description="Accessing invalid key on TypedDict (PEP 589)",
        correct_behavior="error",
    ),

    # ── PEP 591: Final ──────────────────────────────────────────────────
    PEPRule(
        pep_number=591,
        pattern=r"[Cc]annot (?:assign|override|overwrite).*Final|Final.*reassign",
        rule_description="Final variables cannot be reassigned (PEP 591)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=591,
        pattern=r"[Cc]annot override.*[Ff]inal.*method|[Ff]inal.*method.*override",
        rule_description="Final methods cannot be overridden (PEP 591)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=591,
        pattern=r"[Cc]annot (?:subclass|inherit|extend).*[Ff]inal",
        rule_description="Final classes cannot be subclassed (PEP 591)",
        correct_behavior="error",
    ),

    # ── PEP 604: X | Y Union Syntax ────────────────────────────────────
    PEPRule(
        pep_number=604,
        pattern=r"unsupported operand.*\|.*type",
        rule_description="X | Y union syntax requires Python 3.10+ (PEP 604)",
        correct_behavior="error",
    ),

    # ── PEP 612: ParamSpec ──────────────────────────────────────────────
    PEPRule(
        pep_number=612,
        pattern=r"ParamSpec.*(?:invalid|incorrect|misuse)|invalid.*ParamSpec",
        rule_description="ParamSpec must be used correctly (PEP 612)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=612,
        pattern=r"Concatenate.*(?:invalid|incorrect)|invalid.*Concatenate",
        rule_description="Concatenate must be used with ParamSpec (PEP 612)",
        correct_behavior="error",
    ),

    # ── PEP 613: Explicit Type Aliases ──────────────────────────────────
    PEPRule(
        pep_number=613,
        pattern=r"TypeAlias.*(?:invalid|incorrect)|invalid.*TypeAlias",
        rule_description="TypeAlias must be a valid type expression (PEP 613)",
        correct_behavior="error",
    ),

    # ── PEP 634: Structural Pattern Matching ────────────────────────────
    PEPRule(
        pep_number=634,
        pattern=r"[Ss]tatement is unreachable|unreachable code",
        rule_description="Unreachable code after exhaustive match (PEP 634)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=634,
        pattern=r"__match_args__|bad.match|cannot match positional",
        rule_description="Class must define __match_args__ for positional patterns (PEP 634)",
        correct_behavior="error",
    ),

    # ── PEP 646: Variadic Generics ──────────────────────────────────────
    PEPRule(
        pep_number=646,
        pattern=r"TypeVarTuple.*(?:invalid|incorrect)|invalid.*TypeVarTuple",
        rule_description="TypeVarTuple must be used correctly (PEP 646)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=646,
        pattern=r"[Uu]npack.*(?:invalid|only|must)|invalid.*[Uu]npack",
        rule_description="Unpack must be used with TypeVarTuple (PEP 646)",
        correct_behavior="error",
    ),

    # ── PEP 647: TypeGuard ──────────────────────────────────────────────
    PEPRule(
        pep_number=647,
        pattern=r"TypeGuard.*narrow",
        rule_description="TypeGuard narrows to specified type (PEP 647)",
        correct_behavior="ok",
    ),
    PEPRule(
        pep_number=647,
        pattern=r"TypeGuard.*positional argument|[Tt]ype guard.*positional argument",
        rule_description="TypeGuard function must accept at least one positional argument (PEP 647)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=647,
        pattern=r"TypeGuard.*[Bb]ool|TypeGuard.*return",
        rule_description="TypeGuard function must return bool (PEP 647)",
        correct_behavior="error",
    ),

    # ── PEP 655: Required / NotRequired ─────────────────────────────────
    PEPRule(
        pep_number=655,
        pattern=r"Required\[.*\].*missing|missing.*Required",
        rule_description="Required[] TypedDict keys must be present (PEP 655)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=655,
        pattern=r"NotRequired.*(?:invalid|outside TypedDict)|invalid.*NotRequired",
        rule_description="NotRequired can only be used in TypedDict (PEP 655)",
        correct_behavior="error",
    ),

    # ── PEP 673: Self Type ──────────────────────────────────────────────
    PEPRule(
        pep_number=673,
        pattern=r"Self.*outside.*class|Self.*(?:invalid|not allowed).*(?:function|module)",
        rule_description="Self can only be used inside class methods (PEP 673)",
        correct_behavior="error",
    ),

    # ── PEP 675: LiteralString ──────────────────────────────────────────
    PEPRule(
        pep_number=675,
        pattern=r"not.*LiteralString|LiteralString.*expected",
        rule_description="Non-literal string not assignable to LiteralString (PEP 675)",
        correct_behavior="error",
    ),

    # ── PEP 681: Data Class Transforms ──────────────────────────────────
    PEPRule(
        pep_number=681,
        pattern=r"dataclass_transform.*(?:invalid|incorrect)|invalid.*dataclass_transform",
        rule_description="dataclass_transform must be used correctly (PEP 681)",
        correct_behavior="error",
    ),

    # ── PEP 692: Unpack for **kwargs ────────────────────────────────────
    PEPRule(
        pep_number=692,
        pattern=r"Unpack.*kwargs|kwargs.*Unpack.*TypedDict",
        rule_description="**kwargs Unpack must use TypedDict (PEP 692)",
        correct_behavior="error",
    ),

    # ── PEP 695: Type Parameter Syntax ──────────────────────────────────
    PEPRule(
        pep_number=695,
        pattern=r"type.*statement.*invalid|invalid.*type alias.*statement",
        rule_description="Type alias statement must be valid (PEP 695)",
        correct_behavior="error",
    ),

    # ── PEP 696: Type Defaults for Type Parameters ──────────────────────
    PEPRule(
        pep_number=696,
        pattern=r"default.*TypeVar.*invalid|TypeVar.*default.*(?:invalid|not allowed)",
        rule_description="TypeVar default must be valid (PEP 696)",
        correct_behavior="error",
    ),

    # ── PEP 698: @override ──────────────────────────────────────────────
    PEPRule(
        pep_number=698,
        pattern=r"@override.*no base.*method|override.*does not override",
        rule_description="@override method must override a base class method (PEP 698)",
        correct_behavior="error",
    ),

    # ── PEP 705: TypedDict ReadOnly ─────────────────────────────────────
    PEPRule(
        pep_number=705,
        pattern=r"ReadOnly.*(?:only|must).*TypedDict|ReadOnly.*(?:invalid|cannot)",
        rule_description="ReadOnly can only be used in TypedDict (PEP 705)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=705,
        pattern=r"[Cc]annot (?:assign|write|mutate).*ReadOnly|ReadOnly.*(?:assign|mutate|write)",
        rule_description="ReadOnly TypedDict fields cannot be mutated (PEP 705)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=705,
        pattern=r"read.?only.*mutable|mutable.*read.?only|read.?write.*ReadOnly",
        rule_description="ReadOnly field incompatible with mutable parent (PEP 705)",
        correct_behavior="error",
    ),

    # ── PEP 742: TypeIs ─────────────────────────────────────────────────
    PEPRule(
        pep_number=742,
        pattern=r"TypeIs.*positional argument|[Tt]ype.?is.*positional argument",
        rule_description="TypeIs function must accept at least one positional argument (PEP 742)",
        correct_behavior="error",
    ),
    PEPRule(
        pep_number=742,
        pattern=r"TypeIs.*not.*subtype|TypeIs.*narrowing.*invalid",
        rule_description="TypeIs narrowed type must be subtype of input (PEP 742)",
        correct_behavior="error",
    ),
]


MODULE_IMPORT_RE = re.compile(
    r"[Mm]odule.*has no (?:attribute|member)|[Cc]ould not import|"
    r"unresolved.import|missing.module",
    re.IGNORECASE,
)


def run_tier3(source_code: str, checker_outputs: dict[str, str]) -> list[dict]:
    """
    Tier 3: Check against PEP specifications.
    
    Analyzes the code and checker outputs to determine which checker
    follows the official Python typing specifications.
    
    Matches PEP rules line-by-line against checker output to avoid
    false matches from note/info lines or module import errors.
    """
    findings = []
    
    for rule in PEP_RULES:
        for checker, output in checker_outputs.items():
            matched = False
            for text_line in output.splitlines():
                lower = text_line.lower()
                if "note:" in lower or "info[" in lower:
                    continue
                if MODULE_IMPORT_RE.search(text_line):
                    continue
                if re.search(rule.pattern, text_line, re.IGNORECASE):
                    matched = True
                    break
            
            if not matched:
                continue

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
    """Extract line numbers from checker error output (excludes notes/info)."""
    lines = []
    for text_line in output.splitlines():
        lower = text_line.lower()
        if "note:" in lower or "info[" in lower or "info " in lower:
            continue
        m = re.search(r'\.py:(\d+)(?::\d+)?:', text_line)
        if m and ("error" in lower or "Error" in text_line):
            try:
                lines.append(int(m.group(1)))
            except (ValueError, IndexError):
                pass
            continue
        m = re.search(r':(\d+):.*(?:error|Error)', text_line)
        if m:
            try:
                lines.append(int(m.group(1)))
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
                # V2: Also match against all traceback lines, not just primary
                for bug in proven_bugs:
                    caught = False
                    bug_lines = bug.details.get("all_traceback_lines", [bug.line])
                    for error_line in checker_error_lines:
                        for bl in bug_lines:
                            if abs(bl - error_line) <= 5:
                                caught = True
                                break
                        if caught:
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
    debug: DebugArtifactCollector | None = None,
) -> EvaluationResult:
    """
    Run comprehensive tiered evaluation on a code example.
    
    Returns results from all tiers and final verdicts.
    """
    # Tier 1: Runtime crashes
    tier1_bugs = run_tier1(source_code, debug=debug)
    
    tier_reached = 1
    tier2_bugs = []
    tier3_findings = []
    
    # Only proceed to higher tiers if Tier 1 didn't resolve everything
    if not tier1_bugs:
        tier_reached = 2
        
        # Tier 2: Mutation + Typeguard
        annotations = extract_type_annotations(source_code)
        tier2_bugs = run_tier2(source_code, annotations, checker_outputs, debug=debug)
        
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


def evaluate_results_comprehensive(
    results_path: str,
    save_tests_dir: str | None = None,
) -> dict:
    """
    Evaluate all files using the comprehensive tiered system.
    
    Args:
        results_path: Path to results.json from the pipeline.
        save_tests_dir: If set, save ephemeral Tier 1/2 test snippets to this directory.
    """
    if save_tests_dir:
        os.makedirs(save_tests_dir, exist_ok=True)

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
        
        collector = DebugArtifactCollector() if save_tests_dir else None
        result = evaluate_comprehensive(source_code, outputs, filename, debug=collector)
        all_results.append(result)
        tier_distribution[result.tier_reached] += 1
        if collector and save_tests_dir:
            collector.save(save_tests_dir, filename)
        
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
        print("Usage: python comprehensive_eval.py <results.json> [--save-tests <dir>]")
        print()
        print("Comprehensive tiered evaluation system:")
        print("  Tier 1: Runtime crash detection (highest confidence)")
        print("  Tier 2: Mutation + Typeguard testing")
        print("  Tier 3: PEP specification compliance")
        print("  Tier 4: Design differences (uncertain)")
        print()
        print("Options:")
        print("  --save-tests <dir>  Save ephemeral test snippets for debugging")
        sys.exit(1)
    
    save_tests = None
    if "--save-tests" in sys.argv:
        idx = sys.argv.index("--save-tests")
        if idx + 1 < len(sys.argv):
            save_tests = sys.argv[idx + 1]
        else:
            print("Error: --save-tests requires a directory argument")
            sys.exit(1)
    
    evaluate_results_comprehensive(sys.argv[1], save_tests_dir=save_tests)
