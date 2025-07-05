# cli/main.py

import typer
from manga_downloader.core.scraper import MangaScraper
from manga_downloader.core.downloader import MangaDownloader

app = typer.Typer()

@app.command()
def download(manga_url: str = typer.Option(..., "--manga-url", help="The URL of the manga to download."), chapter: int = typer.Option(..., "--chapter", help="The chapter number to download.")):
    """
    Download a specific chapter of a manga.
    """
    scraper = MangaScraper("natomanga")
    manga_title = scraper.get_manga_title(manga_url.strip('"'))
    chapters = scraper.get_chapters(manga_url.strip('"'))

    if chapter > len(chapters) or chapter < 1:
        print(f"Invalid chapter number. Please choose a chapter between 1 and {len(chapters)}.")
        return

    # Chapters are usually listed in descending order, so we need to adjust the index
    chapter_to_download = chapters[len(chapters) - chapter]

    print(f"Downloading {manga_title} - {chapter_to_download['title']}")

    downloader = MangaDownloader(manga_title, chapter_to_download['title'], chapter_to_download['url'])
    downloader.download_chapter()
    print("Download complete!")

if __name__ == "__main__":
    app()
