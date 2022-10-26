import metadata
import download_links
import url_to_path
import download

import logging
import requests
import os

TEMP = "temp"
STEP_ONE_CACHE = ".cache1.csv"
STEP_TWO_CACHE = ".cache2.csv"
STEP_THREE_CACHE = ".cache3.csv"

MUSIC_DIR = os.path.expanduser('~/Music')
TOR = False

logging.basicConfig(level=logging.INFO)


def search_for_metadata(query: str):
    search = metadata.Search(query=query, temp=TEMP)

    print(search.options)
    while True:
        input_ = input(
            "q to quit, ok to download, .. for previous options, . for current options, int for this element: ").lower()
        input_.strip()
        if input_ == "q":
            exit(0)
        if input_ == "ok":
            return search
        if input_ == ".":
            print(search.options)
            continue
        if input_ == "..":
            print(search.get_previous_options())
            continue
        if input_.isdigit():
            print(search.choose(int(input_)))
            continue


def cli(start_at: int = 0):
    session = requests.Session()
    if TOR:
        session.proxies = {
            'http': 'socks5h://127.0.0.1:9150',
            'https': 'socks5h://127.0.0.1:9150'
        }

    if start_at <= 2:
        genre = input("genre to download to: ")

    if start_at <= 0:
        search = search_for_metadata(query=input("initial query: "))
        logging.info("Starting Downloading of metadata")
        search.download(file=STEP_ONE_CACHE)

    if start_at <= 1:
        logging.info("Fetching Download Links")
        download_links.Download(file=STEP_TWO_CACHE, metadata_csv=STEP_ONE_CACHE, temp=TEMP, session=session)

    if start_at <= 2:
        logging.info("creating Paths")
        url_to_path.UrlPath(genre=genre)

    if start_at <= 3:
        logging.info("starting to download the mp3's")
        download.Download(session=session, file=STEP_THREE_CACHE, temp=TEMP, base_path=MUSIC_DIR)


if __name__ == "__main__":
    cli(start_at=0)
