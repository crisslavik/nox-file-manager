# houdini/pythonrc.py or 456.py
"""
Houdini integration with ShotGrid file manager
"""

import hou
import os
from dcc.houdini_file_manager import HoudiniFileManager
from shotgrid.sg_file_manager import ShotGridFileManager

SG_CONFIG = {
    'url': os.getenv('SG_URL', 'https://nox.shotgridstudio.com'),
    'script_name': os.getenv('SG_SCRIPT_NAME'),
    'api_key': os.getenv('SG_API_KEY'),
    'project_id': int(os.getenv('SG_PROJECT_ID', '0'))
}

houdini_manager = HoudiniFileManager()
sg_manager = ShotGridFileManager(houdini_manager, SG_CONFIG)

def save_work_file():
    """Save work file with SG integration"""
    result = sg_manager.save_work_file()
    if result.success:
        hou.ui.displayMessage(f"Saved: {result.path}")
    else:
        hou.ui.displayMessage(f"Save failed: {result.message}", severity=hou.severityType.Error)

def publish_for_review():
    """Publish for review"""
    description = hou.ui.readInput("Publish description:")[1]
    
    result = sg_manager.publish(description=description)
    
    if result.success:
        hou.ui.displayMessage(
            f"Published successfully!\nVersion: {result.metadata['version_number']}"
        )
    else:
        hou.ui.displayMessage(f"Publish failed: {result.message}", severity=hou.severityType.Error)

# Create shelf tools
def create_nox_shelf():
    """Create NOX shelf with file management tools"""
    shelves = hou.shelves.shelves()
    
    if 'nox_tools' not in shelves:
        shelf = hou.shelves.newShelf(
            file_path=os.path.join(hou.homeHoudiniDirectory(), "toolbar", "nox_tools.shelf"),
            name="nox_tools",
            label="NOX"
        )
    else:
        shelf = shelves['nox_tools']
    
    # Add tools
    tools_def = [
        {
            'name': 'save_work',
            'label': 'Save Work',
            'script': 'import nox_houdini\nnox_houdini.save_work_file()',
            'icon': 'COMMON/save'
        },
        {
            'name': 'publish',
            'label': 'Publish',
            'script': 'import nox_houdini\nnox_houdini.publish_for_review()',
            'icon': 'COMMON/export'
        }
    ]
    
    for tool_def in tools_def:
        if tool_def['name'] not in shelf.tools():
            tool = hou.shelves.newTool(
                file_path=shelf.filePath(),
                name=tool_def['name'],
                label=tool_def['label'],
                script=tool_def['script'],
                icon=tool_def['icon']
            )
            shelf.setTools(shelf.tools() + (tool,))

# Create shelf on startup
create_nox_shelf()