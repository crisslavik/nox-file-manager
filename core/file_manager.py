# core/file_manager.py
"""
Core file manager that provides unified load/save operations
Independent of any specific DCC application
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

class FileOperationResult:
    """Result object for file operations"""
    def __init__(self, success: bool, path: str = "", message: str = "", metadata: Dict = None):
        self.success = success
        self.path = path
        self.message = message
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

class FileManagerConfig:
    """Configuration for file manager"""
    def __init__(self, config_path: Optional[str] = None):
        self.project_root = os.getenv('NOX_PROJECT_ROOT', '/mnt/projects')
        self.auto_version = True
        self.backup_enabled = True
        self.backup_count = 5
        self.validate_on_load = True
        self.metadata_enabled = True
        
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
    
    def _load_config(self, path: str):
        with open(path, 'r') as f:
            config = json.load(f)
            self.__dict__.update(config)

class BaseFileManager(ABC):
    """Base class for all DCC-specific file managers"""
    
    def __init__(self, config: Optional[FileManagerConfig] = None):
        self.config = config or FileManagerConfig()
        self.logger = self._setup_logger()
        self._last_operation: Optional[FileOperationResult] = None
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(f'NOX.FileManager.{self.__class__.__name__}')
        logger.setLevel(logging.DEBUG)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def get_versioned_path(self, base_path: str) -> str:
        """Generate next version number for file"""
        if not self.config.auto_version:
            return base_path
        
        path = Path(base_path)
        stem = path.stem
        suffix = path.suffix
        directory = path.parent
        
        # Extract version number if exists
        import re
        version_pattern = r'_v(\d+)$'
        match = re.search(version_pattern, stem)
        
        if match:
            current_version = int(match.group(1))
            base_name = stem[:match.start()]
        else:
            current_version = 0
            base_name = stem
        
        # Find next available version
        version = current_version + 1
        while True:
            new_path = directory / f"{base_name}_v{version:03d}{suffix}"
            if not new_path.exists():
                return str(new_path)
            version += 1
    
    def create_backup(self, file_path: str) -> bool:
        """Create backup of existing file"""
        if not self.config.backup_enabled or not os.path.exists(file_path):
            return True
        
        try:
            path = Path(file_path)
            backup_dir = path.parent / '.backups'
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{path.stem}_{timestamp}{path.suffix}"
            backup_path = backup_dir / backup_name
            
            import shutil
            shutil.copy2(file_path, backup_path)
            
            # Clean old backups
            self._cleanup_old_backups(backup_dir, path.stem)
            
            self.logger.info(f"Backup created: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False
    
    def _cleanup_old_backups(self, backup_dir: Path, base_name: str):
        """Keep only N most recent backups"""
        pattern = f"{base_name}_*"
        backups = sorted(backup_dir.glob(pattern), key=os.path.getmtime, reverse=True)
        
        for old_backup in backups[self.config.backup_count:]:
            try:
                old_backup.unlink()
                self.logger.debug(f"Removed old backup: {old_backup}")
            except Exception as e:
                self.logger.warning(f"Failed to remove old backup {old_backup}: {e}")
    
    def save_metadata(self, file_path: str, metadata: Dict[str, Any]):
        """Save metadata alongside the file"""
        if not self.config.metadata_enabled:
            return
        
        meta_path = Path(file_path).with_suffix('.meta.json')
        
        meta_data = {
            'file': os.path.basename(file_path),
            'saved_at': datetime.now().isoformat(),
            'software': self.get_software_name(),
            'version': self.get_software_version(),
            'user': os.getenv('USER', 'unknown'),
            'host': os.uname().nodename,
            **metadata
        }
        
        try:
            with open(meta_path, 'w') as f:
                json.dump(meta_data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save metadata: {e}")
    
    def load_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load metadata for a file"""
        meta_path = Path(file_path).with_suffix('.meta.json')
        
        if not meta_path.exists():
            return None
        
        try:
            with open(meta_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load metadata: {e}")
            return None
    
    def validate_path(self, file_path: str) -> bool:
        """Validate file path"""
        path = Path(file_path)
        
        # Check if within project root
        try:
            path.resolve().relative_to(Path(self.config.project_root).resolve())
        except ValueError:
            self.logger.warning(f"Path outside project root: {file_path}")
            return False
        
        # Check directory exists or can be created
        if not path.parent.exists():
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.logger.error(f"Cannot create directory: {e}")
                return False
        
        return True
    
    @abstractmethod
    def get_software_name(self) -> str:
        """Return the name of the DCC application"""
        pass
    
    @abstractmethod
    def get_software_version(self) -> str:
        """Return the version of the DCC application"""
        pass
    
    @abstractmethod
    def save_file(self, file_path: str, **kwargs) -> FileOperationResult:
        """Save current file/project"""
        pass
    
    @abstractmethod
    def load_file(self, file_path: str, **kwargs) -> FileOperationResult:
        """Load file/project"""
        pass
    
    @abstractmethod
    def get_current_file(self) -> Optional[str]:
        """Get currently open file path"""
        pass
    
    def get_last_operation(self) -> Optional[FileOperationResult]:
        """Get result of last file operation"""
        return self._last_operation