from typing import Dict, List

from .objects import MusicObject

"""
This is a cache for the objects, that et pulled out of the database.
This is necessary, to not have duplicate objects with the same id.

Using a cache that maps the ojects to their id has multiple benefits:
 - if you modify the object at any point, all objects with the same id get modified *(copy by reference)*
 - less ram usage
"""

class ObjectCache:
    """
    :attr object_to_id: maps any object from the Database like Song or Artist to its id.
    """
    object_to_id: Dict[str, MusicObject]

    def __init__(self) -> None:
        self.object_to_id = dict()
    

    def clear(self) -> None:
        """
        deletes all references and lets the gc clean up the rest
        this should free up memorie.

        If not, check if you have any references to an object in you're code.
        It is likely that this object crossreferences to many objects
        """
        self.object_to_id = dict()

    def exists(self, music_object: MusicObject) -> bool:
        """
        :returns exist: if an element with the same id exists it returns true, else false
        """
        if music_object.dynamic:
            return True
        if music_object.id in self.object_to_id:
            return True
        return False

    def append(self, music_object: MusicObject) -> bool:
        """
        :returns exist: if an element with the same id exists it returns true, else false
        """
        if self.exists(music_object):
            return True

        self.object_to_id[music_object.id] = music_object

        return False

    def extent(self, music_object_list: List[MusicObject]):
        """
        adjacent to the extend method of list, this appends n Object
        """
        for music_object in music_object_list:
            self.append(music_object)