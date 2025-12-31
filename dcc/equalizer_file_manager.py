# dcc/equalizer_file_manager.py
"""
3DEqualizer file manager implementation
"""

import os
from typing import Optional

# 3DEqualizer uses tde4 module
try:
    import tde4
    TDE_API_AVAILABLE = True
except ImportError:
    TDE_API_AVAILABLE = False

from core.file_manager import BaseFileManager, FileOperationResult

class EqualizerFileManager(BaseFileManager):
    
    def get_software_name(self) -> str:
        return "3DEqualizer"
    
    def get_software_version(self) -> str:
        if TDE_API_AVAILABLE:
            try:
                return tde4.get3DEVersion()
            except:
                pass
        return "Unknown"
    
    def save_file(self, file_path: str, **kwargs) -> FileOperationResult:
        """Save 3DEqualizer project"""
        try:
            if not self.validate_path(file_path):
                return FileOperationResult(success=False, message="Invalid path")
            
            if kwargs.get('auto_version', self.config.auto_version):
                file_path = self.get_versioned_path(file_path)
            
            current_file = self.get_current_file()
            if current_file and kwargs.get('backup', self.config.backup_enabled):
                self.create_backup(current_file)
            
            if TDE_API_AVAILABLE:
                # Save using 3DE API
                tde4.saveProject(file_path)
                
                # Collect 3DE-specific metadata
                pg_list = tde4.getPGroupList()
                camera_list = tde4.getCameraList()
                
                metadata = {
                    'point_groups': len(pg_list),
                    'cameras': len(camera_list),
                    '3de_version': tde4.get3DEVersion(),
                    **kwargs.get('metadata', {})
                }
                
                # Get camera info if available
                if camera_list:
                    cam = camera_list[0]
                    metadata['camera_name'] = tde4.getCameraName(cam)
                    num_frames = tde4.getCameraNoFrames(cam)
                    metadata['frames'] = num_frames
            else:
                metadata = kwargs.get('metadata', {})
            
            self.save_metadata(file_path, metadata)
            
            result = FileOperationResult(
                success=True,
                path=file_path,
                message="3DEqualizer project saved successfully",
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
        """Load 3DEqualizer project"""
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
            
            if TDE_API_AVAILABLE:
                if import_mode:
                    # Import/merge project
                    tde4.importProject(file_path)
                    self.logger.info(f"Imported: {file_path}")
                else:
                    # Load project (replace current)
                    tde4.loadProject(file_path)
                    self.logger.info(f"Opened: {file_path}")
            
            result = FileOperationResult(
                success=True,
                path=file_path,
                message="3DEqualizer project loaded successfully"
            )
            
            self._last_operation = result
            return result
            
        except Exception as e:
            result = FileOperationResult(success=False, message=str(e))
            self._last_operation = result
            self.logger.error(f"Load failed: {e}")
            return result
    
    def get_current_file(self) -> Optional[str]:
        """Get currently open 3DEqualizer project"""
        if TDE_API_AVAILABLE:
            try:
                return tde4.getProjectPath()
            except:
                pass
        return None
    
    def export_camera(self, camera_id: str, file_path: str, format: str = "fbx") -> FileOperationResult:
        """Export camera data"""
        try:
            if TDE_API_AVAILABLE:
                # Export camera based on format
                if format.lower() == "fbx":
                    tde4.exportFBX(camera_id, file_path)
                elif format.lower() == "maya":
                    tde4.exportMayaScene(camera_id, file_path)
                elif format.lower() == "nuke":
                    tde4.exportNukeNode(camera_id, file_path)
                
                return FileOperationResult(
                    success=True,
                    path=file_path,
                    message=f"Camera exported as {format}"
                )
            else:
                return FileOperationResult(
                    success=False,
                    message="3DE API not available"
                )
        except Exception as e:
            return FileOperationResult(success=False, message=str(e))