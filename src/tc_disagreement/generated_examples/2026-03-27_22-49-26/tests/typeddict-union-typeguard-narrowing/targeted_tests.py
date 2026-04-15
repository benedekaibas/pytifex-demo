"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: typeddict-union-typeguard-narrowing.py
Patterns detected: 1
    - typeguard_narrowing (6 tests)
Test cases generated: 6
"""

# --- Original source ---

from typing import TypedDict, Union, TypeGuard, NotRequired, TYPE_CHECKING

class RequestBase(TypedDict):
    method: str

class GetRequest(RequestBase):
    query: str

class PostRequest(RequestBase, total=False):
    body: str
    headers: NotRequired[dict[str, str]]

# This TypeGuard checks for the presence of 'body', which is NotRequired in PostRequest.
# A PostRequest without 'body' should still be considered a PostRequest.
# Type checkers may disagree on the precise narrowed type of `req` inside the `if` block,
# especially regarding the 'body' field's Optionality.
def is_post_request_with_body(req: Union[GetRequest, PostRequest]) -> TypeGuard[PostRequest]:
    return "body" in req

def process_request(request: Union[GetRequest, PostRequest]):
    if is_post_request_with_body(request):
        if TYPE_CHECKING:
            # Expect PostRequest with 'body' definitely present (str), 
            # but 'headers' still NotRequired.
            # Some checkers might infer PostRequest and not properly narrow 'body' to str,
            # or treat 'body' as Optional, or even narrow PostRequest incorrectly.
            reveal_type(request) 
            reveal_type(request["body"]) # Expected 'str'
            reveal_type(request.get("headers")) # Expected 'dict[str, str] | None'
    else:
        if TYPE_CHECKING:
            # This branch should contain GetRequest, and PostRequest *without* 'body'.
            reveal_type(request) 
            # If request is PostRequest without 'body', accessing 'body' should be an error
            # but some checkers might infer it could be present.
            # reveal_type(request["body"]) # Should be error if PostRequest (no body) or GetRequest
        print(f"Not a post request with body: {request['method']}")


if __name__ == "__main__":
    get_req: GetRequest = {"method": "GET", "query": "q=test"}
    post_req_full: PostRequest = {"method": "POST", "body": "data", "headers": {"Content-Type": "text/plain"}}
    post_req_empty: PostRequest = {"method": "POST"} # Valid PostRequest without 'body'

    process_request(get_req)
    process_request(post_req_full)
    process_request(post_req_empty) # This is the crucial test case for the TypeGuard

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_is_post_request_with_body_returns_bool():
    """Verify is_post_request_with_body returns a boolean."""
    try:
        result = is_post_request_with_body([])
        if not isinstance(result, bool):
            BUGS.append({"line": 17, "type": "ReturnTypeMismatch", "error": f"TypeGuard is_post_request_with_body returned {type(result).__name__}, expected bool", "test": "typeguard_returns_bool"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 17, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_empty_list"})


def test_is_post_request_with_body_with_none():
    """Call is_post_request_with_body with None."""
    try:
        is_post_request_with_body(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 17, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_none"})


def test_is_post_request_with_body_with_ints():
    """Call is_post_request_with_body with list of ints."""
    try:
        result = is_post_request_with_body([1, 2, 3])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 17, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_ints"})


def test_is_post_request_with_body_with_strings():
    """Call is_post_request_with_body with list of strings."""
    try:
        result = is_post_request_with_body(["a", "b", "c"])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 17, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_strings"})


def test_is_post_request_with_body_with_mixed():
    """Call is_post_request_with_body with mixed type list."""
    try:
        result = is_post_request_with_body([1, "hello", True, 3.14])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 17, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_mixed"})


def test_is_post_request_with_body_with_bools():
    """Call is_post_request_with_body with list of booleans."""
    try:
        result = is_post_request_with_body([True, False, True])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 17, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_bools"})


# --- Runner ---
if __name__ == "__main__":
    import sys
    _test_fns = [(name, fn) for name, fn in list(globals().items()) if name.startswith("test_") and callable(fn)]
    print(f"Running {len(_test_fns)} targeted tests...")
    _passed = 0
    _failed = 0
    for _name, _fn in _test_fns:
        try:
            _fn()
            _passed += 1
        except Exception as _e:
            _failed += 1
    print(f"Passed: {_passed}, Failed: {_failed}, Bugs found: {len(BUGS)}")
    for _bug in BUGS:
        print(f"  BUG L{_bug['line']} [{_bug['type']}] {_bug['error']}")
