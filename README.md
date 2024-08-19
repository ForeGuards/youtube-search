
# YouTube Watch History and Playlist Manager

This script allows you to manage your YouTube watch history and playlists directly from the command line. You can search for videos by title, view your playlists, export playlists to markdown files, and even delete playlists, all with easy-to-use commands.

## Prerequisites

Before using the script, ensure you have the following:

1. **Google API Credentials**:
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
   - Enable the YouTube Data API v3.
   - Create OAuth 2.0 credentials and download the `client_secret.json` file.
   - Place the `client_secret.json` file in the same directory as the script.

2. **Python 3.x**:
   - Ensure Python 3.x is installed on your system.

3. **Dependencies**:
   - The script automatically installs the necessary Python dependencies in a virtual environment.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Run the Script**:
   ```bash
   python yt-search-history.py
   ```

   The script will create a virtual environment, install the necessary dependencies, and authenticate with the YouTube Data API.

## Usage

### Options

```bash
-t, --title                🔍  Search for videos by title in your YouTube history.
-l, --playlists            📂  View your YouTube playlists.
-ep, --export-playlists    💾  Export all playlists to markdown files.
-dp, --delete-playlist     🗑  Delete a playlist by providing the playlist ID.
-h, --help                 Display this help message and exit.
```

### Examples

- **Search for Videos by Title**:
  ```bash
  python yt-search-history.py -t "CLI Tools"
  ```

- **View Playlists**:
  ```bash
  python yt-search-history.py -l
  ```

- **Export Playlists to Markdown**:
  ```bash
  python yt-search-history.py -ep
  ```

- **Delete a Playlist**:
  ```bash
  python yt-search-history.py -dp "YOUR_PLAYLIST_ID"
  ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
