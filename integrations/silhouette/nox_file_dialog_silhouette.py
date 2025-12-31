# integrations/silhouette/nox_file_dialog_silhouette.py
"""
Silhouette NOX File Dialog Integration
"""

import sys
import os
from pathlib import Path

# Add NOX to path
nox_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(nox_path))

try:
    from dcc.silhouette_file_manager import SilhouetteFileManager
    from ui.nox_file_dialog import NOXFileDialog
    
    def show_nox_file_dialog():
        """Show NOX file dialog in Silhouette"""
        try:
            file_manager = SilhouetteFileManager()
            dialog = NOXFileDialog(file_manager)
            dialog.show()
        except Exception as e:
            print(f"Error showing NOX dialog: {e}")
    
    def initialize_silhouette_integration():
        """Initialize NOX integration in Silhouette"""
        # Silhouette-specific menu integration would go here
        print("NOX File Manager initialized for Silhouette")
        
except ImportError as e:
    print(f"Could not import NOX modules: {e}")
