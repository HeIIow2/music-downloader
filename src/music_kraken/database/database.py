from typing import List
import sqlite3
import os
import logging
import json
from pkg_resources import resource_string

from .song import (
    Song,
    Lyrics,
    Metadata,
    Target,
    Artist,
    Source
)
from .get_song import get_song_from_response
from ..utils.shared import (
    DATABASE_LOGGER
)

logger = DATABASE_LOGGER

class Database:
    def __init__(self, path_to_db: str, reset_anyways: bool = False):
        self.path_to_db = path_to_db

        self.connection = sqlite3.connect(self.path_to_db)
        self.cursor = self.connection.cursor()

        # init database
        self.init_db(reset_anyways=reset_anyways)

    def init_db(self, reset_anyways: bool = False):
        # check if db exists
        exists = True
        try:
            query = 'SELECT * FROM track;'
            self.cursor.execute(query)
            _ = self.cursor.fetchall()
        except sqlite3.OperationalError:
            exists = False

        if not exists:
            logger.info("Database does not exist yet.")

        if reset_anyways or not exists:
            # reset the database if reset_anyways is true or if an error has been thrown previously.
            logger.info(f"Reseting the database.")

            query = resource_string("music_kraken", "static_files/temp_database_structure.sql").decode('utf-8')
            self.cursor.executescript(query)
            self.connection.commit()

    def add_artist(
            self,
            musicbrainz_artistid: str,
            artist: str = None
    ):
        query = "INSERT OR REPLACE INTO artist (id, name) VALUES (?, ?);"
        values = musicbrainz_artistid, artist

        self.cursor.execute(query, values)
        self.connection.commit()

    def add_release_group(
            self,
            musicbrainz_releasegroupid: str,
            artist_ids: list,
            albumartist: str = None,
            albumsort: int = None,
            musicbrainz_albumtype: str = None,
            compilation: str = None,
            album_artist_id: str = None
    ):
        # add adjacency
        adjacency_list = []
        for artist_id in artist_ids:
            adjacency_list.append((artist_id, musicbrainz_releasegroupid))
        adjacency_values = tuple(adjacency_list)
        adjacency_query = "INSERT OR REPLACE INTO artist_release_group (artist_id, release_group_id) VALUES (?, ?);"
        self.cursor.executemany(adjacency_query, adjacency_values)
        self.connection.commit()

        # add release group
        query = "INSERT OR REPLACE INTO release_group (id, albumartist, albumsort, musicbrainz_albumtype, compilation, album_artist_id) VALUES (?, ?, ?, ?, ?, ?);"
        values = musicbrainz_releasegroupid, albumartist, albumsort, musicbrainz_albumtype, compilation, album_artist_id
        self.cursor.execute(query, values)
        self.connection.commit()

    def add_release(
            self,
            musicbrainz_albumid: str,
            release_group_id: str,
            title: str = None,
            copyright_: str = None,
            album_status: str = None,
            language: str = None,
            year: str = None,
            date: str = None,
            country: str = None,
            barcode: str = None
    ):
        query = "INSERT OR REPLACE INTO release_ (id, release_group_id, title, copyright, album_status, language, year, date, country, barcode) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        values = musicbrainz_albumid, release_group_id, title, copyright_, album_status, language, year, date, country, barcode

        self.cursor.execute(query, values)
        self.connection.commit()

    def add_track(
            self,
            musicbrainz_releasetrackid: str,
            musicbrainz_albumid: str,
            feature_aritsts: list,
            tracknumber: str = None,
            track: str = None,
            isrc: str = None,
            length: int = None
    ):
        # add adjacency
        adjacency_list = []
        for artist_id in feature_aritsts:
            adjacency_list.append((artist_id, musicbrainz_releasetrackid))
        adjacency_values = tuple(adjacency_list)
        adjacency_query = "INSERT OR REPLACE INTO artist_track (artist_id, track_id) VALUES (?, ?);"
        self.cursor.executemany(adjacency_query, adjacency_values)
        self.connection.commit()

        # add track
        query = "INSERT OR REPLACE INTO track (id, release_id, track, isrc, tracknumber, length) VALUES (?, ?, ?, ?, ?, ?);"
        values = musicbrainz_releasetrackid, musicbrainz_albumid, track, isrc, tracknumber, length
        self.cursor.execute(query, values)
        self.connection.commit()

    @staticmethod
    def get_custom_track_query(custom_where: list) -> str:
        where_args = [
            "1 = 1"
        ]
        where_args.extend(custom_where)

        where_arg = " AND ".join(where_args)
        query = f"""
SELECT DISTINCT
    json_object(
        'artists', json_group_array(
            (
            SELECT DISTINCT json_object(
                'id', artist.id,
                'name', artist.name
                )
            )
        ),
        'source', json_group_array(
            (
            SELECT DISTINCT json_object(
                'src', src_table.src,
                'url', src_table.url,
                'valid', src_table.valid
                )
            )
        ),
        'lyrics', json_group_array(
            (
            SELECT DISTINCT json_object(
                'text', lyrics_table.text
                'language', lyrics_table.language
                )
            )
        ),
        'target', json_group_array(
            (
            SELECT DISTINCT json_object(
                'file', target.file
                'path', target.path
                )
            )
        ),
        'id', track.id,
        'mb_id', track.mb_id,
        'tracknumber', track.tracknumber,
        'titlesort', track.tracknumber,
        'musicbrainz_releasetrackid', track.id,
        'musicbrainz_albumid', release_.id,
        'title', track.track,
        'isrc', track.isrc,
        'album', release_.title,
        'copyright', release_.copyright,
        'album_status', release_.album_status,
        'language', release_.language,
        'year', release_.year,
        'date', release_.date,
        'country', release_.country,
        'barcode', release_.barcode,
        'albumartist', release_group.albumartist,
        'albumsort', release_group.albumsort,
        'musicbrainz_albumtype', release_group.musicbrainz_albumtype,
        'compilation', release_group.compilation,
        'album_artist_id', release_group.album_artist_id,
        'length', track.length,
        'path', track.path,
        'file', track.file,
        'genre', track.genre,
        'url', track.url,
        'src', track.src,
        'lyrics', track.lyrics
        )
FROM track
LEFT JOIN release_          ON track.release_id = release_.id
LEFT JOIN release_group     ON release_.id = release_group.id
LEFT JOIN artist_track      ON track.id = artist_track.track_id
LEFT JOIN artist            ON artist_track.artist_id = artist.id
LEFT JOIN source src_table  ON track.id = src_table.track_id
LEFT JOIN lyrics lyrics_table ON track.id = lyrics_table.track_id
LEFT JOIN target            ON track.id = target.track_id
WHERE
    {where_arg}
GROUP BY track.id;
        """
        return query

    def get_custom_track(self, custom_where: list) -> List[Song]:
        query = Database.get_custom_track_query(custom_where=custom_where)
        return [get_song_from_response(json.loads(i[0])) for i in self.cursor.execute(query)]

    def get_track_metadata(self, musicbrainz_releasetrackid: str):
        # this would be vulnerable if musicbrainz_releasetrackid would be user input
        resulting_tracks = self.get_custom_track([f'track.id == "{musicbrainz_releasetrackid}"'])
        if len(resulting_tracks) != 1:
            return -1

        return resulting_tracks[0]

    def get_tracks_to_download(self) -> List[Song]:
        return self.get_custom_track(['track.downloaded == 0'])

    def get_tracks_without_src(self) -> List[Song]:
        return self.get_custom_track(["(track.url IS NULL OR track.src IS NULL)"])

    def get_tracks_without_isrc(self) -> List[Song]:
        return self.get_custom_track(["track.isrc IS NULL"])

    def get_tracks_without_filepath(self) -> List[Song]:
        return self.get_custom_track(["(track.file IS NULL OR track.path IS NULL OR track.genre IS NULL)"])

    def get_tracks_for_lyrics(self) -> List[Song]:
        return self.get_custom_track(["track.lyrics IS NULL"])

    def add_lyrics(self, song: Song, lyrics: Lyrics):
        query = f"""
UPDATE track
SET lyrics = ?
WHERE '{song.id}' == id;
            """
        self.cursor.execute(query, (str(lyrics.text),))
        self.connection.commit()

    def update_download_status(self, track_id: str):
        query = f"UPDATE track SET downloaded = 1, WHERE '{track_id}' == id;"
        self.cursor.execute(query)
        self.connection.commit()

    def set_field_of_song(self, track_id: str, key: str, value: str):
        query = f"UPDATE track SET {key} = ? WHERE '{track_id}' == id;"
        self.cursor.execute(query, (value,))
        self.connection.commit()

    def set_download_data(self, track_id: str, url: str, src: str):
        query = f"""
UPDATE track
SET url = ?,
    src = ?
WHERE '{track_id}' == id;
            """
        self.cursor.execute(query, (url, src))
        self.connection.commit()

        query = "INSERT OR REPLACE INTO source (track_id, src, url) VALUES (?, ?, ?);"
        self.cursor.execute(query, (track_id, src, url))
        self.connection.commit()

    def set_filepath(self, track_id: str, file: str, path: str, genre: str):
        query = f"""
UPDATE track
SET file = ?,
    path = ?,
    genre = ?
WHERE '{track_id}' == id;
        """
        self.cursor.execute(query, (file, path, genre))
        self.connection.commit()

    def write_target(self, song_id: str, target: Target):
        query = f"UPDATE track SET file = ?, path = ? WHERE '{song_id}' == id;"
        self.cursor.execute(query, (target.file, target.path))
        self.connection.commit()

    def write_artist(self, artist: Artist, song_id: str = None, release_group_id: str = None):
        artist_id = artist.id

        query = "INSERT OR REPLACE INTO artist (id, mb_id, name) VALUES (?, ?, ?);"
        self.cursor.execute(query, (artist_id, artist.mb_id, artist.name))
        self.connection.commit()

        if song_id is not None:
            adjacency_query = "INSERT OR REPLACE INTO artist_track (artist_id, track_id) VALUES (?, ?);"
            self.cursor.execute(adjacency_query, (artist_id, song_id))
            self.connection.commit()

        if release_group_id is not None:
            adjacency_query = "INSERT OR REPLACE INTO artist_release_group (artist_id, release_group_id) VALUES (?, ?);"
            self.cursor.execute(adjacency_query, (artist_id, release_group_id))
            self.connection.commit()

    def write_many_artists(self, song_id: str, artist_list: List[Artist]):
        for artist in artist_list:
            self.write_artist(song_id=song_id, artist=artist)

    def write_source(self, song_id: str, source: Source):
        pass

    def write_many_sources(self, song_id: str, source_list: List[Source]):
        for source in source_list:
            self.write_source(song_id=song_id, source=source)

    def write_song(self, song: Song):
        song_id = song.id
        
        # write artists
        self.write_many_artists(song_id=song_id, artist_list=song.artists)
        # write sources
        self.write_many_sources(song_id=song_id, source_list=song.sources)
        # write target
        self.write_target(song_id=song_id, target=song.target)

    def write_many_song(self, songs: List[Song]):
        for song in songs:
            self.write_song(song=song)
