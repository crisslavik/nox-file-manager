# integrations/blender/nox_save_dialog.py
"""
Blender-specific Save Dialog for NOX VFX
Handles Blender-specific save options and workflow
"""

import os
from typing import Dict, Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QTreeWidget, QTreeWidgetItem, QComboBox,
    QCheckBox, QGroupBox, QSplitter,
    QHeaderView, QMessageBox, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from ui.file_dialog import FileInfo


class NOXSaveDialogBlender(QDialog):
    """
    Blender-specific save dialog with Blender-specific options
    """
    
    def __init__(self, 
                 current_file: str = None,
                 parent: QWidget = None):
        super().__init__(parent)
        
        self.current_file = current_file
        self.selected_file: str = None
        self.is_validated = False
        
        self._setup_ui()
        self._connect_signals()
        self._load_initial_directory()
    
    def _setup_ui(self):
        """Setup the Blender-specific save UI"""
        self.setWindowTitle("NOX Save - Blender")
        self.resize(1200, 800)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Pipeline navigation (will be populated by pipeline setup)
        layout.addWidget(self._create_pipeline_navigation())
        
        # Main splitter: File browser and details
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._create_browser_section())
        splitter.addWidget(self._create_details_section())
        splitter.setSizes([800, 400])
        layout.addWidget(splitter)
        
        # Blender-specific save options
        layout.addWidget(self._create_blender_save_options())
        
        # Actions
        layout.addWidget(self._create_actions_section())
        
        self.setLayout(layout)
        self._apply_stylesheet()
    
    def _create_pipeline_navigation(self) -> QWidget:
        """Create pipeline navigation (placeholder for pipeline setup)"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)
        
        # Left: Pipeline dropdowns (will be populated by pipeline)
        left_widget = QWidget()
        left_layout = QHBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        self.show_combo = QComboBox()
        self.show_combo.setMinimumWidth(110)
        left_layout.addWidget(self.show_combo)
        
        self.sequence_combo = QComboBox()
        self.sequence_combo.setMinimumWidth(110)
        left_layout.addWidget(self.sequence_combo)
        
        self.shot_combo = QComboBox()
        self.shot_combo.setMinimumWidth(110)
        left_layout.addWidget(self.shot_combo)
        
        self.task_combo = QComboBox()
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
        self.filter_combo.addItems(["All Files", "*.blend"])
        self.filter_combo.setCurrentIndex(1)
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
        
        info_layout.addStretch()
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _create_blender_save_options(self) -> QWidget:
        """Create Blender-specific save options"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        save_group = QGroupBox("Blender Save Options")
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
        
        # Blender-specific options
        blender_options_layout = QHBoxLayout()
        blender_options_layout.setContentsMargins(0, 0, 0, 0)
        
        checkbox_layout = QVBoxLayout()
        checkbox_layout.setSpacing(8)
        
        self.auto_increment_checkbox = QCheckBox("Increment version automatically")
        self.auto_increment_checkbox.setChecked(True)
        checkbox_layout.addWidget(self.auto_increment_checkbox)
        
        self.compress_file_checkbox = QCheckBox("Compress blend file")
        self.compress_file_checkbox.setChecked(False)
        checkbox_layout.addWidget(self.compress_file_checkbox)
        
        self.save_relative_paths_checkbox = QCheckBox("Save relative paths")
        self.save_relative_paths_checkbox.setChecked(True)
        checkbox_layout.addWidget(self.save_relative_paths_checkbox)
        
        self.backup_previous_checkbox = QCheckBox("Backup previous version")
        self.backup_previous_checkbox.setChecked(True)
        checkbox_layout.addWidget(self.backup_previous_checkbox)
        
        blender_options_layout.addLayout(checkbox_layout)
        blender_options_layout.addStretch()
        
        save_layout.addLayout(blender_options_layout)
        
        # Checkbox and buttons row
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left: empty (buttons on right)
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
        
        widget.setLayout(layout)
        return widget
    
    def _connect_signals(self):
        """Connect UI signals"""
        # File browser
        self.file_tree.itemSelectionChanged.connect(self._on_file_selected)
        self.file_tree.itemDoubleClicked.connect(self._on_file_double_clicked)
        self.search_input.textChanged.connect(self._filter_files)
        self.filter_combo.currentTextChanged.connect(self._filter_files)
        
        # Actions
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_save.clicked.connect(self._on_save_clicked)
        self.btn_validate.clicked.connect(self._on_validate_clicked)
        
        # Options
        self.auto_increment_checkbox.toggled.connect(self._on_auto_increment_toggled)
        self.version_combo.currentTextChanged.connect(self._on_version_changed)
    
    def _load_initial_directory(self):
        """Load initial directory"""
        if self.current_file and os.path.exists(self.current_file):
            self._navigate_to_directory(os.path.dirname(self.current_file))
        else:
            self._navigate_to_directory(os.path.expanduser("~"))
    
    def _navigate_to_directory(self, path: str):
        """Navigate to a directory"""
        if not os.path.exists(path):
            QMessageBox.warning(self, "Error", f"Directory does not exist: {path}")
            return
        
        self.current_directory = path
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
            
            # List Blender files
            for entry in os.scandir(directory):
                if entry.is_file():
                    ext = os.path.splitext(entry.name)[1]
                    if ext not in [".blend"]:
                        continue
                    
                    file_info = FileInfo(entry.path)

                    # Infer task from filename
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
            self.file_tree.sortItems(0, Qt.AscendingOrder)
            
        except PermissionError:
            QMessageBox.warning(self, "Error", f"Permission denied: {directory}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error reading directory: {e}")
    
    def _filter_files(self):
        """Filter files based on search and extension"""
        search_text = self.search_input.text().lower()
        filter_ext = self.filter_combo.currentText()
        
        for i in range(self.file_tree.topLevelItemCount()):
            item = self.file_tree.topLevelItem(i)
            filename = item.text(0).lower()
            
            if search_text and search_text not in filename:
                item.setHidden(True)
                continue
            
            if filter_ext != "All Files":
                ext = filter_ext.replace("*", "").lower()
                if not filename.endswith(ext) and not os.path.isdir(item.data(0, Qt.UserRole)):
                    item.setHidden(True)
                    continue
            
            item.setHidden(False)
    
    def _on_file_selected(self):
        """Handle file selection"""
        items = self.file_tree.selectedItems()
        if items:
            item = items[0]
            file_path = item.data(0, Qt.UserRole)
            
            if os.path.isfile(file_path):
                self.selected_file = file_path
                file_info = FileInfo(file_path)
                
                self.lbl_filename.setText(file_info.name)
                self.lbl_filepath.setText(f"Path: {file_path}")
                self.lbl_size.setText(f"Size: {file_info.get_size_str()}")
                self.lbl_modified.setText(f"Modified: {file_info.get_date_str()}")
                self.lbl_version.setText(f"Version: v{file_info.version:03d}" if file_info.version > 0 else "Version: -")
                
                # Update version dropdown based on selected file
                if file_info.version > 0:
                    next_version = f"v{file_info.version + 1:03d} (Next)"
                    self.version_combo.clear()
                    self.version_combo.addItem(next_version)
                    for v in range(file_info.version, 0, -1):
                        self.version_combo.addItem(f"v{v:03d}")
            else:
                self._clear_file_info()
        else:
            self._clear_file_info()
    
    def _clear_file_info(self):
        """Clear file information display"""
        self.selected_file = None
        self.lbl_filename.setText("No file selected")
        self.lbl_filepath.setText("")
        self.lbl_size.setText("Size: -")
        self.lbl_modified.setText("Modified: -")
        self.lbl_version.setText("Version: -")
    
    def _on_file_double_clicked(self, item, column):
        """Handle file double-click"""
        file_path = item.data(0, Qt.UserRole)
        if os.path.isfile(file_path):
            self.selected_file = file_path
            self._on_validate_clicked()
    
    def _on_validate_clicked(self):
        """Handle Validate button click"""
        if not self.selected_file:
            QMessageBox.warning(self, "Validation Error", "Please select a file to save.")
            return
        
        self.is_validated = True
        self.btn_save.setEnabled(True)
        self.btn_save.setStyleSheet("background-color: #27ae60; color: white;")
    
    def _on_save_clicked(self):
        """Handle Save button click"""
        if not self.is_validated:
            QMessageBox.warning(self, "Not Validated", "Please validate before saving.")
            return
        
        result = self.get_result()
        self.accept()
    
    def _on_auto_increment_toggled(self, checked: bool):
        """Handle auto-increment checkbox toggle"""
        if checked:
            self.version_combo.setCurrentIndex(0)
    
    def _on_version_changed(self, text: str):
        """Handle version dropdown change"""
        pass
    
    def get_result(self) -> Dict[str, Any]:
        """Get Blender save dialog result"""
        return {
            'file_path': self.selected_file,
            'suffix': self.suffix_input.text(),
            'version': self.version_combo.currentText(),
            'auto_increment': self.auto_increment_checkbox.isChecked(),
            'compress_file': self.compress_file_checkbox.isChecked(),
            'save_relative_paths': self.save_relative_paths_checkbox.isChecked(),
            'backup_previous': self.backup_previous_checkbox.isChecked(),
            'show': self.show_combo.currentText(),
            'sequence': self.sequence_combo.currentText(),
            'shot': self.shot_combo.currentText(),
            'task': self.task_combo.currentText(),
            'my_tasks_only': self.my_tasks_checkbox.isChecked(),
            'is_validated': self.is_validated
        }
    
    def _apply_stylesheet(self):
        """Apply dark theme stylesheet"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
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
            QCheckBox, QRadioButton {
                color: #ffffff;
            }
        """)
