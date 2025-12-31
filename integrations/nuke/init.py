"""
Nuke initialization script for NOX File Manager
Place this in Nuke's plugins directory or import from menu.py
"""

import nuke
import os
import sys

def initialize_nox():
    """Initialize NOX File Manager in Nuke"""
    try:
        # Add NOX to Python path
        nox_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        if nox_path not in sys.path:
            sys.path.insert(0, nox_path)
        
        # Import the menu setup
        import integrations.nuke.menu
        
        print("NOX File Manager initialized for Nuke")
        
    except Exception as e:
        print(f"Failed to initialize NOX File Manager: {e}")

# Auto-initialize when imported
initialize_nox()