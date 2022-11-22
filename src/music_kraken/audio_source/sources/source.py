from ...utils.shared import *
from typing import Tuple

from ...database import song as song_objects


logger = URL_DOWNLOAD_LOGGER

"""
The class "Source" is the superclass every class for specific audio
sources inherits from. This gives the advantage of a consistent
calling of the functions do search for a song and to download it.
"""


class AudioSource:
    @classmethod
    def fetch_source(cls, row: dict):
        logger.info(f"try getting source {row['title']} from {cls.__name__}")

    @classmethod
    def fetch_audio(cls, song: song_objects.Song, src: song_objects.Sourcet):
        logger.info(f"downloading audio from {src.url} from {cls.__name__} to {song['file']}")
