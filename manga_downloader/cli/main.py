# cli/main.py

import typer
import concurrent.futures
from rich.console import Console
from rich.theme import Theme
from manga_downloader.core.scraper import MangaScraper
from manga_downloader.core.downloader import MangaDownloader

custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "bold green",
    "chapter": "bold blue",
})
console = Console(theme=custom_theme)

app = typer.Typer()

@app.command()
def download(
    manga_url: str = typer.Option(..., "--manga-url", help="The URL of the manga to download."),
    chapter_range: str = typer.Option(None, "--chapter-range", help="Optional: Range of chapters to download (e.g., '5-10'). If omitted, all chapters will be downloaded."),
    output_dir: str = typer.Option(None, "--output-dir", help="Optional: Directory to save the downloaded manga. Defaults to a predefined path."),
    concurrency: int = typer.Option(5, "--concurrency", help="Optional: Maximum number of concurrent image downloads. Default is 5."),
    to_pdf: bool = typer.Option(False, "--to-pdf", help="Optional: Convert downloaded chapter to PDF format."),
    delete_images: bool = typer.Option(False, "--delete-images", help="Optional: Delete images after converting to PDF."),
    verbose: bool = typer.Option(False, "--verbose", help="Optional: Enable verbose output for detailed progress and debugging."),
):
    """
    Download a specific chapter of a manga.
    """
    scraper = MangaScraper("natomanga", verbose=verbose)
    manga_title = scraper.get_manga_title(manga_url.strip('"'))
    chapters = scraper.get_chapters(manga_url.strip('"'))

    if chapter_range:
        try:
            chapter_range = chapter_range.strip('"')
            parts = chapter_range.split('-')
            if verbose:
                console.print(f"[info]Debug: parts={parts}[/info]")
            start, end = map(int, parts)
            if start > end or start < 1 or end > len(chapters):
                console.print(f"[danger]Invalid chapter range. Please use a range like '1-10' within the available chapters (1-{len(chapters)}).[/danger]")
                return
            chapters_to_download = chapters[len(chapters) - end : len(chapters) - start + 1]
            chapters_to_download.reverse() # To download in ascending order
        except ValueError:
            console.print("[danger]Invalid chapter range format. Please use 'start-end' (e.g., '5-10').[/danger]")
            return
    else:
        chapters_to_download = chapters # Download all chapters if no range is specified

    if not chapters_to_download:
        console.print("[warning]No chapters to download.[/warning]")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        for chapter_data in chapters_to_download:
            console.print(f"[info]Queueing {manga_title} - {chapter_data['title']} for download[/info]")
            downloader = MangaDownloader(manga_title, chapter_data['title'], chapter_data['url'], output_dir.strip('"') if output_dir else None, concurrency, to_pdf, delete_images, verbose, console=console)
            futures.append(executor.submit(downloader.download_chapter))

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                console.print(f"[danger]An error occurred during chapter download: {e}[/danger]")

    console.print("[success]All selected chapters downloaded![/success]")

@app.command()
def list_chapters(manga_url: str = typer.Option(..., "--manga-url", help="The URL of the manga to list chapters for."), verbose: bool = typer.Option(False, "--verbose", help="Optional: Enable verbose output.")):
    """
    List all available chapters for a given manga URL.
    """
    scraper = MangaScraper("natomanga", verbose=verbose) # Assuming "natomanga" for now
    manga_title = scraper.get_manga_title(manga_url.strip('"'))
    chapters = scraper.get_chapters(manga_url.strip('"'))

    if not chapters:
        console.print(f"[warning]No chapters found for {manga_title} at {manga_url}[/warning]")
        return

    console.print(f"\n[info]Chapters for {manga_title}:[/info]")
    for i, chapter in enumerate(reversed(chapters), 1):
        console.print(f"  [chapter]{i}. {chapter['title']}[/chapter]")

@app.command()
def search(
    title: str = typer.Argument(..., help="The title of the manga to search for."),
    site: str = typer.Option("natomanga", "--site", help="Optional: The manga website to search on. Default is 'natomanga'."),
    verbose: bool = typer.Option(False, "--verbose", help="Optional: Enable verbose output for detailed progress and debugging."),
):
    """
    Search for a manga by title on a specified website.
    """
    scraper = MangaScraper(site, verbose=verbose)
    console.print(f"[info]Searching for '{title}' on {site}...[/info]")
    search_results = scraper.search_manga(title)

    if search_results:
        console.print(f"[success]Search completed. Found {len(search_results)} results:[/success]")
        for i, result in enumerate(search_results, 1):
            console.print(f"  [info]{i}. Title: {result['title']}[/info]")
            console.print(f"     [info]URL: {result['url']}[/info]")
    else:
        console.print("[warning]Search completed. Found 0 results.[/warning]")
    
    console.print("[success]Search process finished.[/success]")

if __name__ == "__main__":
    app()
