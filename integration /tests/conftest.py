"""Pytest path setup for integration test imports."""

import os
import sys

TESTS_DIR = os.path.dirname(__file__)
INTEGRATION_DIR = os.path.abspath(os.path.join(TESTS_DIR, ".."))
CODE_DIR = os.path.join(INTEGRATION_DIR, "code")

for path in (INTEGRATION_DIR, CODE_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)
