# integrations/equalizer/nox_file_dialog_equalizer.py
"""
3DEqualizer NOX File Dialog Integration
"""

import sys
import os
from pathlib import Path

# Add NOX to path
nox_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(nox_path))

try:
    from dcc.equalizer_file_manager import EqualizerFileManager
    from ui.nox_file_dialog import NOXFileDialog
    
    def show_nox_file_dialog():
        """Show NOX file dialog in 3DEqualizer"""
        try:
            file_manager = EqualizerFileManager()
            dialog = NOXFileDialog(file_manager)
            dialog.show()
        except Exception as e:
            print(f"Error showing NOX dialog: {e}")
    
    def initialize_equalizer_integration():
        """Initialize NOX integration in 3DEqualizer"""
        # 3DEqualizer-specific menu integration would go here
        print("NOX File Manager initialized for 3DEqualizer")
        
except ImportError as e:
    print(f"Could not import NOX modules: {e}")
