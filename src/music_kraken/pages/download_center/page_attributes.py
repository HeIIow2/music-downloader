from typing import Tuple, Type, Dict

from ...objects import SourcePages
from ..abstract import Page
from ..encyclopaedia_metallum import EncyclopaediaMetallum
from ..musify import Musify

NAME_PAGE_MAP: Dict[str, Type[Page]] = dict()
PAGE_NAME_MAP: Dict[Type[Page], str] = dict()
SOURCE_PAGE_MAP: Dict[SourcePages, Type[Page]] = dict()

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
    NAME_PAGE_MAP[page.__name__.lower()] = page
    NAME_PAGE_MAP[SHORTHANDS[i].lower()] = page
    
    PAGE_NAME_MAP[page] = SHORTHANDS[i]

    SOURCE_PAGE_MAP[page.SOURCE_TYPE] = page
    