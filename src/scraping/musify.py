import logging
import time

import requests
import bs4

from ..utils.shared import *
from ..utils import phonetic_compares

TRIES = 5
TIMEOUT = 10

session = requests.Session()
session.headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "Connection": "keep-alive",
    "Referer": "https://musify.club/"
}
session.proxies = proxies


def get_musify_url(row):
    title = row['title']
    artists = row['artists']

    url = f"https://musify.club/search/suggestions?term={artists[0]} - {title}"

    try:
        r = session.get(url=url)
    except requests.exceptions.ConnectionError:
        return None
    if r.status_code == 200:
        autocomplete = r.json()
        for row in autocomplete:
            if any(a in row['label'] for a in artists) and "/track" in row['url']:
                return get_download_link(row['url'])

    return None


def get_download_link(default_url):
    # https://musify.club/track/dl/18567672/rauw-alejandro-te-felicito-feat-shakira.mp3
    # /track/sundenklang-wenn-mein-herz-schreit-3883217'

    file_ = default_url.split("/")[-1]
    musify_id = file_.split("-")[-1]
    musify_name = "-".join(file_.split("-")[:-1])

    return f"https://musify.club/track/dl/{musify_id}/{musify_name}.mp3"


def download_from_musify(file, url):
    logging.info(f"downloading: '{url}'")
    try:
        r = session.get(url, timeout=15)
    except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
        return -1
    if r.status_code != 200:
        if r.status_code == 404:
            logging.warning(f"{r.url} was not found")
            return -1
        if r.status_code == 503:
            logging.warning(f"{r.url} raised an internal server error")
            return -1
        raise ConnectionError(f"\"{url}\" returned {r.status_code}: {r.text}")
    with open(file, "wb") as mp3_file:
        mp3_file.write(r.content)
    logging.info("finished")


def download(row):
    url = row['url']
    file_ = row['file']
    return download_from_musify(file_, url)


def get_soup_of_search(query: str, trie=0):
    url = f"https://musify.club/search?searchText={query}"
    logging.debug(f"Trying to get soup from {url}")
    r = session.get(url)
    if r.status_code != 200:
        if r.status_code in [503] and trie < TRIES:
            logging.warning(f"youtube blocked downloading. ({trie}-{TRIES})")
            logging.warning(f"retrying in {TIMEOUT} seconds again")
            time.sleep(TIMEOUT)
            return get_soup_of_search(query, trie=trie + 1)

        logging.warning("too many tries, returning")
        raise ConnectionError(f"{r.url} returned {r.status_code}:\n{r.content}")
    return bs4.BeautifulSoup(r.content, features="html.parser")


def search_for_track(row):
    track = row['title']
    artist = row['artists']

    soup = get_soup_of_search(f"{artist[0]} - {track}")
    tracklist_container_soup = soup.find_all("div", {"class": "playlist"})
    if len(tracklist_container_soup) == 0:
        return None
    if len(tracklist_container_soup) != 1:
        raise Exception("Connfusion Error. HTML Layout of https://musify.club changed.")
    tracklist_container_soup = tracklist_container_soup[0]

    tracklist_soup = tracklist_container_soup.find_all("div", {"class": "playlist__details"})

    def parse_track_soup(_track_soup):
        anchor_soups = _track_soup.find_all("a")
        band_name = anchor_soups[0].text.strip()
        title = anchor_soups[1].text.strip()
        url_ = anchor_soups[1]['href']
        return band_name, title, url_

    for track_soup in tracklist_soup:
        band_option, title_option, track_url = parse_track_soup(track_soup)

        title_match, title_distance = phonetic_compares.match_titles(track, title_option)
        band_match, band_distance = phonetic_compares.match_artists(artist, band_option)

        logging.debug(f"{(track, title_option, title_match, title_distance)}")
        logging.debug(f"{(artist, band_option, band_match, band_distance)}")

        if not title_match and not band_match:
            return get_download_link(track_url)

    return None


def get_musify_url_slow(row):
    result = search_for_track(row)
    if result is not None:
        return result


if __name__ == "__main__":
    pass
