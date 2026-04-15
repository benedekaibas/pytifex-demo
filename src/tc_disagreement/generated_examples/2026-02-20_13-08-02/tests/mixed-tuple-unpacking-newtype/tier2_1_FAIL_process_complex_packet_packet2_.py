"""
Hypothesis Tier 2 — Generated Test

Call: process_complex_packet(packet2)
Kind: function
Line: 37
Status: FAIL

Bug: [ValueError] process_complex_packet(packet2) -> ValueError: not enough values to unpack (expected at least 2, got 0)
"""

# --- Original source (full context) ---

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


# --- Tier 2 test ---

def test_process_complex_packet():
    """Test that process_complex_packet() runs without type errors."""
    try:
        result = process_complex_packet(packet2)
        print(f"OK: {result}")
    except (TypeError, AttributeError, ValueError, KeyError) as e:
        print(f"BUG: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    test_process_complex_packet()
