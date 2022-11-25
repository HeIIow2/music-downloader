import requests
from typing import List
from bs4 import BeautifulSoup
import pycountry

from ..database import (
    Lyrics
)
from ..utils.shared import *
from ..utils import phonetic_compares
from ..utils.object_handeling import get_elem_from_obj

# search doesn't support isrc
# https://genius.com/api/search/multi?q=I Prevail - Breaking Down
# https://genius.com/api/songs/6192944
# https://docs.genius.com/

session = requests.Session()
session.headers = {
    "Connection": "keep-alive",
    "Referer": "https://genius.com/search/embed"
}
session.proxies = proxies

logger = GENIUS_LOGGER


class Song:
    def __init__(self, raw_data: dict, desirered_data: dict):
        self.raw_data = raw_data
        self.desired_data = desirered_data

        song_data = get_elem_from_obj(self.raw_data, ['result'], return_if_none={})
        self.id = get_elem_from_obj(song_data, ['id'])
        self.artist = get_elem_from_obj(song_data, ['primary_artist', 'name'])
        self.title = get_elem_from_obj(song_data, ['title'])

        lang_code = get_elem_from_obj(song_data, ['language']) or "en"
        self.language = pycountry.languages.get(alpha_2=lang_code)
        self.lang = self.language.alpha_3
        self.url = get_elem_from_obj(song_data, ['url'])

        # maybe could be implemented
        self.lyricist: str

        if get_elem_from_obj(song_data, ['lyrics_state']) != "complete":
            logger.warning(
                f"lyrics state of {self.title} by {self.artist} is not complete but {get_elem_from_obj(song_data, ['lyrics_state'])}")

        self.valid = self.is_valid()
        if self.valid:
            logger.info(f"found lyrics for \"{self.__repr__()}\"")
        else:
            return

        self.lyrics = self.fetch_lyrics()
        if self.lyrics is None:
            self.valid = False

    def is_valid(self) -> bool:
        title_match, title_distance = phonetic_compares.match_titles(self.title, self.desired_data['track'])
        artist_match, artist_distance = phonetic_compares.match_artists(self.desired_data['artist'], self.artist)

        return not title_match and not artist_match

    def __repr__(self) -> str:
        return f"{self.title} by {self.artist} ({self.url})"

    def fetch_lyrics(self) -> str | None:
        if not self.valid:
            logger.warning(f"{self.__repr__()} is invalid but the lyrics still get fetched. Something could be wrong.")

        r = session.get(self.url)
        if r.status_code != 200:
            logging.warning(f"{r.url} returned {r.status_code}:\n{r.content}")
            return None

        soup = BeautifulSoup(r.content, "html.parser")
        lyrics_soups = soup.find_all('div', {'data-lyrics-container': "true"})
        if len(lyrics_soups) == 0:
            logger.warning(f"didn't found lyrics on {self.url}")
            return None
        if len(lyrics_soups) != 1:
            logger.warning(f"number of lyrics_soups doesn't equals 1, but {len(lyrics_soups)} on {self.url}")

        lyrics = "\n".join([lyrics_soup.getText(separator="\n", strip=True) for lyrics_soup in lyrics_soups])
        print(lyrics)

        # <div data-lyrics-container="true" class="Lyrics__Container-sc-1ynbvzw-6 YYrds">With the soundle
        self.lyrics = lyrics
        return lyrics


def process_multiple_songs(song_datas: list, desired_data: dict) -> List[Song]:
    all_songs = [Song(song_data, desired_data) for song_data in song_datas]
    return all_songs


def search_song_list(artist: str, track: str) -> List[Song]:
    endpoint = "https://genius.com/api/search/multi?q="
    url = f"{endpoint}{artist} - {track}"
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

    sections = get_elem_from_obj(content, ['response', 'sections'])
    for section in sections:
        section_type = get_elem_from_obj(section, ['type'])
        if section_type == "song":
            return process_multiple_songs(get_elem_from_obj(section, ['hits'], return_if_none=[]), desired_data)

    return []


def search(artist: str, track: str) -> list:
    results = []
    r = search_song_list(artist, track)
    for r_ in r:
        if r_.valid:
            results.append(r_)
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    songs = search("Zombiez", "WALL OF Z")
    for song in songs:
        print(song)
