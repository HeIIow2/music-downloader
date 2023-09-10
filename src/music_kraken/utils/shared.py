import logging
import random
from pathlib import Path
from typing import List, Tuple, Set, Dict
from urllib.parse import ParseResult

from .path_manager import LOCATIONS
from .config import main_settings, logging_settings, youtube_settings
from .enums.album import AlbumType

DEBUG = True
if DEBUG:
    print("DEBUG ACTIVE")

def get_random_message() -> str:
    return random.choice(main_settings['happy_messages'])


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
