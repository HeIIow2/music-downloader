import sqlite3
import os
import logging
from typing import List, Tuple
from pkg_resources import resource_string
import datetime
import pycountry

from .objects.parents import Reference
from .objects.source import Source
from .objects import (
    Song,
    Lyrics,
    Target,
    Artist,
    Album,
    ID3Timestamp,
    SourceTypes,
    SourcePages,
    SourceAttribute
)

logger = logging.getLogger("database")

# Due to this not being deployed on a Server **HOPEFULLY**
# I don't need to parameterize stuff like the where and
# use complicated query builder
SONG_QUERY = """
SELECT 
Song.id AS song_id, Song.name AS title, Song.isrc AS isrc, Song.length AS length, Song.album_id as album_id, Song.tracksort,
Target.id AS target_id, Target.file AS file, Target.path AS path, Song.genre AS genre
FROM Song
LEFT JOIN Target ON Song.id=Target.song_id 
WHERE {where};
"""
SOURCE_QUERY = """
SELECT id, type, src, url, song_id 
FROM Source
WHERE {where};
"""
LYRICS_QUERY = """
SELECT id, text, language, song_id
FROM Lyrics
WHERE {where};
"""
ALBUM_QUERY_UNJOINED = """
SELECT Album.id AS album_id, title, label, album_status, language, date, country, barcode, albumsort, is_split
FROM Album
WHERE {where};
"""
ALBUM_QUERY_JOINED = """
SELECT a.id AS album_id, a.title, a.label, a.album_status, a.language, a.date, a.country, a.barcode, a.albumsort, a.is_split
FROM Song
INNER JOIN Album a ON Song.album_id=a.id
WHERE {where};
"""
ARTIST_QUERY = """
SELECT id as artist_id, name as artist_name
FROM Artist
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
        if db_object.dynamic:
            return

        if type(db_object) == Song:
            return self.push_song(song=db_object)

        if type(db_object) == Lyrics:
            return self.push_lyrics(lyrics=db_object)

        if type(db_object) == Target:
            return self.push_target(target=db_object)

        if type(db_object) == Artist:
            return self.push_artist(artist=db_object)

        if type(db_object) == Source:
            # needs to have the property type_enum or type_str set
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
        query = f"INSERT OR REPLACE INTO {table} (id, title, label, album_status, language, date, country, barcode, albumsort, is_split) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"

        values = (
            album.id,
            album.title,
            album.label,
            album.album_status,
            album.iso_639_2_language,
            album.date.strftime("%Y-%m-%d"),
            album.country,
            album.barcode,
            album.albumsort,
            album.is_split
        )
        self.cursor.execute(query, values)
        self.connection.commit()

        for song in album.tracklist:
            self.push_song(song)
        for artist in album.artists:
            self.push_artist_album(artist_ref=artist.reference, album_ref=album.reference)
            self.push_artist(artist)

        for source in album.source_list:
            source.type_enum = SourceTypes.ALBUM
            source.add_song(album)
            self.push_source(source=source)

    def push_song(self, song: Song):
        if song.dynamic:
            return
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
            song.get_album_id(),
            song.tracksort,
            song.genre
        )
        query = f"INSERT OR REPLACE INTO {table} (id, name, isrc, length, album_id, tracksort, genre) VALUES (?, ?, ?, ?, ?, ?, ?);"

        self.cursor.execute(query, values)
        self.connection.commit()

        # add sources
        for source in song.source_list:
            source.add_song(song)
            source.type_enum = SourceTypes.SONG
            self.push_source(source=source)

        # add lyrics
        for single_lyrics in song.lyrics:
            single_lyrics.add_song(song)
            self.push_lyrics(lyrics=single_lyrics)

        # add target
        song.target.add_song(song)
        self.push_target(target=song.target)

        for main_artist in song.main_artist_list:
            self.push_artist_song(artist_ref=Reference(main_artist.id), song_ref=Reference(song.id), is_feature=False)
            self.push_artist(artist=main_artist)

        for feature_artist in song.feature_artist_list:
            self.push_artist_song(artist_ref=Reference(feature_artist.id), song_ref=Reference(song.id), is_feature=True)
            self.push_artist(artist=feature_artist)

        if song.album is not None:
            self.push_album(song.album)

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
            logger.warning(f"the Source {source} don't refer to a song")

        table = "Source"
        query = f"INSERT OR REPLACE INTO {table} (id, type, song_id, src, url) VALUES (?, ?, ?, ?, ?);"
        values = (
            source.id,
            source.type_str,
            source.song_ref_id,
            source.page_str,
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

    def push_artist_song(self, artist_ref: Reference, song_ref: Reference, is_feature: bool):
        table = "SongArtist"
        # checking if already exists
        query = f"SELECT * FROM {table} WHERE song_id=\"{song_ref.id}\" AND artist_id=\"{artist_ref.id}\""
        self.cursor.execute(query)
        if len(self.cursor.fetchall()) > 0:
            # join already exists
            return

        query = f"INSERT OR REPLACE INTO {table} (song_id, artist_id, is_feature) VALUES (?, ?, ?);"
        values = (
            song_ref.id,
            artist_ref.id,
            is_feature
        )

        self.cursor.execute(query, values)
        self.connection.commit()

    def push_artist_album(self, artist_ref: Reference, album_ref: Reference):
        table = "AlbumArtist"
        # checking if already exists
        query = f"SELECT * FROM {table} WHERE album_id=\"{album_ref.id}\" AND artist_id=\"{artist_ref.id}\""
        self.cursor.execute(query)
        if len(self.cursor.fetchall()) > 0:
            # join already exists
            return

        query = f"INSERT OR REPLACE INTO {table} (album_id, artist_id) VALUES (?, ?);"
        values = (
            album_ref.id,
            artist_ref.id
        )

        self.cursor.execute(query, values)
        self.connection.commit()

    def push_artist(self, artist: Artist):
        table = "Artist"
        query = f"INSERT OR REPLACE INTO {table} (id, name) VALUES (?, ?);"
        values = (
            artist.id,
            artist.name
        )

        self.cursor.execute(query, values)
        self.connection.commit()

        for song in artist.feature_songs:
            self.push_artist_song(artist_ref=artist.reference, song_ref=song.reference, is_feature=True)
            self.push_song(song=song)

        for song in artist.main_songs:
            self.push_artist_song(artist_ref=artist.reference, song_ref=song.reference, is_feature=False)
            self.push_song(song=song)

        for album in artist.main_albums:
            self.push_artist_album(artist_ref=artist.reference, album_ref=album.reference)

        for source in artist.source_list:
            source.type_enum = SourceTypes.ARTIST
            self.push_source(source)

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

    def pull_sources(self, artist_ref: Reference = None, song_ref: Reference = None, source_ref: Reference = None, album_ref: Reference = None) -> List[Source]:
        """
        Gets a list of sources. if source_ref is passed in the List will most likely only
        contain one Element if everything goes accordingly.
        **If neither song_ref nor source_ref are passed in it will return ALL sources**
        :param artist_ref:
        :param song_ref:
        :param source_ref:
        :param type_str: the thing the source belongs to like eg. "song" or "album"
        :return:
        """

        where = "1=1"
        if song_ref is not None:
            where = f"song_id=\"{song_ref.id}\""
        elif source_ref is not None:
            where = f"id=\"{source_ref.id}\" AND type=\"{SourceTypes.SONG.value}\""
        elif artist_ref is not None:
            where = f"song_id=\"{artist_ref.id}\" AND type=\"{SourceTypes.ARTIST.value}\""
        elif album_ref is not None:
            where = f"song_id=\"{album_ref.id}\" AND type=\"{SourceTypes.ALBUM.value}\""

        query = SOURCE_QUERY.format(where=where)
        self.cursor.execute(query)

        source_rows = self.cursor.fetchall()

        return [
            Source(
                page_enum=SourcePages(source_row['src']),
                type_enum=SourceTypes(source_row['type']),
                url=source_row['url'],
                id_=source_row['id']
            ) for source_row in source_rows
        ]

    def pull_artist_song(self, song_ref: Reference = None, artist_ref: Reference = None) -> List[tuple]:
        table = "SongArtist"
        wheres = []
        if song_ref is not None:
            wheres.append(f"song_id=\"{song_ref.id}\"")
        if artist_ref is not None:
            wheres.append(f"artist_id=\"{artist_ref.id}\"")
        where_str = ""
        if len(wheres) > 0:
            where_str = "WHERE " + " AND ".join(wheres)

        query = f"SELECT * FROM {table} {where_str};"
        self.cursor.execute(query)
        joins = self.cursor.fetchall()

        return [(
            Reference(join["song_id"]),
            Reference(join["artist_id"]),
            bool(join["is_feature"])
        ) for join in joins]

    def pull_artist_album(self, album_ref: Reference = None, artist_ref: Reference = None) -> List[tuple]:
        table = "AlbumArtist"
        wheres = []
        if album_ref is not None:
            wheres.append(f"album_id=\"{album_ref.id}\"")
        if artist_ref is not None:
            wheres.append(f"artist_id=\"{artist_ref.id}\"")
        where_str = ""
        if len(wheres) > 0:
            where_str = "WHERE " + " AND ".join(wheres)

        query = f"SELECT * FROM {table} {where_str};"
        self.cursor.execute(query)
        joins = self.cursor.fetchall()

        return [(
            Reference(join["album_id"]),
            Reference(join["artist_id"])
        ) for join in joins]

    def get_artist_from_row(self, artist_row, exclude_relations: set = None, flat: bool = False) -> Artist:
        if exclude_relations is None:
            exclude_relations = set()
        new_exclude_relations: set = set(exclude_relations)
        new_exclude_relations.add(Artist)

        artist_id = artist_row['artist_id']

        artist_obj = Artist(
            id_=artist_id,
            name=artist_row['artist_name'],
            source_list=self.pull_sources(artist_ref=Reference(id_=artist_id))
        )
        if flat:
            return artist_obj

        # fetch songs :D
        for song_ref, _, is_feature in self.pull_artist_song(artist_ref=Reference(id_=artist_id)):
            new_songs = self.pull_songs(song_ref=song_ref, exclude_relations=new_exclude_relations)
            if len(new_songs) < 1:
                continue
            new_song = new_songs[0]

            if is_feature:
                artist_obj.feature_songs.append(new_song)
            else:
                artist_obj.main_songs.append(new_song)

        # fetch albums
        for album_ref, _ in self.pull_artist_album(artist_ref=Reference(id_=artist_id)):
            new_albums = self.pull_albums(album_ref=album_ref, exclude_relations=new_exclude_relations)
            if len(new_albums) < 1:
                continue
            artist_obj.main_albums.append(new_albums[0])

        return artist_obj

    def pull_artists(self, artist_ref: Reference = None, exclude_relations: set = None, flat: bool = False) -> List[Artist]:
        """

        :param artist_ref:
        :param exclude_relations:
        :param flat: if it is true it ONLY fetches the artist data
        :return:
        """

        where = "1=1"
        if artist_ref is not None:
            where = f"Artist.id=\"{artist_ref.id}\""

        query = ARTIST_QUERY.format(where=where)
        self.cursor.execute(query)

        artist_rows = self.cursor.fetchall()
        return [(
            self.get_artist_from_row(artist_row, exclude_relations=exclude_relations, flat=flat)
        ) for artist_row in artist_rows]

    def get_song_from_row(self, song_result, exclude_relations: set = None) -> Song:
        if exclude_relations is None:
            exclude_relations = set()
        new_exclude_relations: set = set(exclude_relations)
        new_exclude_relations.add(Song)

        song_id = song_result['song_id']

        # maybee fetch album

        song_obj = Song(
            id_=song_id,
            title=song_result['title'],
            isrc=song_result['isrc'],
            length=song_result['length'],
            tracksort=song_result['tracksort'],
            genre=song_result['genre'],
            target=Target(
                id_=song_result['target_id'],
                file=song_result['file'],
                path=song_result['path']
            ),
            source_list=self.pull_sources(song_ref=Reference(id_=song_id)),
            lyrics=self.pull_lyrics(song_ref=Reference(id_=song_id)),
        )

        if Album not in exclude_relations and song_result['album_id'] is not None:
            album_obj = self.pull_albums(album_ref=Reference(song_result['album_id']),
                                         exclude_relations=new_exclude_relations)
            if len(album_obj) > 0:
                song_obj.album = album_obj[0]

        flat_artist = Artist in exclude_relations

        main_artists = []
        feature_artists = []
        for song_ref, artist_ref, is_feature in self.pull_artist_song(song_ref=Reference(song_id)):
            if is_feature:
                feature_artists.extend(self.pull_artists(artist_ref=artist_ref, flat=flat_artist))
            else:
                main_artists.extend(self.pull_artists(artist_ref=artist_ref, flat=flat_artist))

        song_obj.main_artist_list = main_artists
        song_obj.feature_artist_list = feature_artists

        return song_obj

    def pull_songs(self, song_ref: Reference = None, album_ref: Reference = None, exclude_relations: set = set()) -> \
            List[Song]:
        """
        This function is used to get one song (including its children like Sources etc)
        from one song id (a reference object)
        :param exclude_relations:
        By default all relations are pulled by this funktion. If the class object of for
        example the Artists is in the set it won't get fetched.
        This is done to prevent an infinite recursion.
        :param song_ref:
        :param album_ref:
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
            exclude_relations=exclude_relations
        ) for song_result in song_rows]

    def get_album_from_row(self, album_result, exclude_relations=None) -> Album:
        if exclude_relations is None:
            exclude_relations = set()
        new_exclude_relations: set = exclude_relations.copy()
        new_exclude_relations.add(Album)

        album_id = album_result['album_id']
        language = album_result['language']
        if language is not None:
            language = pycountry.languages.get(alpha_3=album_result['language'])

        album_obj = Album(
            id_=album_id,
            title=album_result['title'],
            label=album_result['label'],
            album_status=album_result['album_status'],
            language=language,
            date=ID3Timestamp.strptime(album_result['date'], "%Y-%m-%d"),
            country=album_result['country'],
            barcode=album_result['barcode'],
            is_split=album_result['is_split'],
            albumsort=album_result['albumsort'],
            source_list=self.pull_sources(album_ref=Reference(id_=album_id))
        )

        if Song not in exclude_relations:
            # getting the tracklist
            tracklist: List[Song] = self.pull_songs(
                album_ref=Reference(id_=album_id),
                exclude_relations=new_exclude_relations
            )
            album_obj.set_tracklist(tracklist=tracklist)

        flat_artist = Artist in exclude_relations
        for _, artist_ref in self.pull_artist_album(album_ref=Reference(id_=album_id)):
            artists = self.pull_artists(artist_ref, flat=flat_artist, exclude_relations=new_exclude_relations)
            if len(artists) < 1:
                continue
            album_obj.artists.append(artists[0])

        return album_obj

    def pull_albums(self, album_ref: Reference = None, song_ref: Reference = None, exclude_relations: set = None) -> \
            List[Album]:
        """
        This function is used to get matching albums/releses 
        from one song id (a reference object)
        :param exclude_relations:
        By default all relations are pulled by this funktion. If the class object of for
        example the Artists is in the set it won't get fetched.
        This is done to prevent an infinite recursion.
        :param album_ref:
        :return requested_album_list:
        """
        if exclude_relations is None:
            exclude_relations = set()

        query = ALBUM_QUERY_UNJOINED
        where = "1=1"
        if album_ref is not None:
            query = ALBUM_QUERY_UNJOINED
            where = f"Album.id=\"{album_ref.id}\""
        elif song_ref is not None:
            query = ALBUM_QUERY_JOINED
            where = f"Song.id=\"{song_ref.id}\""

        query = query.format(where=where)
        self.cursor.execute(query)

        album_rows = self.cursor.fetchall()

        return [self.get_album_from_row(
            album_result=album_row,
            exclude_relations=exclude_relations
        ) for album_row in album_rows]


if __name__ == "__main__":
    cache = Database("")
