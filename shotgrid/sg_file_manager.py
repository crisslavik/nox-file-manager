# shotgrid/sg_file_manager.py
"""
ShotGrid-integrated file manager that extends the base file manager
Handles publish, work files, and version tracking
"""

import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import shotgun_api3

from core.file_manager import BaseFileManager, FileOperationResult

class ShotGridFileManager:
    """
    Wrapper that adds ShotGrid functionality to any DCC file manager
    """
    
    def __init__(self, dcc_manager: BaseFileManager, sg_config: Dict[str, Any]):
        self.dcc_manager = dcc_manager
        self.logger = dcc_manager.logger
        
        # Initialize ShotGrid connection
        self.sg = shotgun_api3.Shotgun(
            sg_config['url'],
            sg_config.get('script_name'),
            sg_config.get('api_key'),
            login=sg_config.get('login'),
            password=sg_config.get('password')
        )
        
        self.project_id = sg_config.get('project_id')
        self.entity_type = None  # Shot, Asset, etc.
        self.entity_id = None
        self.task_id = None
        self.step_id = None
        
        # Path templates (similar to tk-core)
        self.templates = sg_config.get('templates', {})
    
    def set_context(self, entity_type: str, entity_id: int, 
                    task_id: Optional[int] = None, step_id: Optional[int] = None):
        """Set the current ShotGrid context"""
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.task_id = task_id
        self.step_id = step_id
        
        self.logger.info(f"SG Context: {entity_type}[{entity_id}] Task[{task_id}]")
    
    def get_context_from_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse file path to extract ShotGrid context
        Example: /projects/SHOW/shots/SQ010/SH0010/comp/work/comp_v001.nk
        """
        path = Path(file_path)
        parts = path.parts
        
        try:
            # This is a simplified example - adjust to your naming convention
            if 'shots' in parts:
                idx = parts.index('shots')
                sequence = parts[idx + 1]
                shot_code = parts[idx + 2]
                step = parts[idx + 3]  # comp, light, etc.
                
                # Query ShotGrid for entity
                shot = self.sg.find_one('Shot', 
                    [['code', 'is', shot_code]],
                    ['id', 'code', 'sg_sequence', 'tasks']
                )
                
                if shot:
                    # Find task for this step
                    task = self.sg.find_one('Task',
                        [
                            ['entity', 'is', shot],
                            ['step.Step.short_name', 'is', step]
                        ],
                        ['id', 'step']
                    )
                    
                    return {
                        'entity_type': 'Shot',
                        'entity_id': shot['id'],
                        'entity_code': shot['code'],
                        'task_id': task['id'] if task else None,
                        'step_id': task['step']['id'] if task and task['step'] else None
                    }
            
            elif 'assets' in parts:
                idx = parts.index('assets')
                asset_type = parts[idx + 1]
                asset_code = parts[idx + 2]
                step = parts[idx + 3]
                
                asset = self.sg.find_one('Asset',
                    [['code', 'is', asset_code]],
                    ['id', 'code', 'tasks']
                )
                
                if asset:
                    task = self.sg.find_one('Task',
                        [
                            ['entity', 'is', asset],
                            ['step.Step.short_name', 'is', step]
                        ],
                        ['id', 'step']
                    )
                    
                    return {
                        'entity_type': 'Asset',
                        'entity_id': asset['id'],
                        'entity_code': asset['code'],
                        'task_id': task['id'] if task else None,
                        'step_id': task['step']['id'] if task and task['step'] else None
                    }
        
        except Exception as e:
            self.logger.warning(f"Could not parse context from path: {e}")
        
        return None
    
    def get_work_file_path(self, filename: Optional[str] = None, 
                          version: Optional[int] = None) -> str:
        """
        Generate work file path based on ShotGrid context
        Uses path templates similar to Toolkit
        """
        if not self.entity_id or not self.task_id:
            raise ValueError("ShotGrid context not set")
        
        # Get entity and task info
        entity = self.sg.find_one(
            self.entity_type,
            [['id', 'is', self.entity_id]],
            ['code', 'sg_sequence.Sequence.code' if self.entity_type == 'Shot' else 'sg_asset_type']
        )
        
        task = self.sg.find_one('Task',
            [['id', 'is', self.task_id]],
            ['step.Step.short_name']
        )
        
        step_name = task['step']['short_name']
        
        # Build path based on entity type
        if self.entity_type == 'Shot':
            sequence = entity.get('sg_sequence.Sequence.code', 'SEQ')
            shot_code = entity['code']
            
            work_dir = os.path.join(
                self.dcc_manager.config.project_root,
                'shots',
                sequence,
                shot_code,
                step_name,
                'work',
                self.dcc_manager.get_software_name().lower()
            )
        else:  # Asset
            asset_type = entity.get('sg_asset_type', 'prop')
            asset_code = entity['code']
            
            work_dir = os.path.join(
                self.dcc_manager.config.project_root,
                'assets',
                asset_type,
                asset_code,
                step_name,
                'work',
                self.dcc_manager.get_software_name().lower()
            )
        
        # Create directory if needed
        os.makedirs(work_dir, exist_ok=True)
        
        # Generate filename
        if not filename:
            entity_code = entity['code']
            filename = f"{entity_code}_{step_name}"
        
        # Get file extension for DCC
        ext = self._get_file_extension()
        
        # Add version if specified
        if version:
            filename = f"{filename}_v{version:03d}{ext}"
        else:
            # Find next version
            filename = self._get_next_version_filename(work_dir, filename, ext)
        
        return os.path.join(work_dir, filename)
    
    def _get_file_extension(self) -> str:
        """Get appropriate file extension for current DCC"""
        software = self.dcc_manager.get_software_name().lower()
        
        extensions = {
            'nuke': '.nk',
            'houdini': '.hip',
            'maya': '.ma',
            'blender': '.blend',
            'mocha': '.mocha',
            'silhouette': '.sfx',
            '3dequalizer': '.3de',
            'substance painter': '.spp'
        }
        
        return extensions.get(software, '.file')
    
    def _get_next_version_filename(self, directory: str, base_name: str, ext: str) -> str:
        """Find next available version number"""
        import re
        
        version = 1
        existing_files = os.listdir(directory) if os.path.exists(directory) else []
        
        version_pattern = re.compile(rf"{re.escape(base_name)}_v(\d+){re.escape(ext)}")
        
        for filename in existing_files:
            match = version_pattern.match(filename)
            if match:
                file_version = int(match.group(1))
                version = max(version, file_version + 1)
        
        return f"{base_name}_v{version:03d}{ext}"
    
    def save_work_file(self, **kwargs) -> FileOperationResult:
        """Save work file with ShotGrid context"""
        try:
            # Auto-detect context from current file if not set
            current_file = self.dcc_manager.get_current_file()
            if current_file and not self.entity_id:
                context = self.get_context_from_path(current_file)
                if context:
                    self.set_context(
                        context['entity_type'],
                        context['entity_id'],
                        context['task_id'],
                        context['step_id']
                    )
            
            # Generate work file path
            file_path = self.get_work_file_path()
            
            # Save using DCC manager
            result = self.dcc_manager.save_file(file_path, **kwargs)
            
            if result.success:
                # Register work file in ShotGrid
                self._register_work_file(file_path, result.metadata)
            
            return result
            
        except Exception as e:
            self.logger.error(f"SG save work file failed: {e}")
            return FileOperationResult(success=False, message=str(e))
    
    def _register_work_file(self, file_path: str, metadata: Dict[str, Any]):
        """Register work file in ShotGrid"""
        try:
            # Check if PublishedFile already exists
            existing = self.sg.find_one('PublishedFile',
                [
                    ['path', 'is', {'local_path': file_path}],
                    ['task', 'is', {'type': 'Task', 'id': self.task_id}]
                ],
                ['id']
            )
            
            published_file_type = self.sg.find_one('PublishedFileType',
                [['code', 'is', 'Work File']],
                ['id']
            )
            
            if not published_file_type:
                # Create Work File type if doesn't exist
                published_file_type = self.sg.create('PublishedFileType', {
                    'code': 'Work File'
                })
            
            data = {
                'code': os.path.basename(file_path),
                'path': {'local_path': file_path},
                'task': {'type': 'Task', 'id': self.task_id},
                'entity': {'type': self.entity_type, 'id': self.entity_id},
                'published_file_type': published_file_type,
                'version_number': self._extract_version_from_path(file_path),
                'description': f"Work file from {self.dcc_manager.get_software_name()}",
                'sg_status_list': 'na'  # Work files are not for review
            }
            
            if existing:
                self.sg.update('PublishedFile', existing['id'], data)
                self.logger.info(f"Updated PublishedFile: {existing['id']}")
            else:
                pf = self.sg.create('PublishedFile', data)
                self.logger.info(f"Created PublishedFile: {pf['id']}")
        
        except Exception as e:
            self.logger.warning(f"Failed to register work file in SG: {e}")
    
    def publish(self, file_path: Optional[str] = None, 
                publish_name: Optional[str] = None,
                version_number: Optional[int] = None,
                thumbnail_path: Optional[str] = None,
                description: str = "",
                **kwargs) -> FileOperationResult:
        """
        Publish current work to ShotGrid
        Creates PublishedFile and Version entries
        """
        try:
            if not self.entity_id or not self.task_id:
                return FileOperationResult(
                    success=False,
                    message="ShotGrid context not set"
                )
            
            # Use current file if not specified
            if not file_path:
                file_path = self.dcc_manager.get_current_file()
                if not file_path:
                    return FileOperationResult(
                        success=False,
                        message="No file open to publish"
                    )
            
            # Extract version number
            if not version_number:
                version_number = self._extract_version_from_path(file_path)
            
            # Generate publish path
            publish_path = self._get_publish_path(file_path, publish_name)
            
            # Copy file to publish location
            import shutil
            os.makedirs(os.path.dirname(publish_path), exist_ok=True)
            shutil.copy2(file_path, publish_path)
            
            # Create Version in ShotGrid
            version_data = {
                'code': publish_name or os.path.basename(publish_path),
                'entity': {'type': self.entity_type, 'id': self.entity_id},
                'sg_task': {'type': 'Task', 'id': self.task_id},
                'sg_version_number': version_number,
                'description': description or f"Published from {self.dcc_manager.get_software_name()}",
                'user': self._get_current_user(),
                'sg_path_to_frames': publish_path,
                'sg_status_list': 'rev'  # Pending review
            }
            
            if thumbnail_path and os.path.exists(thumbnail_path):
                version_data['image'] = thumbnail_path
            
            sg_version = self.sg.create('Version', version_data)
            self.logger.info(f"Created Version: {sg_version['id']}")
            
            # Create PublishedFile
            published_file_type = self._get_published_file_type()
            
            pf_data = {
                'code': publish_name or os.path.basename(publish_path),
                'path': {'local_path': publish_path},
                'task': {'type': 'Task', 'id': self.task_id},
                'entity': {'type': self.entity_type, 'id': self.entity_id},
                'version': {'type': 'Version', 'id': sg_version['id']},
                'published_file_type': published_file_type,
                'version_number': version_number,
                'description': description,
                'sg_status_list': 'cmpt'  # Complete
            }
            
            published_file = self.sg.create('PublishedFile', pf_data)
            self.logger.info(f"Created PublishedFile: {published_file['id']}")
            
            result = FileOperationResult(
                success=True,
                path=publish_path,
                message=f"Published successfully: Version {version_number}",
                metadata={
                    'sg_version_id': sg_version['id'],
                    'sg_published_file_id': published_file['id'],
                    'version_number': version_number
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Publish failed: {e}")
            return FileOperationResult(success=False, message=str(e))
    
    def _get_publish_path(self, work_path: str, publish_name: Optional[str] = None) -> str:
        """Generate publish path from work path"""
        work_path = Path(work_path)
        
        # Replace 'work' with 'publish' in path
        parts = list(work_path.parts)
        if 'work' in parts:
            idx = parts.index('work')
            parts[idx] = 'publish'
        
        publish_dir = Path(*parts[:-1])  # Everything except filename
        
        if publish_name:
            filename = publish_name
        else:
            filename = work_path.name
        
        return str(publish_dir / filename)
    
    def _extract_version_from_path(self, file_path: str) -> int:
        """Extract version number from file path"""
        import re
        match = re.search(r'_v(\d+)', file_path)
        return int(match.group(1)) if match else 1
    
    def _get_published_file_type(self) -> Dict[str, Any]:
        """Get or create PublishedFileType for current DCC"""
        software = self.dcc_manager.get_software_name()
        
        pf_type = self.sg.find_one('PublishedFileType',
            [['code', 'is', software]],
            ['id', 'code']
        )
        
        if not pf_type:
            pf_type = self.sg.create('PublishedFileType', {'code': software})
        
        return pf_type
    
    def _get_current_user(self) -> Dict[str, Any]:
        """Get current ShotGrid user"""
        import getpass
        username = getpass.getuser()
        
        user = self.sg.find_one('HumanUser',
            [['login', 'is', username]],
            ['id', 'name']
        )
        
        if user:
            return {'type': 'HumanUser', 'id': user['id']}
        return None
    
    def get_latest_publish(self, published_file_type: Optional[str] = None) -> Optional[str]:
        """Get latest published file for current context"""
        if not self.entity_id:
            return None
        
        filters = [
            ['entity', 'is', {'type': self.entity_type, 'id': self.entity_id}],
            ['sg_status_list', 'is', 'cmpt']
        ]
        
        if self.task_id:
            filters.append(['task', 'is', {'type': 'Task', 'id': self.task_id}])
        
        if published_file_type:
            filters.append(['published_file_type.PublishedFileType.code', 'is', published_file_type])
        
        published_file = self.sg.find_one('PublishedFile',
            filters,
            ['path', 'version_number', 'code'],
            order=[{'field_name': 'version_number', 'direction': 'desc'}]
        )
        
        if published_file and published_file.get('path'):
            return published_file['path']['local_path']
        
        return None
    
    def load_latest_publish(self, published_file_type: Optional[str] = None, **kwargs) -> FileOperationResult:
        """Load latest published file"""
        publish_path = self.get_latest_publish(published_file_type)
        
        if not publish_path:
            return FileOperationResult(
                success=False,
                message="No published file found"
            )
        
        return self.dcc_manager.load_file(publish_path, **kwargs)