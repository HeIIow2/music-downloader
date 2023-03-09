from typing import Optional, Dict, Type
import uuid

from ..utils.shared import (
    SONG_LOGGER as LOGGER
)


class DatabaseObject:
    COLLECTION_ATTRIBUTES: tuple = tuple()
    SIMPLE_ATTRIBUTES: tuple = tuple()
    
    def __init__(self, _id: str = None, dynamic: bool = False, **kwargs) -> None:
        if _id is None and not dynamic:
            """
            generates a random UUID
            https://docs.python.org/3/library/uuid.html
            """
            _id = str(uuid.uuid4())
            LOGGER.info(f"id for {type(self).__name__} isn't set. Setting to {_id}")

        # The id can only be None, if the object is dynamic (self.dynamic = True)
        self.id: Optional[str] = _id

        self.dynamic = dynamic
        
    @property
    def indexing_values(self) -> Dict[str, object]:
        """
        returns a map of the name and values of the attributes.
        This helps in comparing classes for equal data (eg. being the same song but different attributes)

        Returns:
            Dict[str, object]: the key is the name of the attribute, and the value its value
        """
        
        return dict()
        
    def merge(self, other, override: bool = False):
        if isinstance(other, type(self)):
            LOGGER.warning(f"can't merge \"{type(other)}\" into \"{type(self)}\"")
            return

        for collection in type(self).COLLECTION_ATTRIBUTES:
            getattr(self, collection).extend(collection)

        for simple_attribute in type(self).SIMPLE_ATTRIBUTES:
            if getattr(other, simple_attribute) is None:
                continue

            if override or getattr(self, simple_attribute) is None:
                setattr(self, simple_attribute, getattr(other, simple_attribute))


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

    def get_options(self) -> list:
        return []

    def get_option_string(self) -> str:
        return ""

    options = property(fget=get_options)
    options_str = property(fget=get_option_string)
