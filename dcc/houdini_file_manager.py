# dcc/houdini_file_manager.py
"""
SideFX Houdini file manager implementation
"""

import hou
from core.file_manager import BaseFileManager, FileOperationResult

class HoudiniFileManager(BaseFileManager):
    
    def get_software_name(self) -> str:
        return "Houdini"
    
    def get_software_version(self) -> str:
        return hou.applicationVersionString()
    
    def save_file(self, file_path: str, **kwargs) -> FileOperationResult:
        """Save Houdini hip file"""
        try:
            if not self.validate_path(file_path):
                return FileOperationResult(success=False, message="Invalid path")
            
            if kwargs.get('auto_version', self.config.auto_version):
                file_path = self.get_versioned_path(file_path)
            
            current_file = self.get_current_file()
            if current_file and kwargs.get('backup', self.config.backup_enabled):
                self.create_backup(current_file)
            
            hou.hipFile.save(file_path)
            
            # Collect Houdini-specific metadata
            metadata = {
                'frame_range': f"{hou.playbar.playbackRange()[0]}-{hou.playbar.playbackRange()[1]}",
                'fps': hou.fps(),
                'hip_name': hou.hipFile.basename(),
                'node_count': len(hou.node('/').allSubChildren()),
                **kwargs.get('metadata', {})
            }
            self.save_metadata(file_path, metadata)
            
            result = FileOperationResult(
                success=True,
                path=file_path,
                message="Hip file saved successfully",
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
        """Load Houdini hip file"""
        try:
            if not os.path.exists(file_path):
                return FileOperationResult(
                    success=False,
                    message=f"File not found: {file_path}"
                )
            
            if self.config.validate_on_load:
                metadata = self.load_metadata(file_path)
            
            clear = kwargs.get('clear_current', True)
            hou.hipFile.load(file_path, suppress_save_prompt=True, 
                           ignore_load_warnings=False)
            
            result = FileOperationResult(
                success=True,
                path=file_path,
                message="Hip file loaded successfully"
            )
            
            self._last_operation = result
            self.logger.info(f"Loaded: {file_path}")
            return result
            
        except Exception as e:
            result = FileOperationResult(success=False, message=str(e))
            self._last_operation = result
            self.logger.error(f"Load failed: {e}")
            return result
    
    def get_current_file(self) -> Optional[str]:
        """Get currently open hip file"""
        return hou.hipFile.path() if hou.hipFile.name() != "untitled.hip" else None