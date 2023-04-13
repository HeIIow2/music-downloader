import logging
import random
from pathlib import Path
from typing import List, Set, Tuple

from .path_manager import LOCATIONS

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


ID_BITS: int = 64
ID_RANGE: Tuple[int, int] = (0, int(2**ID_BITS))

TEMP_DIR = LOCATIONS.TEMP_DIRECTORY
LOG_PATH = LOCATIONS.get_log_file("download_logs.log")
MUSIC_DIR: Path = LOCATIONS.MUSIC_DIRECTORY


# configure logger default
logging.basicConfig(
    level=logging.INFO,
    format=logging.BASIC_FORMAT,
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)

OBJECT_LOGGER = logging.getLogger("objects")
DATABASE_LOGGER = logging.getLogger("database")

YOUTUBE_LOGGER = logging.getLogger("Youtube")
MUSIFY_LOGGER = logging.getLogger("Musify")
GENIUS_LOGGER = logging.getLogger("genius")
ENCYCLOPAEDIA_METALLUM_LOGGER = logging.getLogger("ma")

DOWNLOAD_LOGGER = logging.getLogger("download")
TAGGING_LOGGER = logging.getLogger("tagging")
CODEX_LOGGER = logging.getLogger("codex")

NOT_A_GENRE_REGEX: Tuple[str] = (
    r'^\.',     # is hidden/starts with a "."
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
