import musicbrainzngs
import logging
import tempfile
import os
import configparser
from sys import platform as current_os


TEMP_FOLDER = "music-downloader"
LOG_FILE = "download_logs.log"
TEMP_DATABASE_FILE = "metadata.db"
DATABASE_STRUCTURE_FILE = "database_structure.sql"
DATABASE_STRUCTURE_FALLBACK = "https://raw.githubusercontent.com/HeIIow2/music-downloader/master/assets/database_structure.sql"
temp_dir = os.path.join(tempfile.gettempdir(), TEMP_FOLDER)
if not os.path.exists(temp_dir):
    os.mkdir(temp_dir)

TEMP_DATABASE_PATH = os.path.join(temp_dir, TEMP_DATABASE_FILE)

# configure logger default
logging.basicConfig(
    level=logging.INFO,
    format=logging.BASIC_FORMAT,
    handlers=[
        logging.FileHandler(os.path.join(temp_dir, LOG_FILE)),
        logging.StreamHandler()
    ]
)

SONG_LOGGER = logging.getLogger("song-obj")
SEARCH_LOGGER = logging.getLogger("mb-cli")
INIT_PATH_LOGGER = logging.getLogger("init_path")
DATABASE_LOGGER = logging.getLogger("database")
METADATA_DOWNLOAD_LOGGER = logging.getLogger("metadata")
URL_DOWNLOAD_LOGGER = logging.getLogger("AudioSource")
YOUTUBE_LOGGER = logging.getLogger("Youtube")
MUSIFY_LOGGER = logging.getLogger("Musify")
PATH_LOGGER = logging.getLogger("create-paths")
DOWNLOAD_LOGGER = logging.getLogger("download")
LYRICS_LOGGER = logging.getLogger("lyrics")
GENIUS_LOGGER = logging.getLogger("genius")

NOT_A_GENRE = ".", "..", "misc_scripts", "Music", "script", ".git", ".idea"
MUSIC_DIR = os.path.join(os.path.expanduser("~"), "Music")

if current_os == "linux":
    # XDG_USER_DIRS_FILE reference: https://freedesktop.org/wiki/Software/xdg-user-dirs/
    XDG_USER_DIRS_FILE = os.path.join(os.path.expanduser("~"), ".config", "user-dirs.dirs")
    logger = logging.getLogger("init_path")
    logger.setLevel(logging.WARNING)
    try:
        with open(XDG_USER_DIRS_FILE, 'r') as f:
            data = "[XDG_USER_DIRS]\n" + f.read()
        config = configparser.ConfigParser(allow_no_value=True)
        config.read_string(data)
        xdg_config = config['XDG_USER_DIRS']
        MUSIC_DIR = os.path.expandvars(xdg_config['xdg_music_dir'].strip('"'))
    except (FileNotFoundError, KeyError) as E:
        logger.warning(f'''
Missing file or No entry found for "xdg_music_dir" in: \'{XDG_USER_DIRS_FILE}\'.
Will fallback on default '$HOME/Music'.
----
                                ''')
TOR = False
proxies = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
} if TOR else {}

# only the sources here will get downloaded, in the order the list is ordered
AUDIO_SOURCES = ["Musify", "Youtube"]
