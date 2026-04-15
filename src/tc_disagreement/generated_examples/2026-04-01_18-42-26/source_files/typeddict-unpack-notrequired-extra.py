from typing import TypedDict, Unpack, NotRequired, Any

class RequestHeader(TypedDict):
    Authorization: str
    ContentType: NotRequired[str]

class HttpRequest(RequestHeader, extra_items=Any):
    method: str
    url: str

def make_request(**kwargs: Unpack[HttpRequest]) -> None:
    print("Making request:")
    for k, v in kwargs.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    # HttpRequest requires 'Authorization', 'method', 'url'.
    # 'ContentType' is NotRequired. Any other fields are allowed by extra_items.
    # The interaction of NotRequired, extra_items, and Unpack is the edge case.

    # This should be allowed.
    make_request(
        method="GET",
        url="/api/data",
        Authorization="Bearer token",
        UserAgent="MyClient/1.0",
        Accept="application/json"
    )

    # This should also be allowed, as ContentType is NotRequired.
    make_request(
        method="POST",
        url="/api/submit",
        Authorization="Bearer token",
        X_Custom_Header="value"
    )
    
    # This should error, missing 'Authorization'.
    print("\nAttempting call with missing required field (should error):")
    try:
        make_request(method="GET", url="/api/data")
    except TypeError as e:
        print(f"Caught expected runtime error: {e}")
    except Exception:
        print("Type checker should have caught this prior to runtime.")

    # This should error, missing 'method'.
    print("\nAttempting call with missing required field (should error):")
    try:
        make_request(url="/api/data", Authorization="Bearer token")
    except TypeError as e:
        print(f"Caught expected runtime error: {e}")
    except Exception:
        print("Type checker should have caught this prior to runtime.")