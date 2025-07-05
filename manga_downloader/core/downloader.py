import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from tqdm import tqdm
import concurrent.futures
from PIL import Image

from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "bold green",
    "chapter": "bold blue",
})
console = Console(theme=custom_theme)

class MangaDownloader:
    def __init__(self, manga_title, chapter_title, chapter_url, output_dir=None, concurrency=5, to_pdf=False, delete_images=False, verbose=False, console=console):
        self.manga_title = manga_title
        self.chapter_title = chapter_title
        self.chapter_url = chapter_url
        self.concurrency = concurrency
        self.to_pdf = to_pdf
        self.delete_images = delete_images
        self.verbose = verbose
        self.console = console
        base_download_path = output_dir if output_dir else os.path.join(os.getcwd(), "downloads")
        self.download_dir = os.path.join(base_download_path, self.manga_title, self.chapter_title)

    def _create_folder(self, path):
        Path(path).mkdir(parents=True, exist_ok=True)

    def _save_metadata(self):
        metadata = {
            "manga_title": self.manga_title,
            "chapter_title": self.chapter_title,
            "chapter_url": self.chapter_url,
        }
        metadata_path = os.path.join(self.download_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
        self.console.print(f"[success]Saved metadata to {metadata_path}[/success]")

    def _save_image_as_screenshot(self, page, img_element, index, save_dir):
        try:
            img_element.scroll_into_view_if_needed(timeout=30000)
            page.wait_for_timeout(500)

            # Get the bounding box of the image element
            bounding_box = img_element.bounding_box()
            if bounding_box:
                width = bounding_box['width']
                height = bounding_box['height']

                # Define a threshold for small images (e.g., logos, irrelevant graphics)
                # You might need to adjust these values based on typical manga page dimensions
                # and the size of unwanted images.
                # Define a threshold for small images (e.g., logos, irrelevant graphics).
                # An image will be skipped only if *both* its width and height are below this threshold.
                # This prevents skipping legitimate manga pages that might be partially rendered
                # but still have one large dimension.
                SMALL_IMAGE_THRESHOLD = 250

                if width < SMALL_IMAGE_THRESHOLD and height < SMALL_IMAGE_THRESHOLD:
                    if self.verbose:
                        self.console.print(f"[info]Skipping small image #{index} ({width}x{height})[/info]")
                    return # Skip saving if image is too small in both dimensions

            filename = os.path.join(save_dir, f"{index:03d}.png")
            img_element.screenshot(path=filename)
            # print(f"✅ Saved image #{index} as screenshot") # Removed for cleaner tqdm output
        except Exception as e:
            self.console.print(f"[danger]Failed to save image #{index}: {e}[/danger]")

    def download_chapter(self):
        self._create_folder(self.download_dir)

        with sync_playwright() as p:
            self.console.print("Launching browser...")
            browser = p.chromium.launch(headless=True) # Set to True for headless operation
            page = browser.new_page()
            page.goto(self.chapter_url, wait_until="networkidle")

            page.wait_for_selector("img", timeout=15000)
            img_elements = page.query_selector_all("img")
            self.console.print(f"Found {len(img_elements)} images")

            with tqdm(total=len(img_elements), desc=f"Downloading {self.chapter_title}") as pbar:
                for i, img in enumerate(img_elements, 1):
                    self._save_image_as_screenshot(page, img, i, self.download_dir)
                    pbar.update(1)

            browser.close()
            self._save_metadata()
            if self.to_pdf:
                self._convert_to_pdf()
                if self.delete_images:
                    self._delete_images()
            self.console.print("[success]Done![/success]")

    def _convert_to_pdf(self):
        image_paths = sorted([os.path.join(self.download_dir, f) for f in os.listdir(self.download_dir) if f.endswith(".png")])
        if not image_paths:
            self.console.print("[warning]No images found to convert to PDF.[/warning]")
            return

        images = []
        for img_path in image_paths:
            try:
                img = Image.open(img_path).convert("RGB")
                images.append(img)
            except Exception as e:
                self.console.print(f"[danger]Error opening image {img_path}: {e}[/danger]")

        if not images:
            self.console.print("[warning]No valid images to convert to PDF.[/warning]")
            return

        pdf_path = os.path.join(self.download_dir, f"{self.manga_title} - {self.chapter_title}.pdf")
        try:
            images[0].save(pdf_path, save_all=True, append_images=images[1:], quality=100)
            self.console.print(f"[success]Converted chapter to PDF: {pdf_path}[/success]")
        except Exception as e:
            self.console.print(f"[danger]Failed to convert to PDF: {e}[/danger]")

    def _delete_images(self):
        image_paths = sorted([os.path.join(self.download_dir, f) for f in os.listdir(self.download_dir) if f.endswith(".png")])
        for img_path in image_paths:
            try:
                os.remove(img_path)
            except Exception as e:
                self.console.print(f"[danger]Error deleting image {img_path}: {e}[/danger]")
        self.console.print("[success]Deleted downloaded images.[/success]")
