from typing import Optional, Union
from enum import Enum
from peewee import (
    SqliteDatabase,
    MySQLDatabase,
    PostgresqlDatabase,
)

from . import data_models


class DatabaseType(Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"

class Database:
    database: Union[SqliteDatabase, PostgresqlDatabase, MySQLDatabase]

    def __init__(
            self,
            db_type: DatabaseType,
            db_name: str,
            db_user: Optional[str] = None,
            db_password: Optional[str] = None,
            db_host: Optional[str] = None,
            db_port: Optional[int] = None
    ):
        self.db_type = db_type
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port

        self.initialize_database()

    def create_database(self) -> Union[SqliteDatabase, PostgresqlDatabase, MySQLDatabase]:
        """Create a database instance based on the configured database type and parameters.

        Returns:
            The created database instance, or None if an invalid database type was specified.
        """

        # SQLITE
        if self.db_type == DatabaseType.SQLITE:
            return SqliteDatabase(self.db_name)

        # POSTGRES
        if self.db_type == DatabaseType.POSTGRESQL:
            return PostgresqlDatabase(
                self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port,
            )

        # MYSQL
        if self.db_type == DatabaseType.MYSQL:
            return MySQLDatabase(
                self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port,
            )

        raise ValueError("define a Valid database type")

    def initialize_database(self):
        """
        Connect to the database
        initialize the previously defined databases
        create tables if they don't exist.
        """
        self.database = self.create_database()
        self.database.connect()

        self.database.create_tables(data_models.ALL_MODELS, safe=True)

        """
        upgrade old databases. 
        If a collumn has been added in a new version this adds it to old Tables, 
        without deleting the data in legacy databases
        """
        for model in data_models.ALL_MODELS:
            for field_name, field_obj in model._meta.fields.items():
                # check if the field exists in the database
                if not self.database.table_column_exists(model._meta.db_table, field_name):
                    # add the missing column to the table
                    self.database.add_column(model._meta.db_table, field_name, field_obj)


    def __del__(self):
        self.database.close()
