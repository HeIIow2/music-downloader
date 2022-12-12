from .new_database import Database

from ..utils.shared import (
    TEMP_DATABASE_PATH,
    DATABASE_LOGGER
)

logger = DATABASE_LOGGER


class TempDatabase(Database):
    def __init__(self, reset_on_start: bool = True) -> None:
        super().__init__(TEMP_DATABASE_PATH)

        if reset_on_start:
            self.reset()


temp_database = TempDatabase()
