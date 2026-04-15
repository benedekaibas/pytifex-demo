from typing import Literal, TypeVar, Union, reveal_type

AllowedKeys = Literal['GET', 'POST', 'PUT']

def process_request_method[T_Key: AllowedKeys](method: T_Key) -> Union[T_Key, Literal['FALLBACK']]:
    """
    A generic function that processes a request method.
    It returns the method itself if it's 'GET' or 'POST', otherwise it returns a 'FALLBACK' string.
    This pattern tests how type checkers handle return type narrowing based on control flow
    when the declared return type is a Union involving the TypeVar.
    """
    print(f"Processing method: {method}")
    if method == 'GET':
        # If T_Key is Literal['GET'], this branch is always taken.
        # The return value is `method`, which is `T_Key`.
        return method
    if method == 'POST':
        # If T_Key is Literal['POST'], this branch is always taken.
        # The return value is `method`, which is `T_Key`.
        return method
    # For any other T_Key (e.g., Literal['PUT']), this branch is taken.
    # The return value is Literal['FALLBACK'].
    return 'FALLBACK'

if __name__ == "__main__":
    my_method: Literal['GET'] = 'GET'
    result_method = process_request_method(my_method)
    reveal_type(result_method) # Divergence point:
                               # Some checkers will infer Literal['GET'] due to control flow analysis.
                               # Others might conservatively infer Union[Literal['GET'], Literal['FALLBACK']]
                               # because that's the declared return type.

    # Another valid method, falling into the 'FALLBACK' case
    other_method: Literal['PUT'] = 'PUT'
    result_other = process_request_method(other_method)
    reveal_type(result_other) # Expecting Literal['FALLBACK'] as the 'PUT' case explicitly returns it.
                              # Less likely to diverge here.

    # Invalid method - this should be a type error if uncommented.
    # process_request_method("DELETE")