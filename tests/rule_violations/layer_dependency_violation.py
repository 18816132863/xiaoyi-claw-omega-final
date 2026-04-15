#!/usr/bin/env python3
"""
Layer Dependency Violation Test Case

This file intentionally violates layer dependency rules for testing.
"""

# This import violates L4 -> L1 dependency rule
# L4 (execution) should not directly import from L1 (core)
from core import ARCHITECTURE  # VIOLATION - intentional for testing

def test_violation():
    """Test case that would trigger layer dependency violation"""
    pass
