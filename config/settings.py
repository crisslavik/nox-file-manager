"""
NOX File Manager Settings
Configuration management for the file manager system
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class Settings:
    """Settings manager for NOX File Manager"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.settings = self._load_settings()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        # Try multiple locations
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'nox_pipeline.yaml'),
            os.path.expanduser('~/.nox/nox_pipeline.yaml'),
            '/etc/nox/nox_pipeline.yaml',
            os.environ.get('NOX_CONFIG_PATH', '')
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                return path
        
        # Return the first one as default (will be created if doesn't exist)
        return possible_paths[0]
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from YAML file"""
        default_settings = {
            'project_root': os.getenv('NOX_PROJECT_ROOT', '/mnt/projects'),
            'shotgrid': {
                'url': 'https://nox.shotgridstudio.com',
                'project_id': 123,
                'script_name': '',
                'api_key': ''
            },
            'file_manager': {
                'auto_version': True,
                'backup_enabled': True,
                'backup_count': 5,
                'validate_on_load': True,
                'metadata_enabled': True
            },
            'ui': {
                'theme': 'dark',
                'window_size': [1200, 800],
                'remember_last_location': True,
                'show_thumbnails': True
            },
            'path_templates': {
                'shot_work': '{project_root}/shots/{sequence}/{shot}/{step}/work/{software}/{shot}_{step}_v{version}.{ext}',
                'shot_publish': '{project_root}/shots/{sequence}/{shot}/{step}/publish/{software}/{shot}_{step}_v{version}.{ext}',
                'asset_work': '{project_root}/assets/{asset_type}/{asset}/{step}/work/{software}/{asset}_{step}_v{version}.{ext}',
                'asset_publish': '{project_root}/assets/{asset_type}/{asset}/{step}/publish/{software}/{asset}_{step}_v{version}.{ext}'
            },
            'software_extensions': {
                'nuke': 'nk',
                'houdini': 'hip',
                'maya': 'ma',
                'blender': 'blend',
                'mocha': 'mocha',
                'silhouette': 'sfx',
                '3dequalizer': '3de',
                'substance_painter': 'spp'
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded_settings = yaml.safe_load(f)
                    # Merge with defaults
                    return self._merge_settings(default_settings, loaded_settings)
            except Exception as e:
                print(f"Failed to load config from {self.config_path}: {e}")
        
        return default_settings
    
    def _merge_settings(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded settings with defaults"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value by key (supports dot notation)"""
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set setting value by key (supports dot notation)"""
        keys = key.split('.')
        settings = self.settings
        
        for k in keys[:-1]:
            if k not in settings:
                settings[k] = {}
            settings = settings[k]
        
        settings[keys[-1]] = value
    
    def save(self):
        """Save current settings to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                yaml.dump(self.settings, f, default_flow_style=False, indent=2)
            
            print(f"Settings saved to {self.config_path}")
            
        except Exception as e:
            print(f"Failed to save settings: {e}")
    
    def reload(self):
        """Reload settings from file"""
        self.settings = self._load_settings()

# Global settings instance
settings = Settings()