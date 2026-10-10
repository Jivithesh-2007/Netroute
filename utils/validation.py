"""
Input validation utilities for NetRoute GUI.
"""
from typing import Tuple, List, Optional


def validate_router_id(router_id: str) -> Tuple[bool, str]:
    """Validate router ID string."""
    clean_id = router_id.strip()
    if not clean_id:
        return False, "Router ID cannot be empty."
    if len(clean_id) > 10:
        return False, "Router ID should be 10 characters or less."
    if not clean_id.isalnum():
        return False, "Router ID should be alphanumeric."
    return True, clean_id


def parse_integer_list(input_str: str) -> Tuple[bool, List[int], str]:
    """Parse comma-separated or space-separated list of integers."""
    if not input_str.strip():
        return False, [], "Input text is empty."
    
    parts = input_str.replace(',', ' ').split()
    nums = []
    for p in parts:
        try:
            val = int(p.strip())
            nums.append(val)
        except ValueError:
            return False, [], f"Invalid integer token '{p}'."

    if not nums:
        return False, [], "No valid integers found in input."
    if len(nums) > 100:
        return False, [], "Maximum supported array size for visualization is 100."
    return True, nums, "Valid array."


def parse_integer(input_str: str) -> Tuple[bool, Optional[int], str]:
    """Parse a single integer input."""
    try:
        val = int(input_str.strip())
        return True, val, "Valid integer."
    except ValueError:
        return False, None, "Please enter a valid integer."
