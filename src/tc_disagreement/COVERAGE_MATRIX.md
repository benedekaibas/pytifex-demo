# Coverage Matrix: source_analysis.py vs Generated Examples

Cross-reference of `source_analysis.py` AST analyzer rules against violation categories
found in the `generated_examples/` directory.

**Status legend:**
- **COVERED** — an existing analyzer rule in `source_analysis.py` detects this category
- **AST-DETECTABLE** — could be detected by AST analysis but no rule exists yet
- **AGENT-ONLY** — requires type-checker-level inference; beyond pure AST analysis

---

## Section 1: Implemented Analyzer Rules

| Category | Status | Rule ID | Notes |
|---|---|---|---|
| Method override signature param count mismatch | COVERED | LSP001 | PEP 484. Fires when override has fewer/more params than base. |
| Method override incompatible param/return types | COVERED | LSP002 | PEP 484. Compares annotation strings between base and override methods. |
| `Self` used outside class body | COVERED | SELF001 | PEP 673. Detects `Self` annotation in module-level functions. |
| `isinstance()` on non-`@runtime_checkable` Protocol | COVERED | PROTO001 | PEP 544. Detects `isinstance(x, P)` where P is a Protocol without `@runtime_checkable`. |
| Abstract method not implemented in concrete subclass | COVERED | ABC001 | PEP 3119. Checks that all `@abstractmethod`s from bases are overridden. |
| `@override` with no base method | COVERED | OVERRIDE001 | PEP 698. Fires when `@override` method has no matching name in any base class. |
| `Final` variable reassignment | COVERED | FINAL001 | PEP 591. Detects re-assignment to a `Final`-annotated name. |
| Subclassing a `@final` class | COVERED | FINAL002 | PEP 591. Fires when a class inherits from a `@final`-decorated class. |
| Overriding a `@final` method | COVERED | FINAL003 | PEP 591. Fires when a subclass redefines a `@final` method. |
| Subscripting a non-generic class | COVERED | GENERIC001 | PEP 484. Detects `MyClass[X]` where `MyClass` doesn't inherit `Generic`/have type params. |
| TypeVar name mismatch | COVERED | TVAR001 | PEP 484. `T = TypeVar("U")` where string arg ≠ variable name. |
| NewType name mismatch | COVERED | NEWTYPE001 | PEP 484. `X = NewType("Y", ...)` where string arg ≠ variable name. |
| Typing form arity/context violations | COVERED | FORM001 | PEP 484+. e.g. `Optional[int, str]`, `Union` with <2 args, empty `Literal[]`. |
| `@overload` without implementation | COVERED | OVERLOAD001 | PEP 484. All signatures are `@overload`-decorated with no plain implementation body. |
| `@runtime_checkable` on non-Protocol class | COVERED | PROTO002 | PEP 544. `@runtime_checkable` applied to a class that doesn't extend `Protocol`. |
| `@override` on module-level function | COVERED | DECO001 | PEP 698. `@override` is only valid inside a class body. |
| `ClassVar` in function scope | COVERED | CLASSVAR001 | PEP 526. `ClassVar` annotation appearing inside a function, not a class. |
| Covariant/contravariant TypeVar in wrong position | COVERED | VARIANCE001 | PEP 484. e.g. covariant TypeVar used in method parameter (contravariant position). |
| `NoReturn` function that returns | COVERED | NORETURN001 | PEP 484. Function annotated `-> NoReturn` but body contains `return <value>`. |
| Direct Protocol instantiation | COVERED | PROTO003 | PEP 544. `Protocol()` or `MyProtocol()` called directly. |
| TypedDict inherits non-TypedDict class | COVERED | TDICT001 | PEP 589. TypedDict base list includes a regular class. |
| TypedDict field type conflict in multiple inheritance | COVERED | TDICT002 | PEP 589. Two TypedDict bases define the same key with different types. |
| Literal type mismatch in annotated assignment | COVERED | ASSIGN001 | PEP 484. `x: int = "hello"` — literal value incompatible with annotation. |
| Single `@overload` (no peer) | COVERED | OVERLOAD002 | PEP 484. Only one `@overload` signature; at least two are required. |
| Non-None return annotation but body returns None | COVERED | RETURN001 | PEP 484. `-> int` but function body is `pass`/`...`/`return None`. |

---

## Section 2: Generated Example Categories — AST-Detectable Gaps (Now Resolved)

| Category | Status | Rule ID | Generated Example Files | Notes |
|---|---|---|---|---|
| Invariant TypeVar in Protocol contravariant position | **COVERED** | VARIANCE002 | `asyncio-generic-protocol-callback.py` | PEP 544. Invariant TypeVar used only in param positions in a Protocol. |
| Generic type parameter count mismatch | **COVERED** | GENERIC002 | `complex-generic-bounds-typevar-nesting.py` | PEP 484. Wrong number of type args for locally-defined generic class. |
| NewType with non-class base type | **COVERED** | NEWTYPE002 | `newtype-list-covariance.py` | PEP 484. NewType base is a subscript/expression, not a simple class name. |
| Overload return type inconsistency (basic) | **COVERED** | OVERLOAD003 | `overload-decorator-return-type-divergence.py` | PEP 484. All overloads return same type but impl returns different type. |
| ParamSpec.args/kwargs misuse | **COVERED** | PARAMSPEC001 | *(structural check)* | PEP 612. P.args/P.kwargs used on wrong parameter kind. |
| Final attribute + property override | **COVERED** | FINAL004 | `final-attribute-override-property.py`, `final-override-property.py` | PEP 591. Property in subclass overrides Final attribute in base. |
| TypedDict literal dict construction type mismatch | **AGENT-ONLY** | — | `dictionary-comprehension-typeddict-literal-divergence.py` | Requires resolving which TypedDict variant a dict literal matches. |
| `@final` ClassVar accessed via subclass | **AGENT-ONLY** | — | `final-class-var-subclass-access.py` | Accessing (not reassigning) Final ClassVar through subclass is valid Python; design difference. |
| TypeGuard/TypeIs return type constraint | **AGENT-ONLY** | — | `typeguard-generic-narrowing.py` | Requires type inference to determine subtype relationship. |

---

## Section 3: Generated Example Categories — Agent-Only

These require type inference, control-flow analysis, generic specialization, or runtime semantics
that pure AST analysis cannot resolve.

| Category | Status | Rule ID | Generated Example Files | Notes |
|---|---|---|---|---|
| ParamSpec propagation through decorators | AGENT-ONLY | — | `paramspec-dummy-var-return-decorator.py`, `paramspec-classmethod-decorator.py`, `paramspec-classmethod-decorator-signature.py`, `paramspec-classmethod-staticmethod.py`, `param-spec-decorator-classmethod-order.py`, `paramspec-decorator-classmethod.py`, `paramspec-async-staticmethod-decorator.py`, `paramspec-decorator-with-classmethod-and-overload.py` | Requires resolving ParamSpec bindings across decorator chains. |
| ParamSpec + Concatenate divergence | AGENT-ONLY | — | `paramspec-concatenate-divergence.py` | Concatenate type arithmetic requires inference engine. |
| ParamSpec + partial/asyncio callbacks | AGENT-ONLY | — | `asyncio-paramspec-partial-callback.py` | `functools.partial` + ParamSpec interaction; needs call-graph analysis. |
| ParamSpec union return types | AGENT-ONLY | — | `paramspec-union-return-type.py`, `nested-paramspec-callable-return.py` | Callable return type resolution through ParamSpec. |
| asyncio callback type violations | AGENT-ONLY | — | `asyncio-generic-protocol-callback.py` | `add_done_callback` signature mismatch; requires library stub knowledge. |
| Cyclic TypeVar with forward references | AGENT-ONLY | — | `self-cyclic-typevar-abstract.py` | Forward-ref TypeVar bounds creating cycles; requires type resolution. |
| Self type in generic abstract methods | AGENT-ONLY | — | `self-in-generic-abstract-methods.py`, `self-in-generic-abstract-method.py`, `self-in-generics-abstract.py`, `self-in-generics-abstract-method.py`, `self-generic-abstract-inference.py`, `self-in-abstract-generic-class-var.py`, `self-in-protocol-default-implementation.py`, `self-generic-dummy-var-abstract-method.py` | Self type narrowing in generic class hierarchies. |
| Self type in generic match/factory/mutation | AGENT-ONLY | — | `self-generic-match-type.py`, `self-generic-narrowing-with-factory.py`, `self-mutation-divergence-refined.py`, `self-constructor-divergence-refined.py`, `type-self-init-divergence-refined.py`, `match-generic-self.py`, `generic-closure-self.py` | Self type resolution in complex patterns (match, closures). |
| NewType + TypeGuard interaction | AGENT-ONLY | — | `newtype-typeguard-divergence-refined.py`, `newtype-typeguard-unsound-divergence.py`, `newtype-typeguard-unreachable-refined.py` | TypeGuard narrowing across NewType boundaries. |
| NewType in generic containers + variance | AGENT-ONLY | — | `newtype-generic-variance-refined.py`, `newtype-in-generic-class-with-covariance.py`, `newtype-generic-container-typeguard-union.py`, `newtype-tuple-list-coercion-refined.py`, `newtype-protocol-divergence-refined.py`, `newtype-base-type-attribute-access.py`, `newtype-liskov-declaration-divergence.py`, `newtype-dummy-var-comprehension.py`, `newtype-nested-multi-line-ignore.py` | Variance correctness of NewType in generic containers. |
| Overload + classmethod + ParamSpec | AGENT-ONLY | — | `overload-classmethod-paramspec.py` | Three-way interaction: overload resolution with classmethod self-type and ParamSpec. |
| Overload + factory + TypeGuard | AGENT-ONLY | — | `overload-factory-typeguard-callable.py` | Overload selection based on TypeGuard return type discrimination. |
| Overload + decorator + TypeAliasType | AGENT-ONLY | — | `overloaded-decorator-generic-typealiastype-recursive-refined.py`, `overload-decorator-any-refined.py` | Recursive type alias + overload resolution. |
| Overload literal discrimination | AGENT-ONLY | — | `overloads-literal-discrimination.py`, `overload-literal-discrimination.py`, `overload-literal-discrimination-union-fallback.py`, `overload-literal-resolution.py` | Literal type dispatch across overload signatures. |
| TypedDict ReadOnly field mutation | AGENT-ONLY | — | `typeddict-readonly-mutation-refined.py`, `typeddict-readonly-generic-field.py` | PEP 705. Requires tracking ReadOnly field identity through assignments. |
| TypedDict Required/NotRequired inheritance conflicts | AGENT-ONLY | — | `typed-dict-inheritance-notrequired-required-clash-refined.py`, `typeddict-inheritance-total-divergence.py`, `typeddict-required-notrequired-total-false.py`, `typeddict-total-mixed-required-notrequired.py`, `typed-dict-total-sticky-required.py`, `typed-dict-mixed-total-inheritance.py`, `typeddict-total-multi-line-instantiation-ignore.py` | Requires resolving `total=True/False` across inheritance chains and Required/NotRequired wrappers. |
| TypedDict + TypeGuard access | AGENT-ONLY | — | `typeddict-typeguard-notrequired-access-divergence.py`, `typeguard-typeddict-soundness.py` | TypeGuard narrowing on TypedDict fields; soundness concerns. |
| TypedDict + kwargs from generic dict | AGENT-ONLY | — | `typeddict-kwargs-from-generic-dict-refined.py`, `typeddict-total-union-field-narrowing.py` | TypedDict used as **kwargs with generic dict interactions. |
| TypeGuard + generic protocol union narrowing | AGENT-ONLY | — | `typeguard-generic-protocol-union-narrowing.py`, `typeguard-tvar-refinement.py`, `typeguard-typevar-bound-divergence.py`, `typeguard-self-protocol-refined.py`, `typeguard-list-narrowing-refined.py`, `typeguard-generic-dict-narrowing.py` | TypeGuard narrowing across generic protocol/union/TypeVar bounds. |
| TypeGuard + generic list + NewType | AGENT-ONLY | — | `typeguard-generic-list-newtype.py` | TypeGuard narrowing list element types to NewType. |
| TypeGuard + match + generic tuple | AGENT-ONLY | — | `match-typeguard-generic-tuple.py`, `match-generic-union-typeguard.py` | match statement exhaustiveness with TypeGuard and generic tuples. |
| ClassVar + Protocol + Self interaction | AGENT-ONLY | — | `classvar-protocol-self.py` | ClassVar in Protocol with Self return type; requires protocol satisfaction analysis. |
| ClassVar + Enum + getattr divergence | AGENT-ONLY | — | `getattr-classvar-enum-divergence.py` | Dynamic attribute access on Enum ClassVars. |
| TypeIs in decorators/descriptors/protocols | AGENT-ONLY | — | `typeis-decorated-method-refined.py`, `typeis-descriptor.py`, `typeis-protocol-method.py`, `typeis-variance-divergence-refined.py` | PEP 742. TypeIs semantics in complex contexts (decorator wrapping, descriptor protocol, variance). |
| TypeAliasType complex interactions | AGENT-ONLY | — | `typealias-forward-reference-evaluation.py`, `typealias-protocol-generic.py`, `typealiastype-complex-nested-generics.py`, `typealiastype-method-binding-refined.py`, `typealiastype-newtype-container.py`, `type-alias-literal-match-exhaustiveness.py`, `recursive-typealiastype-generic-class-union.py`, `pep-695-alias-union-generic-methods.py` | PEP 695/613. Type alias resolution with generics, forward refs, recursion. |
| Callable + Union + ABC/Protocol | AGENT-ONLY | — | `callable-union-abc-vs-typing.py`, `callable-union-generic-protocol.py` | Callable type compatibility across union members and protocols. |
| Bounded TypeVar with complex bounds | AGENT-ONLY | — | `typevar-complex-bounds-inference.py`, `double-bound-typevar-generics.py`, `double-bound-typevar-resolution.py`, `bounded-typevar-nested-protocol.py`, `generic-typevar-bound-with-protocol-and-self.py`, `T-variance-divergence.py`, `tuple-explicit-typevar-divergence.py` | TypeVar bound resolution with nested generics and multiple constraints. |
| Protocol positional-vs-keyword arg divergence | AGENT-ONLY | — | `protocol-positional-vs-keyword-only.py`, `protocol-callable-keyword-only-vs-positional-or-keyword.py`, `protocol-call-keyword-only-vs-positional.py`, `protocol-call-positional-keyword.py`, `keyword-vs-positional-protocol.py`, `kwargs-splat-protocol.py`, `kwargs-splat-union-custom-mapping.py` | Protocol structural subtyping with param kind mismatches. |
| Protocol default arg absence/mismatch | AGENT-ONLY | — | `protocol-default-args.py`, `protocol-default-arg-absence.py`, `protocol-default-arg-compatibility.py`, `protocol-default-args-mismatch.py`, `protocol-default-call-mismatch.py`, `protocol-default-value-divergence.py`, `protocol-default-mixed-dataclass-transform.py` | Whether implementations must match Protocol method default values. |
| Protocol + match + generic type | AGENT-ONLY | — | `match-protocol-generic-type.py` | match statement exhaustiveness with generic Protocol types. |
| Decorator + super() in generic classes | AGENT-ONLY | — | `super-in-generic-classes.py`, `decorator-generics-divergence.py`, `decorator-super-generic-args.py`, `decorator-super-modified-signature.py` | super() type inference inside decorated generic methods. |
| Dataclass transform interactions | AGENT-ONLY | — | `dataclass-kw-only-post-init-generic-base.py`, `dataclass-transform-classmethod-super.py`, `dataclass-transform-param-spec-return.py`, `dataclass-transform-protocol-default-methods.py`, `pydantic-dataclass-typeddict-property.py` | PEP 681. dataclass_transform with generic bases, protocol defaults, pydantic. |
| Generic closure + ParamSpec | AGENT-ONLY | — | `generic-closure-paramspec.py` | ParamSpec capture inside closures of generic methods. |
| Inherited unsound helper methods | AGENT-ONLY | — | `inherited-unsound-helper-refined.py` | Unsound type narrowing through inherited helper methods. |
| isinstance + Protocol structural check divergence | AGENT-ONLY | — | `isinstance-protocol-divergence.py` | Divergence between isinstance and structural subtyping for protocols. |
| Mixed tuple unpacking + NewType | AGENT-ONLY | — | `mixed-tuple-unpacking-newtype.py` | Tuple unpacking with NewType element types. |
| Ternary + TypeGuard/literal inference | AGENT-ONLY | — | `ternary-typeguard-lambda-narrowing.py`, `ternary-typeguard-generic-lambda.py`, `ternary-literal-type-inference.py`, `ternary-union-attribute-method-call.py` | Conditional expression type narrowing with TypeGuard/lambdas. |
| Literal string variable assignment divergence | AGENT-ONLY | — | `literal-str-variable-assignment-divergence.py` | Literal type widening on assignment; checker divergence. |
| Cast + generic protocol method signature | AGENT-ONLY | — | `cast-generic-protocol-method-signature-change.py` | `cast()` applied to generic protocol method results. |
| TypeVarTuple unpacking precision | AGENT-ONLY | — | `typevartuple-unpacking-precision-refined.py` | PEP 646. Unpacking TypeVarTuple in function signatures and generics. |

---

## Summary

| Status | Count |
|---|---|
| COVERED (rules in source_analysis.py) | 30 |
| AST-DETECTABLE (missing rules) | 0 |
| AGENT-ONLY (beyond AST) | 36 |
| **Total generated example categories** | **~130 unique source files across 16 batches** |

The 30 covered rules detect foundational PEP typing violations from AST structure alone.
All 8 original AST-detectable gaps have been resolved: 6 were implemented as new rules
(VARIANCE002, GENERIC002, NEWTYPE002, OVERLOAD003, PARAMSPEC001, FINAL004) and 3 were
reclassified as AGENT-ONLY after closer inspection showed they require type inference or
represent design differences rather than PEP violations. The 36 agent-only categories
represent the long tail of type-checker divergences that fundamentally require type
inference, generic specialization, or control-flow analysis.
