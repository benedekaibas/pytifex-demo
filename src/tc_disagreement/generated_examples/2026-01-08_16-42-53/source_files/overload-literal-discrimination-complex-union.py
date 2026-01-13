# id: overload-literal-discrimination-complex-union
# EXPECTED:
#   mypy: `handle_request("get")` -> `Response`
#   pyright: `handle_request("get")` -> `Response`
#   pyre: `handle_request("get")` -> `Union[Response, ErrorResponse]`
#   zuban: `handle_request("get")` -> `Union[Response, ErrorResponse]` (likely similar to Pyre)
# REASON: Type checkers diverge on the precision of overload resolution, especially when
#         dealing with `Literal` types that discriminate between a specific return type
#         and a more general, catch-all overload that returns a `Union`.
#         Mypy and Pyright are often more aggressive and precise in narrowing the return
#         type based on `Literal` matches to the most specific overload.
#         Pyre (and potentially Zuban) can sometimes be more conservative, inferring a
#         wider `Union` type for the return, even when a `Literal` argument perfectly
#         matches a specific overload, if there's a more general overload with a broader return type.

from typing import overload, Literal, Union

class Response:
    def __init__(self, status: int, body: str) -> None:
        self.status = status
        self.body = body

class ErrorResponse(Response):
    def __init__(self, error_code: int, message: str) -> None:
        super().__init__(error_code, message)
        self.error_code = error_code

@overload
def handle_request(method: Literal["get"]) -> Response: ...
@overload
def handle_request(method: Literal["post"]) -> Response: ...
@overload
def handle_request(method: Literal["delete"]) -> Response: ...
@overload
def handle_request(method: str) -> Union[Response, ErrorResponse]: ... # Catch-all

def handle_request(method: str) -> Union[Response, ErrorResponse]:
    if method in ["get", "post", "delete"]:
        return Response(200, f"Handled {method} request")
    else:
        return ErrorResponse(400, f"Unsupported method: {method}")

if __name__ == "__main__":
    result_get = handle_request("get")
    reveal_type(result_get) # Expected: Response (Mypy, Pyright), Union[Response, ErrorResponse] (Pyre)

    result_put = handle_request("put")
    reveal_type(result_put) # Expected: ErrorResponse (all should agree, as it hits the catch-all)
    # mypy: Revealed type is "main.Response"
    # pyright: Type of "result_get" is "Response"
    # pyre: Revealed type: `typing.Union[main.ErrorResponse, main.Response]`