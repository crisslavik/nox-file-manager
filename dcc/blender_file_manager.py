# dcc/blender_file_manager.py
"""
Blender file manager implementation
"""

import os
import bpy
from typing import Optional
from core.file_manager import BaseFileManager, FileOperationResult

class BlenderFileManager(BaseFileManager):
    
    def get_software_name(self) -> str:
        return "Blender"
    
    def get_software_version(self) -> str:
        return bpy.app.version_string
    
    def save_file(self, file_path: str, **kwargs) -> FileOperationResult:
        """Save Blender file"""
        try:
            if not self.validate_path(file_path):
                return FileOperationResult(success=False, message="Invalid path")
            
            if kwargs.get('auto_version', self.config.auto_version):
                file_path = self.get_versioned_path(file_path)
            
            current_file = self.get_current_file()
            if current_file and kwargs.get('backup', self.config.backup_enabled):
                self.create_backup(current_file)
            
            # Save the blend file
            bpy.ops.wm.save_as_mainfile(filepath=file_path)
            
            # Collect Blender-specific metadata
            scene = bpy.context.scene
            metadata = {
                'frame_range': f"{scene.frame_start}-{scene.frame_end}",
                'fps': scene.render.fps,
                'render_engine': scene.render.engine,
                'resolution': f"{scene.render.resolution_x}x{scene.render.resolution_y}",
                'blender_version': bpy.app.version_string,
                'objects_count': len(bpy.data.objects),
                'meshes_count': len(bpy.data.meshes),
                'materials_count': len(bpy.data.materials),
                'textures_count': len(bpy.data.textures),
                'cameras_count': len(bpy.data.cameras),
                'lights_count': len(bpy.data.lights),
                'collections_count': len(bpy.data.collections),
                **kwargs.get('metadata', {})
            }
            
            # Add render settings
            if scene.render.engine == 'CYCLES':
                metadata['samples'] = scene.cycles.samples
                metadata['device'] = scene.cycles.device
            elif scene.render.engine == 'BLENDER_EEVEE':
                metadata['taa_samples'] = scene.eevee.taa_render_samples
            
            self.save_metadata(file_path, metadata)
            
            result = FileOperationResult(
                success=True,
                path=file_path,
                message="Blender file saved successfully",
                metadata=metadata
            )
            
            self._last_operation = result
            self.logger.info(f"Saved: {file_path}")
            return result
            
        except Exception as e:
            result = FileOperationResult(success=False, message=str(e))
            self._last_operation = result
            self.logger.error(f"Save failed: {e}")
            return result
    
    def load_file(self, file_path: str, **kwargs) -> FileOperationResult:
        """Load Blender file"""
        try:
            if not os.path.exists(file_path):
                return FileOperationResult(
                    success=False,
                    message=f"File not found: {file_path}"
                )
            
            if self.config.validate_on_load:
                metadata = self.load_metadata(file_path)
                if metadata:
                    self.logger.info(f"Loaded metadata: {metadata}")
            
            import_mode = kwargs.get('import_mode', False)
            
            if import_mode:
                # Import/Append/Link objects from another blend file
                link = kwargs.get('link', False)
                
                # Determine what to import
                import_type = kwargs.get('import_type', 'Object')  # Object, Collection, Material, etc.
                import_names = kwargs.get('import_names', None)  # Specific items to import
                
                with bpy.data.libraries.load(file_path, link=link) as (data_from, data_to):
                    if import_type == 'Object':
                        if import_names:
                            data_to.objects = [obj for obj in data_from.objects if obj in import_names]
                        else:
                            data_to.objects = data_from.objects
                    elif import_type == 'Collection':
                        if import_names:
                            data_to.collections = [col for col in data_from.collections if col in import_names]
                        else:
                            data_to.collections = data_from.collections
                    elif import_type == 'Material':
                        if import_names:
                            data_to.materials = [mat for mat in data_from.materials if mat in import_names]
                        else:
                            data_to.materials = data_from.materials
                
                # Link imported objects to the scene
                if import_type == 'Object' and data_to.objects:
                    for obj in data_to.objects:
                        if obj:
                            bpy.context.collection.objects.link(obj)
                elif import_type == 'Collection' and data_to.collections:
                    for col in data_to.collections:
                        if col:
                            bpy.context.scene.collection.children.link(col)
                
                mode_text = "Linked" if link else "Imported"
                self.logger.info(f"{mode_text}: {file_path}")
            else:
                # Open (replace current scene)
                bpy.ops.wm.open_mainfile(filepath=file_path)
                self.logger.info(f"Opened: {file_path}")
            
            result = FileOperationResult(
                success=True,
                path=file_path,
                message="Blender file loaded successfully"
            )
            
            self._last_operation = result
            return result
            
        except Exception as e:
            result = FileOperationResult(success=False, message=str(e))
            self._last_operation = result
            self.logger.error(f"Load failed: {e}")
            return result
    
    def get_current_file(self) -> Optional[str]:
        """Get currently open blend file"""
        return bpy.data.filepath if bpy.data.filepath else None
    
    def import_file(self, file_path: str, import_type: str = 'Object', 
                    import_names: Optional[list] = None) -> FileOperationResult:
        """Import/Append objects from another blend file"""
        return self.load_file(
            file_path, 
            import_mode=True, 
            link=False,
            import_type=import_type,
            import_names=import_names
        )
    
    def link_file(self, file_path: str, import_type: str = 'Object',
                  import_names: Optional[list] = None) -> FileOperationResult:
        """Link objects from another blend file"""
        return self.load_file(
            file_path,
            import_mode=True,
            link=True,
            import_type=import_type,
            import_names=import_names
        )
    
    def export_fbx(self, file_path: str, **kwargs) -> FileOperationResult:
        """Export scene as FBX"""
        try:
            # Default FBX export settings
            use_selection = kwargs.get('use_selection', False)
            apply_modifiers = kwargs.get('apply_modifiers', True)
            
            bpy.ops.export_scene.fbx(
                filepath=file_path,
                use_selection=use_selection,
                apply_modifiers=apply_modifiers,
                path_mode='COPY',
                embed_textures=True
            )
            
            return FileOperationResult(
                success=True,
                path=file_path,
                message="FBX exported successfully"
            )
        except Exception as e:
            return FileOperationResult(success=False, message=str(e))
    
    def export_alembic(self, file_path: str, **kwargs) -> FileOperationResult:
        """Export scene as Alembic"""
        try:
            use_selection = kwargs.get('use_selection', False)
            frame_start = kwargs.get('frame_start', bpy.context.scene.frame_start)
            frame_end = kwargs.get('frame_end', bpy.context.scene.frame_end)
            
            bpy.ops.wm.alembic_export(
                filepath=file_path,
                selected=use_selection,
                start=frame_start,
                end=frame_end
            )
            
            return FileOperationResult(
                success=True,
                path=file_path,
                message="Alembic exported successfully"
            )
        except Exception as e:
            return FileOperationResult(success=False, message=str(e))
    
    def export_obj(self, file_path: str, **kwargs) -> FileOperationResult:
        """Export scene as OBJ"""
        try:
            use_selection = kwargs.get('use_selection', False)
            apply_modifiers = kwargs.get('apply_modifiers', True)
            
            bpy.ops.export_scene.obj(
                filepath=file_path,
                use_selection=use_selection,
                use_materials=True,
                use_triangles=False,
                axis_forward='Y',
                axis_up='Z'
            )
            
            return FileOperationResult(
                success=True,
                path=file_path,
                message="OBJ exported successfully"
            )
        except Exception as e:
            return FileOperationResult(success=False, message=str(e))