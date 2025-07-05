from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QFrame
from PyQt6.QtCore import Qt

class TitledFrame(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet("""
            TitledFrame {
                border: 1px solid #444;
                border-radius: 8px;
                margin-top: 15px;
            }
            #titleLabel {
                background-color: #333;
                color: white;
                padding: 5px;
                border-radius: 5px;
                font-weight: bold;
                qproperty-alignment: 'AlignCenter';
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 20, 10, 10)
        main_layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("titleLabel")
        
        self.content_layout = QVBoxLayout()
        
        main_layout.addWidget(title_label)
        main_layout.addLayout(self.content_layout)

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        self.content_layout.addLayout(layout)

class SearchWidget(TitledFrame):
    def __init__(self, parent=None):
        super().__init__("Manga Search", parent)

        # Site selection
        site_layout = QHBoxLayout()
        site_label = QLabel("Select Site:")
        self.site_combo = QComboBox()
        site_layout.addWidget(site_label)
        site_layout.addWidget(self.site_combo)
        self.add_layout(site_layout)

        # Search input
        search_layout = QHBoxLayout()
        search_label = QLabel("Search Manga:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter manga title")
        self.search_button = QPushButton("Search")
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        self.add_layout(search_layout)

        # Search results
        self.search_results_combo = QComboBox()
        self.search_results_combo.setPlaceholderText("Search results")
        self.add_widget(self.search_results_combo)

        # Manga URL input
        manga_url_layout = QHBoxLayout()
        manga_url_label = QLabel("Manga URL:")
        self.manga_url_input = QLineEdit()
        self.manga_url_input.setPlaceholderText("Or enter manga URL manually")
        manga_url_layout.addWidget(manga_url_label)
        manga_url_layout.addWidget(self.manga_url_input)
        self.add_layout(manga_url_layout)

class ChapterWidget(TitledFrame):
    def __init__(self, parent=None):
        super().__init__("Chapters", parent)

        # Fetch Chapters button
        self.fetch_chapters_button = QPushButton("Fetch Chapters")
        self.add_widget(self.fetch_chapters_button)

        # Chapter selection
        chapter_layout = QHBoxLayout()
        chapter_label = QLabel("Select Chapter:")
        self.chapter_combo = QComboBox()
        self.chapter_combo.setPlaceholderText("Fetch chapters first")
        self.chapter_combo.setEnabled(False)
        chapter_layout.addWidget(chapter_label)
        chapter_layout.addWidget(self.chapter_combo)
        self.add_layout(chapter_layout)

        # Range selection
        range_layout = QHBoxLayout()
        range_label = QLabel("Download Range:")
        self.start_chapter_input = QLineEdit()
        self.start_chapter_input.setPlaceholderText("Start")
        self.end_chapter_input = QLineEdit()
        self.end_chapter_input.setPlaceholderText("End")
        self.download_range_button = QPushButton("Download Range")
        range_layout.addWidget(range_label)
        range_layout.addWidget(self.start_chapter_input)
        range_layout.addWidget(self.end_chapter_input)
        range_layout.addWidget(self.download_range_button)
        self.add_layout(range_layout)

class DownloadWidget(TitledFrame):
    def __init__(self, parent=None):
        super().__init__("Download", parent)

        # Download buttons
        self.download_chapter_button = QPushButton("Download Selected Chapter")
        self.download_chapter_button.setEnabled(False)
        self.add_widget(self.download_chapter_button)

        self.download_all_chapters_button = QPushButton("Download All Chapters")
        self.download_all_chapters_button.setEnabled(False)
        self.add_widget(self.download_all_chapters_button)

        # Settings button
        self.settings_button = QPushButton("Settings")
        self.add_widget(self.settings_button)

        # Cancel button
        self.cancel_button = QPushButton("Cancel Download")
        self.cancel_button.setEnabled(False)
        self.add_widget(self.cancel_button)
