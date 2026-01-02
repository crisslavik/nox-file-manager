# maya/nox_file_dialog_maya.py
"""
Complete Maya integration with NOX File Dialog
"""

import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide6.QtWidgets import QWidget, QMessageBox
from shiboken6 import wrapInstance
from ui.file_dialog import NOXFileDialog
from integrations.maya.nox_save_dialog import NOXSaveDialogMaya
from dcc.maya_file_manager import MayaFileManager

# Initialize file manager
file_manager = MayaFileManager()

def maya_main_window():
    """Get Maya main window as Qt object"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QWidget)

def show_load_dialog():
    """Show NOX load dialog for Maya"""
    dialog = NOXFileDialog(
        mode="load",
        dcc_name="Maya",
        file_extensions=[".ma", ".mb"],
        current_file=cmds.file(q=True, sn=True),
        parent=maya_main_window()
    )
    
    if dialog.exec() == NOXFileDialog.Accepted:
        result = dialog.get_result()
        file_path = result['file_path']
        load_mode = result['load_mode']
        
        try:
            if load_mode == "open":
                # Check for unsaved changes
                if cmds.file(q=True, modified=True):
                    response = cmds.confirmDialog(
                        title='Unsaved Changes',
                        message='Current scene has unsaved changes. Continue?',
                        button=['Yes', 'No'],
                        defaultButton='No',
                        cancelButton='No'
                    )
                    if response == 'No':
                        return
                
                # Use file manager to open
                load_result = file_manager.load_file(file_path, import_mode=False)
                
                if load_result.success:
                    cmds.inViewMessage(
                        msg=f"Opened: {os.path.basename(file_path)}",
                        pos='topCenter',
                        fade=True
                    )
                else:
                    cmds.confirmDialog(
                        title='Error',
                        message=f"Load failed: {load_result.message}",
                        button=['OK']
                    )
            
            else:  # import mode
                # Use file manager to import
                load_result = file_manager.import_file(file_path)
                
                if load_result.success:
                    cmds.inViewMessage(
                        msg=f"Imported: {os.path.basename(file_path)}",
                        pos='topCenter',
                        fade=True
                    )
                else:
                    cmds.confirmDialog(
                        title='Error',
                        message=f"Import failed: {load_result.message}",
                        button=['OK']
                    )
        
        except Exception as e:
            cmds.confirmDialog(
                title='Error',
                message=f"Error: {e}",
                button=['OK']
            )

def show_save_dialog():
    """Show NOX save dialog for Maya"""
    dialog = NOXSaveDialogMaya(
        current_file=cmds.file(q=True, sn=True),
        parent=maya_main_window()
    )
    
    if dialog.exec() == NOXSaveDialogMaya.Accepted:
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
                        ext = os.path.splitext(file_path)[1]
                        file_path = f"{base_path}_v{next_version:03d}{ext}"
            
            # Determine file type
            file_type = result['file_type']
            
            save_result = file_manager.save_file(
                file_path,
                file_type=file_type,
                keep_history=result['keep_history'],
                optimize_scene=result['optimize_scene'],
                backup_previous=result.get('backup_previous', True)
            )
            
            if save_result.success:
                cmds.inViewMessage(
                    msg=f"Saved: {os.path.basename(save_result.path)}",
                    pos='topCenter',
                    fade=True
                )
            else:
                cmds.confirmDialog(
                    title='Error',
                    message=f"Save failed: {save_result.message}",
                    button=['OK']
                )
        
        except Exception as e:
            cmds.confirmDialog(
                title='Error',
                message=f"Error: {e}",
                button=['OK']
            )

def show_reference_dialog():
    """Show dialog to reference a file"""
    dialog = NOXFileDialog(
        mode="load",
        dcc_name="Maya",
        file_extensions=[".ma", ".mb"],
        current_file=cmds.file(q=True, sn=True),
        parent=maya_main_window()
    )
    
    # Override load mode to reference
    dialog.radio_import.setText("Reference (Create reference)")
    
    if dialog.exec() == NOXFileDialog.Accepted:
        result = dialog.get_result()
        file_path = result['file_path']
        
        # Get namespace from user
        namespace_result = cmds.promptDialog(
            title='Reference Namespace',
            message='Enter namespace (leave empty for auto):',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel'
        )
        
        if namespace_result == 'OK':
            namespace = cmds.promptDialog(query=True, text=True)
            namespace = namespace if namespace else None
            
            try:
                ref_result = file_manager.reference_file(file_path, namespace=namespace)
                
                if ref_result.success:
                    cmds.inViewMessage(
                        msg=f"Referenced: {os.path.basename(file_path)}",
                        pos='topCenter',
                        fade=True
                    )
                else:
                    cmds.confirmDialog(
                        title='Error',
                        message=f"Reference failed: {ref_result.message}",
                        button=['OK']
                    )
            except Exception as e:
                cmds.confirmDialog(
                    title='Error',
                    message=f"Error: {e}",
                    button=['OK']
                )

def setup_maya_menu():
    """Setup NOX menu in Maya"""
    if cmds.menu('NOXMenu', exists=True):
        cmds.deleteUI('NOXMenu', menu=True)
    
    nox_menu = cmds.menu('NOXMenu', label='NOX', parent='MayaWindow', tearOff=True)
    
    cmds.menuItem(label='Load...', command=lambda x: show_load_dialog(), parent=nox_menu)
    cmds.menuItem(label='Save As...', command=lambda x: show_save_dialog(), parent=nox_menu)
    cmds.menuItem(divider=True, parent=nox_menu)
    cmds.menuItem(label='Reference...', command=lambda x: show_reference_dialog(), parent=nox_menu)

def setup_maya_shelf():
    """Setup NOX shelf in Maya"""
    shelf_name = 'NOX'
    
    # Delete shelf if it exists
    if cmds.shelfLayout(shelf_name, exists=True):
        cmds.deleteUI(shelf_name, layout=True)
    
    # Create shelf
    shelf = cmds.shelfLayout(shelf_name, parent='ShelfLayout')
    
    # Add buttons
    cmds.shelfButton(
        label='Load',
        annotation='NOX Load File',
        image='fileOpen.png',
        command='import maya.nox_file_dialog_maya as nox; nox.show_load_dialog()',
        parent=shelf
    )
    
    cmds.shelfButton(
        label='Save',
        annotation='NOX Save File',
        image='fileSave.png',
        command='import maya.nox_file_dialog_maya as nox; nox.show_save_dialog()',
        parent=shelf
    )
    
    cmds.shelfButton(
        label='Ref',
        annotation='NOX Reference File',
        image='reference.png',
        command='import maya.nox_file_dialog_maya as nox; nox.show_reference_dialog()',
        parent=shelf
    )

# Initialize on Maya startup
def initialize():
    """Initialize NOX tools in Maya"""
    try:
        setup_maya_menu()
        setup_maya_shelf()
        print("NOX File Manager initialized for Maya")
    except Exception as e:
        print(f"Failed to initialize NOX File Manager: {e}")

# Call this in userSetup.py:
# cmds.evalDeferred('import maya.nox_file_dialog_maya as nox; nox.initialize()')