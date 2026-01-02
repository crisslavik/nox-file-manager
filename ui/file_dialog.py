# ui/file_dialog.py
"""
Universal Qt6 File Load/Saver Dialog for NOX VFX
Works across all DCC applications
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QTreeWidget, QTreeWidgetItem, QComboBox,
    QCheckBox, QGroupBox, QSplitter, QTextEdit, QFileDialog,
    QHeaderView, QMessageBox, QApplication, QWidget, QRadioButton,
    QButtonGroup, QFrame
)
from PySide6.QtCore import Qt, Signal, QSize, QThread
from PySide6.QtGui import QIcon, QFont, QColor, QPixmap

class FileInfo:
    """Container for file information"""
    def __init__(self, path: str):
        self.path = path
        self.name = os.path.basename(path)
        self.size = os.path.getsize(path) if os.path.exists(path) else 0
        self.modified = datetime.fromtimestamp(os.path.getmtime(path)) if os.path.exists(path) else None
        self.version = self._extract_version()
        self.metadata = self._load_metadata()
    
    def _extract_version(self) -> int:
        """Extract version number from filename"""
        import re
        match = re.search(r'_v(\d+)', self.name)
        return int(match.group(1)) if match else 0
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata if exists"""
        meta_path = Path(self.path).with_suffix('.meta.json')
        if meta_path.exists():
            import json
            try:
                with open(meta_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def get_size_str(self) -> str:
        """Get human-readable file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.size < 1024.0:
                return f"{self.size:.1f} {unit}"
            self.size /= 1024.0
        return f"{self.size:.1f} TB"
    
    def get_date_str(self) -> str:
        """Get formatted date string"""
        if self.modified:
            return self.modified.strftime('%Y-%m-%d %H:%M:%S')
        return "Unknown"


class ThumbnailLoader(QThread):
    """Background thread for loading thumbnails"""
    thumbnail_loaded = Signal(str, QPixmap)
    
    def __init__(self, file_paths: List[str]):
        super().__init__()
        self.file_paths = file_paths
    
    def run(self):
        for path in self.file_paths:
            thumbnail = self._generate_thumbnail(path)
            if thumbnail:
                self.thumbnail_loaded.emit(path, thumbnail)
    
    def _generate_thumbnail(self, file_path: str) -> Optional[QPixmap]:
        """Generate or load thumbnail for file"""
        # Check for existing thumbnail
        thumb_path = Path(file_path).with_suffix('.thumb.jpg')
        if thumb_path.exists():
            return QPixmap(str(thumb_path))
        
        # TODO: Generate thumbnail based on file type
        return None


class NOXFileDialog(QDialog):
    """
    Universal file dialog for NOX VFX pipeline
    Supports both Load and Save operations across all DCCs
    """
    
    def __init__(self, 
                 mode: str = "load",  # "load" or "save"
                 dcc_name: str = "Unknown",
                 file_extensions: List[str] = None,
                 current_file: Optional[str] = None,
                 parent: QWidget = None):
        super().__init__(parent)
        
        self.mode = mode
        self.dcc_name = dcc_name
        self.file_extensions = file_extensions or [".file"]
        self.current_file = current_file
        self.selected_file: Optional[str] = None
        self.load_mode: str = "open"  # "open" or "import"
        
        # File operation options
        self.create_backup = True
        self.auto_version = True
        self.save_metadata = True
        
        self._setup_ui()
        self._connect_signals()
        self._load_recent_directories()
        
        # Load initial directory
        if current_file and os.path.exists(current_file):
            self._navigate_to_directory(os.path.dirname(current_file))
        else:
            self._navigate_to_directory(os.path.expanduser("~"))
    
    def _setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle(f"NOX {self.mode.capitalize()} - {self.dcc_name}")
        self.resize(1200, 800)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Pipeline navigation (for both load and save)
        if self.mode == "save":
            layout.addWidget(self._create_pipeline_navigation())
        else:
            # Top section: Path navigation (load mode only)
            layout.addWidget(self._create_navigation_section())
        
        # Main splitter: File browser and details
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._create_browser_section())
        splitter.addWidget(self._create_details_section())
        splitter.setSizes([800, 400])
        layout.addWidget(splitter)
        
        # Bottom section: Options and actions
        if self.mode == "save":
            layout.addWidget(self._create_save_options())
        else:
            layout.addWidget(self._create_options_section())
        layout.addWidget(self._create_actions_section())
        
        self.setLayout(layout)
        
        # Apply stylesheet
        self._apply_stylesheet()
    
    def _create_navigation_section(self) -> QWidget:
        """Create path navigation section"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Back/Forward buttons
        self.btn_back = QPushButton("←")
        self.btn_back.setFixedSize(30, 30)
        self.btn_back.setToolTip("Go back")
        layout.addWidget(self.btn_back)
        
        self.btn_forward = QPushButton("→")
        self.btn_forward.setFixedSize(30, 30)
        self.btn_forward.setToolTip("Go forward")
        layout.addWidget(self.btn_forward)
        
        self.btn_up = QPushButton("↑")
        self.btn_up.setFixedSize(30, 30)
        self.btn_up.setToolTip("Go to parent directory")
        layout.addWidget(self.btn_up)
        
        self.btn_home = QPushButton("🏠")
        self.btn_home.setFixedSize(30, 30)
        self.btn_home.setToolTip("Go to home directory")
        layout.addWidget(self.btn_home)
        
        # Path input
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Enter path or use browser...")
        layout.addWidget(self.path_input)
        
        # Recent locations dropdown
        self.recent_combo = QComboBox()
        self.recent_combo.setMinimumWidth(200)
        self.recent_combo.addItem("Recent Locations")
        layout.addWidget(self.recent_combo)
        
        # Refresh button
        self.btn_refresh = QPushButton("⟳")
        self.btn_refresh.setFixedSize(30, 30)
        self.btn_refresh.setToolTip("Refresh")
        layout.addWidget(self.btn_refresh)
        
        widget.setLayout(layout)
        return widget
    
    def _create_pipeline_navigation(self) -> QWidget:
        """Create pipeline navigation for Save mode"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)
        
        # Left: Pipeline dropdowns
        left_widget = QWidget()
        left_layout = QHBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        self.show_combo = QComboBox()
        self.show_combo.addItems(["SHOW_001"])
        self.show_combo.setMinimumWidth(110)
        left_layout.addWidget(self.show_combo)
        
        self.sequence_combo = QComboBox()
        self.sequence_combo.addItems(["SQ010"])
        self.sequence_combo.setMinimumWidth(110)
        left_layout.addWidget(self.sequence_combo)
        
        self.shot_combo = QComboBox()
        self.shot_combo.addItems(["SH0010"])
        self.shot_combo.setMinimumWidth(110)
        left_layout.addWidget(self.shot_combo)
        
        self.task_combo = QComboBox()
        self.task_combo.addItems(["Comp", "Modeling", "Animation", "Lighting"])
        self.task_combo.setCurrentText("Comp")
        self.task_combo.setMinimumWidth(110)
        left_layout.addWidget(self.task_combo)
        
        left_widget.setLayout(left_layout)
        layout.addWidget(left_widget)
        
        # Right: Filter checkbox
        right_widget = QWidget()
        right_layout = QHBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.my_tasks_checkbox = QCheckBox("My Tasks Only")
        self.my_tasks_checkbox.setChecked(True)
        right_layout.addWidget(self.my_tasks_checkbox)
        
        right_widget.setLayout(right_layout)
        layout.addWidget(right_widget)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_browser_section(self) -> QWidget:
        """Create file browser section"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Search and filter
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files...")
        filter_layout.addWidget(self.search_input)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("All Files")
        for ext in self.file_extensions:
            self.filter_combo.addItem(f"*{ext}")
        self.filter_combo.setCurrentIndex(1 if len(self.file_extensions) > 0 else 0)
        filter_layout.addWidget(self.filter_combo)
        
        layout.addLayout(filter_layout)
        
        # File tree
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Task", "Version", "Size", "Updated"])
        self.file_tree.setAlternatingRowColors(True)
        self.file_tree.setSortingEnabled(True)
        self.file_tree.setSelectionMode(QTreeWidget.SingleSelection)
        
        # Set column widths
        header = self.file_tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        # Header alignment
        header.setDefaultAlignment(Qt.AlignCenter)
        self.file_tree.headerItem().setTextAlignment(0, Qt.AlignLeft | Qt.AlignVCenter)
        
        layout.addWidget(self.file_tree)
        
        widget.setLayout(layout)
        return widget
    
    def _create_details_section(self) -> QWidget:
        """Create file details section"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # File info group
        info_group = QGroupBox("File Information")
        info_layout = QVBoxLayout()
        
        self.lbl_filename = QLabel("No file selected")
        self.lbl_filename.setWordWrap(True)
        font = QFont()
        font.setBold(True)
        self.lbl_filename.setFont(font)
        info_layout.addWidget(self.lbl_filename)
        
        self.lbl_filepath = QLabel("")
        self.lbl_filepath.setWordWrap(True)
        self.lbl_filepath.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info_layout.addWidget(self.lbl_filepath)
        
        info_layout.addWidget(QLabel(""))  # Spacer
        
        self.lbl_size = QLabel("Size: -")
        info_layout.addWidget(self.lbl_size)
        
        self.lbl_modified = QLabel("Modified: -")
        info_layout.addWidget(self.lbl_modified)
        
        self.lbl_version = QLabel("Version: -")
        info_layout.addWidget(self.lbl_version)
        
        # Add Preview only for Load mode
        if self.mode == "load":
            # Add spacing between File Information and Preview
            layout.addSpacing(6)
            
            # Thumbnail
            thumbnail_group = QGroupBox("Preview")
            thumbnail_layout = QVBoxLayout()
            
            self.lbl_thumbnail = QLabel("No preview available")
            self.lbl_thumbnail.setAlignment(Qt.AlignCenter)
            self.lbl_thumbnail.setMinimumSize(250, 250)
            self.lbl_thumbnail.setStyleSheet("background-color: #2b2b2b; border: 1px solid #555;")
            thumbnail_layout.addWidget(self.lbl_thumbnail)
            
            thumbnail_group.setLayout(thumbnail_layout)
            layout.addWidget(thumbnail_group)
            
            # Add spacing between Preview and Metadata
            layout.addSpacing(6)
            
            # Metadata
            metadata_group = QGroupBox("Metadata")
            metadata_layout = QVBoxLayout()
            
            self.metadata_text = QTextEdit()
            self.metadata_text.setReadOnly(True)
            self.metadata_text.setMaximumHeight(150)
            metadata_layout.addWidget(self.metadata_text)
            
            metadata_group.setLayout(metadata_layout)
            layout.addWidget(metadata_group)
        
        info_layout.addStretch()
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _create_options_section(self) -> QWidget:
        """Create options section"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        if self.mode == "load":
            # Load mode options
            load_group = QGroupBox("Load Mode")
            load_layout = QHBoxLayout()
            
            self.radio_open = QRadioButton("Open (Replace current scene)")
            self.radio_open.setChecked(True)
            load_layout.addWidget(self.radio_open)
            
            self.radio_import = QRadioButton("Import (Merge into current scene)")
            load_layout.addWidget(self.radio_import)
            
            # Radio button group
            self.load_mode_group = QButtonGroup()
            self.load_mode_group.addButton(self.radio_open, 0)
            self.load_mode_group.addButton(self.radio_import, 1)
            
            load_layout.addStretch()
            load_group.setLayout(load_layout)
            layout.addWidget(load_group)
            
        else:  # save mode
            # Save options
            save_group = QGroupBox("Save Options")
            save_layout = QHBoxLayout()
            
            self.chk_backup = QCheckBox("Create backup before saving")
            self.chk_backup.setChecked(True)
            save_layout.addWidget(self.chk_backup)
            
            self.chk_version = QCheckBox("Auto-increment version")
            self.chk_version.setChecked(True)
            save_layout.addWidget(self.chk_version)
            
            self.chk_metadata = QCheckBox("Save metadata")
            self.chk_metadata.setChecked(True)
            save_layout.addWidget(self.chk_metadata)
            
            save_layout.addStretch()
            save_group.setLayout(save_layout)
            layout.addWidget(save_group)
            
            # Filename input for save mode
            filename_layout = QHBoxLayout()
            filename_layout.addWidget(QLabel("Filename:"))
            
            self.filename_input = QLineEdit()
            if self.current_file:
                self.filename_input.setText(os.path.basename(self.current_file))
            filename_layout.addWidget(self.filename_input)
            
            layout.addLayout(filename_layout)
        
        widget.setLayout(layout)
        return widget
    
    def _create_save_options(self) -> QWidget:
        """Create Save Options section matching prototype"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        save_group = QGroupBox("Save Options")
        save_layout = QVBoxLayout()
        
        # Filename suffix
        suffix_layout = QHBoxLayout()
        suffix_layout.addWidget(QLabel("Filename suffix:"))
        suffix_layout.setContentsMargins(0, 0, 0, 0)
        
        self.suffix_input = QLineEdit()
        self.suffix_input.setPlaceholderText("Optional (e.g. clientReview)")
        suffix_layout.addWidget(self.suffix_input)
        
        save_layout.addLayout(suffix_layout)
        
        # Version dropdown
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Version:"))
        version_layout.setContentsMargins(0, 0, 0, 0)
        
        self.version_combo = QComboBox()
        self.version_combo.setMinimumWidth(150)
        self.version_combo.addItems(["v005 (Next)", "v004", "v003", "v002", "v001"])
        version_layout.addWidget(self.version_combo)
        
        save_layout.addLayout(version_layout)
        
        # Checkbox and buttons row
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left: checkboxes
        checkbox_layout = QHBoxLayout()
        checkbox_layout.setSpacing(16)
        
        self.auto_increment_checkbox = QCheckBox("Increment version automatically")
        self.auto_increment_checkbox.setChecked(True)
        checkbox_layout.addWidget(self.auto_increment_checkbox)
        
        actions_layout.addLayout(checkbox_layout)
        actions_layout.addStretch()
        
        # Right: buttons
        self.btn_validate = QPushButton("Validate")
        self.btn_validate.setMinimumWidth(80)
        self.btn_validate.setStyleSheet("background-color: #27ae60; color: white;")
        actions_layout.addWidget(self.btn_validate)
        
        actions_layout.addSpacing(10)
        
        self.btn_save = QPushButton("Save")
        self.btn_save.setMinimumWidth(80)
        self.btn_save.setEnabled(False)
        self.btn_save.setStyleSheet("background-color: #0d5aa7; color: white;")
        actions_layout.addWidget(self.btn_save)
        
        save_layout.addLayout(actions_layout)
        save_group.setLayout(save_layout)
        layout.addWidget(save_group)
        
        widget.setLayout(layout)
        return widget
    
    def _create_actions_section(self) -> QWidget:
        """Create action buttons section"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addStretch()
        
        # Cancel button
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setMinimumWidth(100)
        layout.addWidget(self.btn_cancel)
        
        # Validate button (Save mode only)
        if self.mode == "save":
            # Already added in save options, skip here
            pass
        
        # Main action button
        if self.mode == "load":
            self.btn_action = QPushButton("Load")
            self.btn_action.setMinimumWidth(100)
        else:
            # Use btn_save from save options
            self.btn_action = self.btn_save
        
        self.btn_action.setDefault(True)
        if self.mode == "load":
            layout.addWidget(self.btn_action)
        
        widget.setLayout(layout)
        return widget
    
    def _connect_signals(self):
        """Connect UI signals"""
        # Navigation
        self.btn_back.clicked.connect(self._go_back)
        self.btn_forward.clicked.connect(self._go_forward)
        self.btn_up.clicked.connect(self._go_up)
        self.btn_home.clicked.connect(self._go_home)
        self.btn_refresh.clicked.connect(self._refresh_directory)
        self.path_input.returnPressed.connect(self._on_path_entered)
        self.recent_combo.currentTextChanged.connect(self._on_recent_selected)
        
        # File browser
        self.file_tree.itemSelectionChanged.connect(self._on_file_selected)
        self.file_tree.itemDoubleClicked.connect(self._on_file_double_clicked)
        self.search_input.textChanged.connect(self._filter_files)
        self.filter_combo.currentTextChanged.connect(self._filter_files)
        
        # Actions
        self.btn_cancel.clicked.connect(self.reject)
        if self.mode == "load":
            self.btn_action.clicked.connect(self._on_action_clicked)
        else:
            self.btn_save.clicked.connect(self._on_action_clicked)
            self.btn_validate.clicked.connect(self._on_validate_clicked)
        
        # Options
        if self.mode == "load":
            self.radio_open.toggled.connect(self._on_load_mode_changed)
        else:
            self.auto_increment_checkbox.toggled.connect(self._on_auto_increment_toggled)
            self.version_combo.currentTextChanged.connect(self._on_version_changed)
    
    def _navigate_to_directory(self, path: str):
        """Navigate to a directory"""
        if not os.path.exists(path):
            QMessageBox.warning(self, "Error", f"Directory does not exist: {path}")
            return
        
        self.current_directory = path
        self.path_input.setText(path)
        self._populate_file_tree(path)
    
    def _populate_file_tree(self, directory: str):
        """Populate file tree with directory contents"""
        self.file_tree.clear()
        
        try:
            skip_dirs = {"publish"}
            
            # List directories
            items = []
            for entry in os.scandir(directory):
                if entry.is_dir():
                    if entry.name.lower() in skip_dirs:
                        continue
                    item = QTreeWidgetItem([entry.name, "", "", "", ""])
                    item.setData(0, Qt.UserRole, entry.path)
                    item.setForeground(0, QColor(150, 150, 255))
                    for col in range(1, 5):
                        item.setTextAlignment(col, Qt.AlignCenter)
                    items.append(item)
            
            # List files
            for entry in os.scandir(directory):
                if entry.is_file():
                    # Filter by extension
                    if self.file_extensions:
                        ext = os.path.splitext(entry.name)[1]
                        if ext not in self.file_extensions:
                            continue
                    
                    file_info = FileInfo(entry.path)

                    # Infer task (fallback) from filename: SH0010_comp_v004.ma -> Comp
                    task = file_info.metadata.get('task')
                    if not task:
                        import re
                        m = re.search(r'^[^_]+_([^_]+)_v\d+', file_info.name)
                        task = m.group(1) if m else "-"
                    task = task.replace('-', ' ').replace('_', ' ').strip().title() if task and task != "-" else "-"
                    
                    item = QTreeWidgetItem([
                        file_info.name,
                        task,
                        f"v{file_info.version:03d}" if file_info.version > 0 else "-",
                        file_info.get_size_str(),
                        file_info.get_date_str(),
                    ])
                    item.setData(0, Qt.UserRole, entry.path)
                    for col in range(1, 5):
                        item.setTextAlignment(col, Qt.AlignCenter)
                    items.append(item)
            
            self.file_tree.addTopLevelItems(items)
            
            # Sort by name
            self.file_tree.sortItems(0, Qt.AscendingOrder)
            
        except PermissionError:
            QMessageBox.warning(self, "Error", f"Permission denied: {directory}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error reading directory: {e}")
    
    def _filter_files(self):
        """Filter files based on search and filter combo"""
        search_text = self.search_input.text().lower()
        filter_ext = self.filter_combo.currentText()
        
        for i in range(self.file_tree.topLevelItemCount()):
            item = self.file_tree.topLevelItem(i)
            filename = item.text(0).lower()
            
            # Check search
            if search_text and search_text not in filename:
                item.setHidden(True)
                continue
            
            # Check filter
            if filter_ext != "All Files" and not filename.endswith(filter_ext.replace("*", "").lower()):
                # Don't hide directories
                if not os.path.isdir(item.data(0, Qt.UserRole)):
                    item.setHidden(True)
                    continue
            
            item.setHidden(False)
    
    def _on_file_selected(self):
        """Handle file selection"""
        selected = self.file_tree.selectedItems()
        if not selected:
            return
        
        item = selected[0]
        file_path = item.data(0, Qt.UserRole)
        
        if os.path.isfile(file_path):
            self.selected_file = file_path
            self._update_file_details(file_path)
            
            if self.mode == "save":
                self.filename_input.setText(os.path.basename(file_path))
    
    def _on_file_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on file/directory"""
        file_path = item.data(0, Qt.UserRole)
        
        if os.path.isdir(file_path):
            self._navigate_to_directory(file_path)
        else:
            # Double-click on file triggers action
            self._on_action_clicked()
    
    def _update_file_details(self, file_path: str):
        """Update file details panel"""
        file_info = FileInfo(file_path)
        
        self.lbl_filename.setText(file_info.name)
        self.lbl_filepath.setText(f"Path: {file_path}")
        self.lbl_size.setText(f"Size: {file_info.get_size_str()}")
        self.lbl_modified.setText(f"Modified: {file_info.get_date_str()}")
        self.lbl_version.setText(f"Version: v{file_info.version:03d}" if file_info.version > 0 else "Version: -")
        
        # Display metadata
        if file_info.metadata:
            import json
            self.metadata_text.setText(json.dumps(file_info.metadata, indent=2))
        else:
            self.metadata_text.setText("No metadata available")
        
        # Load thumbnail
        self._load_thumbnail(file_path)
    
    def _load_thumbnail(self, file_path: str):
        """Load thumbnail for file"""
        thumb_path = Path(file_path).with_suffix('.thumb.jpg')
        
        if thumb_path.exists():
            pixmap = QPixmap(str(thumb_path))
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.lbl_thumbnail.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.lbl_thumbnail.setPixmap(scaled)
                return
        
        self.lbl_thumbnail.setText("No preview available")
        self.lbl_thumbnail.setPixmap(QPixmap())
    
    def _on_action_clicked(self):
        """Handle main action button click"""
        if self.mode == "load":
            if not self.selected_file:
                QMessageBox.warning(self, "No Selection", "Please select a file to load")
                return
            
            # Get load mode
            self.load_mode = "open" if self.radio_open.isChecked() else "import"
            
            self.accept()
        
        else:  # save mode
            filename = self.filename_input.text().strip()
            if not filename:
                QMessageBox.warning(self, "No Filename", "Please enter a filename")
                return
            
            # Ensure extension
            if not any(filename.endswith(ext) for ext in self.file_extensions):
                filename += self.file_extensions[0]
            
            self.selected_file = os.path.join(self.current_directory, filename)
            
            # Get save options
            self.create_backup = self.chk_backup.isChecked()
            self.auto_version = self.chk_version.isChecked()
            self.save_metadata = self.chk_metadata.isChecked()
            
            # Check if file exists
            if os.path.exists(self.selected_file):
                reply = QMessageBox.question(
                    self,
                    "Overwrite?",
                    f"File already exists:\n{self.selected_file}\n\nOverwrite?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            self.accept()
    
    def _on_load_mode_changed(self, checked: bool):
        """Handle load mode radio button change"""
        if checked:
            self.load_mode = "open" if self.radio_open.isChecked() else "import"
    
    def _go_back(self):
        """Navigate back"""
        # TODO: Implement history
        pass
    
    def _go_forward(self):
        """Navigate forward"""
        # TODO: Implement history
        pass
    
    def _go_up(self):
        """Navigate to parent directory"""
        parent = os.path.dirname(self.current_directory)
        if parent != self.current_directory:
            self._navigate_to_directory(parent)
    
    def _go_home(self):
        """Navigate to home directory"""
        self._navigate_to_directory(os.path.expanduser("~"))
    
    def _refresh_directory(self):
        """Refresh current directory"""
        self._populate_file_tree(self.current_directory)
    
    def _on_path_entered(self):
        """Handle path input"""
        path = self.path_input.text()
        if os.path.exists(path):
            self._navigate_to_directory(path)
    
    def _on_recent_selected(self, text: str):
        """Handle recent location selection"""
        if text != "Recent Locations" and os.path.exists(text):
            self._navigate_to_directory(text)
    
    def _load_recent_directories(self):
        """Load recent directories from config"""
        # TODO: Load from config file
        recent = [
            "/mnt/projects",
            os.path.expanduser("~"),
        ]
        
        for path in recent:
            if os.path.exists(path):
                self.recent_combo.addItem(path)
    
    def _apply_stylesheet(self):
        """Apply custom stylesheet"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QPushButton:default {
                background-color: #0d5aa7;
                border: 1px solid #0d5aa7;
            }
            QPushButton:default:hover {
                background-color: #0e6bbf;
            }
            QLineEdit, QComboBox {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                color: #ffffff;
            }
            QTreeWidget {
                background-color: #2b2b2b;
                border: 1px solid #555555;
                alternate-background-color: #323232;
            }
            QTreeWidget::item:selected {
                background-color: #0d5aa7;
            }
            QTreeWidget::item:hover {
                background-color: #3a3a3a;
            }
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #555555;
                color: #ffffff;
            }
            QCheckBox, QRadioButton {
                color: #ffffff;
            }
        """)
    
    def _on_validate_clicked(self):
        """Handle Validate button click"""
        # In a real implementation, this would validate the file path, permissions, etc.
        # For now, just enable the Save button
        self.btn_save.setEnabled(True)
        self.btn_save.setStyleSheet("background-color: #27ae60; color: white;")
    
    def _on_auto_increment_toggled(self, checked: bool):
        """Handle auto-increment checkbox toggle"""
        if checked:
            # Auto-select next version
            self.version_combo.setCurrentIndex(0)
    
    def _on_version_changed(self, text: str):
        """Handle version dropdown change"""
        # Update UI based on version selection
        pass
    
    def get_result(self) -> Dict[str, Any]:
        """Get dialog result"""
        result = {
            'file_path': self.selected_file,
        }
        
        if self.mode == "load":
            result['load_mode'] = self.load_mode
        else:
            result['suffix'] = self.suffix_input.text()
            result['version'] = self.version_combo.currentText()
            result['auto_increment'] = self.auto_increment_checkbox.isChecked()
            result['show'] = self.show_combo.currentText()
            result['sequence'] = self.sequence_combo.currentText()
            result['shot'] = self.shot_combo.currentText()
            result['task'] = self.task_combo.currentText()
            result['my_tasks_only'] = self.my_tasks_checkbox.isChecked()
        
        return result


# Standalone test
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Test load dialog
    dialog = NOXFileDialog(
        mode="load",
        dcc_name="Nuke",
        file_extensions=[".nk", ".nknc"],
        current_file="/mnt/projects/test/comp_v001.nk"
    )
    
    if dialog.exec() == QDialog.Accepted:
        result = dialog.get_result()
        print(f"Selected file: {result['file_path']}")
        print(f"Load mode: {result['load_mode']}")
    
    sys.exit(app.exec())