"""
3DEqualizer integration for NOX File Manager
Auto-initializes when imported via startup script
"""

def initialize_nox():
    """Initialize NOX File Manager in 3DEqualizer"""
    try:
        from . import nox_file_dialog_equalizer
        print("NOX File Manager initialized for 3DEqualizer")
        return True
    except Exception as e:
        print(f"Failed to initialize NOX for 3DEqualizer: {e}")
        return False

# Auto-initialize when imported
initialize_nox()