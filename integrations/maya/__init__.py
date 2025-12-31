"""
Maya integration for NOX File Manager
Auto-initializes when imported via userSetup.py
"""

def initialize_nox():
    """Initialize NOX File Manager in Maya"""
    try:
        from . import nox_file_dialog_maya
        from . import nox_menu
        print("NOX File Manager initialized for Maya")
        return True
    except Exception as e:
        print(f"Failed to initialize NOX for Maya: {e}")
        return False

# Auto-initialize when imported
initialize_nox()