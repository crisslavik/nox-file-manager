# nuke/menu.py or init.py
"""
Nuke integration with ShotGrid file manager
"""

import nuke
import os
from dcc.nuke_file_manager import NukeFileManager
from shotgrid.sg_file_manager import ShotGridFileManager

# ShotGrid configuration
SG_CONFIG = {
    'url': os.getenv('SG_URL', 'https://nox.shotgridstudio.com'),
    'script_name': os.getenv('SG_SCRIPT_NAME'),
    'api_key': os.getenv('SG_API_KEY'),
    'project_id': int(os.getenv('SG_PROJECT_ID', '0'))
}

# Initialize managers
nuke_manager = NukeFileManager()
sg_manager = ShotGridFileManager(nuke_manager, SG_CONFIG)

def save_work_file():
    """Save work file with ShotGrid integration"""
    result = sg_manager.save_work_file()
    if result.success:
        nuke.message(f"Saved: {result.path}")
    else:
        nuke.message(f"Save failed: {result.message}")

def publish_for_review():
    """Publish current script for review"""
    # Get frame range for thumbnail
    first_frame = int(nuke.root().firstFrame())
    current_frame = int(nuke.frame())
    
    # Optionally render thumbnail
    thumbnail_path = None
    # ... thumbnail generation code ...
    
    result = sg_manager.publish(
        description=nuke.getInput("Publish description:"),
        thumbnail_path=thumbnail_path
    )
    
    if result.success:
        nuke.message(f"Published successfully!\nVersion: {result.metadata['version_number']}")
    else:
        nuke.message(f"Publish failed: {result.message}")

def load_latest_publish():
    """Load latest published file for current context"""
    result = sg_manager.load_latest_publish()
    if result.success:
        nuke.message(f"Loaded: {result.path}")
    else:
        nuke.message(f"Load failed: {result.message}")

def open_work_file_dialog():
    """Show custom file browser with ShotGrid context"""
    # Get current context
    current_file = nuke_manager.get_current_file()
    if current_file:
        context = sg_manager.get_context_from_path(current_file)
        if context:
            sg_manager.set_context(
                context['entity_type'],
                context['entity_id'],
                context['task_id'],
                context['step_id']
            )
    
    # Generate default work file path
    try:
        default_path = sg_manager.get_work_file_path()
        file_path = nuke.getFilename('Save Work File', default=default_path, pattern='*.nk')
        
        if file_path:
            result = nuke_manager.save_file(file_path)
            if result.success:
                nuke.message(f"Saved: {file_path}")
    except ValueError as e:
        nuke.message(f"Error: {e}\nPlease open a file with ShotGrid context first.")

# Add to Nuke menu
menubar = nuke.menu('Nuke')
nox_menu = menubar.addMenu('NOX')

nox_menu.addCommand('File/Save Work File', save_work_file, 'Ctrl+Shift+S')
nox_menu.addCommand('File/Open Work File', open_work_file_dialog, 'Ctrl+Shift+O')
nox_menu.addCommand('File/Load Latest Publish', load_latest_publish)
nox_menu.addSeparator('File/')
nox_menu.addCommand('File/Publish for Review', publish_for_review, 'Ctrl+Shift+P')

# Add toolbar buttons
toolbar = nuke.toolbar("Nodes")
nox_toolbar = toolbar.addMenu("NOX", icon="NOX_icon.png")
nox_toolbar.addCommand("Save Work", save_work_file)
nox_toolbar.addCommand("Publish", publish_for_review)