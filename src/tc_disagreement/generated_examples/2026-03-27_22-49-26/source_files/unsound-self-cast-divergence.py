from typing import Self, Tuple, Union, Generic, TypeVar, TYPE_CHECKING, cast
import random

T = TypeVar('T')

class Node(Generic[T]):
    def __init__(self, value: T, next_node: 'Node[T] | None' = None):
        self.value = value
        # _next is typed as Node[T], meaning it can link to any Node of type T,
        # including instances of subclasses or instances of the base class.
        self._next: Node[T] | None = next_node

    def get_next_or_default(self, default_val: T) -> Self:
        # ORIGINAL ISSUE: This method is declared to return 'Self'.
        # If 'self' is an instance of a subclass (e.g., SpecialNode[T]), then 'Self' refers to that subclass type (SpecialNode[T]).
        # However, '_next' is explicitly typed as 'Node[T] | None'. If '_next' holds an instance of the base Node[T]
        # and not an instance of the specific subclass (e.g., SpecialNode[T]), then returning '_next' here
        # represents a return of a supertype (Node[T]) where a subtype (SpecialNode[T]) is expected.
        # This was the direct "Incompatible return value type" error.

        # MODIFICATION: Introduce an unsound `cast(Self, ...)` to suppress the original error.
        # This explicitly tells the type checker to treat `self._next` (which is `Node[T]`)
        # as `Self` (which could be `SpecialNode[T]`).
        # This cast is unsound when `self` is a `SpecialNode` and `self._next` is a plain `Node`.
        # Type checkers might diverge on:
        # 1. Whether they issue a warning/error about the unsound cast itself.
        # 2. How they track the type of the returned value (`current_node` in the loop)
        #    given this unsound assertion, especially across loop iterations.
        # 3. Whether they detect the runtime `AttributeError` if `current_node.metadata` is accessed
        #    on what is actually a `Node` object but was typed as `SpecialNode` due to the cast.
        if self._next is not None:
            return cast(Self, self._next)
        else:
            return type(self)(default_val)

    def get_value(self) -> T:
        return self.value

# Introduce a generic subclass to highlight the Self interaction
class SpecialNode(Node[T]):
    def __init__(self, value: T, next_node: 'Node[T] | None' = None, metadata: str = "default"):
        super().__init__(value, next_node)
        self.metadata = metadata

    def get_metadata(self) -> str:
        return self.metadata

def process_nodes_in_loop(start_node: Node[int]):
    current_node: Node[int] = start_node
    processed_value: int = 0

    iteration = 0
    while True:
        iteration += 1
        processed_value, current_node = current_node.get_value(), current_node.get_next_or_default(0)
        
        if TYPE_CHECKING:
            # Type checkers might disagree on the precise type of 'current_node' here,
            # especially if the unsound cast caused a widening or incorrect type inference.
            # Some might correctly infer Node[int] if they "see through" the cast,
            # others might incorrectly infer SpecialNode[int] in some iterations.
            reveal_type(current_node)
            reveal_type(processed_value)

        print(f"Iteration {iteration}: Processed {processed_value}, Current node value: {current_node.get_value()}")
        
        # This block checks if 'current_node' is a SpecialNode, further testing type checker's
        # ability to track types across loop iterations and potential `Self` mismatches.
        if isinstance(current_node, SpecialNode):
            if TYPE_CHECKING:
                # If 'current_node' was incorrectly typed as SpecialNode[int] due to the
                # unsound cast earlier, this access might *appear* valid to some checkers,
                # even if at runtime it could be a plain Node[int] leading to AttributeError.
                reveal_type(current_node)
                reveal_type(current_node.metadata)
            print(f"    (SpecialNode detected with metadata: {current_node.get_metadata()})")
        
        if processed_value == 0 or iteration > 5:
            break

if __name__ == "__main__":
    n3_plain = Node(30)
    
    # This chain is specifically designed to trigger the subtle type error in `get_next_or_default`:
    # 1. `n1_plain` (Node[int]) points to `n2_special` (SpecialNode[int]).
    # 2. `n2_special` (SpecialNode[int]) points to `n3_plain` (Node[int]).
    # When `n2_special.get_next_or_default(0)` is called:
    #   - `self` is `n2_special`, which is of type `SpecialNode[int]`.
    #   - Therefore, `Self` in this context resolves to `SpecialNode[int]`.
    #   - The method attempts to return `cast(Self, self._next)`.
    #   - `self._next` is `n3_plain` (of type `Node[int]`).
    #   - So it's `cast(SpecialNode[int], Node[int])`. This is an unsound cast at iteration 2.
    # Type checkers might diverge on whether they flag this specific unsound cast,
    # or how they handle the type of `current_node` in subsequent loop iterations if they don't.
    n2_special = SpecialNode(20, n3_plain, metadata="Intermediate Special") 
    n1_plain = Node(10, n2_special)

    print("\n--- Processing mixed chain (Node -> SpecialNode -> Node) ---")
    process_nodes_in_loop(n1_plain)

    print("\n--- Processing chain of only SpecialNodes (this chain should not trigger the error) ---")
    n_s4 = SpecialNode(400)
    n_s3 = SpecialNode(300, n_s4, metadata="S3")
    n_s2 = SpecialNode(200, n_s3, metadata="S2")
    n_s1 = SpecialNode(100, n_s2, metadata="S1")
    process_nodes_in_loop(n_s1)