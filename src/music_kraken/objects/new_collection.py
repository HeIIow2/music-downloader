from typing import List, Iterable, Iterator, Optional, TypeVar, Generic, Dict, Type
from collections import defaultdict

from .parents import DatabaseObject
from ..utils.functions import replace_all_refs


T = TypeVar('T', bound=DatabaseObject)


class Collection(Generic[T]):
    _data: List[T]

    _indexed_values: Dict[str, set]
    _indexed_to_objects: Dict[any, list]

    shallow_list = property(fget=lambda self: self.data)

    def __init__(self, data: Optional[Iterable[T]]) -> None:
        self._data = []
        self.contained_collections: List[Collection[T]] = []

        self._indexed_values = defaultdict(set)
        self._indexed_to_objects = defaultdict(list)
        
        self.extend(data)

    def _map_element(self, __object: T, no_append: bool = False):
        for name, value in __object.indexing_values:
            if value is None:
                continue

            self._indexed_values[name].add(value)
            if not no_append:
                self._indexed_to_objects[value].append(__object)

    def _unmap_element(self, __object: T):
        for name, value in __object.indexing_values:
            if value is None:
                continue
            if value not in self._indexed_values[name]:
                continue
            
            try:
                self._indexed_to_objects[value].remove(__object)
            except ValueError:
                continue

            if not len(self._indexed_to_objects[value]):
                self._indexed_values[name].remove(value)

    def _contained_in_self(self, __object: T) -> bool:
        for name, value in __object.indexing_values:
            if value is None:
                continue
            if value in self._indexed_values[name]:
                return True
        return False

    def _contained_in(self, __object: T) -> Optional["Collection"]:
        if self._contained_in_self(__object):
            return self
        
        for collection in self.contained_collections:
            return collection._contained_in(__object)
            
        return None
    

    def _merge_in_self(self, __object: T):
        """
        1. find existing objects
        2. merge into existing object
        3. remap existing object
        """
        existing_object: DatabaseObject = None

        for name, value in __object.indexing_values:
            if value is None:
                continue
            if value in self._indexed_values[name]:
                existing_object = self._indexed_to_objects[value][0]
                break
        
        if existing_object is None:
            return None
    
        existing_object.merge(__object)
        replace_all_refs(existing_object, __object)

        print(existing_object, __object)

        if existing_object is not __object:
            raise ValueError("This should NEVER happen. Merging doesn't work.")

        self._map_element(existing_object)

    
    def contains(self, __object: T) -> bool:
        return self._contained_in(__object) is not None


    def _append(self, __object: T):
        self._map_element(__object)
        self._data.append(__object)

    def append(self, __object: Optional[T]):
        if __object is None:
            return
        
        exists_in_collection = self._contained_in(__object)

        if exists_in_collection is None:
            self._append(__object)
        else:
            exists_in_collection._merge_in_self(__object)

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
        replace_all_refs(self, equal_collection)


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