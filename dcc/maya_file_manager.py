# dcc/maya_file_manager.py
"""
Maya file manager implementation
"""

import os
import maya.cmds as cmds
import maya.mel as mel
from typing import Optional
from core.file_manager import BaseFileManager, FileOperationResult

class MayaFileManager(BaseFileManager):
    
    def get_software_name(self) -> str:
        return "Maya"
    
    def get_software_version(self) -> str:
        return cmds.about(version=True)
    
    def save_file(self, file_path: str, **kwargs) -> FileOperationResult:
        """Save Maya scene file"""
        try:
            if not self.validate_path(file_path):
                return FileOperationResult(success=False, message="Invalid path")
            
            if kwargs.get('auto_version', self.config.auto_version):
                file_path = self.get_versioned_path(file_path)
            
            current_file = self.get_current_file()
            if current_file and kwargs.get('backup', self.config.backup_enabled):
                self.create_backup(current_file)
            
            # Determine file type
            file_type = "mayaAscii" if file_path.endswith('.ma') else "mayaBinary"
            
            # Save the file
            cmds.file(rename=file_path)
            cmds.file(save=True, type=file_type)
            
            # Collect Maya-specific metadata
            metadata = {
                'frame_range': f"{cmds.playbackOptions(q=True, min=True)}-{cmds.playbackOptions(q=True, max=True)}",
                'fps': mel.eval('currentTimeUnitToFPS()'),
                'current_unit': cmds.currentUnit(q=True, linear=True),
                'scene_units': cmds.currentUnit(q=True, time=True),
                'render_engine': cmds.getAttr('defaultRenderGlobals.currentRenderer'),
                'maya_version': cmds.about(version=True),
                'dag_objects': len(cmds.ls(dag=True)),
                'meshes': len(cmds.ls(type='mesh')),
                'cameras': len(cmds.ls(type='camera')),
                'lights': len(cmds.ls(type='light')),
                **kwargs.get('metadata', {})
            }
            self.save_metadata(file_path, metadata)
            
            result = FileOperationResult(
                success=True,
                path=file_path,
                message="Maya scene saved successfully",
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
        """Load Maya scene file"""
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
                # Import/Reference into current scene
                reference = kwargs.get('reference', False)
                namespace = kwargs.get('namespace', None)
                
                if reference:
                    # Create reference
                    if namespace:
                        ref_node = cmds.file(file_path, reference=True, namespace=namespace)
                    else:
                        ref_node = cmds.file(file_path, reference=True)
                    self.logger.info(f"Referenced: {file_path}")
                else:
                    # Import
                    file_type = "mayaAscii" if file_path.endswith('.ma') else "mayaBinary"
                    if namespace:
                        cmds.file(file_path, i=True, type=file_type, namespace=namespace)
                    else:
                        cmds.file(file_path, i=True, type=file_type)
                    self.logger.info(f"Imported: {file_path}")
            else:
                # Open (replace current scene)
                force = kwargs.get('force', True)
                cmds.file(file_path, open=True, force=force)
                self.logger.info(f"Opened: {file_path}")
            
            result = FileOperationResult(
                success=True,
                path=file_path,
                message="Maya scene loaded successfully"
            )
            
            self._last_operation = result
            return result
            
        except Exception as e:
            result = FileOperationResult(success=False, message=str(e))
            self._last_operation = result
            self.logger.error(f"Load failed: {e}")
            return result
    
    def get_current_file(self) -> Optional[str]:
        """Get currently open Maya scene"""
        scene_name = cmds.file(q=True, sceneName=True)
        return scene_name if scene_name else None
    
    def import_file(self, file_path: str, namespace: Optional[str] = None) -> FileOperationResult:
        """Import file into current scene"""
        return self.load_file(file_path, import_mode=True, namespace=namespace)
    
    def reference_file(self, file_path: str, namespace: Optional[str] = None) -> FileOperationResult:
        """Reference file into current scene"""
        return self.load_file(file_path, import_mode=True, reference=True, namespace=namespace)