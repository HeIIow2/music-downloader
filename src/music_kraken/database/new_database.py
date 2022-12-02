import sqlite3
import os
import logging

logger = logging.getLogger("database")


class Database:
    def __init__(self, structure_file: str, database_file: str):
        self.structure_file: str = structure_file
        self.database_file: str = database_file

        self.connection = sqlite3.connect(self.database_file)
        self.cursor = self.connection.cursor()

    def reset(self):
        """
        Deletes all Data from the database if it exists
        and resets the schema defined in self.structure_file
        """
        logger.info(f"resetting the database \"{self.__name__}\"")

        # deleting the database
        del self.connection
        del self.cursor
        os.remove(self.database_file)

        # newly creating the database
        self.connection = sqlite3.connect(self.database_file)
        self.cursor = self.connection.cursor()
        with open(self.structure_file, "r") as structure_file_obj:
            query = structure_file_obj.read()

        # fill the database with the schematic
        self.cursor.executescript(query)
        self.connection.commit()
        