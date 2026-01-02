# nuke/nox_file_dialog_nuke.py
"""
NOX File Dialog integration for Nuke
"""

import nuke
import nukescripts
import os
from ui.file_dialog import NOXFileDialog
from integrations.nuke.nox_save_dialog import NOXSaveDialogNuke
from dcc.nuke_file_manager import NukeFileManager

# Initialize file manager
file_manager = NukeFileManager()

def show_load_dialog():
    """Show NOX load dialog for Nuke"""
    dialog = NOXFileDialog(
        mode="load",
        dcc_name="Nuke",
        file_extensions=[".nk", ".nknc"],
        current_file=nuke.root().name()
    )
    
    if dialog.exec() == NOXFileDialog.Accepted:
        result = dialog.get_result()
        file_path = result['file_path']
        load_mode = result['load_mode']
        
        try:
            if load_mode == "open":
                # Clear current script and open new one
                if nuke.root().modified():
                    ret = nuke.ask("Current script has unsaved changes. Continue?")
                    if not ret:
                        return
                
                nuke.scriptClear()
                nuke.scriptOpen(file_path)
                nuke.message(f"Opened: {file_path}")
            
            else:  # import mode
                # Import nodes into current script
                nuke.nodePaste(file_path)
                nuke.message(f"Imported: {file_path}")
        
        except Exception as e:
            nuke.message(f"Error loading file: {e}")

def show_save_dialog():
    """Show NOX save dialog for Nuke"""
    dialog = NOXSaveDialogNuke(
        current_file=nuke.root().name()
    )
    
    if dialog.exec() == NOXSaveDialogNuke.Accepted:
        result = dialog.get_result()
        
        try:
            # Build file path with version and suffix
            file_path = result['file_path']
            if result['suffix']:
                base_path = os.path.splitext(file_path)[0]
                ext = os.path.splitext(file_path)[1]
                file_path = f"{base_path}_{result['suffix']}{ext}"
            
            # Handle version increment
            if result['auto_increment']:
                # Extract next version from result
                version_str = result['version']
                if '(Next)' in version_str:
                    import re
                    m = re.search(r'v(\d+)', version_str)
                    if m:
                        next_version = int(m.group(1))
                        base_path = os.path.splitext(file_path)[0]
                        # Use .nknc extension if compression is enabled
                        ext = '.nknc' if result['compress_script'] else '.nk'
                        file_path = f"{base_path}_v{next_version:03d}{ext}"
            
            # Use file manager for saving with Nuke-specific options
            save_result = file_manager.save_file(
                file_path,
                compress_script=result['compress_script'],
                backup_previous=result['backup_previous'],
                save_comp_script_only=result['save_comp_script_only'],
                metadata={'user_note': 'Saved via NOX dialog'}
            )
            
            if save_result.success:
                nuke.message(f"Saved: {save_result.path}")
            else:
                nuke.message(f"Save failed: {save_result.message}")
        
        except Exception as e:
            nuke.message(f"Error saving file: {e}")

# Add to Nuke menu
def setup_nuke_menu():
    """Setup NOX menu in Nuke"""
    menubar = nuke.menu('Nuke')
    nox_menu = menubar.addMenu('NOX')
    
    nox_menu.addCommand('File/Load...', show_load_dialog, 'Ctrl+Alt+O')
    nox_menu.addCommand('File/Save As...', show_save_dialog, 'Ctrl+Alt+S')

# Call this in menu.py
setup_nuke_menu()