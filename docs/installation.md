# Installation Guide

## System Requirements

- Python 3.8 or higher
- PySide6 (Qt6)
- Supported DCC applications (Nuke, Maya, Houdini, Blender, etc.)

## Quick Installation

### 1. Clone the Repository
```bash
git clone https://github.com/noxvfx/nox-file-manager.git
cd nox-file-manager
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Installer
```bash
python install.py
```

The installer will:
- Detect installed DCC applications
- Install the NOX file manager to each application
- Create necessary menu items and shelf tools
- Set up configuration files

## Manual Installation

### Nuke

1. Copy the entire `nox-file-manager` directory to your preferred location
2. Add the following to your `~/.nuke/menu.py`:
```python
import sys
sys.path.append('/path/to/nox-file-manager')
import integrations.nuke.menu
```

3. Restart Nuke - the NOX menu will appear in the main menu bar

### Maya

1. Copy the `nox-file-manager` directory to your preferred location
2. Copy `integrations/maya/userSetup.py` to your Maya scripts directory:
   - Windows: `%USERPROFILE%\Documents\maya\2024\scripts\`
   - macOS: `~/Library/Preferences/Autodesk/maya/2024/scripts/`
   - Linux: `~/maya/2024/scripts/`

3. Restart Maya - the NOX menu will appear in the main menu bar

### Houdini

1. Copy the `nox-file-manager` directory to your preferred location
2. Copy `integrations/houdini/456.py` to your Houdini scripts directory:
   - Windows: `%USERPROFILE%\Documents\houdini20.5\scripts\python\`
   - macOS: `~/Library/Preferences/houdini/20.5/scripts/python/`
   - Linux: `~/houdini20.5/scripts/python/`

3. Restart Houdini - the NOX shelf will appear

### Blender

1. Copy the `nox-file-manager` directory to your preferred location
2. In Blender, go to `Edit > Preferences > Add-ons`
3. Click `Install...` and select the `integrations/blender` directory
4. Enable the "NOX File Manager" addon
5. The NOX panel will appear in the 3D Viewport sidebar (N key)

## Configuration

### Environment Variables

Optional environment variables you can set:

```bash
export NOX_PROJECT_ROOT="/mnt/projects"
export NOX_CONFIG_PATH="/path/to/your/config.yaml"
export SG_URL="https://your.shotgridstudio.com"
export SG_SCRIPT_NAME="your_script_name"
export SG_API_KEY="your_api_key"
export SG_PROJECT_ID="123"
```

### Configuration File

The main configuration is stored in `config/nox_pipeline.yaml`. You can customize:

- Project root directory
- File naming templates
- ShotGrid connection settings
- UI preferences
- Backup and versioning options

## Troubleshooting

### Common Issues

**Menu doesn't appear in Maya:**
- Check that `userSetup.py` is in the correct scripts directory
- Verify Python path in the userSetup.py file
- Check Maya script editor for error messages

**Import errors in Nuke:**
- Ensure the nox-file-manager path is added to sys.path in menu.py
- Check that all dependencies are installed
- Verify PySide6 is available to Nuke

**Blender addon not loading:**
- Check the Blender console for error messages
- Ensure Python 3.8+ is being used by Blender
- Verify all dependencies are installed in Blender's Python environment

**Permission errors:**
- Run the installer with appropriate permissions
- Check that DCC application directories are writable
- Verify file permissions on the nox-file-manager directory

### Getting Help

If you encounter issues:

1. Check the console/output panels in your DCC application for error messages
2. Verify all dependencies are installed correctly
3. Check that paths in configuration files are correct
4. Create an issue on the GitHub repository with:
   - DCC application and version
   - Operating system
   - Error messages from the console
   - Steps to reproduce the issue

## Uninstallation

To remove NOX File Manager:

1. Run the uninstaller (if available):
```bash
python install.py --uninstall
```

2. Or manually remove:
   - Delete the nox-file-manager directory
   - Remove menu.py/userSetup.py modifications
   - Remove Blender addon through Preferences
   - Delete configuration files from `~/.nox/`