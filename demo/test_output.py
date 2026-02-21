"""
Unit tests for demo output formatting functions.

Tests edge cases and data format handling to ensure robustness.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from demo.output import normalize_priority


def test_normalize_priority_string_format():
    """Test priority normalization from string format (API response)."""
    result = normalize_priority("critical")
    assert result == {
        "level": "critical",
        "score": 0,
        "reason": ""
    }, f"Expected normalized dict, got {result}"
    print("✓ String format test passed")


def test_normalize_priority_dict_format():
    """Test priority normalization from complete dict format."""
    input_dict = {
        "level": "high",
        "score": 8.5,
        "reason": "Multiple pest detections"
    }
    result = normalize_priority(input_dict)
    assert result == input_dict, f"Expected unchanged dict, got {result}"
    print("✓ Complete dict format test passed")


def test_normalize_priority_partial_dict():
    """Test priority normalization from partial dict (missing keys)."""
    input_dict = {"level": "medium"}
    result = normalize_priority(input_dict)
    assert result == {
        "level": "medium",
        "score": 0,
        "reason": ""
    }, f"Expected filled defaults, got {result}"
    print("✓ Partial dict format test passed")


def test_normalize_priority_none():
    """Test priority normalization from None value."""
    result = normalize_priority(None)
    assert result == {
        "level": "unknown",
        "score": 0,
        "reason": ""
    }, f"Expected unknown defaults, got {result}"
    print("✓ None value test passed")


def test_normalize_priority_empty_dict():
    """Test priority normalization from empty dict."""
    result = normalize_priority({})
    assert result == {
        "level": "unknown",
        "score": 0,
        "reason": ""
    }, f"Expected unknown defaults, got {result}"
    print("✓ Empty dict test passed")


def test_normalize_priority_uppercase_string():
    """Test priority normalization converts uppercase to lowercase."""
    result = normalize_priority("CRITICAL")
    assert result["level"] == "critical", f"Expected lowercase, got {result['level']}"
    print("✓ Uppercase string test passed")


def test_normalize_priority_invalid_type():
    """Test priority normalization handles invalid types gracefully."""
    result = normalize_priority(123)  # Number instead of string/dict
    assert result == {
        "level": "unknown",
        "score": 0,
        "reason": ""
    }, f"Expected unknown defaults for invalid type, got {result}"
    print("✓ Invalid type test passed")


def run_all_tests():
    """Run all test cases."""
    print("\n🧪 Running output formatter tests...\n")
    
    tests = [
        test_normalize_priority_string_format,
        test_normalize_priority_dict_format,
        test_normalize_priority_partial_dict,
        test_normalize_priority_none,
        test_normalize_priority_empty_dict,
        test_normalize_priority_uppercase_string,
        test_normalize_priority_invalid_type,
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {failed}/{len(tests)} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
