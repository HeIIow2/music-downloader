from .database import Database, DatabaseType

from ..utils.shared import (
    TEMP_DATABASE_PATH,
    DATABASE_LOGGER
)

logger = DATABASE_LOGGER


class TempDatabase(Database):
    def __init__(self) -> None:
        super().__init__(db_type=DatabaseType.SQLITE, db_name=TEMP_DATABASE_PATH)


temp_database = TempDatabase()
