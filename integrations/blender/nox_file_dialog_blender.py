# blender/nox_file_dialog_blender.py
"""
Complete Blender integration with NOX File Dialog
"""

import bpy
import os
from PySide6.QtWidgets import QApplication
from ui.file_dialog import NOXFileDialog
from dcc.blender_file_manager import BlenderFileManager

# Initialize file manager
file_manager = BlenderFileManager()

class NOXLoadOperator(bpy.types.Operator):
    """NOX Load File Operator"""
    bl_idname = "nox.load_file"
    bl_label = "NOX Load"
    bl_description = "Load file with NOX dialog"
    
    def execute(self, context):
        # Ensure Qt application
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        dialog = NOXFileDialog(
            mode="load",
            dcc_name="Blender",
            file_extensions=[".blend"],
            current_file=bpy.data.filepath
        )
        
        if dialog.exec() == NOXFileDialog.Accepted:
            result = dialog.get_result()
            file_path = result['file_path']
            load_mode = result['load_mode']
            
            try:
                if load_mode == "open":
                    # Use file manager to open
                    load_result = file_manager.load_file(file_path, import_mode=False)
                    
                    if load_result.success:
                        self.report({'INFO'}, f"Opened: {os.path.basename(file_path)}")
                    else:
                        self.report({'ERROR'}, f"Load failed: {load_result.message}")
                        return {'CANCELLED'}
                
                else:  # import mode
                    # Use file manager to import/append
                    load_result = file_manager.load_file(file_path, import_mode=True)
                    
                    if load_result.success:
                        self.report({'INFO'}, f"Imported: {os.path.basename(file_path)}")
                    else:
                        self.report({'ERROR'}, f"Import failed: {load_result.message}")
                        return {'CANCELLED'}
            
            except Exception as e:
                self.report({'ERROR'}, f"Error: {e}")
                return {'CANCELLED'}
        
        return {'FINISHED'}

class NOXSaveOperator(bpy.types.Operator):
    """NOX Save File Operator"""
    bl_idname = "nox.save_file"
    bl_label = "NOX Save"
    bl_description = "Save file with NOX dialog"
    
    def execute(self, context):
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        dialog = NOXFileDialog(
            mode="save",
            dcc_name="Blender",
            file_extensions=[".blend"],
            current_file=bpy.data.filepath
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
                    self.report({'INFO'}, f"Saved: {os.path.basename(save_result.path)}")
                else:
                    self.report({'ERROR'}, f"Save failed: {save_result.message}")
                    return {'CANCELLED'}
            
            except Exception as e:
                self.report({'ERROR'}, f"Error: {e}")
                return {'CANCELLED'}
        
        return {'FINISHED'}

class NOX_PT_FilePanel(bpy.types.Panel):
    """NOX File Management Panel"""
    bl_label = "NOX File Manager"
    bl_idname = "NOX_PT_file_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'NOX'
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator("nox.load_file", text="Load File", icon='FILE_FOLDER')
        layout.operator("nox.save_file", text="Save File", icon='FILE_TICK')
        
        layout.separator()
        
        # Display current file info
        if bpy.data.filepath:
            box = layout.box()
            box.label(text="Current File:", icon='FILE_BLEND')
            box.label(text=os.path.basename(bpy.data.filepath))
        else:
            layout.label(text="No file open", icon='ERROR')

def menu_func_load(self, context):
    """Add load to menu"""
    self.layout.operator(NOXLoadOperator.bl_idname, icon='FILE_FOLDER')

def menu_func_save(self, context):
    """Add save to menu"""
    self.layout.operator(NOXSaveOperator.bl_idname, icon='FILE_TICK')

classes = (
    NOXLoadOperator,
    NOXSaveOperator,
    NOX_PT_FilePanel,
)

def register():
    """Register addon"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.TOPBAR_MT_file.append(menu_func_load)
    bpy.types.TOPBAR_MT_file.append(menu_func_save)
    
    print("NOX File Manager registered for Blender")

def unregister():
    """Unregister addon"""
    bpy.types.TOPBAR_MT_file.remove(menu_func_save)
    bpy.types.TOPBAR_MT_file.remove(menu_func_load)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()