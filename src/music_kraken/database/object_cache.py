from collections import defaultdict
from typing import Dict, List, Optional
import weakref

from src.music_kraken.objects import DatabaseObject

"""
This is a cache for the objects, that et pulled out of the database.
This is necessary, to not have duplicate objects with the same id.

Using a cache that maps the ojects to their id has multiple benefits:
 - if you modify the object at any point, all objects with the same id get modified *(copy by reference)*
 - less ram usage
 - to further decrease ram usage I only store weak refs and not a strong reference, for the gc to still work
"""


class ObjectCache:
    """
    ObjectCache is a cache for the objects retrieved from a database.
    It maps each object to its id and uses weak references to manage its memory usage.
    Using a cache for these objects provides several benefits:

    - Modifying an object updates all objects with the same id (due to copy by reference)
    - Reduced memory usage

    :attr object_to_id: Dictionary that maps MusicObjects to their id.
    :attr weakref_map: Dictionary that uses weak references to MusicObjects as keys and their id as values.

    :method exists: Check if a MusicObject already exists in the cache.
    :method append: Add a MusicObject to the cache if it does not already exist.
    :method extent: Add a list of MusicObjects to the cache.
    :method remove: Remove a MusicObject from the cache by its id.
    :method get: Retrieve a MusicObject from the cache by its id.    """
    object_to_id: Dict[str, DatabaseObject]
    weakref_map: Dict[weakref.ref, str]

    def __init__(self) -> None:
        self.object_to_id = dict()
        self.weakref_map = defaultdict()

    def exists(self, music_object: DatabaseObject) -> bool:
        """
        Check if a MusicObject with the same id already exists in the cache.

        :param music_object: The MusicObject to check for.
        :return: True if the MusicObject exists, False otherwise.
        """
        if music_object.dynamic:
            return True
        return music_object.id in self.object_to_id

    def on_death(self, weakref_: weakref.ref) -> None:
        """
        Callback function that gets triggered when the reference count of a MusicObject drops to 0.
        This function removes the MusicObject from the cache.

        :param weakref_: The weak reference of the MusicObject that has been garbage collected.
        """
        data_id = self.weakref_map.pop(weakref_)
        self.object_to_id.pop(data_id)

    def append(self, music_object: DatabaseObject) -> bool:
        """
        Add a MusicObject to the cache.

        :param music_object: The MusicObject to add to the cache.
        :return: True if the MusicObject already exists in the cache, False otherwise.
        """
        if self.exists(music_object):
            return True

        self.weakref_map[weakref.ref(music_object, self.on_death)] = music_object.id
        self.object_to_id[music_object.id] = music_object

        return False

    def extent(self, music_object_list: List[DatabaseObject]):
        """
        adjacent to the extent method of list, this appends n Object
        """
        for music_object in music_object_list:
            self.append(music_object)

    def remove(self, _id: str):
        """
        Remove a MusicObject from the cache.

        :param _id: The id of the MusicObject to remove from the cache.
        """
        data = self.object_to_id.get(_id)
        if data:
            self.weakref_map.pop(weakref.ref(data))
            self.object_to_id.pop(_id)

    def __getitem__(self, item) -> Optional[DatabaseObject]:
        """
        this returns the data obj
        :param item: the id of the music object
        :return:
        """

        return self.object_to_id.get(item)

    def get(self, _id: str) -> Optional[DatabaseObject]:
        return self.__getitem__(_id)
