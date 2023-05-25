from typing import Tuple, List, Set, Type, Optional, Dict

from . import page_attributes
from .download import Download
from .multiple_options import MultiPageOptions
from ..pages.abstract import Page
from ..utils.support_classes import DownloadResult, Query
from ..objects import DatabaseObject, Source, Artist, Song, Album
from ..utils.enums.source import SourcePages


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
    
    def _process_parsed(self, key_text: Dict[str, str], query: str) -> Query:
        song = None if not "t" in key_text else Song(title=key_text["t"], dynamic=True)
        album = None if not "r" in key_text else Album(title=key_text["r"], dynamic=True)
        artist = None if not "a" in key_text else Artist(name=key_text["a"], dynamic=True)
        
        if song is not None:
            song.album_collection.append(album)
            song.main_artist_collection.append(artist)
            return Query(raw_query=query, music_object=song)
        
        if album is not None:
            album.artist_collection.append(artist)
            return Query(raw_query=query, music_object=album)
        
        if artist is not None:
            return Query(raw_query=query, music_object=artist)
        

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
        
        special_characters = "#\\"
        query = query + " "
        
        key_text = {}
        
        skip_next = False
        escape_next = False
        new_text = ""
        latest_key: str = None
        for i in range(len(query) - 1):
            current_char = query[i]
            next_char = query[i+1]
            
            if skip_next:
                skip_next = False
                continue
            
            if escape_next:
                new_text += current_char
                escape_next = False
            
            # escaping
            if current_char == "\\":
                if next_char in special_characters:
                    escape_next = True
                    continue
                
            if current_char == "#":
                if latest_key is not None:
                    key_text[latest_key] = new_text
                    new_text = ""
                    
                latest_key = next_char
                skip_next = True
                continue
            
            new_text += current_char
        
        if latest_key is not None:
            key_text[latest_key] = new_text
            
            
        parsed_query: Query = self._process_parsed(key_text, query)
            

        for page in self.pages:
            self._current_option[page].extend(page.search(parsed_query))

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
        
        source = Source.match_url(url=url, referer_page=SourcePages.MANUAL)
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
                return page.download(music_object=self._current_option._derive_from, genre=genre, download_all=download_all)

        return DownloadResult(error_message=f"Didn't find a source for {self._current_option._derive_from.option_string}.")

