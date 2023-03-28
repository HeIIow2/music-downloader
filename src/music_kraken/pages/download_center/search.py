from collections import defaultdict
from typing import Tuple, List, Set

from . import page_attributes
from ..abstract import Page

from ...objects import Options


class Search:
    def __init__(
        self,
        query: str,
        pages: Tuple[Page] = page_attributes.ALL_PAGES,
        exclude_pages: Set[Page] = set(),
        exclude_shady: bool = False
    ) -> None:
        _page_list: List[Page] = []
        _audio_page_list: List[Page] = []
        
        for page in pages:
            if exclude_shady and page in page_attributes.SHADY_PAGES:
                continue
            if page in exclude_pages:
                continue
            
            _page_list.append(page)
            
            if page in page_attributes.AUDIO_PAGES:
                _audio_page_list.append(page)
            
        self.pages: Tuple[Page] = tuple(_page_list)
        self.audio_pages: Tuple[Page] = tuple(_audio_page_list)
        
        self.current_option_dict = defaultdict(lambda: Options())
        
        self.search(query)
        
    def search(self, query: str):
        """
        # The Query
        
        You can define a new parameter with "#", 
        the letter behind it defines the *type* of parameter, 
        followed by a space "#a Psychonaut 4 #r Tired, Numb and #t Drop by Drop" 
        if no # is in the query it gets treated as "unspecified query"
        """
        
        for page in self.pages:
            self.current_option_dict[page] = page.search_by_query(query=query)
            
            print("-"*10, page.__name__, "-"*10)
            print(self.current_option_dict[page])
                