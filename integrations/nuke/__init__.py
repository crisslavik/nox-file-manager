"""
Nuke integration for NOX File Manager
Auto-initializes when imported via init.py or menu.py
"""

def initialize_nox():
    """Initialize NOX File Manager in Nuke"""
    try:
        from . import menu
        from . import nox_file_dialog_nuke
        print("NOX File Manager initialized for Nuke")
        return True
    except Exception as e:
        print(f"Failed to initialize NOX for Nuke: {e}")
        return False

# Auto-initialize when imported
initialize_nox()