import os

from ..utils.shared import *
from ..utils import phonetic_compares


def is_valid(a1, a2, t1, t2) -> bool:
    title_match, title_distance = phonetic_compares.match_titles(t1, t2)
    artist_match, artist_distance = phonetic_compares.match_artists(a1, a2)

    return not title_match and not artist_match


def get_metadata(file):
    artist = None
    title = None

    audiofile = EasyID3(file)
    artist = audiofile['artist']
    title = audiofile['title']

    return artist, title


def check_for_song(folder, artists, title):
    if not os.path.exists(folder):
        return False
    files = [os.path.join(folder, i) for i in os.listdir(folder)]

    for file in files:
        artists_, title_ = get_metadata(file)
        if is_valid(artists, artists_, title, title_):
            return True
    return False


def get_path(row):
    title = row['title']
    artists = row['artists']
    path_ = os.path.join(MUSIC_DIR, row['path'])

    print(artists, title, path_)
    check_for_song(path_, artists, title)

    return None


if __name__ == "__main__":
    row = {'artists': ['Psychonaut 4'], 'id': '6b40186b-6678-4328-a4b8-eb7c9806a9fb', 'tracknumber': None,
           'titlesort  ': None, 'musicbrainz_releasetrackid': '6b40186b-6678-4328-a4b8-eb7c9806a9fb',
           'musicbrainz_albumid': '0d229a02-74f6-4c77-8c20-6612295870ae', 'title': 'Sweet Decadance', 'isrc': None,
           'album': 'Neurasthenia', 'copyright': 'Talheim Records', 'album_status': 'Official', 'language': 'eng',
           'year': '2016', 'date': '2016-10-07', 'country': 'AT', 'barcode': None, 'albumartist': 'Psychonaut 4',
           'albumsort': None, 'musicbrainz_albumtype': 'Album', 'compilation': None,
           'album_artist_id': 'c0c720b5-012f-4204-a472-981403f37b12', 'path': 'dsbm/Psychonaut 4/Neurasthenia',
           'file': 'dsbm/Psychonaut 4/Neurasthenia/Sweet Decadance.mp3', 'genre': 'dsbm', 'url': None, 'src': None}
    print(get_path(row))
