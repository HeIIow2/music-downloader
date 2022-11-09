import requests
import sys
import os
import logging
from typing import List

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from tools import phonetic_compares
from tools.object_handeling import get_elem_from_obj

# search doesn't support isrc
# https://genius.com/api/search/multi?q=I Prevail - Breaking Down
# https://genius.com/api/songs/6192944
# https://docs.genius.com/

session = requests.Session()
session.headers = {
    "Connection": "keep-alive",
    "Referer": "https://genius.com/search/embed"
}
logger = logging.getLogger("genius")


def set_proxy(proxies: dict):
    session.proxies = proxies


def set_logger(logger_: logging.Logger):
    global logger
    logger = logger_


class Song:
    def __init__(self, raw_data: dict, desirered_data: dict):
        self.raw_data = raw_data
        self.desired_data = desirered_data

        song_data = get_elem_from_obj(self.raw_data, ['result'], return_if_none={})
        self.id = get_elem_from_obj(song_data, ['id'])
        self.artist = get_elem_from_obj(song_data, ['primary_artist', 'name'])
        self.title = get_elem_from_obj(song_data, ['title'])

        self.language = get_elem_from_obj(song_data, ['language'])
        self.url = get_elem_from_obj(song_data, ['url'])

        # maybe could be implemented
        self.lyricist: str

        if get_elem_from_obj(song_data, ['lyrics_state']) != "complete":
            logger.warning(f"lyrics state of {self.title} by {self.artist} is not complete but {get_elem_from_obj(song_data, ['lyrics_state'])}")

        self.valid = self.is_valid()
        if self.valid:
            logger.info(f"found lyrics for \"{self.__repr__()}\"")

        self.lyrics: str

    def is_valid(self) -> bool:
        title_match, title_distance = phonetic_compares.match_titles(self.title, self.desired_data['track'])
        artist_match, artist_distance = phonetic_compares.match_artists(self.artist, self.desired_data['artist'])

        return title_match and artist_match

    def __repr__(self) -> str:
        return f"{self.title} by {self.artist}"

    def fetch_lyrics(self) -> str:
        if not self.valid:
            logger.warning(f"{self.__repr__()} is invalid but the lyrics still get fetched. Something could be wrong.")
        lyrics = ""


        self.lyrics = lyrics
        return lyrics


def build_search_query(artist: str, track: str) -> str:
    return f"{artist} - {track}"


def process_multiple_songs(song_datas: list, desired_data: dict) -> List[Song]:
    all_songs = [Song(song_data, desired_data) for song_data in song_datas]
    return [song for song in all_songs if not song.valid]


def search_song_list(artist: str, track: str) -> List[Song]:
    endpoint = "https://genius.com/api/search/multi?q="
    url = endpoint + build_search_query(artist, track)
    logging.info(f"requesting {url}")

    desired_data = {
        'artist': artist,
        'track': track
    }

    r = session.get(url)
    if r.status_code != 200:
        logging.warning(f"{r.url} returned {r.status_code}:\n{r.content}")
        return []
    content = r.json()
    if get_elem_from_obj(content, ['meta', 'status']) != 200:
        logging.warning(f"{r.url} returned {get_elem_from_obj(content, ['meta', 'status'])}:\n{content}")
        return []

    # print(r.status_code)
    # print(r.json())

    sections = get_elem_from_obj(content, ['response', 'sections'])
    for section in sections:
        section_type = get_elem_from_obj(section, ['type'])
        print(section_type)
        if section_type == "song":
            return process_multiple_songs(get_elem_from_obj(section, ['hits'], return_if_none=[]), desired_data)

    return []

def search(artist: str, track: str):
    return search_song_list(artist, track)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    songs = search_song_list("Psychonaut 4", "Sana Sana Sana, Cura Cura Cura")
    print(songs)
