"""
Houdini 456.py startup script for NOX File Manager
Place this in Houdini's scripts/python directory
"""

import hou
import os
import sys

def initialize_nox():
    """Initialize NOX File Manager in Houdini"""
    try:
        # Add NOX to Python path
        nox_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        if nox_path not in sys.path:
            sys.path.insert(0, nox_path)
        
        # Import the Houdini integration
        import integrations.houdini.pythonrc
        
        print("NOX File Manager initialized for Houdini")
        
    except Exception as e:
        print(f"Failed to initialize NOX File Manager: {e}")

# Initialize NOX when Houdini starts
initialize_nox()