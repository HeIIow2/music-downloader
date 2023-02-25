from typing import Optional
import uuid

from src.music_kraken.utils.shared import (
    SONG_LOGGER as LOGGER
)


class DatabaseObject:
    def __init__(self, _id: str = None, dynamic: bool = False, **kwargs) -> None:
        if _id is None and not dynamic:
            """
            generates a random UUID
            https://docs.python.org/3/library/uuid.html
            """
            _id = str(uuid.uuid4())
            LOGGER.info(f"id for {self.__name__} isn't set. Setting to {_id}")

        # The id can only be None, if the object is dynamic (self.dynamic = True)
        self.id: Optional[str] = _id

        self.dynamic = dynamic


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
        super().__init__(_id=_id, dynamic=dynamic, **kwargs)

        self.additional_arguments: dict = kwargs

    def get_options(self) -> list:
        return []

    def get_option_string(self) -> str:
        return ""

    options = property(fget=get_options)
    options_str = property(fget=get_option_string)
