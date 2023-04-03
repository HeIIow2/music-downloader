from collections import defaultdict
from typing import Tuple, List, Dict, Type

from . import page_attributes
from ..abstract import Page
from ...objects import Options, DatabaseObject, Source


class MultiPageOptions:
    def __init__(
            self,
            max_displayed_options: int = 10,
            option_digits: int = 3,
            derived_from: DatabaseObject = None
    ) -> None:
        self.max_displayed_options = max_displayed_options
        self.option_digits: int = option_digits

        self._length = 0
        self._current_option_dict: Dict[Type[Page], Options] = defaultdict(lambda: Options())
        
        self._derive_from = derived_from

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
    