"""
Mocha Pro integration for NOX File Manager
Auto-initializes when imported via startup script
"""

def initialize_nox():
    """Initialize NOX File Manager in Mocha Pro"""
    try:
        from . import nox_file_dialog_mocha
        print("NOX File Manager initialized for Mocha Pro")
        return True
    except Exception as e:
        print(f"Failed to initialize NOX for Mocha Pro: {e}")
        return False

# Auto-initialize when imported
initialize_nox()