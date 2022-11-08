<<<<<<< HEAD
import metadata
=======
from metadata.database import Database
from metadata.download import MetadataDownloader
import metadata.download
import metadata.search
>>>>>>> 63f30bffbae20ec3fc368a6093b28e56f0230318
import download_links
import url_to_path
import download

import logging
import requests
import os
import tempfile

logging.basicConfig(level=logging.INFO)

TEMP_FOLDER = "music-downloader"
DATABASE_FILE = "metadata.db"
DATABASE_STRUCTURE_FILE = "database_structure.sql"
DATABASE_STRUCTURE_FALLBACK = "https://raw.githubusercontent.com/HeIIow2/music-downloader/new_metadata/assets/database_structure.sql"

SEARCH_LOGGER = logging.getLogger("mb-cli")
DATABASE_LOGGER = logging.getLogger("database")
METADATA_DOWNLOAD_LOGGER = logging.getLogger("metadata-download")
URL_DOWNLOAD_LOGGER = logging.getLogger("ling-download")
PATH_LOGGER = logging.getLogger("create-paths")
DOWNLOAD_LOGGER = logging.getLogger("download")

NOT_A_GENRE = ".", "..", "misc_scripts", "Music", "script", ".git", ".idea"
MUSIC_DIR = os.path.expanduser('~/Music')
TOR = False

temp_dir = os.path.join(tempfile.gettempdir(), TEMP_FOLDER)
if not os.path.exists(temp_dir):
    os.mkdir(temp_dir)

database = Database(os.path.join(temp_dir, DATABASE_FILE),
                    os.path.join(temp_dir, DATABASE_STRUCTURE_FILE),
                    DATABASE_STRUCTURE_FALLBACK, 
                    DATABASE_LOGGER,
                    reset_anyways=True)


def get_existing_genre():
    valid_directories = []
    for elem in os.listdir(MUSIC_DIR):
        if elem not in NOT_A_GENRE:
            valid_directories.append(elem)

    return valid_directories



def search_for_metadata():
    search = metadata.search.Search(logger=SEARCH_LOGGER)

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


def cli(start_at: int = 0):
    session = requests.Session()
    if TOR:
        session.proxies = {
            'http': 'socks5h://127.0.0.1:9150',
            'https': 'socks5h://127.0.0.1:9150'
        }

    if start_at <= 2:
        genre = get_genre()
        logging.info(f"{genre} has been set as genre.")

    if start_at <= 0:
        search = search_for_metadata()
        logging.info("Starting Downloading of metadata")
        metadata_downloader = MetadataDownloader(database, METADATA_DOWNLOAD_LOGGER)
        metadata_downloader.download(search)

    if start_at <= 1:
        logging.info("creating Paths")
        url_to_path.UrlPath(database, PATH_LOGGER, genre=genre)

    if start_at <= 2:
        logging.info("Fetching Download Links")
        download_links.Download(database, METADATA_DOWNLOAD_LOGGER, MUSIC_DIR, proxies=proxies)

    if start_at <= 3:
        logging.info("starting to download the mp3's")
        download.Download(database, DOWNLOAD_LOGGER, proxies=proxies, base_path=MUSIC_DIR)


if __name__ == "__main__":
    cli(start_at=0)
