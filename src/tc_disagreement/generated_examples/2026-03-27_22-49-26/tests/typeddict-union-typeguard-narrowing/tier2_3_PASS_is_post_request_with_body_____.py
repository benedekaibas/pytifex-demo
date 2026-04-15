"""
Hypothesis Tier 2 — Generated Property Test

Target: is_post_request_with_body(...)
Kind: function
Line: 17
Status: PASS
Max examples: 30

Strategies:
  req: Union -> one_of(build_td(), build_td())
"""

# --- Original source (full context) ---

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


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(req=...)
def test_is_post_request_with_body(req):
    """Property test: is_post_request_with_body() with generated inputs."""
    result = is_post_request_with_body(req)


if __name__ == "__main__":
    test_is_post_request_with_body()
