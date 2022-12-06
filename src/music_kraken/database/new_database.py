import sqlite3
import os
import logging
from typing import List, Tuple
from pkg_resources import resource_string

from .objects.database_object import Reference
from .objects import (
    Song,
    Lyrics,
    Metadata,
    Target,
    Artist,
    Source
)

logger = logging.getLogger("database")

# Due to this not being deployed on a Server **HOPEFULLY**
# I don't need to parameterize stuff like the where and
# use complicated query builder
SONG_QUERY = """
SELECT 
Song.id AS song_id, Song.name AS title, Song.isrc AS isrc, Song.length AS length,
Target.id AS target_id, Target.file AS file, Target.path AS path
FROM Song
LEFT JOIN Target ON Song.id=Target.song_id 
WHERE Song.id="{song_id}";
"""
SOURCE_QUERY = """
SELECT id, src, url, song_id 
FROM Source
WHERE {where};
"""
LYRICS_QUERY = """
SELECT id, text, language, song_id
FROM Lyrics
WHERE {where};
"""


class Database:
    def __init__(self, database_file: str):
        self.database_file: str = database_file
        self.connection, self.cursor = self.reset_cursor()

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
        self.reset_cursor()
        query = resource_string("music_kraken", "static_files/new_db.sql").decode('utf-8')

        # fill the database with the schematic
        self.cursor.executescript(query)
        self.connection.commit()

    def reset_cursor(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        self.connection = sqlite3.connect(self.database_file)
        # This is necessary that fetching rows returns dicts instead of tuple
        self.connection.row_factory = sqlite3.Row

        self.cursor = self.connection.cursor()
        return self.connection, self.cursor

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
        query = f"INSERT OR REPLACE INTO {table} (id, name, isrc, length) VALUES (?, ?, ?, ?);"
        values = (
            song.id,
            song.title,
            song.isrc,
            song.length
        )

        self.cursor.execute(query, values)
        self.connection.commit()

        # add sources
        for source in song.sources:
            self.push_source(source=source)

        # add lyrics
        for single_lyrics in song.lyrics:
            self.push_lyrics(lyrics=single_lyrics)

        # add target
        self.push_target(target=song.target)

    def push_lyrics(self, lyrics: Lyrics, ):
        if lyrics.song_ref_id is None:
            logger.warning("the Lyrics don't refer to a song")

        table = "Lyrics"
        query = f"INSERT OR REPLACE INTO {table} (id, song_id, text, language) VALUES (?, ?, ?, ?);"
        values = (
            lyrics.id,
            lyrics.song_ref_id,
            lyrics.text,
            lyrics.language
        )

        self.cursor.execute(query, values)
        self.connection.commit()

    def push_source(self, source: Source):
        if source.song_ref_id is None:
            logger.warning("the Source don't refer to a song")

        table = "Source"
        query = f"INSERT OR REPLACE INTO {table} (id, song_id, src, url) VALUES (?, ?, ?, ?);"
        values = (
            source.id,
            source.song_ref_id,
            source.src,
            source.url
        )

        self.cursor.execute(query, values)
        self.connection.commit()

    def push_target(self, target: Target):
        if target.song_ref_id is None:
            logger.warning("the Target doesn't refer to a song")

        table = "Target"
        query = f"INSERT OR REPLACE INTO {table} (id, song_id, file, path) VALUES (?, ?, ?, ?);"
        values = (
            target.id,
            target.song_ref_id,
            target.file,
            target.path
        )

        self.cursor.execute(query, values)
        self.connection.commit()

    def push_artist(self, artist: Artist):
        pass

    def pull_lyrics(self, song_ref: Reference = None, lyrics_ref: Reference = None) -> List[Lyrics]:
        pass

    def pull_sources(self, song_ref: Reference = None, source_ref: Reference = None) -> List[Source]:
        """
        Gets a list of sources. if source_ref is passed in the List will most likely only
        contain one Element if everything goes accordingly.
        **If neither song_ref nor source_ref are passed in it will return ALL sources**
        :param song_ref:
        :param source_ref:
        :return:
        """

        where = "1=1"
        if song_ref is not None:
            where = f"song_id=\"{song_ref.id}\""
        elif source_ref is not None:
            where = f"id=\"{source_ref.id}\""

        query = SOURCE_QUERY.format(where=where)
        self.cursor.execute(query)

        source_rows = self.cursor.fetchall()
        return [Source(
            id_=source_row['id'],
            src=source_row['src'],
            url=source_row['url']
        ) for source_row in source_rows]

    def pull_single_song(self, song_ref: Reference = None) -> Song:
        """
        This function is used to get one song (including its children like Sources etc)
        from one song id (a reference object)
        :param song_ref:
        :return requested_song:
        """
        if song_ref.id is None:
            raise ValueError("The Song ref doesn't point anywhere. Remember to use the debugger.")
        query = SONG_QUERY.format(song_id=song_ref.id)
        self.cursor.execute(query)

        song_rows = self.cursor.fetchall()
        if len(song_rows) == 0:
            logger.warning(f"No song found for the id {song_ref.id}")
            return Song()
        if len(song_rows) > 1:
            logger.warning(f"Multiple Songs found for the id {song_ref.id}. Defaulting to the first one.")
        song_result = song_rows[0]

        song = Song(
            id_=song_result['song_id'],
            title=song_result['title'],
            isrc=song_result['isrc'],
            length=song_result['length'],
            target=Target(
                id_=song_result['target_id'],
                file=song_result['file'],
                path=song_result['path']
            ),
            sources=self.pull_sources(song_ref=song_ref)
        )

        return song


if __name__ == "__main__":
    cache = Database("")
