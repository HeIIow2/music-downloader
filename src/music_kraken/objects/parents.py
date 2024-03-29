import random
from collections import defaultdict
from typing import Optional, Dict, Tuple, List, Type

from .metadata import Metadata
from .option import Options
from ..utils.shared import HIGHEST_ID
from ..utils.config import main_settings, logging_settings


LOGGER = logging_settings["object_logger"]


class DatabaseObject:
    COLLECTION_ATTRIBUTES: tuple = tuple()
    SIMPLE_ATTRIBUTES: dict = dict()

    # contains all collection attributes, which describe something "smaller"
    # e.g. album has songs, but not artist.
    DOWNWARDS_COLLECTION_ATTRIBUTES: tuple = tuple()
    UPWARDS_COLLECTION_ATTRIBUTES: tuple = tuple()

    def __init__(self, _id: int = None, dynamic: bool = False, **kwargs) -> None:
        self.automatic_id: bool = False

        if _id is None and not dynamic:
            """
            generates a random integer id
            64 bit integer, but this is defined in shared.py in ID_BITS
            the range is defined in the Tuple ID_RANGE
            """
            _id = random.randint(0, HIGHEST_ID)
            self.automatic_id = True
            LOGGER.debug(f"Id for {type(self).__name__} isn't set. Setting to {_id}")

        # The id can only be None, if the object is dynamic (self.dynamic = True)
        self.id: Optional[int] = _id

        self.dynamic = dynamic
        
        self.build_version = -1

    def __hash__(self):
        if self.dynamic:
            raise TypeError("Dynamic DatabaseObjects are unhashable.")
        return self.id

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False

        # add the checks for dynamic, to not throw an exception
        if not self.dynamic and not other.dynamic and self.id == other.id:
            return True

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
        if other is None:
            return
        
        if self is other:
            return
        
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

    def strip_details(self):
        for collection in type(self).DOWNWARDS_COLLECTION_ATTRIBUTES:
            getattr(self, collection).clear()

    @property
    def metadata(self) -> Metadata:
        return Metadata()

    @property
    def options(self) -> List["DatabaseObject"]:
        return [self]

    @property
    def option_string(self) -> str:
        return self.__repr__()
    
    def _build_recursive_structures(self, build_version: int, merge: False):
        pass

    def compile(self, merge_into: bool = False):
        """
        compiles the recursive structures,
        and does depending on the object some other stuff.
        
        no need to override if only the recursive structure should be build.
        override self.build_recursive_structures() instead
        """
        
        self._build_recursive_structures(build_version=random.randint(0, 99999), merge=merge_into)

    def _add_other_db_objects(self, object_type: Type["DatabaseObject"], object_list: List["DatabaseObject"]):
        pass

    def add_list_of_other_objects(self, object_list: List["DatabaseObject"]):
        d: Dict[Type[DatabaseObject], List[DatabaseObject]] = defaultdict(list)

        for db_object in object_list:
            d[type(db_object)].append(db_object)

        for key, value in d.items():
            self._add_other_db_objects(key, value)


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

    def __init__(self, _id: int = None, dynamic: bool = False, **kwargs):
        DatabaseObject.__init__(self, _id=_id, dynamic=dynamic, **kwargs)

        self.additional_arguments: dict = kwargs
