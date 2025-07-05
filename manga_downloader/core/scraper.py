# core/scraper.py

import time
import requests
from bs4 import BeautifulSoup
from .config import BASE_URLS, HEADERS
import re
from urllib.parse import urljoin

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

class MangaScraper:
    def __init__(self, site_name, verbose=False, console=console):
        self.site_name = site_name
        self.base_url = BASE_URLS.get(site_name)
        self.verbose = verbose
        self.console = console
        if not self.base_url:
            raise ValueError(f"Invalid site name: {site_name}")

    def search_manga(self, title):
        search_results = []
        try:
            headers = HEADERS.copy()
            headers["Referer"] = self.base_url
            
            if self.site_name == "mangakakalot" or self.site_name == "natomanga":
                search_url = f"{self.base_url}/search/story/{title.replace(' ', '_')}"
            else:
                search_url = f"{self.base_url}/search?q={title.replace(' ', '+')}"

            self.console.print(f"[info]Searching for '{title}' on {self.site_name} at {search_url}[/info]")
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "lxml")

            # --- Parsing logic for search results ---
            # This part might need adjustment based on the actual HTML structure of each site's search results.
            # Common patterns:
            # - mangakakalot.gg: div.story_item, h3 a
            # - natomanga.com: div.manga-item, a
            # - nelomanga.net: div.manga-item, a

            if self.site_name == "mangakakalot" or self.site_name == "natomanga":
                for item in soup.select("div.story_item"):
                    link_element = item.find("h3", class_="story_name").find("a")
                    if link_element:
                        title_text = link_element.text.strip()
                        url = urljoin(self.base_url, link_element.get("href"))
                        search_results.append({"title": title_text, "url": url})
            elif self.site_name == "nelomanga":
                for item in soup.select("div.manga-item"): # Assuming a common class for manga items
                    link_element = item.find("a")
                    if link_element and link_element.get("title"): # Assuming title is in the 'title' attribute of the link
                        title_text = link_element.get("title").strip()
                        url = urljoin(self.base_url, link_element.get("href"))
                        search_results.append({"title": title_text, "url": url})
            else:
                self.console.print(f"[warning]Search parsing not specifically implemented for {self.site_name}. Attempting generic parsing.[/warning]")
                # Generic parsing attempt: look for any link that might represent a manga
                for link_element in soup.find_all("a", href=True):
                    href = link_element.get("href")
                    text = link_element.get_text(strip=True)
                    if text and "/manga/" in href: # Simple heuristic
                        search_results.append({"title": text, "url": urljoin(self.base_url, href)})
                        if len(search_results) > 20: # Limit results for generic search
                            break

            if not search_results and self.verbose:
                self.console.print(f"[warning]No specific search results found for '{title}' on {self.site_name}. Check HTML structure.[/warning]")

        except requests.exceptions.RequestException as e:
            if self.verbose:
                self.console.print(f"[danger]Error during manga search on {self.site_name}: {e}[/danger]")
        except Exception as e:
            if self.verbose:
                self.console.print(f"[danger]An unexpected error occurred during search: {e}[/danger]")
        
        return search_results

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
            if self.verbose:
                self.console.print(f"[danger]Error fetching manga title: {e}[/danger]")
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
                    title = link.get("title")
                    url = link.get("href")
                    
                    # More flexible regex to capture numbers (integers or floats)
                    # It tries to find a number that might be preceded by "Chapter " or just a standalone number.
                    chapter_number_match = re.search(r"(?:Chapter\s*)?([\d.]+)", title, re.IGNORECASE)
                    
                    chapter_number = 0.0
                    if chapter_number_match:
                        try:
                            chapter_number = float(chapter_number_match.group(1))
                        except ValueError:
                            # If conversion to float fails, assign a very high number to push it to the end
                            chapter_number = float('inf') 
                    else:
                        # If no number is found, assign a very high number
                        chapter_number = float('inf')

                    chapter_list.append({
                        "title": title,
                        "url": url,
                        "number": chapter_number
                    })
            
            # Sort chapters by number in ascending order
            chapter_list.sort(key=lambda x: x["number"])
            return chapter_list
        except requests.exceptions.RequestException as e:
            if self.verbose:
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
