from .database import Database

from ..utils.shared import (
    TEMP_DATABASE_PATH,
    DATABASE_STRUCTURE_FILE,
    DATABASE_STRUCTURE_FALLBACK,
    DATABASE_LOGGER
)

class TempDatabase(Database):
    def __init__(self) -> None:
        super().__init__(TEMP_DATABASE_PATH, DATABASE_STRUCTURE_FILE, DATABASE_STRUCTURE_FALLBACK, DATABASE_LOGGER, False)


temp_database = TempDatabase()
