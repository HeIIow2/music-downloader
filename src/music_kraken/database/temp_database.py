from .database import Database

from ..utils.shared import (
    TEMP_DATABASE_PATH,
    DATABASE_LOGGER
)

logger = DATABASE_LOGGER


class TempDatabase(Database):
    def __init__(self) -> None:
        super().__init__(TEMP_DATABASE_PATH, False)


temp_database = TempDatabase()
