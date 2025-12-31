# houdini/nox_file_dialog_houdini.py
"""
NOX File Dialog integration for Houdini
"""

import hou
from PySide6.QtWidgets import QApplication
from ui.file_dialog import NOXFileDialog
from dcc.houdini_file_manager import HoudiniFileManager

file_manager = HoudiniFileManager()

def show_load_dialog():
    """Show NOX load dialog for Houdini"""
    # Ensure Qt application exists
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    
    dialog = NOXFileDialog(
        mode="load",
        dcc_name="Houdini",
        file_extensions=[".hip", ".hipnc", ".hiplc"],
        current_file=hou.hipFile.path(),
        parent=hou.qt.mainWindow()
    )
    
    if dialog.exec() == NOXFileDialog.Accepted:
        result = dialog.get_result()
        file_path = result['file_path']
        load_mode = result['load_mode']
        
        try:
            if load_mode == "open":
                # Check for unsaved changes
                if hou.hipFile.hasUnsavedChanges():
                    choice = hou.ui.displayMessage(
                        "Current file has unsaved changes. Continue?",
                        buttons=("Yes", "No"),
                        default_choice=1
                    )
                    if choice == 1:
                        return
                
                hou.hipFile.load(file_path, suppress_save_prompt=True)
                hou.ui.displayMessage(f"Opened: {file_path}")
            
            else:  # import mode
                hou.hipFile.merge(file_path)
                hou.ui.displayMessage(f"Imported: {file_path}")
        
        except Exception as e:
            hou.ui.displayMessage(f"Error loading file: {e}", severity=hou.severityType.Error)

def show_save_dialog():
    """Show NOX save dialog for Houdini"""
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    
    dialog = NOXFileDialog(
        mode="save",
        dcc_name="Houdini",
        file_extensions=[".hip"],
        current_file=hou.hipFile.path(),
        parent=hou.qt.mainWindow()
    )
    
    if dialog.exec() == NOXFileDialog.Accepted:
        result = dialog.get_result()
        
        try:
            save_result = file_manager.save_file(
                result['file_path'],
                backup=result['create_backup'],
                auto_version=result['auto_version']
            )
            
            if save_result.success:
                hou.ui.displayMessage(f"Saved: {save_result.path}")
            else:
                hou.ui.displayMessage(f"Save failed: {save_result.message}", severity=hou.severityType.Error)
        
        except Exception as e:
            hou.ui.displayMessage(f"Error saving file: {e}", severity=hou.severityType.Error)

# Create shelf tools or menu items
def create_nox_menu():
    """Create NOX menu in Houdini"""
    # This would typically go in your MainMenuCommon.xml or be added via Python
    pass