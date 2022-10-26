import logging
import requests
import bs4

import phonetic_compares

session = requests.Session()
session.headers = {
    "Connection": "keep-alive",
    "Referer": "https://musify.club/"
}


def get_musify_url(row):
    title = row.title
    artists = row.artist

    url = f"https://musify.club/search/suggestions?term={artists[0]} - {title}"

    r = session.get(url=url)
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

    logging.info(f"https://musify.club/track/dl/{musify_id}/{musify_name}.mp3")

    return f"https://musify.club/track/dl/{musify_id}/{musify_name}.mp3"


def download_from_musify(file, url):
    logging.info(f"downloading: '{url}'")
    r = session.get(url)
    if r.status_code != 200:
        if r.status_code == 404:
            logging.warning(f"{url} was not found")
            return -1
        raise ConnectionError(f"\"{url}\" returned {r.status_code}: {r.text}")
    with open(file, "wb") as mp3_file:
        mp3_file.write(r.content)
    logging.info("finished")


def download(row):
    url = row['url']
    file_ = row['file']
    return download_from_musify(file_, url)


def get_soup_of_search(query: str):
    url = f"https://musify.club/search?searchText={query}"
    print(url)
    r = session.get(url)
    if r.status_code != 200:
        raise ConnectionError(f"{r.url} returned {r.status_code}:\n{r.content}")
    return bs4.BeautifulSoup(r.content, features="html.parser")

def search_for_track(row):
    track = row.title
    artist = row.artist

    soup = get_soup_of_search(f"{artist[0]} - {track}")
    tracklist_container_soup = soup.find_all("div", {"class": "playlist"})
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

        print(track, title_option, title_match, title_distance)
        print(artist, band_option, band_match, band_distance)

        if not title_match and not band_match:
            return get_download_link(track_url)

    return None


def get_musify_url_slow(row):
    result = search_for_track(row)
    if result is not None:
        return result


if __name__ == "__main__":
    import pandas as pd
    import json

    df = pd.read_csv("../temp/.cache1.csv")

    for idx, row in df.iterrows():
        row['artist'] = json.loads(row['artist'].replace("'", '"'))
        print("-" * 200)
        print("fast")
        print(get_musify_url(row))
        print("slow")
        print(get_musify_url_slow(row))
