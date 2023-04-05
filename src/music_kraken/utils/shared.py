from typing import List, Set
import logging
import tempfile
import os
import configparser
from sys import platform as current_os
from pathlib import Path
import random

# modifies the garbage collector to speed up the program
# https://mkennedy.codes/posts/python-gc-settings-change-this-and-make-your-app-go-20pc-faster/
# https://web.archive.org/web/20221124122222/https://mkennedy.codes/posts/python-gc-settings-change-this-and-make-your-app-go-20pc-faster/
MODIFY_GC: bool = True

"""
I will now and then use those messages in the programm.
But I won't overuse them dw.

I will keep those messages, if you disagree with me on the messages,
feel free to fork the programm and edit them, or just edit them in the config
file once I implemented it.
"""
HAPPY_MESSAGES: List[str] = [
    "Support the artist.",
    "Star Me: https://github.com/HeIIow2/music-downloader",
    "🏳️‍⚧️🏳️‍⚧️ Trans rights are human rights. 🏳️‍⚧️🏳️‍⚧️",
    "🏳️‍⚧️🏳️‍⚧️ Trans women are women, trans men are men. 🏳️‍⚧️🏳️‍⚧️",
    "🏴‍☠️🏴‍☠️ Unite under one flag, fuck borders. 🏴‍☠️🏴‍☠️",
    "Join my Matrix Space: https://matrix.to/#/#music-kraken:matrix.org",
    "Gotta love the BPJM!! >:(",
    "🏳️‍⚧️🏳️‍⚧️ Protect trans youth. 🏳️‍⚧️🏳️‍⚧️"
]


def get_random_message() -> str:
    return random.choice(HAPPY_MESSAGES)


TEMP_DIR = Path(tempfile.gettempdir(), "music-downloader")
TEMP_DIR.mkdir(exist_ok=True)
LOG_PATH = Path(TEMP_DIR, "download_logs.log")


# configure logger default
logging.basicConfig(
    level=logging.INFO,
    format=logging.BASIC_FORMAT,
    handlers=[
        logging.FileHandler(Path(TEMP_DIR, LOG_PATH)),
        logging.StreamHandler()
    ]
)

OBJECT_LOGGER = logging.getLogger("objects")
TARGET_LOGGER = logging.getLogger("target")
DATABASE_LOGGER = logging.getLogger("database")

YOUTUBE_LOGGER = logging.getLogger("Youtube")
MUSIFY_LOGGER = logging.getLogger("Musify")
GENIUS_LOGGER = logging.getLogger("genius")
ENCYCLOPAEDIA_METALLUM_LOGGER = logging.getLogger("ma")

DOWNLOAD_LOGGER = logging.getLogger("download")
TAGGING_LOGGER = logging.getLogger("tagging")
CODEX_LOGGER = logging.getLogger("codex")

MUSIC_DIR: Path = Path(os.path.expanduser("~"), "Music")
NOT_A_GENRE_REGEX: List[str] = (
    r'^\.',     # is hidden/starts with a "."
)

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
        MUSIC_DIR: Path = Path(os.path.expandvars(xdg_config['xdg_music_dir'].strip('"')))

    except (FileNotFoundError, KeyError) as E:
        logger.warning(
            f"Missing file or No entry found for \"xdg_music_dir\" in: \"{XDG_USER_DIRS_FILE}\".\n"
            f"Will fallback on default \"$HOME/Music\"."
        )

TOR: bool = False
proxies = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
} if TOR else {}


# Only the formats with id3 metadata can be used
# https://www.audioranger.com/audio-formats.php
# https://web.archive.org/web/20230322234434/https://www.audioranger.com/audio-formats.php
ALLOWED_FILE_FORMATS: Set[str] = {
    "mp3", "mp2", "mp1",    # MPEG-1                ID3.2
    "wav", "wave", "rmi",   # RIFF (including WAV)  ID3.2
    "aiff", "aif", "aifc",  # AIFF                  ID3.2
    "aac", "aacp",          # Raw AAC	            ID3.2
    "tta",                  # True Audio            ID3.2
    "ape",                  # Monkey's Audio        ID3.1
    "mpc", "mpp", "mp+",    # MusePack              ID3.1
    "wv",                   # WavPack               ID3.1
    "ofr", "ofs"            # OptimFrog             ID3.1
}

# kB per second
BITRATE = 125
AUDIO_FORMAT = "mp3"
if AUDIO_FORMAT not in ALLOWED_FILE_FORMATS:
    raise ValueError(f"The Audio Format is not in {ALLOWED_FILE_FORMATS} ({AUDIO_FORMAT}).")

"""
available variables:
- genre
- label
- artist
- album
- song
- album_type
"""
DOWNLOAD_PATH = "{genre}/{artist}/{album_type}/{album}"
DOWNLOAD_FILE = "{song}.{audio_format}"
DEFAULT_VALUES = {
    "genre": "Various Genre",
    "label": "Various Labels",
    "artist": "Various Artists",
    "album": "Various Album",
    "song": "Various Song",
    "album_type": "Other",
    "audio_format": AUDIO_FORMAT
}


# size of the chunks that are streamed
CHUNK_SIZE = 1024
# this is a percentage describing the percentage of failed downloads,
# relative to the total downloads.
# If the percentage goes over this threshold DownloadResult returns the download errors
# in the __str__ method
SHOW_DOWNLOAD_ERRORS_THRESHOLD = 0.3
