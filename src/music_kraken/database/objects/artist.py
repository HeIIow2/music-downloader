from ...utils.shared import (
    DATABASE_LOGGER as logger
)
from .parents import (
    DatabaseObject,
    Reference
)


class Artist(DatabaseObject):
    def __init__(self, id_: str = None, mb_id: str = None, name: str = None) -> None:
        super().__init__(id_=id_)
        self.mb_id = mb_id
        self.name = name

    def __eq__(self, __o: object) -> bool:
        if type(__o) != type(self):
            return False
        return self.id == __o.id

    def __str__(self) -> str:
        return self.name
