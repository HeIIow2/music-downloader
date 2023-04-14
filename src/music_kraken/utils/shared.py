import logging
import random
from pathlib import Path
from typing import List, Set, Tuple

from .path_manager import LOCATIONS
from .config import LOGGING_SECTION, AUDIO_SECTION

# modifies the garbage collector to speed up the program
# https://mkennedy.codes/posts/python-gc-settings-change-this-and-make-your-app-go-20pc-faster/
# https://web.archive.org/web/20221124122222/https://mkennedy.codes/posts/python-gc-settings-change-this-and-make-your-app-go-20pc-faster/
MODIFY_GC: bool = True

ID_BITS: int = 64
ID_RANGE: Tuple[int, int] = (0, int(2**ID_BITS))

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


TEMP_DIR = LOCATIONS.TEMP_DIRECTORY
LOG_PATH = LOCATIONS.get_log_file("download_logs.log")
MUSIC_DIR: Path = LOCATIONS.MUSIC_DIRECTORY

NOT_A_GENRE_REGEX: Tuple[str] = (
    r'^\.',     # is hidden/starts with a "."
)


# configure logger default
logging.basicConfig(
    level=LOGGING_SECTION.LOG_LEVEL.object_from_value,
    format=LOGGING_SECTION.FORMAT.object_from_value,
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)

OBJECT_LOGGER = LOGGING_SECTION.OBJECT_LOGGER.object_from_value
DATABASE_LOGGER = LOGGING_SECTION.DATABASE_LOGGER.object_from_value

YOUTUBE_LOGGER = LOGGING_SECTION.YOUTUBE_LOGGER.object_from_value
MUSIFY_LOGGER = LOGGING_SECTION.MUSIFY_LOGGER.object_from_value
GENIUS_LOGGER = LOGGING_SECTION.GENIUS_LOGGER
ENCYCLOPAEDIA_METALLUM_LOGGER = LOGGING_SECTION.ENCYCLOPAEDIA_METALLUM_LOGGER.object_from_value

DOWNLOAD_LOGGER = LOGGING_SECTION.DOWNLOAD_LOGGER.object_from_value
TAGGING_LOGGER = LOGGING_SECTION.TAGGING_LOGGER.object_from_value
CODEX_LOGGER = LOGGING_SECTION.CODEX_LOGGER.object_from_value

# kB per second
BITRATE = AUDIO_SECTION.BITRATE.object_from_value
AUDIO_FORMAT = AUDIO_SECTION.AUDIO_FORMAT.object_from_value


DOWNLOAD_PATH = AUDIO_SECTION.DOWNLOAD_PATH.object_from_value
DOWNLOAD_FILE = AUDIO_SECTION.DOWNLOAD_FILE.object_from_value
DEFAULT_VALUES = {
    "genre": AUDIO_SECTION.DEFAULT_GENRE.object_from_value,
    "label": AUDIO_SECTION.DEFAULT_LABEL.object_from_value,
    "artist": AUDIO_SECTION.DEFAULT_ARTIST.object_from_value,
    "album": AUDIO_SECTION.DEFAULT_ALBUM.object_from_value,
    "song": AUDIO_SECTION.DEFAULT_SONG.object_from_value,
    "album_type": AUDIO_SECTION.DEFAULT_ALBUM_TYPE.object_from_value,
    "audio_format": AUDIO_FORMAT
}


TOR: bool = False
proxies = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
} if TOR else {}

# size of the chunks that are streamed
CHUNK_SIZE = 1024
# this is a percentage describing the percentage of failed downloads,
# relative to the total downloads.
# If the percentage goes over this threshold DownloadResult returns the download errors
# in the __str__ method
SHOW_DOWNLOAD_ERRORS_THRESHOLD = 0.3
