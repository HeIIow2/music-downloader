from typing import Set

from ..abstract import Page
from ..encyclopaedia_metallum import EncyclopaediaMetallum
from ..musify import Musify

ALL_PAGES: Set[Page] = {
    EncyclopaediaMetallum,
    Musify
}

AUDIO_PAGES: Set[Page] = {
    Musify
}
