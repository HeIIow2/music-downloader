from collections import defaultdict
from typing import Optional, Dict, Type, Tuple, List
import uuid

from ..utils.shared import (
    SONG_LOGGER as LOGGER
)
from .metadata import Metadata
from .option import Options


class DatabaseObject:
    COLLECTION_ATTRIBUTES: tuple = tuple()
    SIMPLE_ATTRIBUTES: dict = dict()

    def __init__(self, _id: str = None, dynamic: bool = False, **kwargs) -> None:
        self.automatic_id: bool = False

        if _id is None and not dynamic:
            """
            generates a random UUID
            https://docs.python.org/3/library/uuid.html
            """
            _id = str(uuid.uuid4())
            self.automatic_id = True
            LOGGER.debug(f"id for {type(self).__name__} isn't set. Setting to {_id}")

        # The id can only be None, if the object is dynamic (self.dynamic = True)
        self.id: Optional[str] = _id

        self.dynamic = dynamic

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False

        temp_attribute_map: Dict[str, set] = defaultdict(set)

        # building map with sets
        for name, value in self.indexing_values:
            temp_attribute_map[name].add(value)

        # check against the attributes of the other object
        for name, other_value in other.indexing_values:
            if other_value in temp_attribute_map[name]:
                return True

        return False

    @property
    def indexing_values(self) -> List[Tuple[str, object]]:
        """
        returns a map of the name and values of the attributes.
        This helps in comparing classes for equal data (eg. being the same song but different attributes)

        Returns:
            List[Tuple[str, object]]: the first element in the tuple is the name of the attribute, the second the value.
        """

        return list()

    def merge(self, other, override: bool = False):
        if not isinstance(other, type(self)):
            LOGGER.warning(f"can't merge \"{type(other)}\" into \"{type(self)}\"")
            return

        for collection in type(self).COLLECTION_ATTRIBUTES:
            getattr(self, collection).extend(getattr(other, collection))

        for simple_attribute, default_value in type(self).SIMPLE_ATTRIBUTES.items():
            if getattr(other, simple_attribute) == default_value:
                continue

            if override or getattr(self, simple_attribute) == default_value:
                setattr(self, simple_attribute, getattr(other, simple_attribute))

    @property
    def metadata(self) -> Metadata:
        return Metadata()

    @property
    def options(self) -> Options:
        return Options([self])

    @property
    def option_string(self) -> str:
        return self.__repr__()

    def compile(self) -> bool:
        """
        compiles the recursive structures,

        Args:
            traceback (set, optional): Defaults to an empty set.

        Returns:
            bool: returns true if id has been found in set
        """
        pass


class MainObject(DatabaseObject):
    """
    This is the parent class for all "main" data objects:
    - Song
    - Album
    - Artist
    - Label

    It has all the functionality of the "DatabaseObject" (it inherits from said class)
    but also some added functions as well.
    """

    def __init__(self, _id: str = None, dynamic: bool = False, **kwargs):
        DatabaseObject.__init__(self, _id=_id, dynamic=dynamic, **kwargs)

        self.additional_arguments: dict = kwargs
