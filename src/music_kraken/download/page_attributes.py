from typing import Tuple, Type, Dict, List, Set

from ..utils.enums.source import SourcePages
from ..utils.support_classes import Query, EndThread
from ..pages import Page, EncyclopaediaMetallum, Musify

ALL_PAGES: Set[Type[Page]] = {
    EncyclopaediaMetallum,
    Musify
}

AUDIO_PAGES: Set[Type[Page]] = {
    Musify,
}

SHADY_PAGES: Set[Type[Page]] = {
    Musify,
}



class Pages:
    def __init__(self, exclude_pages: Set[Type[Page]] = None, exclude_shady: bool = False) -> None:
        # initialize all page instances
        self._page_instances: Dict[Type[Page], Page] = dict()
        
        exclude_pages = exclude_pages if exclude_pages is not None else set()
        
        if exclude_shady:
            exclude_pages = exclude_pages.union(SHADY_PAGES)
        
        if not exclude_pages.issubset(ALL_PAGES):
            raise ValueError(f"The excluded pages have to be a subset of all pages: {exclude_pages} | {ALL_PAGES}")
        
        def _set_to_tuple(page_set: Set[Type[Page]]) -> Tuple[Type[Page], ...]:
            return tuple(sorted(page_set, key=lambda page: page.__name__))
        
        self.pages: Tuple[Type[Page], ...] = _set_to_tuple(ALL_PAGES.difference(exclude_pages))
        self.audio_pages: Tuple[Type[Page], ...] = _set_to_tuple(set(self.pages).intersection(AUDIO_PAGES))
        
        for page_type in ALL_PAGES:
            self._page_instances[page_type] = page_type()
            
    def search(self, query: Query):
        for page_type in self.pages:
            self._page_instances[page_type].search(query=query)


"""
# this needs to be case-insensitive
SHORTHANDS = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')
for i, page in enumerate(ALL_PAGES):
    NAME_PAGE_MAP[type(page).__name__.lower()] = page
    NAME_PAGE_MAP[SHORTHANDS[i].lower()] = page
    
    PAGE_NAME_MAP[type(page)] = SHORTHANDS[i]

    SOURCE_PAGE_MAP[page.SOURCE_TYPE] = page
"""