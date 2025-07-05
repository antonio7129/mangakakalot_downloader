# Manga Downloader GUI Usage

This document explains how to use the graphical user interface (GUI) for the Manga Downloader application.

## Overview

The GUI provides an intuitive way to search for manga, view its chapters, and download them from various supported manga websites.

## Main Window

Upon launching the GUI, you will see the main window with the following key elements:

-   **Manga Title Search Bar:** An input field where you can type the name of the manga you want to search for.
-   **Search Button:** Click this button to initiate the manga search based on the title entered.
-   **Site Selection (Dropdown/Radio Buttons):** Allows you to choose which manga website to search on (e.g., MangaKakalot, Natomanga, Nelomanga).
-   **Search Results Area:** Displays a list of manga titles that match your search query. Each result typically shows the manga title and a link.
-   **Manga Details Area:** Once you select a manga from the search results, this area will display more information about the selected manga, including its title and a list of available chapters.
-   **Chapter List:** Shows all chapters for the selected manga, usually with their titles and numbers.
-   **Download Button:** Initiates the download process for the selected chapters.
-   **Settings Button:** Opens a dialog for configuring application settings (e.g., download directory, verbose mode).
-   **Progress Bar/Status Area:** Provides feedback on the download progress and other operations.

## How to Use

1.  **Launch the GUI:**
    Run the application using the command: `python -m manga_downloader.gui.main`

2.  **Select a Manga Website:**
    Choose your desired manga website from the site selection option (e.g., "mangakakalot", "natomanga", "nelomanga").

3.  **Search for Manga:**
    In the "Manga Title Search Bar," type the full or partial title of the manga you are looking for (e.g., "Solo Leveling", "One Piece").
    Click the "Search" button.
    The "Search Results Area" will populate with matching manga titles.

4.  **Select a Manga from Results:**
    Click on a manga title in the "Search Results Area" to view its details and available chapters. The "Manga Details Area" and "Chapter List" will update.

5.  **Select Chapters to Download:**
    In the "Chapter List," you can select individual chapters or a range of chapters you wish to download. (Specific selection methods like checkboxes or range input might vary based on implementation).

6.  **Download Chapters:**
    Click the "Download" button. The application will start downloading the selected chapters to your configured download directory.
    Monitor the "Progress Bar/Status Area" for download status.

7.  **Access Settings:**
    Click the "Settings" button to open the settings dialog. Here you can:
    *   Change the default download directory.
    *   Toggle verbose mode for more detailed console output during operations.
    *   (Potentially) Configure other site-specific settings or proxy settings.

## Important Notes

-   **Cloudflare Protection:** Some websites (like `nelomanga.net`) might be protected by Cloudflare, which can sometimes prevent automated searching. If you encounter issues, ensure your `cookies.json` file (located in `manga_downloader/core/`) is updated with valid Cloudflare bypass cookies from your browser.
-   **Error Handling:** The GUI will display error messages in the status area or console if issues occur during searching or downloading.
-   **Referer Headers:** The application automatically sets appropriate `Referer` headers to mimic browser behavior, which is crucial for some sites.
-   **Chapter Sorting:** Chapters are automatically sorted by their numerical order for easier navigation.
