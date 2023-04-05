from typing import Tuple, List, Set, Type, Optional

from . import page_attributes
from .download import Download
from .multiple_options import MultiPageOptions
from ..abstract import Page
from ..support_classes.download_result import DownloadResult
from ...objects import DatabaseObject, Source


class Search(Download):
    def __init__(
            self,
            pages: Tuple[Type[Page]] = page_attributes.ALL_PAGES,
            exclude_pages: Set[Type[Page]] = set(),
            exclude_shady: bool = False,
            max_displayed_options: int = 10,
            option_digits: int = 3,
    ) -> None:
        super().__init__(
            pages=pages,
            exclude_pages=exclude_pages,
            exclude_shady=exclude_shady
        )

        self.max_displayed_options = max_displayed_options
        self.option_digits: int = option_digits

        self._option_history: List[MultiPageOptions] = []

        self._current_option: MultiPageOptions = self.next_options()


    def __repr__(self):
        return self._current_option.__repr__()
    
    def next_options(self, derive_from: DatabaseObject = None) -> MultiPageOptions:
        mpo = MultiPageOptions(
            max_displayed_options=self.max_displayed_options,
            option_digits=self.option_digits,
            derived_from=derive_from
        )
        
        self._option_history.append(mpo)
        self._current_option = mpo
        
        return mpo

    def _previous_options(self) -> MultiPageOptions:
        self._option_history.pop()
        self._current_option = self._option_history[-1]
        
        return self._option_history[-1]

    def search(self, query: str):
        """
        # The Query
        
        You can define a new parameter with "#", 
        the letter behind it defines the *type* of parameter, 
        followed by a space "#a Psychonaut 4 #r Tired, Numb and #t Drop by Drop" 
        if no # is in the query it gets treated as "unspecified query"
        
        doesn't set derived_from thus,
        can't download right after
        """

        for page in self.pages:
            self._current_option[page] = page.search_by_query(query=query)

    def choose_page(self, page: Type[Page]):
        """
        doesn't set derived_from thus,
        can't download right after
        """
        
        if page not in page_attributes.ALL_PAGES:
            raise ValueError(f"Page \"{page.__name__}\" does not exist in page_attributes.ALL_PAGES")
        
        prev_mpo = self._current_option
        mpo = self.next_options()
        
        mpo[page] = prev_mpo[page]
        
    def get_page_from_query(self, query: str) -> Optional[Type[Page]]:
        """
        query can be for example:
        "a" or "EncyclopaediaMetallum" to choose a page
        """
        
        page = page_attributes.NAME_PAGE_MAP.get(query.lower().strip())
        
        if page in self.pages:
            return page
        
    def _get_page_from_source(self, source: Source) -> Optional[Type[Page]]:
        return page_attributes.SOURCE_PAGE_MAP.get(source.page_enum)

    def choose_index(self, index: int):
        db_object, page = self._current_option.choose_from_all_pages(index=index)
        
        music_object = self.fetch_details(db_object)
        mpo = self.next_options(derive_from=music_object)
        
        mpo[page] = music_object.options
        
    def goto_previous(self):
        try:
            self._previous_options()
        except IndexError:
            pass
        
    def search_url(self, url: str) -> bool:
        """
        sets derived_from, thus
        can download directly after
        """
        
        source = Source.match_url(url=url)
        if source is None: 
            return False
        
        new_object = self.fetch_source(source)
        if new_object is None:
            return False
        
        page = page_attributes.SOURCE_PAGE_MAP[source.page_enum]
        mpo = self.next_options(derive_from=new_object)
        mpo[page] = new_object.options
        
        return True
    
    def download_chosen(self, genre: str = None, download_all: bool = False, **kwargs) -> DownloadResult:
        if self._current_option._derive_from is None:
            return DownloadResult(error_message="No option has been chosen yet.")
        
        source: Source
        for source in self._current_option._derive_from.source_collection:
            page = self._get_page_from_source(source=source)
            
            if page in self.audio_pages:
                return page.download(music_object=self._current_option._derive_from, genre=genre, download_all=download_all, **kwargs)

        return DownloadResult(error_message=f"Didn't find a source for {self._current_option._derive_from.option_string}.")

