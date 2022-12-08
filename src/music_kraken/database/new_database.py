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
    Source,
    Album
)

logger = logging.getLogger("database")

# Due to this not being deployed on a Server **HOPEFULLY**
# I don't need to parameterize stuff like the where and
# use complicated query builder
SONG_QUERY = """
SELECT 
Song.id AS song_id, Song.name AS title, Song.isrc AS isrc, Song.length AS length, Song.album_id,
Target.id AS target_id, Target.file AS file, Target.path AS path
FROM Song
LEFT JOIN Target ON Song.id=Target.song_id 
WHERE {where};
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
ALBUM_QUERY = """
SELECT Album.id AS album_id, title, copyright, album_status, language, year, date, country, barcode
FROM Album
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

    def push_one(self, db_object: Song | Lyrics | Target | Artist | Source | Album):
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

        if type(db_object) == Album:
            return self.push_album(album=db_object)

        logger.warning(f"type {type(db_object)} isn't yet supported by the db")

    def push(self, db_object_list: List[Song | Lyrics | Target | Artist | Source | Album]):
        """
        This function is used to Write the data of any db_object to the database

        It syncs a whole list of db_objects to the database and is meant
        as the primary method to add to the database.

        :param db_object_list:
        """

        for db_object in db_object_list:
            self.push_one(db_object)

    def push_album(self, album: Album):
        table = "Album"
        query = f"INSERT OR REPLACE INTO {table} (id, title, copyright, album_status, language, year, date, country, barcode) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"

        values = (
            album.id,
            album.title,
            album.copyright,
            album.album_status,
            album.language,
            album.year,
            album.date,
            album.country,
            album.barcode
        )
        self.cursor.execute(query, values)
        self.connection.commit()

    def push_song(self, song: Song):
        # ADDING THE DATA FOR THE SONG OBJECT
        """
        db_field    - object attribute
        -------------------------------
        id          - id
        name        - title
        """
        table = "Song"

        values = (
            song.id,
            song.title,
            song.isrc,
            song.length,
            song.get_album_id()
        )
        query = f"INSERT OR REPLACE INTO {table} (id, name, isrc, length, album_id) VALUES (?, ?, ?, ?, ?);"

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
        """
        Gets a list of sources. if lyrics_ref is passed in the List will most likely only
        contain one Element if everything goes accordingly.
        **If neither song_ref nor lyrics_ref are passed in it will return ALL lyrics**
        :param song_ref:
        :param lyrics_ref:
        :return:
        """

        where = "1=1"
        if song_ref is not None:
            where = f"song_id=\"{song_ref.id}\""
        elif lyrics_ref is not None:
            where = f"id=\"{lyrics_ref.id}\""

        query = LYRICS_QUERY.format(where=where)
        self.cursor.execute(query)

        lyrics_rows = self.cursor.fetchall()
        return [Lyrics(
            id_=lyrics_row['id'],
            text=lyrics_row['text'],
            language=lyrics_row['language']
        ) for lyrics_row in lyrics_rows]

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

    def get_song_from_row(self, song_result, exclude_independent_relations: bool = False) -> Song:
        song_id = song_result['song_id']
        
        return Song(
            id_=song_id,
            title=song_result['title'],
            isrc=song_result['isrc'],
            length=song_result['length'],
            target=Target(
                id_=song_result['target_id'],
                file=song_result['file'],
                path=song_result['path']
            ),
            sources=self.pull_sources(song_ref=Reference(id_=song_id)),
            lyrics=self.pull_lyrics(song_ref=Reference(id_=song_id)),
            album_ref=Reference(song_result['album_id'])
        )

    def pull_songs(self, song_ref: Reference = None, album_ref: Reference = None, exclude_independent_relations: bool = False) -> List[Song]:
        """
        This function is used to get one song (including its children like Sources etc)
        from one song id (a reference object)
        :param song_ref:
        :param album_ref:
        :param exclude_independent_relations:
        This excludes all relations from being fetched like for example the Album of the Song.
        This is necessary when adding the Song as subclass as e.g. an Album (as tracklist or whatever).
        :return requested_song:
        """

        where = "1=1"
        if song_ref is not None:
            where = f"Song.id=\"{song_ref.id}\""
        elif album_ref is not None:
            where = f"Song.album_id=\"{album_ref.id}\""
        
        query = SONG_QUERY.format(where=where)
        self.cursor.execute(query)

        song_rows = self.cursor.fetchall()

        return [self.get_song_from_row(
            song_result=song_result,
            exclude_independent_relations=exclude_independent_relations
        ) for song_result in song_rows]

    def get_album_from_row(self, album_result, exclude_independent_relations: bool = False) -> Album:
        album_id = album_result['album_id']

        album_obj = Album(
            id_=album_id,
            title=album_result['title'],
            copyright_=album_result['copyright'],
            album_status=album_result['album_status'],
            language=album_result['language'],
            year=album_result['year'],
            date=album_result['date'],
            country=album_result['country'],
            barcode=album_result['barcode']
        )

        if not exclude_independent_relations:
            # getting the tracklist
            tracklist: List[Song] = self.pull_songs(
                album_ref=Reference(id_=album_id),
                exclude_independent_relations=True
            )
            album_obj.set_tracklist(tracklist=tracklist)

        return album_obj

    def pull_albums(self, album_ref: Reference = None, exclude_independent_relations: bool = False) -> List[Album]:
        """
        This function is used to get matching albums/releses 
        from one song id (a reference object)
        :param album_ref:
        :return requested_album_list:
        """
        where = "1=1"
        if album_ref is not None:
            where = f"Album.id=\"{album_ref.id}\""

        query = ALBUM_QUERY.format(where=where)
        self.cursor.execute(query)

        album_rows = self.cursor.fetchall()

        return [self.get_album_from_row(
            album_result=album_row,
            exclude_independent_relations=exclude_independent_relations
        ) for album_row in album_rows]


if __name__ == "__main__":
    cache = Database("")
