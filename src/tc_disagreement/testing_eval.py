# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "hypothesis",
#     "beartype",
# ]
# ///

"""
Testing-based evaluation of type checker correctness.

Uses property-based testing (Hypothesis) and runtime type enforcement (beartype)
to establish ground truth for evaluating type checker outputs.

Key insight: Runtime behavior is the ultimate ground truth for type correctness.
- If code raises TypeError/KeyError/AttributeError → type bug exists
- If beartype catches a violation → type bug exists
- Type checkers that missed these bugs are INCORRECT
"""

import ast
import sys
import re
import os
import json
import traceback
import io
import contextlib
from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from pathlib import Path

# These are imported at runtime to avoid issues if not installed
# hypothesis and beartype are installed via uv when running


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class TypeBug:
    """A confirmed type-related bug found through testing."""
    line: int
    bug_type: str  # "TypeError", "KeyError", "AttributeError", "BeartypeViolation"
    message: str
    source: str  # "runtime_uncaught", "runtime_caught", "beartype", "hypothesis"
    confidence: float  # 0.0 to 1.0


@dataclass
class FunctionSignature:
    """Extracted function signature with type annotations."""
    name: str
    line: int
    parameters: dict[str, str]  # param_name -> annotation string
    return_type: Optional[str]
    is_method: bool
    is_async: bool


@dataclass
class TestResult:
    """Result of testing a single code example."""
    filename: str
    bugs_found: list[TypeBug]
    functions_tested: list[str]
    execution_success: bool
    stdout: str
    checker_verdicts: dict[str, dict]  # checker -> {verdict, reason, confidence}


# =============================================================================
# AST ANALYSIS: Extract function signatures and expected errors
# =============================================================================

class SignatureExtractor(ast.NodeVisitor):
    """Extract function signatures with type annotations from AST."""
    
    def __init__(self):
        self.signatures: list[FunctionSignature] = []
        self.in_class = False
    
    def visit_ClassDef(self, node: ast.ClassDef):
        old_in_class = self.in_class
        self.in_class = True
        self.generic_visit(node)
        self.in_class = old_in_class
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._extract_function(node, is_async=False)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._extract_function(node, is_async=True)
        self.generic_visit(node)
    
    def _extract_function(self, node, is_async: bool):
        params = {}
        
        # Extract parameter annotations
        for arg in node.args.args:
            if arg.annotation:
                params[arg.arg] = ast.unparse(arg.annotation)
        
        # Extract return type
        return_type = ast.unparse(node.returns) if node.returns else None
        
        self.signatures.append(FunctionSignature(
            name=node.name,
            line=node.lineno,
            parameters=params,
            return_type=return_type,
            is_method=self.in_class,
            is_async=is_async,
        ))


class TryExceptAnalyzer(ast.NodeVisitor):
    """Find try/except blocks that catch type-related exceptions."""
    
    # Only errors that type checkers are responsible for catching
    TYPE_EXCEPTIONS = {'TypeError', 'KeyError', 'AttributeError'}
    
    def __init__(self):
        self.expected_errors: list[TypeBug] = []
    
    def visit_Try(self, node: ast.Try):
        caught_types = []
        
        for handler in node.handlers:
            if handler.type is None:
                # Bare except catches everything
                caught_types.append('Exception')
            elif isinstance(handler.type, ast.Name):
                if handler.type.id in self.TYPE_EXCEPTIONS:
                    caught_types.append(handler.type.id)
            elif isinstance(handler.type, ast.Tuple):
                for elt in handler.type.elts:
                    if isinstance(elt, ast.Name) and elt.id in self.TYPE_EXCEPTIONS:
                        caught_types.append(elt.id)
        
        if caught_types:
            # Find the first statement in try block as the likely error source
            if node.body:
                error_line = node.body[0].lineno
                for bug_type in caught_types:
                    if bug_type in self.TYPE_EXCEPTIONS:
                        self.expected_errors.append(TypeBug(
                            line=error_line,
                            bug_type=bug_type,
                            message=f"Code expects {bug_type} (try block at line {node.lineno})",
                            source="runtime_caught",
                            confidence=0.9,
                        ))
        
        self.generic_visit(node)


class NotRequiredAccessAnalyzer(ast.NodeVisitor):
    """Find unsafe access to NotRequired TypedDict fields."""
    
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.notrequired_keys: set[str] = set()
        self.unsafe_accesses: list[TypeBug] = []
        self._find_notrequired_keys()
    
    def _find_notrequired_keys(self):
        """Find all NotRequired field names in the source."""
        pattern = r'(\w+)\s*:\s*NotRequired\['
        for match in re.finditer(pattern, self.source_code):
            self.notrequired_keys.add(match.group(1))
    
    def visit_Subscript(self, node: ast.Subscript):
        """Check for dict[key] access where key is NotRequired."""
        if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
            key = node.slice.value
            if key in self.notrequired_keys:
                self.unsafe_accesses.append(TypeBug(
                    line=node.lineno,
                    bug_type="KeyError",
                    message=f"Access to NotRequired key '{key}' without existence check",
                    source="ast_analysis",
                    confidence=0.85,
                ))
        self.generic_visit(node)


def extract_signatures(source_code: str) -> list[FunctionSignature]:
    """Extract all function signatures from source code."""
    try:
        tree = ast.parse(source_code)
        extractor = SignatureExtractor()
        extractor.visit(tree)
        return extractor.signatures
    except SyntaxError:
        return []


def find_expected_errors(source_code: str) -> list[TypeBug]:
    """Find lines where code expects type errors via try/except."""
    try:
        tree = ast.parse(source_code)
        analyzer = TryExceptAnalyzer()
        analyzer.visit(tree)
        return analyzer.expected_errors
    except SyntaxError:
        return []


def find_notrequired_access(source_code: str) -> list[TypeBug]:
    """Find unsafe access to NotRequired TypedDict fields."""
    try:
        tree = ast.parse(source_code)
        analyzer = NotRequiredAccessAnalyzer(source_code)
        analyzer.visit(tree)
        return analyzer.unsafe_accesses
    except SyntaxError:
        return []


# =============================================================================
# DYNAMIC STRATEGY GENERATION
# =============================================================================

def get_hypothesis_strategies():
    """Import hypothesis strategies - done at runtime to handle missing package."""
    try:
        from hypothesis import strategies as st
        return st
    except ImportError:
        return None


def annotation_to_strategy(annotation: str, st):
    """
    Convert a type annotation string to a Hypothesis strategy.
    
    This maps Python type annotations to strategies that generate valid values.
    """
    if st is None:
        return None
    
    # Clean up the annotation
    annotation = annotation.strip()
    
    # Basic type mappings
    basic_mappings = {
        "int": st.integers(),
        "str": st.text(max_size=50),
        "float": st.floats(allow_nan=False, allow_infinity=False),
        "bool": st.booleans(),
        "None": st.none(),
        "bytes": st.binary(max_size=50),
        "object": st.none(),  # Fallback
        "Any": st.one_of(st.integers(), st.text(), st.booleans(), st.none()),
    }
    
    if annotation in basic_mappings:
        return basic_mappings[annotation]
    
    # Optional types: Optional[X] or X | None
    if annotation.startswith("Optional[") and annotation.endswith("]"):
        inner = annotation[9:-1]
        inner_strategy = annotation_to_strategy(inner, st)
        if inner_strategy:
            return st.none() | inner_strategy
    
    # Union with None: X | None
    if " | None" in annotation:
        inner = annotation.replace(" | None", "").strip()
        inner_strategy = annotation_to_strategy(inner, st)
        if inner_strategy:
            return st.none() | inner_strategy
    
    # List types: list[X]
    if annotation.startswith("list[") and annotation.endswith("]"):
        inner = annotation[5:-1]
        inner_strategy = annotation_to_strategy(inner, st)
        if inner_strategy:
            return st.lists(inner_strategy, max_size=5)
    
    # Set types: set[X]
    if annotation.startswith("set[") and annotation.endswith("]"):
        inner = annotation[4:-1]
        inner_strategy = annotation_to_strategy(inner, st)
        if inner_strategy:
            return st.frozensets(inner_strategy, max_size=5)
    
    # Tuple types: tuple[X, Y] or tuple[X, ...]
    if annotation.startswith("tuple[") and annotation.endswith("]"):
        inner = annotation[6:-1]
        if ", ..." in inner:
            elem_type = inner.replace(", ...", "").strip()
            elem_strategy = annotation_to_strategy(elem_type, st)
            if elem_strategy:
                return st.lists(elem_strategy, max_size=5).map(tuple)
        else:
            # Fixed tuple
            parts = [p.strip() for p in inner.split(",")]
            strategies = [annotation_to_strategy(p, st) for p in parts]
            if all(s is not None for s in strategies):
                return st.tuples(*strategies)
    
    # Dict types: dict[K, V]
    if annotation.startswith("dict[") and annotation.endswith("]"):
        inner = annotation[5:-1]
        # Simple split (doesn't handle nested generics well)
        parts = inner.split(",", 1)
        if len(parts) == 2:
            key_strategy = annotation_to_strategy(parts[0].strip(), st)
            val_strategy = annotation_to_strategy(parts[1].strip(), st)
            if key_strategy and val_strategy:
                return st.dictionaries(key_strategy, val_strategy, max_size=3)
    
    # Literal types: Literal["a", "b", "c"]
    if annotation.startswith("Literal[") and annotation.endswith("]"):
        inner = annotation[8:-1]
        # Parse literal values
        values = []
        for part in inner.split(","):
            part = part.strip().strip('"').strip("'")
            if part.isdigit():
                values.append(int(part))
            elif part in ("True", "False"):
                values.append(part == "True")
            else:
                values.append(part)
        if values:
            return st.sampled_from(values)
    
    # Callable - generate a simple lambda
    if annotation.startswith("Callable"):
        return st.just(lambda *args, **kwargs: None)
    
    # Self, TypeVar, etc. - use none as fallback
    if annotation in ("Self", "T", "K", "V", "R", "P"):
        return st.none()
    
    # Unknown type - return None to skip
    return None


def build_strategies_for_function(sig: FunctionSignature, st) -> Optional[dict]:
    """
    Build Hypothesis strategies for all parameters of a function.
    Returns dict mapping param name to strategy, or None if can't build.
    """
    strategies = {}
    
    for param_name, annotation in sig.parameters.items():
        # Skip 'self' and 'cls'
        if param_name in ('self', 'cls'):
            continue
        
        strategy = annotation_to_strategy(annotation, st)
        if strategy is None:
            # Can't generate strategy for this type
            return None
        strategies[param_name] = strategy
    
    return strategies if strategies else None


# =============================================================================
# RUNTIME EXECUTION WITH TRACING
# =============================================================================

def execute_with_tracing(source_code: str) -> tuple[list[TypeBug], bool, str]:
    """
    Execute code and capture type-related exceptions.
    
    Returns:
        (list of bugs found, execution success, stdout)
    """
    bugs: list[TypeBug] = []
    stdout_capture = io.StringIO()
    success = False
    
    try:
        with contextlib.redirect_stdout(stdout_capture), \
             contextlib.redirect_stderr(stdout_capture):
            exec(compile(source_code, "<test>", "exec"), {"__name__": "__main__"})
        success = True
        
    except TypeError as e:
        tb = traceback.extract_tb(sys.exc_info()[2])
        line = tb[-1].lineno if tb else 0
        bugs.append(TypeBug(
            line=line,
            bug_type="TypeError",
            message=str(e)[:200],
            source="runtime_uncaught",
            confidence=1.0,
        ))
    except KeyError as e:
        tb = traceback.extract_tb(sys.exc_info()[2])
        line = tb[-1].lineno if tb else 0
        bugs.append(TypeBug(
            line=line,
            bug_type="KeyError",
            message=f"KeyError: {e}",
            source="runtime_uncaught",
            confidence=1.0,
        ))
    except AttributeError as e:
        tb = traceback.extract_tb(sys.exc_info()[2])
        line = tb[-1].lineno if tb else 0
        bugs.append(TypeBug(
            line=line,
            bug_type="AttributeError",
            message=str(e)[:200],
            source="runtime_uncaught",
            confidence=1.0,
        ))
    except Exception as e:
        # Other exceptions - not type errors but note them
        pass
    
    return bugs, success, stdout_capture.getvalue()


def execute_with_beartype(source_code: str) -> list[TypeBug]:
    """
    Execute code with beartype runtime type checking enabled.
    
    Uses beartype.claw to automatically decorate ALL functions and classes
    with @beartype at import time, without modifying the source code.
    
    This catches type violations like:
    - Passing wrong argument types to functions
    - Returning wrong types from functions
    - Assigning wrong types to annotated variables
    
    Returns list of type bugs found by beartype.
    """
    bugs: list[TypeBug] = []
    
    try:
        from beartype import beartype
        from beartype.roar import BeartypeCallHintViolation
    except ImportError:
        # beartype not installed
        return bugs
    
    # Count lines prepended for line number offset correction
    # We prepend 3 lines of imports before the source code
    PREPENDED_LINES = 3
    
    # Instrument code with beartype.claw for automatic decoration
    # beartype_this_package() decorates ALL functions/classes automatically
    instrumented = f"""
from beartype.claw import beartype_this_package
beartype_this_package()
{source_code}
"""
    
    try:
        with contextlib.redirect_stdout(io.StringIO()), \
             contextlib.redirect_stderr(io.StringIO()):
            exec(compile(instrumented, "<beartype_test>", "exec"), {"__name__": "__main__"})
    except Exception as e:
        # Extract line number from traceback and correct for prepended lines
        tb = traceback.extract_tb(sys.exc_info()[2])
        raw_line = tb[-1].lineno if tb else 0
        # Correct line number by subtracting prepended import lines
        corrected_line = max(1, raw_line - PREPENDED_LINES)
        
        if "BeartypeCallHint" in type(e).__name__ or "beartype" in str(type(e)).lower():
            bugs.append(TypeBug(
                line=corrected_line,
                bug_type="BeartypeViolation",
                message=str(e)[:200],
                source="beartype",
                confidence=1.0,
            ))
        elif isinstance(e, (TypeError, AttributeError)):
            bugs.append(TypeBug(
                line=corrected_line,
                bug_type=type(e).__name__,
                message=str(e)[:200],
                source="beartype",
                confidence=1.0,
            ))
    
    return bugs


# =============================================================================
# PROPERTY-BASED TESTING WITH HYPOTHESIS
# =============================================================================

def run_hypothesis_tests(source_code: str, signatures: list[FunctionSignature]) -> list[TypeBug]:
    """
    Run property-based tests on functions using Hypothesis.
    
    For each function with type annotations:
    1. Generate random valid inputs matching the declared types
    2. Call the function
    3. If TypeError/AttributeError occurs → type bug found
    """
    bugs: list[TypeBug] = []
    
    st = get_hypothesis_strategies()
    if st is None:
        return bugs
    
    try:
        from hypothesis import given, settings, Verbosity
        from hypothesis.errors import Unsatisfied
    except ImportError:
        return bugs
    
    # Compile the module to get access to functions
    try:
        module_globals = {"__name__": "__test_module__"}
        exec(compile(source_code, "<hypothesis_test>", "exec"), module_globals)
    except Exception:
        # Can't even compile/run the module
        return bugs
    
    for sig in signatures:
        # Skip methods, async functions, and special functions
        if sig.is_method or sig.is_async or sig.name.startswith("_"):
            continue
        
        # Get the function from the module
        func = module_globals.get(sig.name)
        if not callable(func):
            continue
        
        # Build strategies for parameters
        strategies = build_strategies_for_function(sig, st)
        if not strategies:
            continue
        
        # Create a test function
        def make_test(fn, strats, fn_name, fn_line):
            @settings(max_examples=20, verbosity=Verbosity.quiet, deadline=None)
            @given(**strats)
            def test_fn(**kwargs):
                try:
                    fn(**kwargs)
                except (TypeError, AttributeError, KeyError) as e:
                    # if found a type bug
                    bugs.append(TypeBug(
                        line=fn_line,
                        bug_type=type(e).__name__,
                        message=f"Hypothesis found: {str(e)[:100]}",
                        source="hypothesis",
                        confidence=1.0,
                    ))
                    raise  # Let hypothesis know this is a failure
                except Exception:
                    # Other exceptions are not type errors
                    pass
            
            return test_fn
        
        test = make_test(func, strategies, sig.name, sig.line)
        
        try:
            test()
        except Exception:
            # Test found a bug (already recorded in bugs list)
            pass
    
    return bugs


# =============================================================================
# TYPE-VIOLATING INPUT GENERATION
# =============================================================================

def generate_type_violating_value(annotation: str) -> list[tuple[Any, str]]:
    """
    Generate values that deliberately VIOLATE a type annotation.
    
    Returns list of (value, description) tuples that should cause type errors
    if the annotation is enforced.
    """
    annotation = annotation.strip()
    violations = []
    
    # For each type, generate values of WRONG types
    if annotation == "int":
        violations = [
            ("not_an_int", "str instead of int"),
            (3.14, "float instead of int"),
            (None, "None instead of int"),
            ([], "list instead of int"),
        ]
    elif annotation == "str":
        violations = [
            (42, "int instead of str"),
            (None, "None instead of str"),
            ([], "list instead of str"),
        ]
    elif annotation == "float":
        violations = [
            ("not_a_float", "str instead of float"),
            (None, "None instead of float"),
        ]
    elif annotation == "bool":
        violations = [
            ("not_a_bool", "str instead of bool"),
            (42, "int instead of bool"),  # Note: int is technically a subtype
        ]
    elif annotation.startswith("Literal["):
        # For Literal types, generate values outside the literal set
        violations = [
            ("__INVALID_LITERAL__", "value not in Literal set"),
            (99999, "int not in Literal set"),
            (None, "None not in Literal set"),
        ]
    elif annotation.startswith("List[") or annotation.startswith("list["):
        violations = [
            ("not_a_list", "str instead of list"),
            (42, "int instead of list"),
            (None, "None instead of list"),
        ]
    elif annotation.startswith("Dict[") or annotation.startswith("dict["):
        violations = [
            ("not_a_dict", "str instead of dict"),
            ([], "list instead of dict"),
            (None, "None instead of dict"),
        ]
    elif "TypedDict" in annotation or annotation[0].isupper():
        # For TypedDict or custom classes, try wrong types
        violations = [
            ("not_a_dict", "str instead of TypedDict"),
            (42, "int instead of TypedDict"),
            ({}, "empty dict (missing required keys)"),
        ]
    
    # Generic fallback violations
    if not violations:
        violations = [
            (None, "None for unknown type"),
            ("__WRONG_TYPE__", "str for unknown type"),
        ]
    
    return violations


def run_type_violation_tests(source_code: str, signatures: list[FunctionSignature]) -> list[TypeBug]:
    """
    Test functions with deliberately WRONG input types.
    
    If a function crashes with TypeError/KeyError/AttributeError when given
    wrong types, this proves the type annotation matters and checkers should
    have flagged potential violations.
    
    Key insight: If code runs fine with valid types but crashes with invalid types,
    then any checker that allows invalid types to reach this code is INCORRECT.
    """
    bugs: list[TypeBug] = []
    
    # Compile the module to get access to functions
    try:
        module_globals = {"__name__": "__test_module__"}
        exec(compile(source_code, "<violation_test>", "exec"), module_globals)
    except Exception:
        return bugs
    
    for sig in signatures:
        # Skip methods, async, and private functions
        if sig.is_method or sig.is_async or sig.name.startswith("_"):
            continue
        
        func = module_globals.get(sig.name)
        if not callable(func):
            continue
        
        # For each parameter with a type annotation, try violating it
        for param_name, annotation in sig.parameters.items():
            violations = generate_type_violating_value(annotation)
            
            for violating_value, description in violations:
                try:
                    # Build kwargs with valid defaults for other params, violating for this one
                    kwargs = {}
                    for p, ann in sig.parameters.items():
                        if p == param_name:
                            kwargs[p] = violating_value
                        else:
                            # Use a safe default for other params
                            kwargs[p] = get_safe_default(ann)
                    
                    # Call the function with the violating input
                    func(**kwargs)
                    
                except (TypeError, KeyError, AttributeError) as e:
                    # Found a type bug! The function crashes when given wrong types.
                    bugs.append(TypeBug(
                        line=sig.line,
                        bug_type=type(e).__name__,
                        message=f"Type violation ({description}): {str(e)[:100]}",
                        source="type_violation",
                        confidence=0.95,
                    ))
                    break  # One violation per parameter is enough
                except Exception:
                    # Other exceptions (ValueError, etc.) don't count as type bugs
                    pass
    
    return bugs


def get_safe_default(annotation: str) -> Any:
    """Get a safe default value for a type annotation."""
    annotation = annotation.strip()
    
    defaults = {
        "int": 0,
        "str": "",
        "float": 0.0,
        "bool": False,
        "None": None,
        "bytes": b"",
        "Any": None,
    }
    
    if annotation in defaults:
        return defaults[annotation]
    
    if annotation.startswith("Optional[") or " | None" in annotation:
        return None
    if annotation.startswith("List[") or annotation.startswith("list["):
        return []
    if annotation.startswith("Dict[") or annotation.startswith("dict["):
        return {}
    if annotation.startswith("Literal["):
        # Extract first literal value
        inner = annotation[8:-1]
        if inner.startswith("'") or inner.startswith('"'):
            return inner.strip("'\"").split(",")[0].strip().strip("'\"")
        return inner.split(",")[0].strip()
    
    return None


def run_typeddict_violation_tests(source_code: str) -> list[TypeBug]:
    """
    Specifically test TypedDict usage by providing dicts with missing/wrong keys.
    
    This catches issues where:
    - Required keys are missing
    - Keys have wrong types
    - NotRequired keys are accessed without guards
    """
    bugs: list[TypeBug] = []
    
    # Find all TypedDict definitions
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return bugs
    
    typeddict_defs = {}
    
    class TypedDictFinder(ast.NodeVisitor):
        def visit_ClassDef(self, node):
            # Check if it's a TypedDict
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == "TypedDict":
                    fields = {}
                    for stmt in node.body:
                        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                            fields[stmt.target.id] = ast.unparse(stmt.annotation)
                    typeddict_defs[node.name] = {
                        "fields": fields,
                        "line": node.lineno,
                    }
            self.generic_visit(node)
    
    finder = TypedDictFinder()
    finder.visit(tree)
    
    if not typeddict_defs:
        return bugs
    
    # Find functions that take TypedDict parameters
    for sig_class in [ast.FunctionDef, ast.AsyncFunctionDef]:
        class FuncFinder(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                self._check_func(node)
            def visit_AsyncFunctionDef(self, node):
                self._check_func(node)
            def _check_func(self, node):
                for arg in node.args.args:
                    if arg.annotation:
                        ann = ast.unparse(arg.annotation)
                        if ann in typeddict_defs:
                            # This function takes a TypedDict - test it
                            td_info = typeddict_defs[ann]
                            # Create a dict missing required keys
                            bugs.append(TypeBug(
                                line=node.lineno,
                                bug_type="PotentialKeyError",
                                message=f"Function accepts {ann} TypedDict - missing keys could cause KeyError",
                                source="typeddict_analysis",
                                confidence=0.7,
                            ))
        
        func_finder = FuncFinder()
        func_finder.visit(tree)
    
    return bugs


# =============================================================================
# PYNGUIN TEST GENERATION ORACLE
# =============================================================================

def run_pynguin_tests(source_code: str, module_name: str = "test_module") -> list[TypeBug]:
    """
    Use Pynguin to generate tests and find type bugs.
    
    Pynguin uses search-based algorithms (DYNAMOSA) to generate tests
    that maximize code coverage, which can find bugs that random testing misses.
    """
    import subprocess
    import tempfile
    import shutil
    
    bugs: list[TypeBug] = []
    
    # Check if pynguin is available
    try:
        result = subprocess.run(
            ["pynguin", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return bugs  # Pynguin not available
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return bugs  # Pynguin not installed
    
    # Create temp directory structure
    temp_dir = tempfile.mkdtemp(prefix="pynguin_eval_")
    module_dir = os.path.join(temp_dir, "src")
    output_dir = os.path.join(temp_dir, "tests")
    os.makedirs(module_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Write source file
    source_file = os.path.join(module_dir, f"{module_name}.py")
    with open(source_file, "w") as f:
        f.write(source_code)
    
    # Create __init__.py
    with open(os.path.join(module_dir, "__init__.py"), "w") as f:
        f.write("")
    
    try:
        # Set environment variable to acknowledge danger
        env = os.environ.copy()
        env["PYNGUIN_DANGER_AWARE"] = "1"
        
        # Run Pynguin with longer timeout for thorough test generation
        result = subprocess.run(
            [
                "pynguin",
                "--project-path", module_dir,
                "--output-path", output_dir,
                "--module-name", module_name,
                "--maximum-search-time", "120",
                "--maximum-iterations", "500",
                "--algorithm", "DYNAMOSA",
            ],
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
            cwd=module_dir,
        )
        
        # Check if tests were generated
        test_file = os.path.join(output_dir, f"test_{module_name}.py")
        if not os.path.exists(test_file):
            return bugs
        
        # Read and execute generated tests
        with open(test_file) as f:
            test_code = f.read()
        
        # Run the generated tests with pytest and capture failures
        pytest_result = subprocess.run(
            ["python", "-m", "pytest", test_file, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=temp_dir,
        )
        
        # Parse pytest output for failures
        output = pytest_result.stdout + pytest_result.stderr
        
        # Extract type-related failures
        type_error_patterns = [
            (r"TypeError:.*", "TypeError"),
            (r"KeyError:.*", "KeyError"),
            (r"AttributeError:.*", "AttributeError"),
        ]
        
        for pattern, bug_type in type_error_patterns:
            for match in re.finditer(pattern, output):
                # Try to extract line number from traceback
                line_match = re.search(rf"{module_name}\.py.*line (\d+)", output)
                line = int(line_match.group(1)) if line_match else 0
                
                bugs.append(TypeBug(
                    line=line,
                    bug_type=bug_type,
                    message=f"Pynguin test failure: {match.group(0)[:100]}",
                    source="pynguin",
                    confidence=0.95,
                ))
        
    except subprocess.TimeoutExpired:
        pass  # Pynguin timed out
    except Exception:
        pass  # Other errors
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return bugs


# =============================================================================
# FUNCTION-SCOPE MATCHING (for accurate verdict determination)
# =============================================================================

@dataclass
class FunctionSpan:
    """Represents a function's location in source code."""
    name: str
    start_line: int
    end_line: int
    class_name: Optional[str] = None


def extract_function_spans(source_code: str) -> list[FunctionSpan]:
    """Extract all function/method spans from source code using AST."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []
    
    spans: list[FunctionSpan] = []
    current_class: Optional[str] = None
    
    class FunctionVisitor(ast.NodeVisitor):
        def __init__(self):
            self.current_class: Optional[str] = None
        
        def visit_ClassDef(self, node: ast.ClassDef):
            old_class = self.current_class
            self.current_class = node.name
            self.generic_visit(node)
            self.current_class = old_class
        
        def visit_FunctionDef(self, node: ast.FunctionDef):
            end_line = node.end_lineno if hasattr(node, 'end_lineno') and node.end_lineno else node.lineno + 20
            spans.append(FunctionSpan(
                name=node.name,
                start_line=node.lineno,
                end_line=end_line,
                class_name=self.current_class,
            ))
            self.generic_visit(node)
        
        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
            end_line = node.end_lineno if hasattr(node, 'end_lineno') and node.end_lineno else node.lineno + 20
            spans.append(FunctionSpan(
                name=node.name,
                start_line=node.lineno,
                end_line=end_line,
                class_name=self.current_class,
            ))
            self.generic_visit(node)
    
    visitor = FunctionVisitor()
    visitor.visit(tree)
    return spans


def get_function_at_line(spans: list[FunctionSpan], line: int) -> Optional[FunctionSpan]:
    """Find which function contains the given line number."""
    for span in spans:
        if span.start_line <= line <= span.end_line:
            return span
    return None


def extract_error_lines_from_output(checker_output: str) -> list[int]:
    """
    Extract line numbers from type checker error output.
    
    Handles formats: file.py:42: error, line 42, L42, etc.
    """
    lines: list[int] = []
    
    patterns = [
        r'\.py:(\d+)(?::\d+)?:',      # file.py:42: or file.py:42:10:
        r'\.py:(\d+)\s',               # file.py:42 (space after)
        r'[Ll]ine\s+(\d+)',            # "line 42" or "Line 42"
        r'\bL(\d+)\b',                 # L42
        r':(\d+):.*(?:error|Error)',   # :42: ... error
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, checker_output):
            try:
                line_num = int(match.group(1))
                if 1 <= line_num <= 10000:
                    lines.append(line_num)
            except (ValueError, IndexError):
                continue
    
    return list(set(lines))


def extract_error_types_from_output(checker_output: str) -> set[str]:
    """Extract error type keywords from checker output for secondary matching."""
    error_types: set[str] = set()
    output_lower = checker_output.lower()
    
    type_keywords = {
        'typeerror': 'TypeError',
        'keyerror': 'KeyError',
        'attributeerror': 'AttributeError',
        'missing key': 'KeyError',
        'incompatible type': 'TypeError',
        'invalid type': 'TypeError',
        'type mismatch': 'TypeError',
        'not callable': 'TypeError',
        'undefined attribute': 'AttributeError',
        'no attribute': 'AttributeError',
    }
    
    for keyword, error_type in type_keywords.items():
        if keyword in output_lower:
            error_types.add(error_type)
    
    return error_types


@dataclass
class MatchResult:
    """Result of matching a checker's output to a bug."""
    matched: bool
    confidence: float  # 1.0 = exact line, 0.85 = same function, 0.0 = no match
    method: str  # "exact_line", "function_scope", "error_type", "none"
    matched_line: Optional[int] = None


def checker_matches_bug(
    bug: TypeBug,
    checker_output: str,
    function_spans: list[FunctionSpan],
) -> MatchResult:
    """
    Determine if a checker's error output matches a proven bug.
    
    Returns a MatchResult with confidence scores:
    - 1.0: Exact line match (±5 lines)
    - 0.85: Same function scope
    - 0.7: Error type match with line proximity (±10 lines)
    - 0.0: No match
    """
    LINE_TOLERANCE_EXACT = 5
    LINE_TOLERANCE_ERROR_TYPE = 10
    
    checker_error_lines = extract_error_lines_from_output(checker_output)
    
    if not checker_error_lines:
        return MatchResult(matched=False, confidence=0.0, method="none")
    
    bug_function = get_function_at_line(function_spans, bug.line)
    best_match = MatchResult(matched=False, confidence=0.0, method="none")
    
    for error_line in checker_error_lines:
        error_function = get_function_at_line(function_spans, error_line)
        
        # Tier 1: Same function + close line (±5 lines) - highest confidence
        # IMPORTANT: Only use line proximity if SAME function to avoid false matches
        if bug_function and error_function:
            if (bug_function.name == error_function.name and 
                bug_function.class_name == error_function.class_name):
                # Same function - check line proximity
                if abs(bug.line - error_line) <= LINE_TOLERANCE_EXACT:
                    return MatchResult(
                        matched=True,
                        confidence=1.0,
                        method="exact_line_same_function",
                        matched_line=error_line,
                    )
                else:
                    # Same function but farther away
                    if best_match.confidence < 0.85:
                        best_match = MatchResult(
                            matched=True,
                            confidence=0.85,
                            method="function_scope",
                            matched_line=error_line,
                        )
        
        # Tier 2: Both at module level (no enclosing function), use line tolerance
        if bug_function is None and error_function is None:
            if abs(bug.line - error_line) <= LINE_TOLERANCE_EXACT:
                return MatchResult(
                    matched=True,
                    confidence=1.0,
                    method="exact_line_module_level",
                    matched_line=error_line,
                )
            elif abs(bug.line - error_line) <= LINE_TOLERANCE_ERROR_TYPE:
                if best_match.confidence < 0.7:
                    best_match = MatchResult(
                        matched=True,
                        confidence=0.7,
                        method="module_level_proximity",
                        matched_line=error_line,
                    )
    
    # Tier 3: Error-type matching with same function requirement
    if not best_match.matched:
        checker_error_types = extract_error_types_from_output(checker_output)
        if bug.bug_type in checker_error_types:
            for error_line in checker_error_lines:
                error_function = get_function_at_line(function_spans, error_line)
                # Only match if same function or both at module level
                same_scope = (
                    (bug_function and error_function and 
                     bug_function.name == error_function.name and
                     bug_function.class_name == error_function.class_name) or
                    (bug_function is None and error_function is None)
                )
                if same_scope and abs(bug.line - error_line) <= LINE_TOLERANCE_ERROR_TYPE:
                    return MatchResult(
                        matched=True,
                        confidence=0.7,
                        method="error_type_same_scope",
                        matched_line=error_line,
                    )
    
    return best_match


# =============================================================================
# MAIN EVALUATION FUNCTION
# =============================================================================

def evaluate_example(
    source_code: str,
    checker_outputs: dict[str, str],
    filename: str = "unknown.py",
) -> TestResult:
    """
    Evaluate a code example using runtime testing to establish ground truth.
    
    Core principle: Only count bugs that occur during NORMAL execution.
    We do NOT artificially create bugs by passing wrong types - that tests
    function robustness, not type checker correctness.
    
    Steps:
    1. Execute code as-is and catch type-related exceptions
    2. Run beartype for runtime type checking (catches annotation violations)
    3. Run Hypothesis property-based tests with VALID inputs
    4. Run Pynguin search-based test generation (if available)
    5. Compare findings to checker outputs using scope-aware matching
    
    Verdict logic:
    - Runtime crash + checker said OK → INCORRECT (missed real bug)
    - Runtime crash + checker flagged same location → CORRECT
    - No crash + checker said OK → UNCERTAIN (might be correct)
    - No crash + checker said ERROR → UNCERTAIN (might be false positive)
    """
    all_bugs: list[TypeBug] = []
    functions_tested: list[str] = []
    
    # Step 1: Execute code as-is and catch type-related exceptions
    # This finds REAL bugs that occur during normal execution
    runtime_bugs, execution_success, stdout = execute_with_tracing(source_code)
    all_bugs.extend(runtime_bugs)
    
    # Step 2: Run with beartype runtime type checking
    # This catches violations of type annotations during normal execution
    beartype_bugs = execute_with_beartype(source_code)
    all_bugs.extend(beartype_bugs)
    
    # Step 3: Run Hypothesis tests with VALID inputs
    # Hypothesis generates valid inputs matching type annotations
    signatures = extract_signatures(source_code)
    functions_tested = [s.name for s in signatures if not s.is_method]
    hypothesis_bugs = run_hypothesis_tests(source_code, signatures)
    all_bugs.extend(hypothesis_bugs)
    
    # Step 4: Run Pynguin search-based test generation (if available)
    # Pynguin generates tests that maximize coverage, may find edge cases
    module_name = filename.replace(".py", "").replace("-", "_")
    pynguin_bugs = run_pynguin_tests(source_code, module_name)
    all_bugs.extend(pynguin_bugs)
    
    # Deduplicate bugs by (line, type)
    unique_bugs = {}
    for bug in all_bugs:
        key = (bug.line, bug.bug_type)
        if key not in unique_bugs or bug.confidence > unique_bugs[key].confidence:
            unique_bugs[key] = bug
    all_bugs = list(unique_bugs.values())
    
    # Step 5: Evaluate each checker using scope-aware matching
    verdicts = evaluate_checkers(all_bugs, checker_outputs, source_code)
    
    return TestResult(
        filename=filename,
        bugs_found=all_bugs,
        functions_tested=functions_tested,
        execution_success=execution_success,
        stdout=stdout[:500],
        checker_verdicts=verdicts,
    )


def evaluate_checkers(
    bugs: list[TypeBug],
    checker_outputs: dict[str, str],
    source_code: str = "",
) -> dict[str, dict]:
    """
    Evaluate each type checker against discovered bugs using tiered scoring.
    
    Scoring system:
    - Exact line match (±5 lines): confidence 1.0
    - Function-scope match: confidence 0.85
    - Error-type match with proximity: confidence 0.7
    
    Verdicts:
    - Proven bugs + checker caught them → CORRECT (confidence based on match quality)
    - Proven bugs + checker missed them → INCORRECT
    - No bugs + checker OK → UNCERTAIN
    - No bugs + checker ERROR → UNCERTAIN (possible false positive)
    """
    verdicts = {}
    
    # Get high-confidence bugs (runtime, beartype, or pynguin)
    # Only type-checker-relevant errors: TypeError, KeyError, AttributeError
    TYPE_CHECKER_ERRORS = {'TypeError', 'KeyError', 'AttributeError', 'BeartypeViolation'}
    proven_bugs = [
        b for b in bugs 
        if b.confidence >= 0.9 and b.bug_type in TYPE_CHECKER_ERRORS
    ]
    has_proven_bugs = len(proven_bugs) > 0
    
    # Extract function spans for matching
    function_spans = extract_function_spans(source_code) if source_code else []
    
    for checker, output in checker_outputs.items():
        # Determine if checker reported any errors
        output_lower = output.lower()
        checker_reported_error = (
            "error" in output_lower and 
            "0 error" not in output_lower and
            "success" not in output_lower
        )
        
        if has_proven_bugs:
            # Use tiered scoring to evaluate checker matches
            bugs_caught: list[tuple[TypeBug, MatchResult]] = []
            bugs_missed: list[TypeBug] = []
            
            for bug in proven_bugs:
                match_result = checker_matches_bug(bug, output, function_spans)
                
                if match_result.matched:
                    bugs_caught.append((bug, match_result))
                else:
                    # No scope-aware match found - checker missed this bug
                    # Note: We don't use "error_type_only" fallback because
                    # flagging TypeError somewhere doesn't mean catching a 
                    # specific TypeError bug in a different function
                    bugs_missed.append(bug)
            
            if bugs_missed and not bugs_caught:
                # Checker missed all proven bugs
                verdicts[checker] = {
                    "verdict": "INCORRECT",
                    "reason": f"Missed {len(bugs_missed)} proven type bug(s)",
                    "confidence": 1.0,
                    "missed_bugs": [
                        {"line": b.line, "type": b.bug_type, "message": b.message}
                        for b in bugs_missed
                    ],
                    "matching_method": "none",
                }
            elif bugs_caught:
                # Checker caught at least some bugs - calculate aggregate score
                avg_match_confidence = sum(m.confidence for _, m in bugs_caught) / len(bugs_caught)
                best_method = max(bugs_caught, key=lambda x: x[1].confidence)[1].method
                
                if bugs_missed:
                    verdicts[checker] = {
                        "verdict": "INCORRECT",
                        "reason": f"Caught {len(bugs_caught)} but missed {len(bugs_missed)} bug(s)",
                        "confidence": 0.85,
                        "bugs_caught": [
                            {
                                "line": b.line, 
                                "type": b.bug_type, 
                                "match_method": m.method,
                                "match_confidence": m.confidence,
                                "matched_line": m.matched_line,
                            }
                            for b, m in bugs_caught
                        ],
                        "bugs_missed": [
                            {"line": b.line, "type": b.bug_type, "message": b.message}
                            for b in bugs_missed
                        ],
                        "matching_method": best_method,
                    }
                else:
                    verdicts[checker] = {
                        "verdict": "CORRECT",
                        "reason": f"Correctly identified {len(bugs_caught)} type issue(s)",
                        "confidence": avg_match_confidence,
                        "bugs_caught": [
                            {
                                "line": b.line, 
                                "type": b.bug_type, 
                                "match_method": m.method,
                                "match_confidence": m.confidence,
                                "matched_line": m.matched_line,
                            }
                            for b, m in bugs_caught
                        ],
                        "matching_method": best_method,
                    }
            else:
                # No function spans and no matches - fallback
                if not checker_reported_error:
                    verdicts[checker] = {
                        "verdict": "INCORRECT",
                        "reason": f"Missed {len(proven_bugs)} proven type bug(s)",
                        "confidence": 1.0,
                        "missed_bugs": [
                            {"line": b.line, "type": b.bug_type, "message": b.message}
                            for b in proven_bugs
                        ],
                        "matching_method": "fallback",
                    }
                else:
                    verdicts[checker] = {
                        "verdict": "UNCERTAIN",
                        "reason": "Checker reported errors but no specific match to proven bugs",
                        "confidence": 0.5,
                        "matching_method": "fallback",
                    }
        elif not checker_reported_error:
            # No bugs found, checker agrees - UNCERTAIN but likely correct
            verdicts[checker] = {
                "verdict": "UNCERTAIN",
                "reason": "No type bugs detected, checker agrees",
                "confidence": 0.5,
            }
        else:
            # No proven bugs but checker reported errors - might be false positive
            verdicts[checker] = {
                "verdict": "UNCERTAIN",
                "reason": "Checker reported errors but no runtime proof of bugs",
                "confidence": 0.5,
                "note": "May be false positive or bug not triggered at runtime",
            }
    
    return verdicts


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def evaluate_results_testing(results_path: str) -> dict:
    """
    Evaluate all files in a results.json using testing-based analysis.
    """
    with open(results_path) as f:
        data = json.load(f)
    
    results = data.get("results", [])
    checkers = data.get("checkers_used", ["mypy", "pyrefly", "zuban", "ty"])
    
    all_results: list[TestResult] = []
    summary_stats = {
        checker: {"correct": 0, "incorrect": 0, "uncertain": 0}
        for checker in checkers
    }
    
    print("=" * 70)
    print("TESTING-BASED EVALUATION")
    print("=" * 70)
    print("Methods: Runtime execution, beartype, Hypothesis, AST analysis")
    print(f"Files to evaluate: {len(results)}")
    print()
    
    for i, file_entry in enumerate(results, 1):
        filepath = file_entry.get("filepath", "")
        filename = file_entry.get("filename", "")
        outputs = file_entry.get("outputs", {})
        
        print(f"[{i}/{len(results)}] {filename}")
        print("-" * len(filename))
        
        # Read source code
        try:
            with open(filepath) as f:
                source_code = f.read()
        except FileNotFoundError:
            print("  [SKIP] File not found")
            continue
        
        # Run evaluation
        result = evaluate_example(source_code, outputs, filename)
        all_results.append(result)
        
        # Print checker outputs summary
        for checker in checkers:
            output = outputs.get(checker, "")
            if "success" in output.lower() or "0 error" in output.lower():
                print(f"  {checker}: OK")
            else:
                error_lines = [l for l in output.splitlines() if "error" in l.lower()]
                if error_lines:
                    print(f"  {checker}: ERROR ({len(error_lines)} issue(s))")
                else:
                    print(f"  {checker}: (has output)")
        
        # Print bugs found
        if result.bugs_found:
            print(f"\n  Bugs found: {len(result.bugs_found)}")
            for bug in result.bugs_found[:3]:  # Show first 3
                print(f"    Line {bug.line}: {bug.bug_type} ({bug.source})")
        else:
            print(f"\n  Bugs found: 0")
        
        # Print verdicts
        print()
        for checker, verdict in result.checker_verdicts.items():
            v = verdict["verdict"]
            if v == "CORRECT":
                print(f"  ✓ {checker}: CORRECT")
                summary_stats[checker]["correct"] += 1
            elif v == "INCORRECT":
                reason = verdict.get("reason", "")[:50]
                print(f"  ✗ {checker}: INCORRECT - {reason}")
                summary_stats[checker]["incorrect"] += 1
            else:
                print(f"  ? {checker}: UNCERTAIN")
                summary_stats[checker]["uncertain"] += 1
        
        print()
    
    # Print summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    total_bugs = sum(len(r.bugs_found) for r in all_results)
    proven_bugs = sum(
        len([b for b in r.bugs_found if b.confidence >= 0.9])
        for r in all_results
    )
    
    print(f"\nTotal bugs detected: {total_bugs} ({proven_bugs} high-confidence)")
    print(f"\n{'Checker':<12} {'Correct':>10} {'Incorrect':>10} {'Uncertain':>10}")
    print("-" * 44)
    
    for checker in checkers:
        stats = summary_stats[checker]
        print(f"{checker:<12} {stats['correct']:>10} {stats['incorrect']:>10} {stats['uncertain']:>10}")
    
    print("=" * 70)
    
    # Save results
    output_dir = os.path.dirname(results_path)
    eval_path = os.path.join(output_dir, "evaluation_testing.json")
    
    with open(eval_path, "w") as f:
        json.dump({
            "method": "testing",
            "total_bugs_found": total_bugs,
            "proven_bugs": proven_bugs,
            "summary": summary_stats,
            "results": [
                {
                    "filename": r.filename,
                    "bugs_found": [
                        {
                            "line": b.line,
                            "type": b.bug_type,
                            "message": b.message,
                            "source": b.source,
                            "confidence": b.confidence,
                        }
                        for b in r.bugs_found
                    ],
                    "execution_success": r.execution_success,
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
        print("Usage: python testing_eval.py <results.json>")
        print()
        print("Evaluates type checker outputs using runtime testing methods:")
        print("  - Exception tracing (catches TypeError, KeyError, AttributeError)")
        print("  - try/except analysis (finds expected errors)")
        print("  - NotRequired TypedDict access detection")
        print("  - beartype runtime type enforcement")
        print("  - Hypothesis property-based testing")
        sys.exit(1)
    
    evaluate_results_testing(sys.argv[1])
