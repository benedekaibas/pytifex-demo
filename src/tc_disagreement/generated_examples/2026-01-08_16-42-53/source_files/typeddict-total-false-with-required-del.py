# id: typeddict-total-false-with-required-del
# EXPECTED:
#   mypy: Error (cannot delete Required key)
#   pyright: No error (allows deleting Required key in total=False TypedDict)
#   pyre: Error (cannot delete Required key)
#   zuban: Error (likely similar to Mypy/Pyre)
# REASON: When a `TypedDict` is declared with `total=False` but contains explicitly `Required` keys,
#         type checkers diverge on whether these `Required` keys can be deleted.
#         Mypy and Pyre strictly interpret `Required` as meaning the key *must* always be present
#         in a valid instance, disallowing deletion. Pyright is more lenient here, allowing deletion
#         in `total=False` TypedDicts, as `total=False` implies that keys can be absent, even `Required` ones
#         in specific contexts (though typically `Required` overrides `total=False` for existence check).
#         This divergence highlights different interpretations of `Required`'s semantic weight
#         when `total=False` is also present.

from typing import TypedDict
from typing_extensions import Required, NotRequired

class Task(TypedDict, total=False):
    id: Required[str]
    title: Required[str]
    description: NotRequired[str]
    assignee_id: str

def delete_task_field(task_data: Task) -> None:
    if 'id' in task_data:
        del task_data['id'] # Mypy/Pyre might error, Pyright might allow.

if __name__ == "__main__":
    my_task: Task = {'id': 'T123', 'title': 'Implement Feature X'}
    delete_task_field(my_task)
    # mypy: Cannot delete key "id" from TypedDict "Task" [typeddict-item]
    # pyright: No error (as of 1.1.346)
    # pyre: Cannot delete required key `id` from `Task` [1]