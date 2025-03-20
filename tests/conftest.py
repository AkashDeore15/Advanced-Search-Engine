"""
Pytest configuration file.
This file is automatically recognized by pytest and can modify the Python path.
"""
import os
import sys

# Get the absolute path of the project root directory (parent of tests)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add project root to Python path
sys.path.insert(0, project_root)
