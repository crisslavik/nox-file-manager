"""
Silhouette integration for NOX File Manager
Auto-initializes when imported via startup script
"""

def initialize_nox():
    """Initialize NOX File Manager in Silhouette"""
    try:
        from . import nox_file_dialog_silhouette
        print("NOX File Manager initialized for Silhouette")
        return True
    except Exception as e:
        print(f"Failed to initialize NOX for Silhouette: {e}")
        return False

# Auto-initialize when imported
initialize_nox()