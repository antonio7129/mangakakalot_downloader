import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QProgressBar, QTextEdit, QDialog, QHBoxLayout
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from manga_downloader.core.scraper import MangaScraper
from manga_downloader.core.downloader import MangaDownloader
from manga_downloader.core.config import BASE_URLS
from manga_downloader.gui.settings_dialog import SettingsDialog
from manga_downloader.gui.widgets import SearchWidget, ChapterWidget, DownloadWidget
from qt_material import apply_stylesheet

class Worker(QThread):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    log = pyqtSignal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._is_running = True

    def run(self):
        try:
            self.func(*self.args, **self.kwargs)
        except Exception as e:
            self.log.emit(f"Error: {e}")
        finally:
            if self._is_running:
                self.finished.emit()

    def stop(self):
        self._is_running = False
        self.log.emit("Worker stopped.")

class MangaDownloaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manga Downloader")
        self.setGeometry(100, 100, 900, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        self.settings = self._load_settings()
        self.chapters = []
        self.search_results = []
        self.worker = None

        self.init_ui()
        self.connect_signals()
        self.apply_animations()

    def init_ui(self):
        # Widgets
        self.search_widget = SearchWidget()
        self.chapter_widget = ChapterWidget()
        self.download_widget = DownloadWidget()

        # Layout
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.search_widget, 1)
        top_layout.addWidget(self.chapter_widget, 1)
        self.layout.addLayout(top_layout)
        self.layout.addWidget(self.download_widget)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.progress_bar)

        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.layout.addWidget(self.log_output)
        
        # Settings button
        self.settings_button = self.download_widget.settings_button
        self.layout.addWidget(self.settings_button)

        # Apply stylesheet
        self.search_widget.site_combo.addItems(BASE_URLS.keys())

    def connect_signals(self):
        self.search_widget.search_button.clicked.connect(self.search_manga_gui)
        self.search_widget.search_results_combo.currentIndexChanged.connect(self.on_search_result_selected)
        self.chapter_widget.fetch_chapters_button.clicked.connect(self.fetch_chapters)
        self.chapter_widget.download_range_button.clicked.connect(self.download_chapter_range)
        self.download_widget.download_chapter_button.clicked.connect(self.download_selected_chapter)
        self.download_widget.download_all_chapters_button.clicked.connect(self.download_all_chapters)
        self.download_widget.cancel_button.clicked.connect(self.cancel_download)
        self.settings_button.clicked.connect(self.open_settings)

    def log_message(self, message):
        self.log_output.append(message)

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

    def search_manga_gui(self):
        search_query = self.search_widget.search_input.text().strip()
        site_name = self.search_widget.site_combo.currentText()
        if not search_query:
            self.log_message("Please enter a manga title to search.")
            return

        self.log_message(f"Searching for '{search_query}' on {site_name}...")
        self.scraper = MangaScraper(site_name=site_name, verbose=True)
        
        self.worker = Worker(self._perform_search, search_query)
        self.worker.finished.connect(self._search_finished)
        self.worker.log.connect(self.log_message)
        self.worker.start()

    def _perform_search(self, search_query):
        try:
            self.search_results = self.scraper.search_manga(search_query)
            self.worker.log.emit(f"Search completed. Found {len(self.search_results)} results.")
            
            self.search_widget.search_results_combo.clear()
            if self.search_results:
                self.search_widget.search_results_combo.addItem("Select a manga from results...", "")
                for result in self.search_results:
                    self.search_widget.search_results_combo.addItem(result["title"], result["url"])
                self.search_widget.search_results_combo.setEnabled(True)
            else:
                self.search_widget.search_results_combo.addItem("No results found.", "")
                self.search_widget.search_results_combo.setEnabled(False)
        except Exception as e:
            self.worker.log.emit(f"Error during search: {e}")

    def _search_finished(self):
        self.log_message("Search process finished.")

    def on_search_result_selected(self, index):
        if index > 0:
            selected_url = self.search_widget.search_results_combo.currentData()
            if selected_url:
                self.search_widget.manga_url_input.setText(selected_url)
                self.log_message(f"Selected manga: {self.search_widget.search_results_combo.currentText()}")
        else:
            self.search_widget.manga_url_input.clear()

    def fetch_chapters(self):
        manga_url = self.search_widget.manga_url_input.text().strip()
        site_name = self.search_widget.site_combo.currentText()
        if not manga_url:
            self.log_message("Please enter a manga URL or select from search results.")
            return

        self.log_message(f"Fetching chapters from {manga_url}...")
        self.scraper = MangaScraper(site_name=site_name, verbose=True)
        
        self.worker = Worker(self._perform_fetch_chapters, manga_url)
        self.worker.finished.connect(self._fetch_chapters_finished)
        self.worker.log.connect(self.log_message)
        self.worker.start()

    def _perform_fetch_chapters(self, manga_url):
        try:
            self.chapters = self.scraper.get_chapters(manga_url)
            self.worker.log.emit(f"Chapter fetching completed. Found {len(self.chapters)} chapters.")

            self.chapter_widget.chapter_combo.clear()
            if self.chapters:
                for chapter in self.chapters:
                    self.chapter_widget.chapter_combo.addItem(chapter["title"], chapter["url"])
                self.chapter_widget.chapter_combo.setEnabled(True)
                self.download_widget.download_chapter_button.setEnabled(True)
                self.download_widget.download_all_chapters_button.setEnabled(True)
            else:
                self.chapter_widget.chapter_combo.addItem("No chapters found.", "")
                self.chapter_widget.chapter_combo.setEnabled(False)
                self.download_widget.download_chapter_button.setEnabled(False)
                self.download_widget.download_all_chapters_button.setEnabled(False)
        except Exception as e:
            self.worker.log.emit(f"Error fetching chapters: {e}")

    def _fetch_chapters_finished(self):
        self.log_message("Chapter fetching process finished.")

    def open_settings(self):
        dialog = SettingsDialog(self, initial_settings=self.settings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings = dialog.get_settings()
            self.log_message("Settings saved.")

    def download_selected_chapter(self):
        selected_index = self.chapter_widget.chapter_combo.currentIndex()
        if selected_index == -1:
            self.log_message("Please select a chapter to download.")
            return

        chapter_title = self.chapter_widget.chapter_combo.currentText()
        chapter_url = self.chapter_widget.chapter_combo.currentData()
        manga_title = self.scraper.get_manga_title(self.search_widget.manga_url_input.text())

        self.log_message(f"Downloading chapter: {chapter_title} from {manga_title}...")
        self.progress_bar.setValue(0)

        downloader = MangaDownloader(
            manga_title=manga_title,
            chapter_title=chapter_title,
            chapter_url=chapter_url,
            output_dir=self.settings.get("output_dir"),
            concurrency=self.settings.get("concurrency"),
            to_pdf=self.settings.get("to_pdf"),
            delete_images=self.settings.get("delete_images"),
            verbose=True,
            progress_callback=self.progress_bar.setValue
        )
        
        self.worker = Worker(downloader.download_chapter)
        self.worker.finished.connect(self.download_finished)
        self.worker.log.connect(self.log_message)
        self.worker.start()
        self.download_widget.cancel_button.setEnabled(True)

    def download_chapter_range(self):
        start_chapter_text = self.chapter_widget.start_chapter_input.text().strip()
        end_chapter_text = self.chapter_widget.end_chapter_input.text().strip()

        if not start_chapter_text or not end_chapter_text:
            self.log_message("Please enter a valid chapter range.")
            return

        try:
            start_chapter = float(start_chapter_text)
            end_chapter = float(end_chapter_text)
        except ValueError:
            self.log_message("Invalid chapter range. Please enter numbers only.")
            return

        start_index = -1
        end_index = -1

        for i, chapter in enumerate(self.chapters):
            if chapter["number"] >= start_chapter and start_index == -1:
                start_index = i
            if chapter["number"] >= end_chapter:
                end_index = i
                break
        
        if end_index == -1:
            end_index = len(self.chapters) -1

        if start_index == -1 or start_index > end_index:
            self.log_message("Invalid chapter range.")
            return

        chapters_to_download = self.chapters[start_index:end_index + 1]
        manga_title = self.scraper.get_manga_title(self.search_widget.manga_url_input.text())

        self.log_message(f"Downloading chapters {start_chapter}-{end_chapter} of {manga_title}...")
        self.progress_bar.setValue(0)

        self.worker = Worker(self._download_all_chapters_threaded, manga_title, chapters_to_download)
        self.worker.finished.connect(self.download_finished)
        self.worker.log.connect(self.log_message)
        self.worker.start()
        self.download_widget.cancel_button.setEnabled(True)

    def download_all_chapters(self):
        manga_url = self.search_widget.manga_url_input.text()
        if not manga_url:
            self.log_message("Please enter a manga URL.")
            return

        self.log_message(f"Downloading all chapters from {manga_url}...")
        self.progress_bar.setValue(0)

        manga_title = self.scraper.get_manga_title(manga_url)

        self.worker = Worker(self._download_all_chapters_threaded, manga_title, self.chapters)
        self.worker.finished.connect(self.download_finished)
        self.worker.log.connect(self.log_message)
        self.worker.start()
        self.download_widget.cancel_button.setEnabled(True)

    def _download_all_chapters_threaded(self, manga_title, chapters):
        import concurrent.futures
        total_chapters = len(chapters)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.settings.get("concurrency", 5)) as executor:
            futures = []
            for chapter in chapters:
                if not self.worker._is_running:
                    self.worker.log.emit("Download of all chapters cancelled.")
                    break
                
                chapter_title = chapter["title"]
                chapter_url = chapter["url"]
                self.worker.log.emit(f"Queueing chapter {chapter_title} for download...")
                
                downloader = MangaDownloader(
                    manga_title=manga_title,
                    chapter_title=chapter_title,
                    chapter_url=chapter_url,
                    output_dir=self.settings.get("output_dir"),
                    concurrency=self.settings.get("concurrency"),
                    to_pdf=self.settings.get("to_pdf"),
                    delete_images=self.settings.get("delete_images"),
                    verbose=True,
                    progress_callback=self.progress_bar.setValue
                )
                futures.append(executor.submit(downloader.download_chapter))

            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                try:
                    future.result()
                    progress = int(((i + 1) / total_chapters) * 100)
                    self.progress_bar.setValue(progress)
                except Exception as e:
                    self.worker.log.emit(f"An error occurred during chapter download: {e}")

        if self.worker._is_running:
            self.worker.log.emit("All chapters downloaded.")

    def download_finished(self):
        self.log_message("Download process finished.")
        self.progress_bar.setValue(100)
        self.download_widget.cancel_button.setEnabled(False)

    def cancel_download(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.log_message("Download cancelled by user.")
            self.progress_bar.setValue(0)
            self.download_widget.cancel_button.setEnabled(False)

    def apply_animations(self):
        self.search_animation = QPropertyAnimation(self.search_widget, b"geometry")
        self.search_animation.setDuration(500)
        self.search_animation.setStartValue(self.search_widget.geometry().adjusted(-200, 0, -200, 0))
        self.search_animation.setEndValue(self.search_widget.geometry())
        self.search_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.search_animation.start()

        self.chapter_animation = QPropertyAnimation(self.chapter_widget, b"geometry")
        self.chapter_animation.setDuration(500)
        self.chapter_animation.setStartValue(self.chapter_widget.geometry().adjusted(200, 0, 200, 0))
        self.chapter_animation.setEndValue(self.chapter_widget.geometry())
        self.chapter_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.chapter_animation.start()

        self.download_animation = QPropertyAnimation(self.download_widget, b"windowOpacity")
        self.download_animation.setDuration(800)
        self.download_animation.setStartValue(0)
        self.download_animation.setEndValue(1)
        self.download_animation.start()

        self.progress_animation = QPropertyAnimation(self.progress_bar, b"windowOpacity")
        self.progress_animation.setDuration(800)
        self.progress_animation.setStartValue(0)
        self.progress_animation.setEndValue(1)
        self.progress_animation.start()

        self.log_animation = QPropertyAnimation(self.log_output, b"windowOpacity")
        self.log_animation.setDuration(800)
        self.log_animation.setStartValue(0)
        self.log_animation.setEndValue(1)
        self.log_animation.start()

def main():
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')
    window = MangaDownloaderGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
