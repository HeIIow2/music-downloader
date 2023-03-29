from typing import Tuple, Type, Dict

from ..abstract import Page
from ..encyclopaedia_metallum import EncyclopaediaMetallum
from ..musify import Musify

page_names: Dict[str, Type[Page]] = dict()

shorthand_of_page: Dict[Type[Page], str] = dict()

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

# this needs to be case insensitive
SHORTHANDS = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')
for i, page in enumerate(ALL_PAGES):
    page_names[page.__name__.lower()] = page
    page_names[SHORTHANDS[i].lower()] = page
    
    shorthand_of_page[page] = SHORTHANDS[i]
