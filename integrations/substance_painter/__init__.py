"""
Substance Painter integration for NOX File Manager
Auto-initializes when imported via startup script
"""

def initialize_nox():
    """Initialize NOX File Manager in Substance Painter"""
    try:
        from . import nox_file_dialog_substance_painter
        print("NOX File Manager initialized for Substance Painter")
        return True
    except Exception as e:
        print(f"Failed to initialize NOX for Substance Painter: {e}")
        return False

# Auto-initialize when imported
initialize_nox()