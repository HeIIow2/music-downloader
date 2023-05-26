from typing import Tuple, Type, Dict, List
import threading
from queue import Queue

from ..utils.enums.source import SourcePages
from ..utils.support_classes import Query, EndThread
from ..pages import Page, EncyclopaediaMetallum, Musify

ALL_PAGES: Tuple[Type[Page], ...] = (
    EncyclopaediaMetallum,
    Musify
)

AUDIO_PAGES: Tuple[Type[Page], ...] = (
    Musify,
)

SHADY_PAGES: Tuple[Type[Page], ...] = (
    Musify,
)


exit_threads = EndThread()
search_queue: Queue[Query] = Queue()

_page_threads: Dict[Type[Page], List[Page]] = dict()


"""
# this needs to be case-insensitive
SHORTHANDS = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')
for i, page in enumerate(ALL_PAGES):
    NAME_PAGE_MAP[type(page).__name__.lower()] = page
    NAME_PAGE_MAP[SHORTHANDS[i].lower()] = page
    
    PAGE_NAME_MAP[type(page)] = SHORTHANDS[i]

    SOURCE_PAGE_MAP[page.SOURCE_TYPE] = page
"""