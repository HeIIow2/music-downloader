from typing import List, Iterable, Dict
from collections import defaultdict
from dataclasses import dataclass

from .parents import DatabaseObject


@dataclass
class AppendResult:
    was_in_collection: bool
    current_element: DatabaseObject


class Collection:
    """
    This a class for the iterables
    like tracklist or discography
    """
    _data: List[DatabaseObject]

    _by_url: dict
    _by_attribute: dict

    def __init__(self, data: List[DatabaseObject] = None, element_type=None, *args, **kwargs) -> None:
        # Attribute needs to point to
        self.element_type = element_type

        self._data: List[DatabaseObject] = list()

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
        self._attribute_to_object_map: Dict[str, Dict[object, DatabaseObject]] = defaultdict(dict)
        self._used_ids: set = set()

        if data is not None:
            self.extend(data, merge_on_conflict=True)

    def sort(self, reverse: bool = False, **kwargs):
        self._data.sort(reverse=reverse, **kwargs)

    def map_element(self, element: DatabaseObject):
        for name, value in element.indexing_values:
            if value is None:
                continue

            self._attribute_to_object_map[name][value] = element

        self._used_ids.add(element.id)

    def unmap_element(self, element: DatabaseObject):
        for name, value in element.indexing_values:
            if value is None:
                continue

            if value in self._attribute_to_object_map[name]:
                if element is self._attribute_to_object_map[name][value]:
                    try:
                        self._attribute_to_object_map[name].pop(value)
                    except KeyError:
                        pass

    def append(self, element: DatabaseObject, merge_on_conflict: bool = True,
               merge_into_existing: bool = True) -> AppendResult:
        """
        :param element:
        :param merge_on_conflict:
        :param merge_into_existing:
        :return did_not_exist:
        """

        # if the element type has been defined in the initializer it checks if the type matches
        if self.element_type is not None and not isinstance(element, self.element_type):
            raise TypeError(f"{type(element)} is not the set type {self.element_type}")

        for name, value in element.indexing_values:
            if value in self._attribute_to_object_map[name]:
                existing_object = self._attribute_to_object_map[name][value]

                if not merge_on_conflict:
                    return AppendResult(True, existing_object)

                # if the object does already exist
                # thus merging and don't add it afterwards
                if merge_into_existing:
                    existing_object.merge(element)
                    # in case any relevant data has been added (e.g. it remaps the old object)
                    self.map_element(existing_object)
                    return AppendResult(True, existing_object)

                element.merge(existing_object)

                exists_at = self._data.index(existing_object)
                self._data[exists_at] = element

                self.unmap_element(existing_object)
                self.map_element(element)
                return AppendResult(True, existing_object)

        self._data.append(element)
        self.map_element(element)

        return AppendResult(False, element)

    def extend(self, element_list: Iterable[DatabaseObject], merge_on_conflict: bool = True,
               merge_into_existing: bool = True):
        for element in element_list:
            self.append(element, merge_on_conflict=merge_on_conflict, merge_into_existing=merge_into_existing)

    def __iter__(self):
        for element in self.shallow_list:
            yield element

    def __str__(self) -> str:
        return "\n".join([f"{str(j).zfill(2)}: {i.__repr__()}" for j, i in enumerate(self._data)])

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, key):
        if type(key) != int:
            return ValueError("key needs to be an integer")

        return self._data[key]

    def __setitem__(self, key, value: DatabaseObject):
        print(key, value)
        if type(key) != int:
            return ValueError("key needs to be an integer")

        old_item = self._data[key]
        self.unmap_element(old_item)
        self.map_element(value)

        self._data[key] = value

    @property
    def shallow_list(self) -> List[DatabaseObject]:
        """
        returns a shallow copy of the data list
        """
        return self._data.copy()
