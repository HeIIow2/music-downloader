import musicbrainzngs
import logging
import os

from music_kraken.utils.shared import (
    MUSIC_DIR,
    NOT_A_GENRE
)
from src.music_kraken.not_used_anymore.metadata import metadata_search, metadata_fetch
from music_kraken.target import set_target
from music_kraken.not_used_anymore import (
    fetch_source,
    fetch_audio
)
from music_kraken.lyrics import lyrics


def clear_console():
    os.system('cls' if os.name in ('nt', 'dos') else 'clear')

logging.getLogger("musicbrainzngs").setLevel(logging.WARNING)
musicbrainzngs.set_useragent("metadata receiver", "0.1", "https://github.com/HeIIow2/music-downloader")


def get_existing_genre():
    valid_directories = []
    for elem in os.listdir(MUSIC_DIR):
        if elem not in NOT_A_GENRE:
            valid_directories.append(elem)

    return valid_directories

def help_search_metadata():
    msg = """
- - - Type the command you want to execute - - -
.. - Previous Options
(query_string) - Search for songs, albums, bands...
(int) - Select an item from the search results
d - Start the download
h - Help
q - Quit / Exit
"""
    print(msg)


def search_for_metadata():
    clear_console()

    search = metadata_search.Search()

    while True:
        input_ = input("\"help\" for an overfiew of commands: ")

        match (input_.strip().lower()):
            case "d" | "ok" | "dl" | "download":
                break
            case "q" | "quit" | "exit":
                clear_console()
                exit()
            case "h" | "help":
                help_search_metadata()
                continue
            case inp if inp.isdigit():
                print()
                print(search.choose(int(input_)))
                continue
            case ".." :
                print()
                print(search.get_previous_options())
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


def cli(start_at: int = 0, only_lyrics: bool = False, clear_console: bool = True):
    if clear_console:
        clear_console()

    if start_at <= 2 and not only_lyrics:
        genre = get_genre()
        logging.info(f"{genre} has been set as genre.")

    if start_at <= 0:
        search = search_for_metadata()
        # search = metadata.search.Option("release", "f8d4b24d-2c46-4e9c-8078-0c0f337c84dd", "Beautyfall")
        logging.info("Starting Downloading of metadata")
        metadata_downloader = metadata_fetch.MetadataDownloader()
        metadata_downloader.download({'type': search.type, 'id': search.id})

    if start_at <= 1 and not only_lyrics:
        logging.info("creating Paths")
        set_target.UrlPath(genre=genre)

    if start_at <= 2 and not only_lyrics:
        logging.info("Fetching Download Links")
        fetch_source.Download()

    if start_at <= 3 and not only_lyrics:
        logging.info("starting to download the mp3's")
        fetch_audio.Download()

    if start_at <= 4:
        logging.info("starting to fetch the lyrics")
        lyrics.fetch_lyrics()



if __name__ == "__main__":
    cli()
