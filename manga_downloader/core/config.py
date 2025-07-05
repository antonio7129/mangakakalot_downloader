# core/config.py

# Base URLs for the manga websites
BASE_URLS = {
    "natomanga": "https://www.natomanga.com",
    "mangakakalot": "https://mangakakalot.gg",
    "nelomanga": "https://nelomanga.net",
}

# Headers to mimic a real browser visit
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "Referer": "https://www.natomanga.com/",
}

# Download settings
DOWNLOAD_PATH = "manga_downloads"  # Root folder for downloaded manga