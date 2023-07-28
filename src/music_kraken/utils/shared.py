import logging
import random
from pathlib import Path
from typing import List, Tuple, Set, Dict
from urllib.parse import ParseResult

from .path_manager import LOCATIONS
from .config import LOGGING_SECTION, AUDIO_SECTION, CONNECTION_SECTION, MISC_SECTION, PATHS_SECTION
from .enums.album import AlbumType

CONFIG_FILE = LOCATIONS.CONFIG_FILE

# modifies the garbage collector to speed up the program
# https://mkennedy.codes/posts/python-gc-settings-change-this-and-make-your-app-go-20pc-faster/
# https://web.archive.org/web/20221124122222/https://mkennedy.codes/posts/python-gc-settings-change-this-and-make-your-app-go-20pc-faster/
MODIFY_GC: bool = MISC_SECTION.MODIFY_GC.object_from_value

ID_BITS: int = MISC_SECTION.ID_BITS.object_from_value
ID_RANGE: Tuple[int, int] = (0, int(2 ** ID_BITS))

"""
I will now and then use those messages in the programm.
But I won't overuse them dw.

I will keep those messages, if you disagree with me on the messages,
feel free to fork the programm and edit them, or just edit them in the config
file once I implemented it. (I did it is in ~/.config/music-kraken/music-kraken.conf)
"""
HAPPY_MESSAGES: List[str] = MISC_SECTION.HAPPY_MESSAGES.object_from_value


def get_random_message() -> str:
    return random.choice(HAPPY_MESSAGES)


TEMP_DIR = PATHS_SECTION.TEMP_DIRECTORY.object_from_value
LOG_PATH = PATHS_SECTION.LOG_PATH.object_from_value
MUSIC_DIR: Path = PATHS_SECTION.MUSIC_DIRECTORY.object_from_value

NOT_A_GENRE_REGEX: Tuple[str] = PATHS_SECTION.NOT_A_GENRE_REGEX.object_from_value

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
YOUTUBE_MUSIC_LOGGER = LOGGING_SECTION.YOUTUBE_MUSIC_LOGGER.object_from_value
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

TOR: bool = CONNECTION_SECTION.USE_TOR.object_from_value
PROXIES_LIST: List[Dict[str, str]] = CONNECTION_SECTION.PROXIES.object_from_value
proxies = {}
if len(CONNECTION_SECTION.PROXIES) > 0:
    """
    TODO
    rotating proxies
    """
    proxies = CONNECTION_SECTION.PROXIES.object_from_value[0]
if TOR:
    proxies = {
        'http': f'socks5h://127.0.0.1:{CONNECTION_SECTION.TOR_PORT.object_from_value}',
        'https': f'socks5h://127.0.0.1:{CONNECTION_SECTION.TOR_PORT.object_from_value}'
    }
INVIDIOUS_INSTANCE: ParseResult = CONNECTION_SECTION.INVIDIOUS_INSTANCE.object_from_value
PIPED_INSTANCE: ParseResult = CONNECTION_SECTION.PIPED_INSTANCE.object_from_value

ALL_YOUTUBE_URLS: List[ParseResult] = CONNECTION_SECTION.ALL_YOUTUBE_URLS.object_from_value
ENABLE_SPONSOR_BLOCK: bool = CONNECTION_SECTION.SPONSOR_BLOCK.object_from_value

# size of the chunks that are streamed
CHUNK_SIZE = CONNECTION_SECTION.CHUNK_SIZE.object_from_value
# this is a percentage describing the percentage of failed downloads,
# relative to the total downloads.
# If the percentage goes over this threshold DownloadResult returns the download errors
# in the __str__ method
SHOW_DOWNLOAD_ERRORS_THRESHOLD = CONNECTION_SECTION.SHOW_DOWNLOAD_ERRORS_THRESHOLD.object_from_value

SORT_BY_DATE = AUDIO_SECTION.SORT_BY_DATE.object_from_value
SORT_BY_ALBUM_TYPE = AUDIO_SECTION.SORT_BY_ALBUM_TYPE.object_from_value

ALBUM_TYPE_BLACKLIST: Set[AlbumType] = set(AUDIO_SECTION.ALBUM_TYPE_BLACKLIST.object_from_value)

THREADED = False

ENABLE_RESULT_HISTORY: bool = MISC_SECTION.ENABLE_RESULT_HISTORY.object_from_value
HISTORY_LENGTH: int = MISC_SECTION.HISTORY_LENGTH.object_from_value

HELP_MESSAGE = """
to search:
> s: {query or url}
> s: https://musify.club/release/some-random-release-183028492
> s: #a {artist} #r {release} #t {track}

to download:
> d: {option ids or direct url}
> d: 0, 3, 4
> d: 1
> d: https://musify.club/release/some-random-release-183028492

have fun :3
""".strip()

FFMPEG_BINARY: Path = PATHS_SECTION.FFMPEG_BINARY.object_from_value

HASNT_YET_STARTED: bool = MISC_SECTION.HASNT_YET_STARTED.object_from_value
SLEEP_AFTER_YOUTUBE_403: float = CONNECTION_SECTION.SLEEP_AFTER_YOUTUBE_403.object_from_value

DEBUG = True
if DEBUG:
    print("DEBUG ACTIVE")

YOUTUBE_MUSIC_CLEAN_DATA: bool = CONNECTION_SECTION.YOUTUBE_MUSIC_CLEAN_DATA.object_from_value
