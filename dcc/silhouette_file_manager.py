# dcc/silhouette_file_manager.py
"""
Silhouette file manager implementation
"""

import os
from typing import Optional

# Silhouette Python API
try:
    import fx
    SILHOUETTE_API_AVAILABLE = True
except ImportError:
    SILHOUETTE_API_AVAILABLE = False

from core.file_manager import BaseFileManager, FileOperationResult

class SilhouetteFileManager(BaseFileManager):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = None
        if SILHOUETTE_API_AVAILABLE:
            try:
                self.app = fx.activeApplication()
            except:
                pass
    
    def get_software_name(self) -> str:
        return "Silhouette"
    
    def get_software_version(self) -> str:
        if SILHOUETTE_API_AVAILABLE and self.app:
            try:
                return self.app.version()
            except:
                pass
        return "Unknown"
    
    def save_file(self, file_path: str, **kwargs) -> FileOperationResult:
        """Save Silhouette project"""
        try:
            if not self.validate_path(file_path):
                return FileOperationResult(success=False, message="Invalid path")
            
            if kwargs.get('auto_version', self.config.auto_version):
                file_path = self.get_versioned_path(file_path)
            
            current_file = self.get_current_file()
            if current_file and kwargs.get('backup', self.config.backup_enabled):
                self.create_backup(current_file)
            
            if SILHOUETTE_API_AVAILABLE and self.app:
                # Use Silhouette API
                project = self.app.project
                project.save(file_path)
                
                # Collect Silhouette-specific metadata
                session = project.currentSession
                metadata = {
                    'frame_range': f"{session.startFrame}-{session.endFrame}",
                    'fps': session.frameRate,
                    'width': session.width,
                    'height': session.height,
                    'sessions_count': len(project.sessions),
                    'objects_count': len(session.objects),
                    **kwargs.get('metadata', {})
                }
            else:
                metadata = kwargs.get('metadata', {})
            
            self.save_metadata(file_path, metadata)
            
            result = FileOperationResult(
                success=True,
                path=file_path,
                message="Silhouette project saved successfully",
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
        """Load Silhouette project"""
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
            
            if SILHOUETTE_API_AVAILABLE and self.app:
                project = self.app.project
                
                if import_mode:
                    # Import into current project
                    session = project.currentSession
                    # Silhouette import would depend on what you're importing
                    # (shapes, sessions, etc.)
                    self.logger.warning("Import mode not fully implemented for Silhouette")
                else:
                    # Open new project
                    self.app.openProject(file_path)
                    self.logger.info(f"Opened: {file_path}")
            
            result = FileOperationResult(
                success=True,
                path=file_path,
                message="Silhouette project loaded successfully"
            )
            
            self._last_operation = result
            return result
            
        except Exception as e:
            result = FileOperationResult(success=False, message=str(e))
            self._last_operation = result
            self.logger.error(f"Load failed: {e}")
            return result
    
    def get_current_file(self) -> Optional[str]:
        """Get currently open Silhouette project"""
        if SILHOUETTE_API_AVAILABLE and self.app:
            try:
                project = self.app.project
                return project.path if hasattr(project, 'path') else None
            except:
                pass
        return None