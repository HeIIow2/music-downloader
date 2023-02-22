import os
import sys

# Add the parent directory of the current file (i.e., the "tests" directory) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
