"""
Maya NOX menu setup
Alternative menu system if not using userSetup.py
"""

import maya.cmds as cmds
import maya.mel as mel

def create_nox_menu():
    """Create NOX menu in Maya"""
    # Delete existing menu if it exists
    if cmds.menu('NOXMenu', exists=True):
        cmds.deleteUI('NOXMenu', menu=True)
    
    # Create main menu
    nox_menu = cmds.menu('NOXMenu', label='NOX', parent='MayaWindow', tearOff=True)
    
    # File operations submenu
    file_menu = cmds.menuItem(label='File', subMenu=True, parent=nox_menu)
    cmds.menuItem(label='Load...', command='import integrations.maya.nox_file_dialog_maya as nox; nox.show_load_dialog()', parent=file_menu)
    cmds.menuItem(label='Save As...', command='import integrations.maya.nox_file_dialog_maya as nox; nox.show_save_dialog()', parent=file_menu)
    cmds.menuItem(divider=True, parent=file_menu)
    cmds.menuItem(label='Reference...', command='import integrations.maya.nox_file_dialog_maya as nox; nox.show_reference_dialog()', parent=file_menu)
    cmds.menuItem(label='Import...', command='import integrations.maya.nox_file_dialog_maya as nox; nox.show_import_dialog()', parent=file_menu)
    
    cmds.menuItem(divider=True, parent=nox_menu)
    
    # ShotGrid submenu
    sg_menu = cmds.menuItem(label='ShotGrid', subMenu=True, parent=nox_menu)
    cmds.menuItem(label='Save Work File', command='import integrations.maya.nox_shotgrid as sg; sg.save_work_file()', parent=sg_menu)
    cmds.menuItem(label='Publish for Review', command='import integrations.maya.nox_shotgrid as sg; sg.publish_for_review()', parent=sg_menu)
    cmds.menuItem(label='Load Latest Publish', command='import integrations.maya.nox_shotgrid as sg; sg.load_latest_publish()', parent=sg_menu)
    
    cmds.menuItem(divider=True, parent=nox_menu)
    
    # Utilities
    cmds.menuItem(label='Scene Info', command='import integrations.maya.nox_file_dialog_maya as nox; nox.show_scene_info()', parent=nox_menu)
    cmds.menuItem(label='Preferences', command='import integrations.maya.nox_file_dialog_maya as nox; nox.show_preferences()', parent=nox_menu)
    
    print("NOX menu created in Maya")

def remove_nox_menu():
    """Remove NOX menu from Maya"""
    if cmds.menu('NOXMenu', exists=True):
        cmds.deleteUI('NOXMenu', menu=True)
        print("NOX menu removed from Maya")

# Auto-create menu when imported
if __name__ == "__main__":
    create_nox_menu()