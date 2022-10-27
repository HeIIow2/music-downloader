import sqlite3
import os
import logging


def get_temp_dir():
    import tempfile

    temp_folder = "music-downloader"
    temp_dir = os.path.join(tempfile.gettempdir(), temp_folder)
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    return temp_dir


DATABASE_STRUCTURE_FILE = "database_structure.sql"
TEMP_DIR = get_temp_dir()
DATABASE_FILE = "metadata.db"
db_path = os.path.join(TEMP_DIR, DATABASE_FILE)

connection = sqlite3.connect(db_path)
cursor = connection.cursor()


def init_db(cursor, connection, reset_anyways: bool = False):
    # check if db exists
    exists = True
    try:
        query = 'SELECT * FROM track;'
        cursor.execute(query)
        _ = cursor.fetchall()
    except sqlite3.OperationalError:
        exists = False

    if not exists:
        logging.info("Database does not exist yet.")

    if reset_anyways or not exists:
        # reset the database if reset_anyways is true or if an error has been thrown previously.
        logging.info("Creating/Reseting Database.")

        # read the file
        with open(DATABASE_STRUCTURE_FILE, "r") as database_structure_file:
            query = database_structure_file.read()
            cursor.executescript(query)
            connection.commit()


def add_artist(
        musicbrainz_artistid: str,
        artist: str = None
):
    query = "INSERT OR REPLACE INTO artist (id, name) VALUES (?, ?);"
    values = musicbrainz_artistid, artist

    cursor.execute(query, values)
    connection.commit()


def add_release_group(
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
    cursor.executemany(adjacency_query, adjacency_values)
    connection.commit()

    # add release group
    query = "INSERT OR REPLACE INTO release_group (id, albumartist, albumsort, musicbrainz_albumtype, compilation, album_artist_id) VALUES (?, ?, ?, ?, ?, ?);"
    values = musicbrainz_releasegroupid, albumartist, albumsort, musicbrainz_albumtype, compilation, album_artist_id
    cursor.execute(query, values)
    connection.commit()


def add_release(
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

    cursor.execute(query, values)
    connection.commit()


def add_track(
        musicbrainz_releasetrackid: str,
        musicbrainz_albumid: str,
        feature_aritsts: list,
        track: str = None,
        isrc: str = None
):
    # add adjacency
    adjacency_list = []
    for artist_id in feature_aritsts:
        adjacency_list.append((artist_id, musicbrainz_releasetrackid))
    adjacency_values = tuple(adjacency_list)
    adjacency_query = "INSERT OR REPLACE INTO artist_track (artist_id, track_id) VALUES (?, ?);"
    cursor.executemany(adjacency_query, adjacency_values)
    connection.commit()

    # add track
    query = "INSERT OR REPLACE INTO track (id, release_id, track, isrc) VALUES (?, ?, ?, ?);"
    values = musicbrainz_releasetrackid, musicbrainz_albumid, track, isrc
    cursor.execute(query, values)
    connection.commit()


init_db(cursor=cursor, connection=connection, reset_anyways=False)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
