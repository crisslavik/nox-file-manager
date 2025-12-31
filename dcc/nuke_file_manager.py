# dcc/nuke_file_manager.py
"""
Foundry Nuke file manager implementation
"""

import nuke
from core.file_manager import BaseFileManager, FileOperationResult, FileManagerConfig

class NukeFileManager(BaseFileManager):
    
    def get_software_name(self) -> str:
        return "Nuke"
    
    def get_software_version(self) -> str:
        return nuke.NUKE_VERSION_STRING
    
    def save_file(self, file_path: str, **kwargs) -> FileOperationResult:
        """Save Nuke script"""
        try:
            # Validate path
            if not self.validate_path(file_path):
                return FileOperationResult(
                    success=False,
                    message="Invalid file path"
                )
            
            # Handle versioning
            if kwargs.get('auto_version', self.config.auto_version):
                file_path = self.get_versioned_path(file_path)
            
            # Create backup
            current_file = self.get_current_file()
            if current_file and kwargs.get('backup', self.config.backup_enabled):
                self.create_backup(current_file)
            
            # Save the file
            nuke.scriptSaveAs(file_path, overwrite=1)
            
            # Save metadata
            metadata = {
                'frame_range': f"{nuke.root().firstFrame()}-{nuke.root().lastFrame()}",
                'fps': nuke.root()['fps'].value(),
                'format': nuke.root().format().name(),
                'nodes_count': len(nuke.allNodes()),
                **kwargs.get('metadata', {})
            }
            self.save_metadata(file_path, metadata)
            
            result = FileOperationResult(
                success=True,
                path=file_path,
                message=f"Script saved successfully",
                metadata=metadata
            )
            
            self._last_operation = result
            self.logger.info(f"Saved: {file_path}")
            return result
            
        except Exception as e:
            result = FileOperationResult(
                success=False,
                message=f"Save failed: {str(e)}"
            )
            self._last_operation = result
            self.logger.error(f"Save failed: {e}")
            return result
    
    def load_file(self, file_path: str, **kwargs) -> FileOperationResult:
        """Load Nuke script"""
        try:
            if not os.path.exists(file_path):
                return FileOperationResult(
                    success=False,
                    message=f"File not found: {file_path}"
                )
            
            # Load metadata if validation enabled
            if self.config.validate_on_load:
                metadata = self.load_metadata(file_path)
                if metadata:
                    self.logger.info(f"Loaded metadata: {metadata}")
            
            # Clear current script or load as new
            if kwargs.get('clear_current', True):
                nuke.scriptClear()
            
            nuke.scriptOpen(file_path)
            
            result = FileOperationResult(
                success=True,
                path=file_path,
                message="Script loaded successfully"
            )
            
            self._last_operation = result
            self.logger.info(f"Loaded: {file_path}")
            return result
            
        except Exception as e:
            result = FileOperationResult(
                success=False,
                message=f"Load failed: {str(e)}"
            )
            self._last_operation = result
            self.logger.error(f"Load failed: {e}")
            return result
    
    def get_current_file(self) -> Optional[str]:
        """Get currently open Nuke script"""
        return nuke.root().name()

# Initialize in Nuke's menu.py or init.py
def initialize_nuke_file_manager():
    """Initialize file manager in Nuke"""
    global nox_file_manager
    nox_file_manager = NukeFileManager()
    
    # Add to Nuke menu
    menubar = nuke.menu('Nuke')
    nox_menu = menubar.addMenu('NOX')
    
    nox_menu.addCommand('Save Versioned', 
                        lambda: nox_file_manager.save_file(
                            nox_file_manager.get_current_file(),
                            auto_version=True
                        ))
    
    nox_menu.addCommand('Load with Validation',
                        lambda: nox_file_manager.load_file(
                            nuke.getFilename('Load Script', '*.nk')
                        ))