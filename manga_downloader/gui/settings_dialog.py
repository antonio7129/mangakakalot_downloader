import os
import json
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QSpinBox, QLabel, QPushButton, QFileDialog, QFrame
from PyQt6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, parent=None, initial_settings=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)

        self.settings = initial_settings if initial_settings else self._load_settings()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        self.init_ui()

    def init_ui(self):
        # PDF Settings
        pdf_frame = QFrame()
        pdf_frame.setObjectName("settingsFrame")
        pdf_layout = QVBoxLayout(pdf_frame)
        
        self.to_pdf_checkbox = QCheckBox("Convert to PDF after download")
        self.to_pdf_checkbox.setChecked(self.settings.get("to_pdf", False))
        pdf_layout.addWidget(self.to_pdf_checkbox)

        self.delete_images_checkbox = QCheckBox("Delete images after PDF conversion")
        self.delete_images_checkbox.setChecked(self.settings.get("delete_images", False))
        pdf_layout.addWidget(self.delete_images_checkbox)
        
        self.layout.addWidget(pdf_frame)

        # Concurrency Setting
        concurrency_frame = QFrame()
        concurrency_frame.setObjectName("settingsFrame")
        concurrency_layout = QHBoxLayout(concurrency_frame)
        concurrency_label = QLabel("Concurrent Downloads:")
        self.concurrency_spinbox = QSpinBox()
        self.concurrency_spinbox.setRange(1, 10)
        self.concurrency_spinbox.setValue(self.settings.get("concurrency", 5))
        concurrency_layout.addWidget(concurrency_label)
        concurrency_layout.addWidget(self.concurrency_spinbox)
        self.layout.addWidget(concurrency_frame)

        # Output Directory Setting
        output_dir_frame = QFrame()
        output_dir_frame.setObjectName("settingsFrame")
        output_dir_layout = QVBoxLayout(output_dir_frame)
        
        output_dir_label = QLabel("Output Directory:")
        output_dir_layout.addWidget(output_dir_label)
        
        output_dir_inner_layout = QHBoxLayout()
        self.output_dir_input = QLabel(self.settings.get("output_dir", os.path.join(os.getcwd(), "downloads")))
        self.output_dir_input.setWordWrap(True)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_output_directory)
        output_dir_inner_layout.addWidget(self.output_dir_input, 1)
        output_dir_inner_layout.addWidget(self.browse_button)
        output_dir_layout.addLayout(output_dir_inner_layout)
        self.layout.addWidget(output_dir_frame)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

    def browse_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_dir_input.setText(directory)

    def _load_settings(self):
        settings_path = os.path.join(os.getcwd(), "settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                return json.load(f)
        return {
            "to_pdf": False,
            "delete_images": False,
            "concurrency": 5,
            "output_dir": os.path.join(os.getcwd(), "downloads")
        }

    def _save_settings(self):
        settings_path = os.path.join(os.getcwd(), "settings.json")
        with open(settings_path, "w") as f:
            json.dump(self.settings, f, indent=4)

    def accept(self):
        self.settings["to_pdf"] = self.to_pdf_checkbox.isChecked()
        self.settings["delete_images"] = self.delete_images_checkbox.isChecked()
        self.settings["concurrency"] = self.concurrency_spinbox.value()
        self.settings["output_dir"] = self.output_dir_input.text()
        self._save_settings()
        super().accept()

    def get_settings(self):
        return self.settings
