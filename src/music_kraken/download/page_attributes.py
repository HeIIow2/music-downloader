from typing import Tuple, Type, Dict

from ..utils.enums.source import SourcePages
from ..pages import Page, EncyclopaediaMetallum, Musify


NAME_PAGE_MAP: Dict[str, Page] = dict()
PAGE_NAME_MAP: Dict[Page, str] = dict()
SOURCE_PAGE_MAP: Dict[SourcePages, Page] = dict()

ALL_PAGES: Tuple[Page, ...] = (
    EncyclopaediaMetallum(),
    Musify()
)

AUDIO_PAGES: Tuple[Page, ...] = (
    Musify(),
)

SHADY_PAGES: Tuple[Page, ...] = (
    Musify(),
)

# this needs to be case-insensitive
SHORTHANDS = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')
for i, page in enumerate(ALL_PAGES):
    NAME_PAGE_MAP[type(page).__name__.lower()] = page
    NAME_PAGE_MAP[SHORTHANDS[i].lower()] = page
    
    PAGE_NAME_MAP[page] = SHORTHANDS[i]

    SOURCE_PAGE_MAP[page.SOURCE_TYPE] = page
    