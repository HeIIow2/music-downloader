from .utils.shared import *

from .metadata.download import MetadataDownloader
from .metadata import download
from .metadata import search as s
from . import download_links
from . import url_to_path
from . import download_

# NEEDS REFACTORING
from .lyrics.lyrics import fetch_lyrics

import logging
import os

# configure logger default
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(temp_dir, LOG_FILE)),
        logging.StreamHandler()
    ]
)


def get_existing_genre():
    valid_directories = []
    for elem in os.listdir(MUSIC_DIR):
        if elem not in NOT_A_GENRE:
            valid_directories.append(elem)

    return valid_directories


def search_for_metadata():
    search = s.Search()

    while True:
        input_ = input(
            "q to quit, .. for previous options, int for this element, str to search for query, ok to download\n")
        input_.strip()
        if input_.lower() == "ok":
            break
        if input_.lower() == "q":
            break
        if input_.lower() == "..":
            print()
            print(search.get_previous_options())
            continue
        if input_.isdigit():
            print()
            print(search.choose(int(input_)))
            continue
        print()
        print(search.search_from_query(input_))

    print(search.current_option)
    return search.current_option


def get_genre():
    existing_genres = get_existing_genre()
    print("printing available genres:")
    for i, genre_option in enumerate(existing_genres):
        print(f"{i}: {genre_option}")

    genre = input("Input the ID for an existing genre or text for a new one: ")

    if genre.isdigit():
        genre_id = int(genre)
        if genre_id >= len(existing_genres):
            logging.warning("An invalid genre id has been given")
            return get_genre()
        return existing_genres[genre_id]

    return genre


def cli(start_at: int = 0, only_lyrics: bool = False):
    if start_at <= 2 and not only_lyrics:
        genre = get_genre()
        logging.info(f"{genre} has been set as genre.")

    if start_at <= 0:
        search = search_for_metadata()
        # search = metadata.search.Option("release", "f8d4b24d-2c46-4e9c-8078-0c0f337c84dd", "Beautyfall")
        logging.info("Starting Downloading of metadata")
        metadata_downloader = MetadataDownloader()
        metadata_downloader.download({'type': search.type, 'id': search.id})

    if start_at <= 1 and not only_lyrics:
        logging.info("creating Paths")
        url_to_path.UrlPath(genre=genre)

    if start_at <= 2 and not only_lyrics:
        logging.info("Fetching Download Links")
        download_links.Download()

    if start_at <= 3 and not only_lyrics:
        logging.info("starting to download the mp3's")
        d.Download()

    if start_at <= 4:
        logging.info("starting to fetch the lyrics")
        fetch_lyrics()