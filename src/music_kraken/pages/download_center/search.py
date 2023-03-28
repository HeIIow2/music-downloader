from collections import defaultdict
from typing import Tuple, List, Set, Dict, Type

from . import page_attributes
from ..abstract import Page

from ...objects import Options


class MultiPageOptions:
    def __init__(
        self,
        max_displayed_options: int = 10,
        option_digits: int = 3
    ) -> None:
        self.max_displayed_options = max_displayed_options
        self.option_digits: int = option_digits
        
        self._current_option_dict: Dict[Type[Page], Options] = defaultdict(lambda: Options())

    def __getitem__(self, key: Page):
        return self._current_option_dict[key]
    
    def __setitem__(self, key: Page, value: Options):
        self._current_option_dict[key] = value
        
    def __repr__(self) -> str:
        lines: List[str] = []
        
        j = 0
        for page, options in self._current_option_dict.items():
            lines.append(f"----------{page.__name__}----------")
            
            
        return "\n".join(lines)


class Search:
    def __init__(
        self,
        query: str,
        pages: Tuple[Page] = page_attributes.ALL_PAGES,
        exclude_pages: Set[Page] = set(),
        exclude_shady: bool = False,
        max_displayed_options: int = 10,
        option_digits: int = 3
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
        
        self.max_displayed_options = max_displayed_options
        self.option_digits: int = option_digits
        
        self._option_history: List[MultiPageOptions] = []
        
        self._current_option: MultiPageOptions = self.next_options
        
        self.search(query)
        
    @property
    def next_options(self) -> MultiPageOptions:
        mpo = MultiPageOptions(
            max_displayed_options=self.max_displayed_options,
            option_digits=self.option_digits
        )
        self._option_history.append(mpo)
        return mpo
    
    @property
    def previous_options(self) -> MultiPageOptions:
        self._option_history.pop()
        return self._option_history[-1]
        
        
    def search(self, query: str):
        """
        # The Query
        
        You can define a new parameter with "#", 
        the letter behind it defines the *type* of parameter, 
        followed by a space "#a Psychonaut 4 #r Tired, Numb and #t Drop by Drop" 
        if no # is in the query it gets treated as "unspecified query"
        """
        
        for page in self.pages:
            self._current_option[page] = page.search_by_query(query=query)
            
        print(self._current_option)
                