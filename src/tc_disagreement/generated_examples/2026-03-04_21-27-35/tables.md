# TABLE 1: Code Metrics

| File | # of lines of code (ncss) | # of functions | # of type related imports USED | # of type (declared - untyped) / total lines | # of interactions between functions |
| --- | --- | --- | --- | --- | --- |
| asyncio-paramspec-partial-callback.py | 32 | 5 | 5 | 0.0625 | 1 |
| newtype-typeguard-divergence-refined.py | 25 | 1 | 4 | -0.0800 | 0 |
| paramspec-concatenate-divergence.py | 51 | 7 | 6 | 0.0980 | 2 |
| dictionary-comprehension-typeddict-literal-divergence.py | 45 | 0 | 5 | 0.1333 | 0 |
| asyncio-generic-protocol-callback.py | 35 | 8 | 6 | 0.2286 | 3 |
| overload-factory-typeguard-callable.py | 57 | 8 | 7 | 0.2807 | 0 |
| overload-classmethod-paramspec.py | 56 | 9 | 6 | 0.2500 | 0 |
| self-cyclic-typevar-abstract.py | 49 | 11 | 5 | 0.2041 | 0 |


# TABLE 2: Type Related Runtime Error Caught (TRREC)

| File | Caused Runtime Error (Yes) | Caused Runtime Error (No) | Mypy | Pyrefly | Ty | Zuban |
| --- | --- | --- | --- | --- | --- | --- |
| asyncio-paramspec-partial-callback.py | ✓ |  |  |  |  | ✓ |
| newtype-typeguard-divergence-refined.py | ✓ |  |  |  | ✓ |  |
| paramspec-concatenate-divergence.py | ✓ |  |  | ✓ | ✓ | ✓ |
| dictionary-comprehension-typeddict-literal-divergence.py | ✓ |  |  |  | ✓ | ✓ |
| asyncio-generic-protocol-callback.py | ✓ |  | ✓ |  |  | ✓ |
| overload-factory-typeguard-callable.py | ✓ |  |  |  | ✓ |  |
| overload-classmethod-paramspec.py | ✓ |  | ✓ | ✓ |  |  |
| self-cyclic-typevar-abstract.py | ✓ |  | ✓ | ✓ |  |  |


**Mypy**: 3 / 8
**Pyrefly**: 3 / 8
**Ty**: 4 / 8
**Zuban**: 4 / 8


# TABLE 3: Full Covered CFG - Sieving Based Testing

| File | Yes | No | Mypy | Pyrefly | Ty | Zuban |
| --- | --- | --- | --- | --- | --- | --- |
| asyncio-paramspec-partial-callback.py |  | ✓ |  |  |  |  |
| newtype-typeguard-divergence-refined.py |  | ✓ |  |  |  |  |
| paramspec-concatenate-divergence.py |  | ✓ |  |  |  |  |
| dictionary-comprehension-typeddict-literal-divergence.py |  | ✓ |  |  |  |  |
| asyncio-generic-protocol-callback.py |  | ✓ |  |  |  |  |
| overload-factory-typeguard-callable.py |  | ✓ |  |  |  |  |
| overload-classmethod-paramspec.py |  | ✓ |  |  |  |  |
| self-cyclic-typevar-abstract.py |  | ✓ |  |  |  |  |


**Mypy**: 0 / 8
**Pyrefly**: 0 / 8
**Ty**: 0 / 8
**Zuban**: 0 / 8