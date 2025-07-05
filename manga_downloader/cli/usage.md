# Manga Downloader CLI Usage

This document provides instructions on how to use the manga downloader from the command line.

## Listing Chapters

To list all available chapters for a manga, use the `list-chapters` command with the manga's URL.

### Command
```bash
python -m manga_downloader.cli.main list-chapters --manga-url "MANGA_URL"
```

### Example
```bash
python -m manga_downloader.cli.main list-chapters --manga-url "https://www.natomanga.com/manga/immortal-undertaker"
```

## Downloading Chapters

To download chapters of a manga, use the `download` command.

### Command
```bash
python -m manga_downloader.cli.main download --manga-url "MANGA_URL" [OPTIONS]
```

### Options
- `--manga-url`: (Required) The URL of the manga to download.
- `--chapter-range`: (Optional) The range of chapters to download (e.g., "5-10"). If omitted, all chapters will be downloaded.
- `--output-dir`: (Optional) The directory where the downloaded manga will be saved. Defaults to a "downloads" folder in the current directory.
- `--concurrency`: (Optional) The maximum number of concurrent image downloads. Defaults to 5.
- `--to-pdf`: (Optional) Convert the downloaded chapter into a PDF file.
- `--delete-images`: (Optional) Delete the downloaded images after converting to PDF. This option is only effective when used with `--to-pdf`.
- `--verbose`: (Optional) Enable verbose output for more detailed information.

### Examples

#### Download all chapters
```bash
python -m manga_downloader.cli.main download --manga-url "https://www.natomanga.com/manga/immortal-undertaker"
```

#### Download a specific range of chapters
```bash
python -m manga_downloader.cli.main download --manga-url "https://www.natomanga.com/manga/immortal-undertaker" --chapter-range "1-5"
```

#### Download chapters and convert to PDF
```bash
python -m manga_downloader.cli.main download --manga-url "https://www.natomanga.com/manga/immortal-undertaker" --to-pdf
```

#### Download chapters, convert to PDF, and delete images
```bash
python -m manga_downloader.cli.main download --manga-url "https://www.natomanga.com/manga/immortal-undertaker" --to-pdf --delete-images
