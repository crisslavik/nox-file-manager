"""
Maya userSetup.py - Automatically loads NOX File Manager on Maya startup
Place this in Maya's scripts directory
"""

import maya.cmds as cmds
import os
import sys

def initialize_nox():
    """Initialize NOX File Manager in Maya"""
    try:
        # Add NOX to Python path if not already there
        nox_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        if nox_path not in sys.path:
            sys.path.insert(0, nox_path)
        
        # Import and initialize
        import integrations.maya.nox_file_dialog_maya as nox_maya
        cmds.evalDeferred('import integrations.maya.nox_file_dialog_maya as nox_maya; nox_maya.initialize()')
        
        print("NOX File Manager initialized for Maya")
        
    except Exception as e:
        print(f"Failed to initialize NOX File Manager: {e}")

# Initialize NOX when Maya starts
initialize_nox()