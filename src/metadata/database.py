import sqlite3
import os
import logging
import json
import requests


class Database:
    def __init__(self, path_to_db: str, db_structure: str, db_structure_fallback: str, logger: logging.Logger, reset_anyways: bool = False):
        self.logger = logger
        self.path_to_db = path_to_db

        self.connection = sqlite3.connect(self.path_to_db)
        self.cursor = self.connection.cursor()

        # init database
        self.init_db(database_structure=db_structure, database_structure_fallback=db_structure_fallback, reset_anyways=reset_anyways)

    def init_db(self, database_structure: str, database_structure_fallback: str, reset_anyways: bool = False):
        # check if db exists
        exists = True
        try:
            query = 'SELECT * FROM track;'
            self.cursor.execute(query)
            _ = self.cursor.fetchall()
        except sqlite3.OperationalError:
            exists = False

        if not exists:
            self.logger.info("Database does not exist yet.")

        if reset_anyways or not exists:
            # reset the database if reset_anyways is true or if an error has been thrown previously.
            self.logger.info("Creating/Reseting Database.")

            if not os.path.exists(database_structure):
                self.logger.info("database structure file doesn't exist yet, fetching from github")
                r = requests.get(database_structure_fallback)
                
                with open(database_structure, "w") as f:
                    f.write(r.text)

            # read the file
            with open(database_structure, "r") as database_structure_file:
                query = database_structure_file.read()
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
            isrc: str = None
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
        query = "INSERT OR REPLACE INTO track (id, release_id, track, isrc, tracknumber) VALUES (?, ?, ?, ?, ?);"
        values = musicbrainz_releasetrackid, musicbrainz_albumid, track, isrc, tracknumber
        self.cursor.execute(query, values)
        self.connection.commit()

    @staticmethod
    def get_custom_track_query(custom_where: list) -> str:
        where_args = [
            "track.release_id == release_.id",
            "release_group.id == release_.release_group_id",
            "artist_track.artist_id == artist.id",
            "artist_track.track_id == track.id"
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
        'id', track.id,
        'tracknumber', track.tracknumber,
        'titlesort  ', track.tracknumber,
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
        'path', track.path,
        'file', track.file,
        'genre', track.genre,
        'url', track.url,
        'src', track.src,
        'lyrics', track.lyrics
        )
FROM track, release_, release_group,artist, artist_track
WHERE
    {where_arg}
GROUP BY track.id;
        """
        return query

    def get_custom_track(self, custom_where: list):
        query = Database.get_custom_track_query(custom_where=custom_where)
        return [json.loads(i[0]) for i in self.cursor.execute(query)]

    def get_track_metadata(self, musicbrainz_releasetrackid: str):
        # this would be vulnerable if musicbrainz_releasetrackid would be user input
        resulting_tracks = self.get_custom_track([f'track.id == "{musicbrainz_releasetrackid}"'])
        if len(resulting_tracks) != 1:
            return -1

        return resulting_tracks[0]

    def get_tracks_to_download(self):
        return self.get_custom_track(['track.downloaded == 0'])

    def get_tracks_without_src(self):
        return self.get_custom_track(["(track.url IS NULL OR track.src IS NULL)"])

    def get_tracks_without_isrc(self):
        return self.get_custom_track(["track.isrc IS NULL"])

    def get_tracks_without_filepath(self):
        return self.get_custom_track(["(track.file IS NULL OR track.path IS NULL OR track.genre IS NULL)"])

    def get_tracks_for_lyrics(self):
        return self.get_custom_track(["track.lyrics IS NULL"])

    def add_lyrics(self, track_id: str, lyrics: str):
        query = f"""
UPDATE track
SET lyrics = ?
WHERE '{track_id}' == id;
            """
        self.cursor.execute(query, (str(lyrics), ))
        self.connection.commit()

    def update_download_status(self, track_id: str):
        query = f"UPDATE track SET downloaded = 1, WHERE '{track_id}' == id;"
        self.cursor.execute(query)
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


if __name__ == "__main__":
    import tempfile

    temp_folder = "music-downloader"
    temp_dir = os.path.join(tempfile.gettempdir(), temp_folder)
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    temp_dir = get_temp_dir()
    DATABASE_FILE = "metadata.db"
    DATABASE_STRUCTURE_FILE = "database_structure.sql"
    db_path = os.path.join(TEMP_DIR, DATABASE_FILE)

    logging.basicConfig()

    logger = logging.getLogger("database")
    logger.setLevel(logging.DEBUG)

    database = Database(os.path.join(temp_dir, "metadata.db"), os.path.join(temp_dir, "database_structure.sql"), logger,
                        reset_anyways=True)
