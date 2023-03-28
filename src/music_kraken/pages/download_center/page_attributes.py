from typing import Tuple, Type

from ..abstract import Page
from ..encyclopaedia_metallum import EncyclopaediaMetallum
from ..musify import Musify

ALL_PAGES: Tuple[Type[Page]] = (
    EncyclopaediaMetallum,
    Musify
)

AUDIO_PAGES: Tuple[Type[Page]] = (
    Musify,
)

SHADY_PAGES: Tuple[Type[Page]] = (
    Musify,
)

