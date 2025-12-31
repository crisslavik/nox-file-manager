# dcc/mocha_file_manager.py
"""
Mocha Pro file manager implementation
"""

import os
from typing import Optional

# Mocha uses Python API if available
try:
    import mocha
    MOCHA_API_AVAILABLE = True
except ImportError:
    MOCHA_API_AVAILABLE = False
    import subprocess

from core.file_manager import BaseFileManager, FileOperationResult

class MochaFileManager(BaseFileManager):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = None
        if MOCHA_API_AVAILABLE:
            try:
                self.app = mocha.app
            except:
                pass
    
    def get_software_name(self) -> str:
        return "Mocha"
    
    def get_software_version(self) -> str:
        if MOCHA_API_AVAILABLE and self.app:
            try:
                return self.app.version()
            except:
                pass
        return "Unknown"
    
    def save_file(self, file_path: str, **kwargs) -> FileOperationResult:
        """Save Mocha project"""
        try:
            if not self.validate_path(file_path):
                return FileOperationResult(success=False, message="Invalid path")
            
            if kwargs.get('auto_version', self.config.auto_version):
                file_path = self.get_versioned_path(file_path)
            
            current_file = self.get_current_file()
            if current_file and kwargs.get('backup', self.config.backup_enabled):
                self.create_backup(current_file)
            
            if MOCHA_API_AVAILABLE and self.app:
                # Use Mocha API
                project = self.app.project
                project.save_as(file_path)
                
                # Collect Mocha-specific metadata
                metadata = {
                    'frame_range': f"{project.start_frame}-{project.end_frame}",
                    'fps': project.frame_rate,
                    'width': project.width,
                    'height': project.height,
                    'pixel_aspect_ratio': project.pixel_aspect_ratio,
                    'layers_count': len(project.layers),
                    **kwargs.get('metadata', {})
                }
            else:
                # Fallback: use file operations or command line
                # This assumes Mocha can be controlled via command line or script
                metadata = kwargs.get('metadata', {})
            
            self.save_metadata(file_path, metadata)
            
            result = FileOperationResult(
                success=True,
                path=file_path,
                message="Mocha project saved successfully",
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
        """Load Mocha project"""
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
            
            if MOCHA_API_AVAILABLE and self.app:
                project = self.app.project
                
                if import_mode:
                    # Import/merge into current project
                    project.import_project(file_path)
                    self.logger.info(f"Imported: {file_path}")
                else:
                    # Open new project
                    self.app.open_project(file_path)
                    self.logger.info(f"Opened: {file_path}")
            else:
                # Fallback method
                self.logger.warning("Mocha API not available, using fallback method")
            
            result = FileOperationResult(
                success=True,
                path=file_path,
                message="Mocha project loaded successfully"
            )
            
            self._last_operation = result
            return result
            
        except Exception as e:
            result = FileOperationResult(success=False, message=str(e))
            self._last_operation = result
            self.logger.error(f"Load failed: {e}")
            return result
    
    def get_current_file(self) -> Optional[str]:
        """Get currently open Mocha project"""
        if MOCHA_API_AVAILABLE and self.app:
            try:
                project = self.app.project
                return project.path if project.path else None
            except:
                pass
        return None