"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: mixed-tuple-unpacking-newtype.py
Patterns detected: 2
    - tuple_length (5 tests)
  - newtype (10 tests)
Test cases generated: 15
"""

# --- Original source ---

from typing import Tuple, List, NewType, Any

HeaderToken = NewType('HeaderToken', str)
PayloadSegment = NewType('PayloadSegment', bytes)
FooterSignature = NewType('FooterSignature', str)

def process_complex_packet(
    packet: Tuple[HeaderToken, PayloadSegment, *Tuple[PayloadSegment, ...], FooterSignature]
):
    # Unpack a complex tuple where the variable part can contain a NewType
    # and the *rest* part needs careful type inference.
    header, first_payload, *remaining_payloads_and_footer = packet

    # reveal_type(header) # Expected: HeaderToken
    # reveal_type(first_payload) # Expected: PayloadSegment
    # reveal_type(remaining_payloads_and_footer) # Expected: list[PayloadSegment | FooterSignature]

    print(f"Header: {header}")
    print(f"First Payload: {first_payload}")
    print(f"Remaining (payloads & footer): {remaining_payloads_and_footer}")

if __name__ == "__main__":
    packet1 = (
        HeaderToken("token123"),
        PayloadSegment(b"payload_a"),
        FooterSignature("sig456")
    )
    process_complex_packet(packet1)

    packet2 = (
        HeaderToken("token789"),
        PayloadSegment(b"payload_b"),
        PayloadSegment(b"payload_c"),
        PayloadSegment(b"payload_d"),
        FooterSignature("sig101")
    )
    process_complex_packet(packet2)

    # Some checkers might infer a simpler type for remaining_payloads_and_footer
    # like list[Any] or list[Union[bytes, str]] rather than the specific NewTypes.

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 12

# --- Test cases ---

def test_process_complex_packet_empty_tuple():
    """Call process_complex_packet with empty tuple for param 'packet'."""
    try:
        process_complex_packet(packet=())
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "empty_tuple"})


def test_process_complex_packet_single_element_tuple():
    """Call process_complex_packet with single-element tuple for param 'packet'."""
    try:
        process_complex_packet(packet=(1,))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "single_element_tuple"})


def test_process_complex_packet_none_in_tuple():
    """Call process_complex_packet with None element in tuple for param 'packet'."""
    try:
        process_complex_packet(packet=(None,))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "none_in_tuple"})


def test_process_complex_packet_wrong_types_in_tuple():
    """Call process_complex_packet with wrong types in tuple for param 'packet'."""
    try:
        process_complex_packet(packet=(123, 456, 789))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "wrong_types_in_tuple"})


def test_process_complex_packet_string_instead_of_tuple():
    """Call process_complex_packet with a string instead of tuple for param 'packet'."""
    try:
        process_complex_packet(packet="not a tuple")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "string_instead_of_tuple"})


def test_HeaderToken_from_string():
    """Create HeaderToken from a plain string."""
    try:
        val = HeaderToken("test_value")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 3, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_HeaderToken_from_int():
    """Create HeaderToken from an int (wrong base type)."""
    try:
        val = HeaderToken(42)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 3, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


def test_HeaderToken_from_none():
    """Create HeaderToken from None."""
    try:
        val = HeaderToken(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 3, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_none"})


def test_PayloadSegment_from_bytes():
    """Create PayloadSegment from bytes."""
    try:
        val = PayloadSegment(b"test_bytes")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_PayloadSegment_from_string():
    """Create PayloadSegment from a string (wrong base type for bytes)."""
    try:
        val = PayloadSegment("not_bytes")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


def test_FooterSignature_from_string():
    """Create FooterSignature from a plain string."""
    try:
        val = FooterSignature("test_value")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 5, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_FooterSignature_from_int():
    """Create FooterSignature from an int (wrong base type)."""
    try:
        val = FooterSignature(42)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 5, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


def test_FooterSignature_from_none():
    """Create FooterSignature from None."""
    try:
        val = FooterSignature(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 5, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_none"})


def test_process_complex_packet_wrong_newtype_packet_FooterSignature():
    """Call process_complex_packet passing FooterSignature where HeaderToken expected for param 'packet'."""
    try:
        process_complex_packet(packet=FooterSignature("wrong_newtype"))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "wrong_newtype"})


def test_process_complex_packet_wrong_newtype_packet_HeaderToken():
    """Call process_complex_packet passing HeaderToken where FooterSignature expected for param 'packet'."""
    try:
        process_complex_packet(packet=HeaderToken("wrong_newtype"))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "wrong_newtype"})


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
