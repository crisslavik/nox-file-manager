# integrations/mocha/nox_file_dialog_mocha.py
"""
Mocha Pro NOX File Dialog Integration
"""

import sys
import os
from pathlib import Path

# Add NOX to path
nox_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(nox_path))

try:
    from dcc.mocha_file_manager import MochaFileManager
    from ui.nox_file_dialog import NOXFileDialog
    
    def show_nox_file_dialog():
        """Show NOX file dialog in Mocha"""
        try:
            file_manager = MochaFileManager()
            dialog = NOXFileDialog(file_manager)
            dialog.show()
        except Exception as e:
            print(f"Error showing NOX dialog: {e}")
    
    def initialize_mocha_integration():
        """Initialize NOX integration in Mocha"""
        # Mocha-specific menu integration would go here
        print("NOX File Manager initialized for Mocha")
        
except ImportError as e:
    print(f"Could not import NOX modules: {e}")
