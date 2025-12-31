# integrations/substance_painter/nox_file_dialog_substance_painter.py
"""
Substance Painter NOX File Dialog Integration
"""

import sys
import os
from pathlib import Path

# Add NOX to path
nox_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(nox_path))

try:
    from dcc.substance_painter_file_manager import SubstancePainterFileManager
    from ui.nox_file_dialog import NOXFileDialog
    
    def show_nox_file_dialog():
        """Show NOX file dialog in Substance Painter"""
        try:
            file_manager = SubstancePainterFileManager()
            dialog = NOXFileDialog(file_manager)
            dialog.show()
        except Exception as e:
            print(f"Error showing NOX dialog: {e}")
    
    def initialize_substance_painter_integration():
        """Initialize NOX integration in Substance Painter"""
        # Substance Painter-specific menu integration would go here
        print("NOX File Manager initialized for Substance Painter")
        
except ImportError as e:
    print(f"Could not import NOX modules: {e}")
