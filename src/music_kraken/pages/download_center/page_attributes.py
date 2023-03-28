from typing import Tuple

from ..abstract import Page
from ..encyclopaedia_metallum import EncyclopaediaMetallum
from ..musify import Musify

ALL_PAGES: Tuple[Page] = (
    EncyclopaediaMetallum,
    Musify
)

AUDIO_PAGES: Tuple[Page] = (
    Musify,
)

SHADY_PAGES: Tuple[Page] = (
    Musify,
)

