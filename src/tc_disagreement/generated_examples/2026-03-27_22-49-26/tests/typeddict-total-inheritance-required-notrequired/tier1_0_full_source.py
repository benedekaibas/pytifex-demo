from typing import TypedDict, Required, NotRequired, TYPE_CHECKING, Optional

class BaseResource(TypedDict): # total=True by default
    id: int
    name: str

class MutableResource(TypedDict, total=False):
    description: str
    status: NotRequired[str] # explicitly NotRequired

class ComplexResource(BaseResource, MutableResource, total=True):
    # 'metadata' is required here because total=True
    metadata: dict[str, str]
    # 'version' is explicitly NotRequired in ComplexResource
    version: NotRequired[Optional[str]]
    
    # What happens to 'description' and 'status' from MutableResource?
    # Are they considered Required by ComplexResource's total=True?
    # This is a key point of disagreement among type checkers.

def check_resource(resource: ComplexResource):
    if TYPE_CHECKING:
        reveal_type(resource["id"]) # Expected int
        reveal_type(resource["name"]) # Expected str
        reveal_type(resource["metadata"]) # Expected dict[str, str]

        # These are highly likely to cause disagreement:
        # Some checkers might infer 'description' is Required[str], others Optional[str] or str.
        reveal_type(resource["description"]) # Expected str (if Required) or potentially error.
        reveal_type(resource.get("description")) # Expected str | None (if NotRequired)
        
        # 'status' was NotRequired in MutableResource. Does total=True in ComplexResource override this?
        reveal_type(resource["status"]) # Expected str (if Required) or potentially error.
        reveal_type(resource.get("status")) # Expected str | None
        
        # 'version' is explicitly NotRequired in ComplexResource.
        reveal_type(resource.get("version")) # Expected Optional[str]

    print(f"ID: {resource['id']}, Name: {resource['name']}, Metadata: {resource['metadata']}")
    if "description" in resource:
        print(f"Description: {resource['description']}")
    if "status" in resource:
        print(f"Status: {resource['status']}")
    if "version" in resource:
        print(f"Version: {resource['version']}")

if __name__ == "__main__":
    # Test case 1: Missing 'description' and 'status'
    # Mypy will typically flag this as an error due to ComplexResource's total=True.
    resource1: ComplexResource = {
        "id": 1,
        "name": "Primary",
        "metadata": {"source": "manual"},
        "version": "1.0"
    }
    print("--- Resource 1 (missing description, status) ---")
    check_resource(resource1)

    # Test case 2: All fields present
    resource2: ComplexResource = {
        "id": 2,
        "name": "Secondary",
        "description": "Detailed info",
        "status": "active",
        "metadata": {"source": "auto"},
        "version": None # Optional field can be None
    }
    print("\n--- Resource 2 (full) ---")
    check_resource(resource2)

    # Test case 3: 'status' explicitly missing, 'description' present
    resource3: ComplexResource = {
        "id": 3,
        "name": "Partial",
        "description": "Only desc",
        "metadata": {"source": "user"},
    }
    print("\n--- Resource 3 (missing status) ---")
    check_resource(resource3)