import sqlite3
import os
import logging
from typing import List
from pkg_resources import resource_string

from .objects import (
    Song,
    Lyrics,
    Metadata,
    Target,
    Artist,
    Source
)

logger = logging.getLogger("database")


class Database:
    def __init__(self, database_file: str):
        self.database_file: str = database_file

        self.connection = sqlite3.connect(self.database_file)
        self.cursor = self.connection.cursor()

    def reset(self):
        """
        Deletes all Data from the database if it exists
        and resets the schema defined in self.structure_file
        """
        logger.info(f"resetting the database")

        # deleting the database
        del self.connection
        del self.cursor
        os.remove(self.database_file)

        # newly creating the database
        self.connection = sqlite3.connect(self.database_file)
        self.cursor = self.connection.cursor()
        query = resource_string("music_kraken", "static_files/new_db.sql").decode('utf-8')

        # fill the database with the schematic
        self.cursor.executescript(query)
        self.connection.commit()

    def push_one(self, db_object: Song | Lyrics | Target | Artist | Source):
        if type(db_object) == Song:
            return self.push_song(song=db_object)

        if type(db_object) == Lyrics:
            return self.push_lyrics(lyrics=db_object)

        if type(db_object) == Target:
            return self.push_target(target=db_object)

        if type(db_object) == Artist:
            return self.push_artist(artist=db_object)

        if type(db_object) == Source:
            return self.push_source(source=db_object)

    def push(self, db_object_list: List[Song | Lyrics | Target | Artist | Source]):
        """
        This function is used to Write the data of any db_object to the database

        It syncs a whole list of db_objects to the database and is meant
        as the primary method to add to the database.

        :param db_object_list:
        """

        for db_object in db_object_list:
            self.push_one(db_object)

    def push_song(self, song: Song):
        # ADDING THE DATA FOR THE SONG OBJECT
        """
        db_field    - object attribute
        -------------------------------
        id          - id
        name        - title
        """
        table = "Song"
        query = f"INSERT OR REPLACE INTO {table} (id, name) VALUES (?, ?);"
        values = (
            song.id,
            song.title
        )

        self.cursor.execute(query, values)
        self.connection.commit()

    def push_lyrics(self, lyrics: Lyrics):
        pass

    def push_target(self, target: Target):
        pass

    def push_artist(self, artist: Artist):
        pass

    def push_source(self, source: Source):
        pass


if __name__ == "__main__":
    cache = Database("")
