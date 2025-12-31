"""
Blender addon for NOX File Manager
Blender addon manifest
"""

bl_info = {
    "name": "NOX File Manager",
    "author": "NOX VFX",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > NOX, File menu",
    "description": "Unified file management for VFX pipeline",
    "category": "System",
}

def register():
    """Register the addon"""
    try:
        from . import nox_file_dialog_blender
        nox_file_dialog_blender.register()
        print("NOX File Manager addon registered")
    except Exception as e:
        print(f"Failed to register NOX addon: {e}")

def unregister():
    """Unregister the addon"""
    try:
        from . import nox_file_dialog_blender
        nox_file_dialog_blender.unregister()
        print("NOX File Manager addon unregistered")
    except Exception as e:
        print(f"Failed to unregister NOX addon: {e}")

if __name__ == "__main__":
    register()