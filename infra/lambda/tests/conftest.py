import os
import sys

# Ensure the Lambda source directory is importable as a top-level module
TESTS_DIR = os.path.dirname(__file__)
LAMBDA_SRC_DIR = os.path.abspath(os.path.join(TESTS_DIR, os.pardir))
if LAMBDA_SRC_DIR not in sys.path:
    sys.path.insert(0, LAMBDA_SRC_DIR)


