from collections import defaultdict
from typing import Tuple, List, Set, Dict, Type, Union, Optional

from . import page_attributes
from .download import Download
from ..abstract import Page
from ...objects import Options, DatabaseObject, Source


class MultiPageOptions:
    def __init__(
            self,
            max_displayed_options: int = 10,
            option_digits: int = 3
    ) -> None:
        self.max_displayed_options = max_displayed_options
        self.option_digits: int = option_digits

        self._length = 0
        self._current_option_dict: Dict[Type[Page], Options] = defaultdict(lambda: Options())

    def __getitem__(self, key: Type[Page]):
        return self._current_option_dict[key]

    def __setitem__(self, key: Type[Page], value: Options):
        self._current_option_dict[key] = value
        
        self._length = 0
        for key in self._current_option_dict:
            self._length += 1

    def __len__(self) -> int:
        return self._length

    def get_page_str(self, page: Type[Page]) -> str:
        page_name_fill = "-"
        max_page_len = 21
        
        return f"({page_attributes.PAGE_NAME_MAP[page]}) ------------------------{page.__name__:{page_name_fill}<{max_page_len}}------------"

    def string_from_all_pages(self) -> str:
        if self._length == 1:
            for key in self._current_option_dict:
                return self.string_from_single_page(key)
        
        lines: List[str] = []

        j = 0
        for page, options in self._current_option_dict.items():
            lines.append(self.get_page_str(page))

            i = -1

            option_obj: DatabaseObject
            for i, option_obj in enumerate(options):
                if i >= self.max_displayed_options:
                    lines.append("...")
                    break

                lines.append(f"{j + i:0{self.option_digits}} {option_obj.option_string}")

            j += i + 1

        return "\n".join(lines)

    def choose_from_all_pages(self, index: int) -> Tuple[DatabaseObject, Type[Page]]:
        if self._length == 1:
            for key in self._current_option_dict:
                return self.choose_from_single_page(key, index), key
        
        sum_of_length = 0
        for page, options in self._current_option_dict.items():
            option_len = min((len(options), self.max_displayed_options))

            index_of_list = index - sum_of_length
            
            if index_of_list < option_len:
                return options[index_of_list], page

            sum_of_length += option_len

        raise IndexError("index is out of range")

    def string_from_single_page(self, page: Type[Page]) -> str:
        lines: List[str] = [self.get_page_str(page)]

        option_obj: DatabaseObject
        for i, option_obj in enumerate(self._current_option_dict[page]):
            lines.append(f"{i:0{self.option_digits}} {option_obj.option_string}")

        return "\n".join(lines)

    def choose_from_single_page(self, page: Type[Page], index: int) -> DatabaseObject:
        return self._current_option_dict[page][index]

    def __repr__(self) -> str:
        return self.string_from_all_pages()


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

        self._current_option: MultiPageOptions = self.next_options


    def __repr__(self):
        return self._current_option.__repr__()

    @property
    def next_options(self) -> MultiPageOptions:
        mpo = MultiPageOptions(
            max_displayed_options=self.max_displayed_options,
            option_digits=self.option_digits
        )
        self._option_history.append(mpo)
        self._current_option = mpo
        return mpo

    @property
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
        """

        for page in self.pages:
            self._current_option[page] = page.search_by_query(query=query)

    def choose_page(self, page: Type[Page]):
        if page not in page_attributes.ALL_PAGES:
            raise ValueError(f"Page \"{page.__name__}\" does not exist in page_attributes.ALL_PAGES")
        
        prev_mpo = self._current_option
        mpo = self.next_options
        
        mpo[page] = prev_mpo[page]
        
    def get_page_from_query(self, query: str) -> Optional[Type[Page]]:
        page = page_attributes.NAME_PAGE_MAP.get(query.lower().strip())
        
        if page in self.pages:
            return page

    def choose_index(self, index: int):
        db_object, page = self._current_option.choose_from_all_pages(index=index)
        
        music_object = self.fetch_details(db_object)
        
        mpo = self.next_options
        mpo[page] = music_object.options
        
    def goto_previous(self):
        try:
            self._current_option = self._previous_options
        except IndexError:
            pass
        
    def search_url(self, url: str) -> bool:
        source = Source.match_url(url=url)
        if source is None: 
            return False
        
        new_object = self.fetch_source(source)
        if new_object is None:
            return False
        
        page = page_attributes.SOURCE_PAGE_MAP[source.page_enum]
        mpo = self.next_options
        mpo[page] = new_object.options
        
        return True
