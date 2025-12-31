# install.py
"""
NOX File Manager Unified Installer
Installs file management system across all DCC applications
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import json

class Colors:
    """Terminal colors for pretty output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class NOXInstaller:
    """Unified installer for NOX File Manager"""
    
    def __init__(self):
        self.system = platform.system()
        self.install_root = Path(__file__).parent.absolute()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        
        # Installation paths for each DCC
        self.dcc_paths = self._get_dcc_paths()
        
        # Track installation status
        self.installed_dccs = []
        self.failed_dccs = []
    
    def _get_dcc_paths(self) -> Dict[str, Dict[str, str]]:
        """Get installation paths for each DCC based on OS"""
        home = Path.home()
        
        if self.system == "Linux":
            return {
                'nuke': {
                    'name': 'Foundry Nuke',
                    'path': home / '.nuke',
                    'python_path': home / '.nuke/python',
                    'menu_file': home / '.nuke/menu.py',
                    'init_file': home / '.nuke/init.py'
                },
                'houdini': {
                    'name': 'SideFX Houdini',
                    'path': home / 'houdini20.5',  # Adjust version as needed
                    'python_path': home / 'houdini20.5/scripts/python',
                    'pythonrc': home / 'houdini20.5/scripts/pythonrc.py',
                    '456': home / 'houdini20.5/scripts/456.py'
                },
                'maya': {
                    'name': 'Autodesk Maya',
                    'path': home / 'maya/2024',  # Adjust version
                    'scripts_path': home / 'maya/2024/scripts',
                    'userSetup': home / 'maya/2024/scripts/userSetup.py'
                },
                'blender': {
                    'name': 'Blender',
                    'path': home / '.config/blender',  # Version agnostic
                    'addons_path': None,  # Will be detected
                    'scripts_path': None
                },
                'mocha': {
                    'name': 'Mocha Pro',
                    'path': home / '.mocha',
                    'scripts_path': home / '.mocha/scripts'
                },
                'silhouette': {
                    'name': 'Silhouette',
                    'path': home / '.silhouette',
                    'scripts_path': home / '.silhouette/scripts'
                },
                '3dequalizer': {
                    'name': '3DEqualizer',
                    'path': home / '.3de4',
                    'scripts_path': home / '.3de4/scripts'
                },
                'substance_painter': {
                    'name': 'Substance Painter',
                    'path': home / '.local/share/Allegorithmic/Substance Painter',
                    'scripts_path': home / '.local/share/Allegorithmic/Substance Painter/python'
                }
            }
        
        elif self.system == "Windows":
            appdata = Path(os.getenv('APPDATA'))
            documents = Path(os.getenv('USERPROFILE')) / 'Documents'
            
            return {
                'nuke': {
                    'name': 'Foundry Nuke',
                    'path': home / '.nuke',
                    'python_path': home / '.nuke/python',
                    'menu_file': home / '.nuke/menu.py',
                    'init_file': home / '.nuke/init.py'
                },
                'houdini': {
                    'name': 'SideFX Houdini',
                    'path': documents / 'houdini20.5',
                    'python_path': documents / 'houdini20.5/scripts/python',
                    'pythonrc': documents / 'houdini20.5/scripts/pythonrc.py',
                    '456': documents / 'houdini20.5/scripts/456.py'
                },
                'maya': {
                    'name': 'Autodesk Maya',
                    'path': documents / 'maya/2024',
                    'scripts_path': documents / 'maya/2024/scripts',
                    'userSetup': documents / 'maya/2024/scripts/userSetup.py'
                },
                'blender': {
                    'name': 'Blender',
                    'path': appdata / 'Blender Foundation/Blender',
                    'addons_path': None,
                    'scripts_path': None
                },
                'mocha': {
                    'name': 'Mocha Pro',
                    'path': appdata / 'Imagineer Systems Ltd/Mocha Pro',
                    'scripts_path': appdata / 'Imagineer Systems Ltd/Mocha Pro/scripts'
                },
                'silhouette': {
                    'name': 'Silhouette',
                    'path': appdata / 'Silhouette',
                    'scripts_path': appdata / 'Silhouette/scripts'
                },
                '3dequalizer': {
                    'name': '3DEqualizer',
                    'path': documents / '3DEqualizer',
                    'scripts_path': documents / '3DEqualizer/scripts'
                },
                'substance_painter': {
                    'name': 'Substance Painter',
                    'path': documents / 'Adobe/Adobe Substance 3D Painter',
                    'scripts_path': documents / 'Adobe/Adobe Substance 3D Painter/python'
                }
            }
        
        elif self.system == "Darwin":  # macOS
            return {
                'nuke': {
                    'name': 'Foundry Nuke',
                    'path': home / '.nuke',
                    'python_path': home / '.nuke/python',
                    'menu_file': home / '.nuke/menu.py',
                    'init_file': home / '.nuke/init.py'
                },
                'houdini': {
                    'name': 'SideFX Houdini',
                    'path': home / 'Library/Preferences/houdini/20.5',
                    'python_path': home / 'Library/Preferences/houdini/20.5/scripts/python',
                    'pythonrc': home / 'Library/Preferences/houdini/20.5/scripts/pythonrc.py',
                    '456': home / 'Library/Preferences/houdini/20.5/scripts/456.py'
                },
                'maya': {
                    'name': 'Autodesk Maya',
                    'path': home / 'Library/Preferences/Autodesk/maya/2024',
                    'scripts_path': home / 'Library/Preferences/Autodesk/maya/2024/scripts',
                    'userSetup': home / 'Library/Preferences/Autodesk/maya/2024/scripts/userSetup.py'
                },
                'blender': {
                    'name': 'Blender',
                    'path': home / 'Library/Application Support/Blender',
                    'addons_path': None,
                    'scripts_path': None
                },
                'mocha': {
                    'name': 'Mocha Pro',
                    'path': home / 'Library/Application Support/Imagineer Systems Ltd',
                    'scripts_path': home / 'Library/Application Support/Imagineer Systems Ltd/scripts'
                },
                'silhouette': {
                    'name': 'Silhouette',
                    'path': home / 'Library/Application Support/Silhouette',
                    'scripts_path': home / 'Library/Application Support/Silhouette/scripts'
                },
                '3dequalizer': {
                    'name': '3DEqualizer',
                    'path': home / 'Library/Preferences/3DE4',
                    'scripts_path': home / 'Library/Preferences/3DE4/scripts'
                },
                'substance_painter': {
                    'name': 'Substance Painter',
                    'path': home / 'Library/Application Support/Adobe/Adobe Substance 3D Painter',
                    'scripts_path': home / 'Library/Application Support/Adobe/Adobe Substance 3D Painter/python'
                }
            }
        
        return {}
    
    def print_header(self):
        """Print installer header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("=" * 60)
        print("  NOX VFX - File Manager Unified Installer")
        print("=" * 60)
        print(f"{Colors.ENDC}")
        print(f"System: {Colors.OKBLUE}{self.system}{Colors.ENDC}")
        print(f"Python: {Colors.OKBLUE}{self.python_version}{Colors.ENDC}")
        print(f"Install Root: {Colors.OKBLUE}{self.install_root}{Colors.ENDC}\n")
    
    def check_dependencies(self) -> bool:
        """Check if required Python packages are installed"""
        print(f"{Colors.BOLD}Checking dependencies...{Colors.ENDC}")
        
        required = ['PySide6']
        missing = []
        
        for package in required:
            try:
                __import__(package)
                print(f"  ✓ {package} {Colors.OKGREEN}found{Colors.ENDC}")
            except ImportError:
                print(f"  ✗ {package} {Colors.FAIL}missing{Colors.ENDC}")
                missing.append(package)
        
        if missing:
            print(f"\n{Colors.WARNING}Missing dependencies: {', '.join(missing)}{Colors.ENDC}")
            response = input("Install missing dependencies? (y/n): ")
            if response.lower() == 'y':
                return self.install_dependencies(missing)
            return False
        
        print(f"{Colors.OKGREEN}All dependencies satisfied!{Colors.ENDC}\n")
        return True
    
    def install_dependencies(self, packages: List[str]) -> bool:
        """Install missing Python packages"""
        print(f"\n{Colors.BOLD}Installing dependencies...{Colors.ENDC}")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", *packages
            ])
            print(f"{Colors.OKGREEN}Dependencies installed successfully!{Colors.ENDC}\n")
            return True
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}Failed to install dependencies: {e}{Colors.ENDC}")
            return False
    
    def detect_installed_dccs(self) -> List[str]:
        """Detect which DCCs are installed"""
        print(f"{Colors.BOLD}Detecting installed DCCs...{Colors.ENDC}")
        
        installed = []
        
        for dcc_key, dcc_info in self.dcc_paths.items():
            if dcc_info['path'].exists():
                print(f"  ✓ {dcc_info['name']} {Colors.OKGREEN}found{Colors.ENDC}")
                installed.append(dcc_key)
            else:
                print(f"  ✗ {dcc_info['name']} {Colors.WARNING}not found{Colors.ENDC}")
        
        print()
        return installed
    
    def install_core_modules(self, dcc_key: str) -> bool:
        """Install core modules (file_manager, ui, etc.) to DCC"""
        dcc_info = self.dcc_paths[dcc_key]
        
        try:
            # Determine python path for this DCC
            if 'python_path' in dcc_info:
                python_path = dcc_info['python_path']
            elif 'scripts_path' in dcc_info:
                python_path = dcc_info['scripts_path']
            else:
                print(f"  {Colors.WARNING}No Python path defined for {dcc_info['name']}{Colors.ENDC}")
                return False
            
            # Create python path if it doesn't exist
            python_path.mkdir(parents=True, exist_ok=True)
            
            # Install NOX package
            nox_package_path = python_path / 'nox_file_manager'
            if nox_package_path.exists():
                shutil.rmtree(nox_package_path)
            
            nox_package_path.mkdir(exist_ok=True)
            
            # Copy core modules
            modules_to_copy = ['core', 'ui', 'dcc', 'config']
            
            for module in modules_to_copy:
                src = self.install_root / module
                dst = nox_package_path / module
                
                if src.exists():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                    print(f"    Copied {module}")
            
            # Create __init__.py
            init_file = nox_package_path / '__init__.py'
            init_file.write_text('"""NOX File Manager Package"""\n__version__ = "1.0.0"\n')
            
            return True
            
        except Exception as e:
            print(f"  {Colors.FAIL}Failed to install core modules: {e}{Colors.ENDC}")
            return False
    
    def install_nuke(self) -> bool:
        """Install NOX File Manager for Nuke"""
        print(f"\n{Colors.BOLD}Installing for Nuke...{Colors.ENDC}")
        
        dcc_info = self.dcc_paths['nuke']
        
        try:
            # Install core modules
            if not self.install_core_modules('nuke'):
                return False
            
            # Install Nuke-specific integration
            nuke_integration = self.install_root / 'integrations/nuke'
            
            # Copy menu.py
            menu_src = nuke_integration / 'menu.py'
            menu_dst = dcc_info['menu_file']
            
            if menu_dst.exists():
                # Backup existing
                backup = menu_dst.with_suffix('.py.backup')
                shutil.copy2(menu_dst, backup)
                print(f"  Backed up existing menu.py")
            
            # Append our code to menu.py
            nox_menu_code = menu_src.read_text()
            
            with open(menu_dst, 'a') as f:
                f.write("\n\n# NOX File Manager Integration\n")
                f.write(nox_menu_code)
            
            print(f"  {Colors.OKGREEN}Installed Nuke integration{Colors.ENDC}")
            return True
            
        except Exception as e:
            print(f"  {Colors.FAIL}Failed: {e}{Colors.ENDC}")
            return False
    
    def install_houdini(self) -> bool:
        """Install NOX File Manager for Houdini"""
        print(f"\n{Colors.BOLD}Installing for Houdini...{Colors.ENDC}")
        
        dcc_info = self.dcc_paths['houdini']
        
        try:
            # Install core modules
            if not self.install_core_modules('houdini'):
                return False
            
            # Install Houdini-specific integration
            houdini_integration = self.install_root / 'integrations/houdini'
            
            # Copy 456.py
            init456_src = houdini_integration / '456.py'
            init456_dst = dcc_info['456']
            
            init456_dst.parent.mkdir(parents=True, exist_ok=True)
            
            if init456_dst.exists():
                backup = init456_dst.with_suffix('.py.backup')
                shutil.copy2(init456_dst, backup)
                print(f"  Backed up existing 456.py")
            
            # Append our code
            nox_code = init456_src.read_text()
            
            with open(init456_dst, 'a') as f:
                f.write("\n\n# NOX File Manager Integration\n")
                f.write(nox_code)
            
            print(f"  {Colors.OKGREEN}Installed Houdini integration{Colors.ENDC}")
            return True
            
        except Exception as e:
            print(f"  {Colors.FAIL}Failed: {e}{Colors.ENDC}")
            return False
    
    def install_maya(self) -> bool:
        """Install NOX File Manager for Maya"""
        print(f"\n{Colors.BOLD}Installing for Maya...{Colors.ENDC}")
        
        dcc_info = self.dcc_paths['maya']
        
        try:
            # Install core modules
            if not self.install_core_modules('maya'):
                return False
            
            # Install Maya-specific integration
            maya_integration = self.install_root / 'integrations/maya'
            
            # Copy userSetup.py
            usersetup_src = maya_integration / 'userSetup.py'
            usersetup_dst = dcc_info['userSetup']
            
            usersetup_dst.parent.mkdir(parents=True, exist_ok=True)
            
            if usersetup_dst.exists():
                backup = usersetup_dst.with_suffix('.py.backup')
                shutil.copy2(usersetup_dst, backup)
                print(f"  Backed up existing userSetup.py")
            
            # Append our code
            nox_code = usersetup_src.read_text()
            
            with open(usersetup_dst, 'a') as f:
                f.write("\n\n# NOX File Manager Integration\n")
                f.write(nox_code)
            
            print(f"  {Colors.OKGREEN}Installed Maya integration{Colors.ENDC}")
            return True
            
        except Exception as e:
            print(f"  {Colors.FAIL}Failed: {e}{Colors.ENDC}")
            return False
    
    def install_blender(self) -> bool:
        """Install NOX File Manager for Blender"""
        print(f"\n{Colors.BOLD}Installing for Blender...{Colors.ENDC}")
        
        dcc_info = self.dcc_paths['blender']
        
        try:
            # Find Blender version folders
            blender_root = dcc_info['path']
            if not blender_root.exists():
                print(f"  {Colors.WARNING}Blender config path not found{Colors.ENDC}")
                return False
            
            # Find most recent version
            version_dirs = [d for d in blender_root.iterdir() if d.is_dir() and d.name[0].isdigit()]
            if not version_dirs:
                print(f"  {Colors.WARNING}No Blender version found{Colors.ENDC}")
                return False
            
            latest_version = sorted(version_dirs)[-1]
            addons_path = latest_version / 'scripts/addons'
            addons_path.mkdir(parents=True, exist_ok=True)
            
            print(f"  Installing to Blender {latest_version.name}")
            
            # Create addon package
            addon_path = addons_path / 'nox_file_manager'
            if addon_path.exists():
                shutil.rmtree(addon_path)
            
            addon_path.mkdir(exist_ok=True)
            
            # Copy core modules
            modules = ['core', 'ui', 'dcc', 'config']
            for module in modules:
                src = self.install_root / module
                dst = addon_path / module
                if src.exists():
                    shutil.copytree(src, dst)
            
            # Copy Blender integration
            blender_integration = self.install_root / 'integrations/blender/__init__.py'
            shutil.copy2(blender_integration, addon_path / '__init__.py')
            
            print(f"  {Colors.OKGREEN}Installed Blender addon{Colors.ENDC}")
            print(f"  {Colors.WARNING}Remember to enable the addon in Blender preferences{Colors.ENDC}")
            return True
            
        except Exception as e:
            print(f"  {Colors.FAIL}Failed: {e}{Colors.ENDC}")
            return False
    
    def install_for_dcc(self, dcc_key: str) -> bool:
        """Install for specific DCC"""
        installers = {
            'nuke': self.install_nuke,
            'houdini': self.install_houdini,
            'maya': self.install_maya,
            'blender': self.install_blender,
            # Add others as needed
        }
        
        if dcc_key in installers:
            return installers[dcc_key]()
        else:
            print(f"  {Colors.WARNING}Installer not yet implemented for {dcc_key}{Colors.ENDC}")
            return False
    
    def run(self):
        """Run the installer"""
        self.print_header()
        
        # Check dependencies
        if not self.check_dependencies():
            print(f"{Colors.FAIL}Cannot proceed without dependencies{Colors.ENDC}")
            return
        
        # Detect installed DCCs
        installed_dccs = self.detect_installed_dccs()
        
        if not installed_dccs:
            print(f"{Colors.WARNING}No supported DCCs found{Colors.ENDC}")
            return
        
        # Ask which DCCs to install for
        print(f"{Colors.BOLD}Select DCCs to install for:{Colors.ENDC}")
        print("  a) All detected DCCs")
        for i, dcc in enumerate(installed_dccs, 1):
            print(f"  {i}) {self.dcc_paths[dcc]['name']}")
        print("  0) Cancel")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '0':
            print("Installation cancelled")
            return
        
        dccs_to_install = []
        
        if choice.lower() == 'a':
            dccs_to_install = installed_dccs
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(installed_dccs):
                    dccs_to_install = [installed_dccs[idx]]
                else:
                    print(f"{Colors.FAIL}Invalid choice{Colors.ENDC}")
                    return
            except ValueError:
                print(f"{Colors.FAIL}Invalid choice{Colors.ENDC}")
                return
        
        # Install for selected DCCs
        print(f"\n{Colors.BOLD}Installing for {len(dccs_to_install)} DCC(s)...{Colors.ENDC}\n")
        
        for dcc in dccs_to_install:
            if self.install_for_dcc(dcc):
                self.installed_dccs.append(dcc)
            else:
                self.failed_dccs.append(dcc)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print installation summary"""
        print(f"\n{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
        print(f"{Colors.BOLD}Installation Summary{Colors.ENDC}")
        print(f"{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")
        
        if self.installed_dccs:
            print(f"{Colors.OKGREEN}Successfully installed for:{Colors.ENDC}")
            for dcc in self.installed_dccs:
                print(f"  ✓ {self.dcc_paths[dcc]['name']}")
        
        if self.failed_dccs:
            print(f"\n{Colors.FAIL}Failed to install for:{Colors.ENDC}")
            for dcc in self.failed_dccs:
                print(f"  ✗ {self.dcc_paths[dcc]['name']}")
        
        print(f"\n{Colors.BOLD}Next Steps:{Colors.ENDC}")
        print("  1. Restart your DCC applications")
        print("  2. Look for 'NOX' menu or panel")
        print("  3. Configure paths in config/nox_pipeline.yaml")
        print()

if __name__ == "__main__":
    installer = NOXInstaller()
    installer.run()