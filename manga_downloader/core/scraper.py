# core/scraper.py

import time
import requests
from bs4 import BeautifulSoup
from .config import BASE_URLS, HEADERS
import re
from urllib.parse import urljoin

class MangaScraper:
    def __init__(self, site_name):
        self.site_name = site_name
        self.base_url = BASE_URLS.get(site_name)
        if not self.base_url:
            raise ValueError(f"Invalid site name: {site_name}")

    def search_manga(self, title):
        # This will be implemented later
        pass

    def get_manga_title(self, manga_url):
        try:
            headers = HEADERS.copy()
            headers["Referer"] = self.base_url
            response = requests.get(manga_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "lxml")
            title_element = soup.find("div", class_="manga-info-content").find("h1")
            return title_element.text.strip() if title_element else "Unknown Title"
        except requests.exceptions.RequestException as e:
            print(f"Error fetching manga title: {e}")
            return "Unknown Title"

    def get_chapters(self, manga_url):
        try:
            headers = HEADERS.copy()
            headers["Referer"] = self.base_url
            response = requests.get(manga_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "lxml")
            chapter_list = []
            for chapter_element in soup.select(".chapter-list .row"):
                link = chapter_element.find("a")
                if link:
                    chapter_list.append({
                        "title": link.get("title"),
                        "url": link.get("href"),
                    })
            return chapter_list
        except requests.exceptions.RequestException as e:
            print(f"Error fetching chapters: {e}")
            return []

    def get_chapter_images(self, chapter_url):
        try:
            headers = HEADERS.copy()
            headers["Referer"] = self.base_url
            response = requests.get(chapter_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "lxml")
            image_urls = []

            # Find the script containing the chapter images
            script_content = ""
            for script in soup.find_all("script"):
                if "chapterImages" in str(script):
                    script_content = str(script)
                    break

            if script_content:
                # Extract the image paths
                image_paths_match = re.search(r'var chapterImages = \[(.*?)\];', script_content)
                if image_paths_match:
                    image_paths_str = image_paths_match.group(1)
                    image_paths = [path.strip().strip('"') for path in image_paths_str.split(',')]

                    # Extract the CDN URL
                    cdn_match = re.search(r'var cdns = \[(.*?)\];', script_content)
                    if cdn_match:
                        cdn_url_str = cdn_match.group(1)
                        cdn_url = cdn_url_str.strip().strip('"').replace('\\/', '/')
                        
                        from urllib.parse import urljoin
                        for path in image_paths:
                            image_urls.append(urljoin(cdn_url, path))

            return image_urls
        except requests.exceptions.RequestException as e:
            print(f"Error fetching chapter images: {e}")
            return []
