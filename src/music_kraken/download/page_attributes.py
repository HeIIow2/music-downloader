from typing import Tuple, Type, Dict, List, Set

from .results import SearchResults
from ..objects import DatabaseObject
from ..utils.enums.source import SourcePages
from ..utils.support_classes import Query, DownloadResult
from ..pages import Page, EncyclopaediaMetallum, Musify, INDEPENDENT_DB_OBJECTS

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
        self._source_to_page: Dict[SourcePages, Type[Page]] = dict()
        
        exclude_pages = exclude_pages if exclude_pages is not None else set()
        
        if exclude_shady:
            exclude_pages = exclude_pages.union(SHADY_PAGES)
        
        if not exclude_pages.issubset(ALL_PAGES):
            raise ValueError(f"The excluded pages have to be a subset of all pages: {exclude_pages} | {ALL_PAGES}")
        
        def _set_to_tuple(page_set: Set[Type[Page]]) -> Tuple[Type[Page], ...]:
            return tuple(sorted(page_set, key=lambda page: page.__name__))
        
        self._pages_set: Set[Type[Page]] = ALL_PAGES.difference(exclude_pages)
        self.pages: Tuple[Type[Page], ...] = _set_to_tuple(ALL_PAGES.difference(self.pages))
                                                           
        self._audio_pages_set: Set[Type[Page]] = self._pages_set.intersection(AUDIO_PAGES)
        self.audio_pages: Tuple[Type[Page], ...] = _set_to_tuple(self._audio_pages_set)
        
        for page_type in self.pages:
            self._page_instances[page_type] = page_type()
            self._source_to_page[page_type.SOURCE_TYPE] = page_type
            
    def search(self, query: Query) -> SearchResults:
        result = SearchResults()
        
        for page_type in self.pages:
            result.add(
                page=page_type,
                search_result=self._page_instances[page_type].search(query=query)
            )
            
        return result
    
    def fetch_details(self, music_object: DatabaseObject, stop_at_level: int = 1) -> DatabaseObject:
        if not isinstance(music_object, INDEPENDENT_DB_OBJECTS):
            return music_object
        
        for source_page in music_object.source_collection.source_pages:
            page_type = self._source_to_page[source_page]
            
            if page_type in self._pages_set:
                music_object.merge(self._page_instances[page_type].fetch_details(music_object=music_object, stop_at_level=stop_at_level))
        
        return music_object
    
    def download(self, music_object: DatabaseObject, genre: str, download_all: bool = False) -> DownloadResult:
        if not isinstance(music_object, INDEPENDENT_DB_OBJECTS):
            return DownloadResult(error_message=f"{type(music_object).__name__} can't be downloaded.")
        
        _page_types = set(self._source_to_page[src] for src in music_object.source_collection.source_pages)
        audio_pages = self._audio_pages_set.intersection(_page_types)
        
        for download_page in audio_pages:
            return self._page_instances[download_page].download(genre=genre, download_all=download_all)
        
        return DownloadResult(error_message=f"No audio source has been found for {music_object}.")


"""
# this needs to be case-insensitive
SHORTHANDS = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')
for i, page in enumerate(ALL_PAGES):
    NAME_PAGE_MAP[type(page).__name__.lower()] = page
    NAME_PAGE_MAP[SHORTHANDS[i].lower()] = page
    
    PAGE_NAME_MAP[type(page)] = SHORTHANDS[i]

    SOURCE_PAGE_MAP[page.SOURCE_TYPE] = page
"""