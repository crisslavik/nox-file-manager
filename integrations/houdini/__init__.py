"""
Houdini integration for NOX File Manager
Auto-initializes when imported via 456.py or pythonrc.py
"""

def initialize_nox():
    """Initialize NOX File Manager in Houdini"""
    try:
        from . import nox_file_dialog_houdini
        print("NOX File Manager initialized for Houdini")
        return True
    except Exception as e:
        print(f"Failed to initialize NOX for Houdini: {e}")
        return False

# Auto-initialize when imported
initialize_nox()