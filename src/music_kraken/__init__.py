import musicbrainzngs
import logging
import os

from .utils.shared import (
    MUSIC_DIR,
    NOT_A_GENRE
)
from .metadata import (
    metadata_search,
    metadata_fetch
)
from .target import set_target
from .audio_source import (
    fetch_source,
    fetch_audio
)
from .lyrics import lyrics

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
- - - Available Options - - -
.. - Previous Options
(query_string) - Search for songs, albums, bands...
(int) - Select an item from the search results
d - Start the download
h - Help
q - Quit / Exit

- - - How the Query works (examples) - - -
> #a <any artist>
searches for the artist <any artist>

> #a <any artist> #r <any releas>
searches for the release (album) <any release> by the artist <any artist>

> #r <any release> Me #t <any track>
searches for the track <any track> from the release <any relaese>
"""
    print(msg)


def execute_input(_input: str, search: metadata_search.Search) -> bool:
    """
    :returns: True if it should break out of the loop else False
    """
    _input = _input.strip().lower()
    if _input in ("d", "ok", "dl", "download"):
        return True
    if _input in ("q", "quit", "exit"):
        exit()
    if _input in ("h", "help"):
        help_search_metadata()
        return False
    if _input.isdigit():
        print()
        print(search.choose(int(_input)))
        return False
    if _input == "..":
        print()
        print(search.get_previous_options())
        return False

    print()
    print(search.search_from_query(_input))


def search_for_metadata():
    search = metadata_search.Search()

    while True:
        _input = input("\"help\" for an overview of commands: ")
        if execute_input(_input=_input, search=search):
            break

    print(f"downloading: {search.current_option}")
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


def gtk_gui():
    # please maximaly a minimal gui, the fully fleshed out gui should be made externally
    # to avoid ending up with a huge monolyth
    pass
