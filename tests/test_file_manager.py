"""
Test core file manager functionality
"""

import unittest
import tempfile
import os
from pathlib import Path

from core.file_manager import BaseFileManager, FileOperationResult, FileManagerConfig

class MockFileManager(BaseFileManager):
    """Mock file manager for testing"""
    
    def get_software_name(self) -> str:
        return "MockSoftware"
    
    def get_software_version(self) -> str:
        return "1.0.0"
    
    def save_file(self, file_path: str, **kwargs) -> FileOperationResult:
        # Mock save - create the file
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write("Mock file content")
            return FileOperationResult(success=True, path=file_path, message="Mock save successful")
        except Exception as e:
            return FileOperationResult(success=False, message=str(e))
    
    def load_file(self, file_path: str, **kwargs) -> FileOperationResult:
        # Mock load - check if file exists
        if os.path.exists(file_path):
            return FileOperationResult(success=True, path=file_path, message="Mock load successful")
        else:
            return FileOperationResult(success=False, message="File not found")
    
    def get_current_file(self) -> str:
        return "/mock/current/file.txt"

class TestFileManager(unittest.TestCase):
    """Test file manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = FileManagerConfig()
        self.config.project_root = self.temp_dir
        self.file_manager = MockFileManager(self.config)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_versioned_path(self):
        """Test versioned path generation"""
        # Test first version
        base_path = os.path.join(self.temp_dir, "test.txt")
        versioned = self.file_manager.get_versioned_path(base_path)
        self.assertTrue(versioned.endswith("_v001.txt"))
        
        # Create file and test next version
        Path(versioned).touch()
        next_version = self.file_manager.get_versioned_path(base_path)
        self.assertTrue(next_version.endswith("_v002.txt"))
    
    def test_backup_creation(self):
        """Test backup creation"""
        test_file = os.path.join(self.temp_dir, "test.txt")
        
        # Create original file
        with open(test_file, 'w') as f:
            f.write("original content")
        
        # Create backup
        result = self.file_manager.create_backup(test_file)
        self.assertTrue(result)
        
        # Check backup exists
        backup_dir = os.path.join(os.path.dirname(test_file), '.backups')
        self.assertTrue(os.path.exists(backup_dir))
        backups = os.listdir(backup_dir)
        self.assertEqual(len(backups), 1)
        self.assertTrue(backups[0].startswith('test_'))
    
    def test_metadata_save_load(self):
        """Test metadata save and load"""
        test_file = os.path.join(self.temp_dir, "test.txt")
        test_metadata = {"test_key": "test_value", "number": 42}
        
        # Save metadata
        self.file_manager.save_metadata(test_file, test_metadata)
        
        # Load metadata
        loaded_metadata = self.file_manager.load_metadata(test_file)
        self.assertEqual(loaded_metadata["test_key"], "test_value")
        self.assertEqual(loaded_metadata["number"], 42)
    
    def test_path_validation(self):
        """Test path validation"""
        # Valid path within project root
        valid_path = os.path.join(self.temp_dir, "subdir", "test.txt")
        self.assertTrue(self.file_manager.validate_path(valid_path))
        
        # Invalid path outside project root
        invalid_path = "/outside/project/root/test.txt"
        self.assertFalse(self.file_manager.validate_path(invalid_path))

if __name__ == '__main__':
    unittest.main()