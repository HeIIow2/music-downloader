import uuid

from ..utils.shared import (
    SONG_LOGGER as logger
)

class DatabaseObject:
    def __init__(self, id_: str = None) -> None:
        self.id_: str | None = id_
        
    def get_id(self):
        """
        returns the id if it is set, else
        it returns a randomly generated UUID
        https://docs.python.org/3/library/uuid.html
        """
        if self.id_ is None:
            self.id_ = str(uuid.uuid4())
            logger.info(f"id for {self.__str__()} isn't set. Setting to {self.id_}")

        return self.id_

    id = property(fget=get_id)
