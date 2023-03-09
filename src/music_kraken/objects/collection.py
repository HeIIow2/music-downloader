from typing import List, Iterable, Dict

from .source import SourceAttribute
from .parents import DatabaseObject
from ..utils import string_processing


class Collection:
    """
    This an class for the iterables
    like tracklist or discography
    """
    _data: List[SourceAttribute]

    _by_url: dict
    _by_attribute: dict

    def __init__(self, data: List[DatabaseObject] = None, element_type = None, *args, **kwargs) -> None:
        # Attribute needs to point to
        self.element_type = element_type
        
        self._data: list = list()
        
        """
        example of attribute_to_object_map
        the song objects are references pointing to objects
        in _data
        
        ```python
        {
            'id': {323: song_1, 563: song_2, 666: song_3},
            'url': {'www.song_2.com': song_2}
        }
        ```
        """
        self.attribute_to_object_map: Dict[str, dict] = dict()
        
        self.extend(data, merge_on_conflict=True)

    def sort(self, reverse: bool = False, **kwargs):
        self._data.sort(reverse=reverse, **kwargs)

    def map_element(self, element: SourceAttribute):
        for source_url in element.source_url_map:
            self._by_url[source_url] = element

        for attr in self.map_attributes:
            value = element.__getattribute__(attr)
            if type(value) != str:
                # this also throws out all none values
                continue

            self._by_attribute[attr][string_processing.unify(value)] = element

    def append(self, element: DatabaseObject, merge_on_conflict: bool = True):
        if self.element_type is not None and isinstance(element, self.element_type):
            raise TypeError(f"{type(element)} is not the set type {self.element_type}")

        for source_url in element.source_url_map:
            if source_url in self._by_url:
                if merge_on_conflict:
                    self._by_url[source_url].merge(element)
                return

        for attr in self.map_attributes:
            value = element.__getattribute__(attr)
            if value in self._by_attribute[attr]:
                if merge_on_conflict:
                    self._by_attribute[attr][value].merge(element)
                return

        self._data.append(element)
        self.map_element(element)

    def extend(self, element_list: Iterable, merge_on_conflict: bool = True):
        for element in element_list:
            self.append(element, merge_on_conflict=merge_on_conflict)

    def __iter__(self):
        for element in self._data:
            yield element

    def __str__(self) -> str:
        return "\n".join([f"{str(j).zfill(2)}: {i.__repr__()}" for j, i in enumerate(self._data)])

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, item):
        if type(item) != int:
            return ValueError("key needs to be an integer")

        return self._data[item]

    def copy(self) -> List:
        """
        returns a shallow copy of the data list
        """
        return self._data.copy()
