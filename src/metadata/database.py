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


# DATABASE_STRUCTURE_FILE = "database_structure.sql"
DATABASE_STRUCTURE_FILE = "src/metadata/database_structure.sql"
TEMP_DIR = get_temp_dir()
DATABASE_FILE = "metadata.db"
db_path = os.path.join(TEMP_DIR, DATABASE_FILE)

connection = sqlite3.connect(db_path)
connection.row_factory = sqlite3.Row
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

def get_custom_track_querry(custom_where: list) -> str:
    where_args = [
        "track.release_id == release_.id",
        "release_group.id == release_.release_group_id"
    ]
    where_args.extend(custom_where)

    where_arg = " AND ".join(where_args)
    query = f"""
SELECT DISTINCT 
    track.id as musicbrainz_releasetrackid,
    release_.id as musicbrainz_albumid,
    release_group.id as musicbrainz_releasegroupid,
    track.track as track,
    track.isrc as isrc,
    release_.title as title,
    release_.copyright as copyright,
    release_.album_status as album_status,
    release_.language as language,
    release_.year as year,
    release_.date as date,
    release_.country as country,
    release_.barcode as barcode,
    release_group.albumartist as albumartist,
    release_group.albumsort as albumsort,
    release_group.musicbrainz_albumtype as musicbrainz_albumtype,
    release_group.compilation as compilation,
    release_group.album_artist_id as album_artist_id
FROM track, release_, release_group, artist
WHERE
    {where_arg};
    """
    return query

def get_custom_track(custom_where: list):
    query = get_custom_track_querry(custom_where=custom_where)
    return [dict(i) for i in cursor.execute(query)]

def get_track_metadata(musicbrainz_releasetrackid: str):
    # this would be vulnerable if musicbrainz_releasetrackid would be user input
    resulting_tracks = get_custom_track([f'track.id == "{musicbrainz_releasetrackid}"'])
    if len(resulting_tracks) != 1:
        return -1

    return dict(resulting_tracks[0])

def get_tracks_to_download():
    return get_custom_track(["track.downloaded == 0"])

def get_tracks_without_isrc():
    return get_custom_track(["track.isrc IS NULL"])

init_db(cursor=cursor, connection=connection, reset_anyways=False)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # get_track(["track.downloaded == 0", "track.isrc IS NOT NULL"])
    #
    for track in get_tracks_without_isrc():
        print(track['track'])

    #print(get_track_metadata("a85d5ed5-20e5-4f95-8034-d204d81a36dd"))
