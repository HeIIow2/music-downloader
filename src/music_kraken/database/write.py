from typing import Union
from peewee import (
    SqliteDatabase,
    MySQLDatabase,
    PostgresqlDatabase,
)

from . import objects

# just a Type for type hintung. You can't do anything with it.
Database = Union[SqliteDatabase, PostgresqlDatabase, MySQLDatabase]


class Session:
    """
    do the thingie with the with keyword
    overload __end__ and maybe __start__ i dunfckinnow
    """
    pass
