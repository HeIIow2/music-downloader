from typing import List

from .source import SourceAttribute
from ...utils import string_processing

class Collection:
    """
    This an class for the iterables
    like tracklist or discography
    """
    _data: List[SourceAttribute]
    
    _by_url: dict
    _by_attribute: dict


    def __init__(self, data: list = None, map_attributes: list = None) -> None:
        """
        Attribute needs to point to
        """
        self._by_url = dict()
        

        self.map_attributes = map_attributes or []
        self._by_attribute = {attr: dict() for attr in map_attributes}

        self._data = data or []

        for element in self._data:
            self.map_element(element=element)

    def map_element(self, element: SourceAttribute):
        self._by_url.update(element.source_url_map)
        for attr in self.map_attributes:
            value = element.__getattribute__(attr)
            if type(value) != str:
                # this also throws out all none values
                continue

            self._by_attribute[attr][string_processing.unify(value)] = element

            
    def get_object_with_source(self, url: str) -> any:
        """
        Returns either None, or the object, that has a source
        matching the url.
        """
        if url in self._by_url:
            return self._by_url[url]

    def get_object_with_attribute(self, name: str, value: str):
        if name not in self.map_attributes:
            raise ValueError(f"didn't map the attribute {name}")

        unified = string_processing.unify(value)
        if unified in self._by_attribute[name][unified]:
            return self._by_attribute[name][unified]

    def append(self, element: SourceAttribute):
        self._data.append(element)
        self.map_element(element)
