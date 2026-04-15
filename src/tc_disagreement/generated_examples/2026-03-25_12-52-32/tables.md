# TABLE 1: Code Metrics

| File | # of lines of code (ncss) | # of functions | # of type related imports USED | # of type (declared - untyped) / total lines | # of interactions between functions |
| --- | --- | --- | --- | --- | --- |
| literal_narrowing.py | 16 | 4 | 1 | 0 | 0 |
| walrus_comprehension.py | 5 | 0 | 0 | 0 | 0 |
| typeddict_single_field.py | 5 | 1 | 1 | 0 | 0 |


# TABLE 2: Type Related Runtime Error Caught (TRREC)

| File | Caused Runtime Error (Yes) | Caused Runtime Error (No) | Mypy | Pyrefly | Ty | Zuban |
| --- | --- | --- | --- | --- | --- | --- |
| literal_narrowing.py | ✓ |  | ✓ |  | ✓ |  |
| walrus_comprehension.py | ✓ |  |  | ✓ | ✓ |  |
| typeddict_single_field.py | ✓ |  | ✓ | ✓ | ✓ | ✓ |


**Mypy**: 2 / 3
**Pyrefly**: 2 / 3
**Ty**: 3 / 3
**Zuban**: 1 / 3


# TABLE 3: Full Covered CFG - Sieving Based Testing

| File | Yes | No | Mypy | Pyrefly | Ty | Zuban |
| --- | --- | --- | --- | --- | --- | --- |
| literal_narrowing.py |  | ✓ |  |  |  |  |
| walrus_comprehension.py |  | ✓ |  |  |  |  |
| typeddict_single_field.py |  | ✓ |  |  |  |  |


**Mypy**: 0 / 3
**Pyrefly**: 0 / 3
**Ty**: 0 / 3
**Zuban**: 0 / 3