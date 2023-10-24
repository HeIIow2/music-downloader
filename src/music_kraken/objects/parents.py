import random
from collections import defaultdict
from typing import Optional, Dict, Tuple, List, Type, Generic, TypeVar, Any
from dataclasses import dataclass

from .metadata import Metadata
from .option import Options
from ..utils.shared import HIGHEST_ID
from ..utils.config import main_settings, logging_settings
from ..utils.support_classes.hacking import MetaClass


LOGGER = logging_settings["object_logger"]

P = TypeVar('P')

@dataclass
class StaticAttribute(Generic[P]):
    name: str

    default_value: Any = None
    weight: float = 0

    is_collection: bool = False
    is_downwards_collection: bool = False
    is_upwards_collection: bool = False


class Attribute(Generic[P]):
    def __init__(self, database_object: "DatabaseObject", static_attribute: StaticAttribute) -> None:
        self.database_object: DatabaseObject = database_object
        self.static_attribute: StaticAttribute = static_attribute

    @property
    def name(self) -> str:
        return self.static_attribute.name

    def get(self) -> P:
        return self.database_object.__getattribute__(self.name)
    
    def set(self, value: P):
        self.database_object.__setattr__(self.name, value)



class DatabaseObject(metaclass=MetaClass):
    COLLECTION_STRING_ATTRIBUTES: tuple = tuple()
    SIMPLE_STRING_ATTRIBUTES: dict = dict()

    # contains all collection attributes, which describe something "smaller"
    # e.g. album has songs, but not artist.
    DOWNWARDS_COLLECTION_STRING_ATTRIBUTES: tuple = tuple()
    UPWARDS_COLLECTION_STRING_ATTRIBUTES: tuple = tuple()

    STATIC_ATTRIBUTES: List[StaticAttribute] = list()

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
            # LOGGER.debug(f"Id for {type(self).__name__} isn't set. Setting to {_id}")

        self._attributes: List[Attribute] = []
        self._simple_attribute_list: List[Attribute] = []
        self._collection_attributes: List[Attribute] = []
        self._downwards_collection_attributes: List[Attribute] = []
        self._upwards_collection_attributes: List[Attribute] = []

        for static_attribute in self.STATIC_ATTRIBUTES:
            attribute: Attribute = Attribute(self, static_attribute)
            self._attributes.append(attribute)
            
            if static_attribute.is_collection:
                if static_attribute.is_collection:
                    self._collection_attributes.append(attribute)
                    if static_attribute.is_upwards_collection:
                        self._upwards_collection_attributes.append(attribute)
                    if static_attribute.is_downwards_collection:
                        self._downwards_collection_attributes.append(attribute)
            else:
                self._simple_attribute_list.append(attribute)

        # The id can only be None, if the object is dynamic (self.dynamic = True)
        self.id: Optional[int] = _id

        self.dynamic = dynamic
        self.build_version = -1

    @property
    def upwards_collection(self) -> "Collection":
        for attribute in self._upwards_collection_attributes:
            yield attribute.get()

    @property
    def downwards_collection(self) -> "Collection":
        for attribute in self._downwards_collection_attributes:
            yield attribute.get()

    @property
    def all_collections(self) -> "Collection":
        for attribute in self._collection_attributes:
            yield attribute.get()

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

    def merge(self, other, override: bool = False, replace_all_refs: bool = False):
        print("merge")

        if other is None:
            return
        
        if self is other:
            return
        
        if not isinstance(other, type(self)):
            LOGGER.warning(f"can't merge \"{type(other)}\" into \"{type(self)}\"")
            return

        for collection in self._collection_attributes:
            if hasattr(self, collection.name) and hasattr(other, collection.name):
                if collection.get() is not getattr(other, collection.name):
                    collection.get().extend(getattr(other, collection.name))

        for simple_attribute, default_value in type(self).SIMPLE_STRING_ATTRIBUTES.items():
            if getattr(other, simple_attribute) == default_value:
                continue

            if override or getattr(self, simple_attribute) == default_value:
                setattr(self, simple_attribute, getattr(other, simple_attribute))

        if replace_all_refs:
            self.merge(other)

    def strip_details(self):
        for collection in type(self).DOWNWARDS_COLLECTION_STRING_ATTRIBUTES:
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
