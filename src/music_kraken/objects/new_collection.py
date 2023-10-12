from typing import List, Iterable, Iterator, Optional, TypeVar, Generic
import guppy
from guppy.heapy import Path

from .parents import DatabaseObject


T = TypeVar('T', bound=DatabaseObject)


hp = guppy.hpy()

def _replace_all_refs(replace_with, replace):
    """
    NO
    I have a very good reason to use this here
    DONT use this anywhere else...

    This replaces **ALL** references to replace with a reference to replace_with.

    https://benkurtovic.com/2015/01/28/python-object-replacement.html 
    """
    for path in hp.iso(replace).pathsin:
        relation = path.path[1]
        if isinstance(relation, Path.R_INDEXVAL):
            path.src.theone[relation.r] = replace_with


class Collection(Generic[T]):
    _data: List[T]

    shallow_list = property(fget=lambda self: self.data)

    def __init__(self, data: Optional[Iterable[T]]) -> None:
        self._data = []
        self.contained_collections: List[Collection[T]] = []
        
        self.extend(data)

    def append(self, __object: T):
        self._data.append(__object)

    def extend(self, __iterable: Optional[Iterable[T]]):
        if __iterable is None:
            return
        
        for __object in __iterable:
            self.append(__object)

    def sync_with_other_collection(self, equal_collection: "Collection"):
        """
        If two collections always need to have the same values, this can be used.
        
        Internally:
        1. import the data from other to self
            - _data
            - contained_collections
        2. replace all refs from the other object, with refs from this object
        """
        if equal_collection is self:
            return

        # don't add the elements from the subelements from the other collection.
        # this will be done in the next step.
        self.extend(equal_collection._data)
        # add all submodules
        for equal_sub_collection in equal_collection.contained_collections:
            self.contain_collection_inside(equal_sub_collection)

        # now the ugly part
        # replace all refs of the other element with this one
        _replace_all_refs(self, equal_collection)


    def contain_collection_inside(self, sub_collection: "Collection"):
        """
        This collection will ALWAYS contain everything from the passed in collection
        """
        if sub_collection in self.contained_collections:
            return
        
        self.contained_collections.append(sub_collection)

    @property
    def data(self) -> List[T]:
        return [*self._data, *(__object for collection in self.contained_collections for __object in collection.shallow_list)]
    
    def __len__(self) -> int:
        return len(self._data) + sum(len(collection) for collection in self.contained_collections)

    def __iter__(self) -> Iterator[T]:
        for element in self._data:
            yield element