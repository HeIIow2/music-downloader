import time

import requests
import bs4

from ...utils.shared import *
from ...utils import phonetic_compares

from .source import AudioSource
from ...database import song as song_objects


TRIES = 5
TIMEOUT = 10

logger = MUSIFY_LOGGER

session = requests.Session()
session.headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "Connection": "keep-alive",
    "Referer": "https://musify.club/"
}
session.proxies = proxies


class Musify(AudioSource):
    @classmethod
    def fetch_source(cls, song: dict) -> str | None:
        super().fetch_source(song)

        title = song.title
        artists = song.get_artist_names()

        # trying to get a download link via the autocomplete api
        for artist in artists:
            url = cls.fetch_source_from_autocomplete(title=title, artist=artist)
            if url is not None:
                logger.info(f"found download link {url}")
                return url

        # trying to get a download link via the html of the direct search page
        for artist in artists:
            url = cls.fetch_source_from_search(title=title, artist=artist)
            if url is not None:
                logger.info(f"found download link {url}")
                return url

        logger.warning(f"Didn't find the audio on {cls.__name__}")

    @classmethod
    def get_download_link(cls, track_url: str) -> str | None:
        # https://musify.club/track/dl/18567672/rauw-alejandro-te-felicito-feat-shakira.mp3
        # /track/sundenklang-wenn-mein-herz-schreit-3883217'

        file_ = track_url.split("/")[-1]
        if len(file_) == 0:
            return None
        musify_id = file_.split("-")[-1]
        musify_name = "-".join(file_.split("-")[:-1])

        return f"https://musify.club/track/dl/{musify_id}/{musify_name}.mp3"

    @classmethod
    def fetch_source_from_autocomplete(cls, title: str, artist: str) -> str | None:
        url = f"https://musify.club/search/suggestions?term={artist} - {title}"

        try:
            logger.info(f"calling {url}")
            r = session.get(url=url)
        except requests.exceptions.ConnectionError:
            logger.info("connection error occurred")
            return None
        if r.status_code == 200:
            autocomplete = r.json()
            for song in autocomplete:
                if artist in song['label'] and "/track" in song['url']:
                    return cls.get_download_link(song['url'])

        return None

    @classmethod
    def get_soup_of_search(cls, query: str, trie=0) -> bs4.BeautifulSoup | None:
        url = f"https://musify.club/search?searchText={query}"
        logger.debug(f"Trying to get soup from {url}")
        r = session.get(url)
        if r.status_code != 200:
            if r.status_code in [503] and trie < TRIES:
                logging.warning(f"youtube blocked downloading. ({trie}-{TRIES})")
                logging.warning(f"retrying in {TIMEOUT} seconds again")
                time.sleep(TIMEOUT)
                return cls.get_soup_of_search(query, trie=trie + 1)

            logging.warning("too many tries, returning")
            return None
        return bs4.BeautifulSoup(r.content, features="html.parser")

    @classmethod
    def fetch_source_from_search(cls, title: str, artist: str) -> str | None:
        query: str = f"{artist[0]} - {title}"
        search_soup = cls.get_soup_of_search(query=query)
        if search_soup is None:
            return None

        # get the soup of the container with all track results
        tracklist_container_soup = search_soup.find_all("div", {"class": "playlist"})
        if len(tracklist_container_soup) == 0:
            return None
        if len(tracklist_container_soup) != 1:
            logger.warning("HTML Layout of https://musify.club changed. (or bug)")
        tracklist_container_soup = tracklist_container_soup[0]

        tracklist_soup = tracklist_container_soup.find_all("div", {"class": "playlist__details"})

        def parse_track_soup(_track_soup):
            anchor_soups = _track_soup.find_all("a")
            artist_ = anchor_soups[0].text.strip()
            track_ = anchor_soups[1].text.strip()
            url_ = anchor_soups[1]['href']
            return artist_, track_, url_

        # check each track in the container, if they match
        for track_soup in tracklist_soup:
            artist_option, title_option, track_url = parse_track_soup(track_soup)

            title_match, title_distance = phonetic_compares.match_titles(title, title_option)
            artist_match, artist_distance = phonetic_compares.match_artists(artist, artist_option)

            logging.debug(f"{(title, title_option, title_match, title_distance)}")
            logging.debug(f"{(artist, artist_option, artist_match, artist_distance)}")

            if not title_match and not artist_match:
                return cls.get_download_link(track_url)

        return None

    @classmethod
    def download_from_musify(cls, target: song_objects.Target, url):
        # returns if target hasn't been set
        if target.path is None or target.file is None:
            logger.warning(f"target hasn't been set. Can't download. Most likely a bug.")
            return False

        # download the audio data
        logger.info(f"downloading: '{url}'")
        try:
            r = session.get(url, timeout=15)
        except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
            return False
        if r.status_code != 200:
            if r.status_code == 404:
                logger.warning(f"{r.url} was not found")
                return False
            if r.status_code == 503:
                logger.warning(f"{r.url} raised an internal server error")
                return False
            logger.error(f"\"{url}\" returned {r.status_code}: {r.text}")
            return False

        # write to the file and create folder if it doesn't exist
        if not os.path.exists(target.path):
            os.makedirs(target.path, exist_ok=True)
        with open(target.file, "wb") as mp3_file:
            mp3_file.write(r.content)
        logger.info("finished")
        return True

    @classmethod
    def fetch_audio(cls, song: song_objects.Song, src: song_objects.Source):
        super().fetch_audio(song, src)
        return cls.download_from_musify(song.target, src.url)


if __name__ == "__main__":
    pass
