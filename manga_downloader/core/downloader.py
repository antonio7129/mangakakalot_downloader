import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from tqdm import tqdm
from .config import DOWNLOAD_PATH

class MangaDownloader:
    def __init__(self, manga_title, chapter_title, chapter_url):
        self.manga_title = manga_title
        self.chapter_title = chapter_title
        self.chapter_url = chapter_url
        self.download_dir = os.path.join(DOWNLOAD_PATH, self.manga_title, self.chapter_title)

    def _create_folder(self, path):
        Path(path).mkdir(parents=True, exist_ok=True)

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
                    # print(f"ℹ️ Skipping small image #{index} ({width}x{height})") # For debugging
                    return # Skip saving if image is too small in both dimensions

            filename = os.path.join(save_dir, f"{index:03d}.png")
            img_element.screenshot(path=filename)
            # print(f"✅ Saved image #{index} as screenshot") # Removed for cleaner tqdm output
        except Exception as e:
            print(f"❌ Failed to save image #{index}: {e}")

    def download_chapter(self):
        self._create_folder(self.download_dir)

        with sync_playwright() as p:
            print("🚀 Launching browser...")
            browser = p.chromium.launch(headless=True) # Set to True for headless operation
            page = browser.new_page()
            page.goto(self.chapter_url, wait_until="networkidle")

            page.wait_for_selector("img", timeout=15000)
            img_elements = page.query_selector_all("img")
            print(f"📸 Found {len(img_elements)} images")

            with tqdm(total=len(img_elements), desc=f"Downloading {self.chapter_title}") as pbar:
                for i, img in enumerate(img_elements, 1):
                    self._save_image_as_screenshot(page, img, i, self.download_dir)
                    pbar.update(1)

            browser.close()
            print("✅ Done!")