import os
import sys
import subprocess
import argparse
import venv
from datetime import datetime

# Directory name for the virtual environment
VENV_DIR = "youtube_search_env"

# List of required packages and their corresponding import names
required_packages = {
    "google-auth": "google.auth",
    "google-auth-oauthlib": "google_auth_oauthlib",
    "google-auth-httplib2": "google_auth_httplib2",
    "google-api-python-client": "googleapiclient",
    "oauth2client": "oauth2client",
    "markdown2": "markdown2"
}

# Flag to check if re-execution is needed
REEXECUTE_FLAG = os.environ.get("REEXECUTE_FLAG", "0") == "1"

# Function to create the virtual environment
def create_venv(venv_dir):
    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment in {venv_dir}...")
        venv.create(venv_dir, with_pip=True)
    else:
        print(f"Virtual environment already exists in {venv_dir}.")

# Function to activate the virtual environment
def activate_venv(venv_dir):
    if os.name == "nt":  # Windows
        bin_dir = os.path.join(venv_dir, "Scripts")
    else:
        bin_dir = os.path.join(venv_dir, "bin")

    # Return the path to the Python executable within the virtual environment
    return os.path.join(bin_dir, "python")

# Function to check if a package is installed in the virtual environment
def is_package_installed(import_name, python_executable):
    try:
        subprocess.check_call(
            [python_executable, "-c", f"import {import_name}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False

# Function to install missing packages silently
def install_packages(packages, python_executable):
    for package_name, import_name in packages.items():
        if not is_package_installed(import_name, python_executable):
            subprocess.check_call(
                [python_executable, "-m", "pip", "install", package_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

# Function to re-execute the script within the virtual environment
def reexecute_in_venv(python_executable):
    if not REEXECUTE_FLAG:
        print("Re-executing the script within the virtual environment...")
        os.environ["REEXECUTE_FLAG"] = "1"
        os.execv(python_executable, [python_executable] + sys.argv)

# Function to deactivate the virtual environment
def deactivate_venv():
    if os.name != 'nt':
        return
    deactivate_script = os.path.join(VENV_DIR, "Scripts", "deactivate.bat")
    if os.path.exists(deactivate_script):
        subprocess.call(deactivate_script)

# Clear the terminal screen
def clear_screen():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

# Authenticate and construct the API service
def authenticate_youtube(client_secrets_file):
    import google_auth_oauthlib.flow
    import googleapiclient.discovery

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_local_server(port=0)  # This opens a browser for authentication
    return googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

# Function to retrieve and display user playlists
def get_playlists(youtube):
    request = youtube.playlists().list(
        part="snippet",
        mine=True,
        maxResults=25  # Adjust as needed
    )
    response = request.execute()
    playlists = response.get('items', [])
    return playlists

# Function to retrieve videos from a playlist
def get_videos_from_playlist(youtube, playlist_id):
    videos = []
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50  # Adjust as needed
    )
    while request:
        response = request.execute()
        videos.extend(response.get('items', []))
        request = youtube.playlistItems().list_next(request, response)
    return videos

# Function to create a markdown file from playlist data
def create_markdown_for_playlist(playlist_name, videos):
    safe_playlist_name = "".join([c for c in playlist_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    filename = f"{safe_playlist_name}.md"
    with open(filename, 'w') as f:
        f.write(f"# {playlist_name}\n\n")
        f.write("| Author | Title | Description | Release Date | URL |\n")
        f.write("|--------|-------|-------------|--------------|-----|\n")
        for video in videos:
            snippet = video['snippet']
            title = snippet['title']
            description = snippet.get('description', '').replace('\n', ' ').replace('|', '\\|')
            author = snippet.get('videoOwnerChannelTitle', 'Unknown')
            published_at = datetime.strptime(snippet['publishedAt'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
            video_id = snippet['resourceId']['videoId']
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Truncate the description and add "show more" if it's too long
            if len(description) > 50:
                description = f"{description[:50]}... [show more]({url})"
            
            f.write(f"| {author} | {title} | {description} | {published_at} | [Link]({url}) |\n")

def main():
    # Custom help formatter to add more space between option and description
    class CustomHelpFormatter(argparse.HelpFormatter):
        def __init__(self, prog):
            super().__init__(prog, max_help_position=40)

    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="A tool to manage your YouTube watch history and playlists.",
        formatter_class=CustomHelpFormatter,
    )

    parser.add_argument(
        "-t", "--title",
        metavar="",
        type=str,
        help="🔍  Search for videos by title in your YouTube history."
    )
    parser.add_argument(
        "-l", "--playlists",
        action="store_true",
        help="📂  View your YouTube playlists."
    )
    parser.add_argument(
        "-ep", "--export-playlists",
        action="store_true",
        help="💾  Export all playlists to markdown files."
    )
    parser.add_argument(
        "-dp", "--delete-playlist",
        metavar="",
        type=str,
        help="🗑  Delete a playlist by providing the playlist ID."
    )

    # Print help and exit if no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    return args

if __name__ == "__main__":
    # Clear the screen at the start
    clear_screen()

    # Parse arguments and show help if needed before any authentication
    args = main()

    try:
        # Create the virtual environment
        create_venv(VENV_DIR)

        # Activate the virtual environment and get the path to the Python executable
        python_executable = activate_venv(VENV_DIR)

        # Re-execute the script within the virtual environment if not already running within it
        reexecute_in_venv(python_executable)

        # Install required packages in the virtual environment silently
        install_packages(required_packages, python_executable)

        # Import necessary modules after ensuring the script is running in the virtual environment
        import google_auth_oauthlib
        import googleapiclient.discovery
        import markdown2

        # Authenticate YouTube
        client_secrets_file = os.path.expanduser(".client_secret.json")
        scopes = [
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.force-ssl"
        ]
        api_service_name = "youtube"
        api_version = "v3"

        youtube = authenticate_youtube(client_secrets_file)

        # Clear the screen again after consent
        clear_screen()

        # Execute the functionality based on arguments
        if args.playlists:
            playlists = get_playlists(youtube)
            for playlist in playlists:
                print(f"📜  {playlist['snippet']['title']} (ID: {playlist['id']})")
        elif args.delete_playlist:
            delete_playlist(youtube, args.delete_playlist)
        elif args.export_playlists:
            playlists = get_playlists(youtube)
            for playlist in playlists:
                playlist_name = playlist['snippet']['title']
                playlist_id = playlist['id']
                videos = get_videos_from_playlist(youtube, playlist_id)
                create_markdown_for_playlist(playlist_name, videos)
                print(f"✅  Exported playlist '{playlist_name}' to markdown file.")
        elif args.title:
            search_title = args.title
            search_videos_by_title(youtube, search_title)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Deactivate the virtual environment after use
        deactivate_venv()
