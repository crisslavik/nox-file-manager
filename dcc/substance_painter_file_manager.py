# dcc/substance_painter_file_manager.py
"""
Substance Painter file manager implementation
"""

import os
from typing import Optional

# Substance Painter API
try:
    import substance_painter as sp
    from substance_painter import project
    SP_API_AVAILABLE = True
except ImportError:
    SP_API_AVAILABLE = False

from core.file_manager import BaseFileManager, FileOperationResult

class SubstancePainterFileManager(BaseFileManager):
    
    def get_software_name(self) -> str:
        return "Substance Painter"
    
    def get_software_version(self) -> str:
        if SP_API_AVAILABLE:
            try:
                return sp.application.version_info()
            except:
                pass
        return "Unknown"
    
    def save_file(self, file_path: str, **kwargs) -> FileOperationResult:
        """Save Substance Painter project"""
        try:
            if not self.validate_path(file_path):
                return FileOperationResult(success=False, message="Invalid path")
            
            if kwargs.get('auto_version', self.config.auto_version):
                file_path = self.get_versioned_path(file_path)
            
            current_file = self.get_current_file()
            if current_file and kwargs.get('backup', self.config.backup_enabled):
                self.create_backup(current_file)
            
            if SP_API_AVAILABLE:
                # Check if project is open
                if not project.is_open():
                    return FileOperationResult(
                        success=False,
                        message="No project open"
                    )
                
                # Save project
                project.save_as(file_path)
                
                # Collect Substance Painter metadata
                metadata = {
                    'mesh_name': project.Mesh.name() if project.Mesh else "Unknown",
                    'texture_sets': len(project.list_texture_sets()),
                    'materials': len(project.list_materials()),
                    'shader': project.get_shader_name(),
                    **kwargs.get('metadata', {})
                }
            else:
                metadata = kwargs.get('metadata', {})
            
            self.save_metadata(file_path, metadata)
            
            result = FileOperationResult(
                success=True,
                path=file_path,
                message="Substance Painter project saved successfully",
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
        """Load Substance Painter project"""
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
            
            if SP_API_AVAILABLE:
                # Close current project if open
                if project.is_open():
                    project.close()
                
                # Open project
                project.open(file_path)
                self.logger.info(f"Opened: {file_path}")
            
            result = FileOperationResult(
                success=True,
                path=file_path,
                message="Substance Painter project loaded successfully"
            )
            
            self._last_operation = result
            return result
            
        except Exception as e:
            result = FileOperationResult(success=False, message=str(e))
            self._last_operation = result
            self.logger.error(f"Load failed: {e}")
            return result
    
    def get_current_file(self) -> Optional[str]:
        """Get currently open Substance Painter project"""
        if SP_API_AVAILABLE:
            try:
                if project.is_open():
                    return project.file_path()
            except:
                pass
        return None
    
    def export_textures(self, export_path: str, export_preset: str = "PBR Metallic Roughness") -> FileOperationResult:
        """Export textures from current project"""
        try:
            if not SP_API_AVAILABLE:
                return FileOperationResult(
                    success=False,
                    message="Substance Painter API not available"
                )
            
            if not project.is_open():
                return FileOperationResult(
                    success=False,
                    message="No project open"
                )
            
            # Export textures
            export_result = project.export_project_textures(
                export_path,
                export_preset
            )
            
            return FileOperationResult(
                success=True,
                path=export_path,
                message="Textures exported successfully"
            )
            
        except Exception as e:
            return FileOperationResult(success=False, message=str(e))