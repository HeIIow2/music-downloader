from typing import Tuple, Type, Dict, List

from ..objects import DatabaseObject
from ..utils.enums.source import SourcePages
from ..pages import Page, EncyclopaediaMetallum, Musify

class SearchResults:
    def __init__(
        self,
        pages: Tuple[Type[Page], ...]
        
    ) -> None:
        self.pages = pages
        # this would initialize a list for every page, which I don't think I want
        # self.results = Dict[Type[Page], List[DatabaseObject]] = {page: [] for page in self.pages}
        self.results = Dict[Type[Page], List[DatabaseObject]] = {}
        
    def add(self, page: Type[Page], search_result: List[DatabaseObject]):
        """
        adds a list of found music objects to the according page
        WARNING: if a page already has search results, they are just gonna be overwritten
        """
        
        self.results[page] = search_result
        
    def __str__(self) -> str:
        for page in self.pages:
            if page not in self.results:
                continue
        