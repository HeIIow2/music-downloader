from collections import defaultdict
from typing import Tuple, List, Set, Dict, Type, Union

from . import page_attributes
from .download import Download
from ..abstract import Page
from ...objects import Options, DatabaseObject


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
        
        return f"({page_attributes.shorthand_of_page[page]}) ------------------------{page.__name__:{page_name_fill}<{max_page_len}}------------"

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
        
        j = 0
        for page, options in self._current_option_dict.items():
            option_len = len(options)
            if option_len > self.max_displayed_options:
                option_len = self.max_displayed_options

            if j <= index < j + option_len:
                return options[j + option_len - 1], page

            j += option_len

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
    def previous_options(self) -> MultiPageOptions:
        self._option_history.pop()
        self._current_option = self._option_history[-1]
        return self._option_history[-1]

    def search(self, query: str) -> "Search":
        """
        # The Query
        
        You can define a new parameter with "#", 
        the letter behind it defines the *type* of parameter, 
        followed by a space "#a Psychonaut 4 #r Tired, Numb and #t Drop by Drop" 
        if no # is in the query it gets treated as "unspecified query"
        """

        for page in self.pages:
            self._current_option[page] = page.search_by_query(query=query)
            
        return self

    def choose_page(self, page: Type[Page]) -> "Search":
        if page not in page_attributes.ALL_PAGES:
            raise ValueError(f"Page \"{page.__name__}\" does not exist in page_attributes.ALL_PAGES")
        
        prev_mpo = self._current_option
        mpo = self.next_options
        
        mpo[page] = prev_mpo[page]
        return self

    
    def choose_index(self, index: int) -> "Search":
        db_object, page = self._current_option.choose_from_all_pages(index=index)
        
        music_object = self.fetch_details(db_object)
        
        mpo = self.next_options
        mpo[page] = music_object.options
        
        return self
    
    def choose(self, choosen: Union[Type[Page], int]) -> "Search":
        if type(choosen) == int:
            return self.choose_index(choosen)
        
        if choosen in page_attributes.ALL_PAGES:
            return self.choose_page(choosen)
        
        raise ValueError("choose is neiter an integer, nor a page in page_attributes.ALL_PAGES.")
    
    def next_input(self, query: str) -> "Search":
        query: str = query.strip()
        
        if query == ".":
            return self
        
        if query == "..":
            try:
                self.previous_options
            except IndexError:
                pass
            return self
        
        if query.isdigit():
            try:
                return self.choose_index(int(query))
            except IndexError:
                return self
            
        if query.lower() in page_attributes.page_names:
            return self.choose_page(page_attributes.page_names[query.lower()])
            
        return self.search(query=query)
