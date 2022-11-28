import gc

from typing import List
import musicbrainzngs
import logging
import os

from . import (
    database,
    audio_source,
    target,
    metadata
)

from .utils.shared import (
    MUSIC_DIR,
    NOT_A_GENRE
)

from .lyrics import lyrics


# try reading a static file:
print("TEST")
import pkgutil

data = pkgutil.get_data(__name__, "temp_database_structure.sql")
print(data)

"""
At the start I modify the garbage collector to run a bit fewer times.
This should increase speed:
https://mkennedy.codes/posts/python-gc-settings-change-this-and-make-your-app-go-20pc-faster/
"""
# Clean up what might be garbage so far.
gc.collect(2)

allocs, gen1, gen2 = gc.get_threshold()
allocs = 50_000  # Start the GC sequence every 50K not 700 allocations.
gen1 = gen1 * 2
gen2 = gen2 * 2
gc.set_threshold(allocs, gen1, gen2)

logging.getLogger("musicbrainzngs").setLevel(logging.WARNING)
musicbrainzngs.set_useragent("metadata receiver", "0.1", "https://github.com/HeIIow2/music-downloader")

# define the most important values and function for import in the __init__ file
Song = database.Song
MetadataSearch = metadata.MetadataSearch
MetadataDownload = metadata.MetadataDownload

cache = database.cache


def fetch_metadata(type_: str, id_: str):
    metadata_downloader = MetadataDownload()
    metadata_downloader.download({'type': type_, 'id': id_})


def fetch_metadata_from_search(search_instance: MetadataSearch):
    current_option = search_instance.current_option
    fetch_metadata(type_=current_option.type, id_=current_option.id)


def set_targets(genre: str):
    target.set_target.UrlPath(genre=genre)


def fetch_sources(songs: List[Song], skip_existing_files: bool = True):
    audio_source.fetch_sources(songs=songs, skip_existing_files=skip_existing_files)


def fetch_audios(songs: List[Song], override_existing: bool = False):
    audio_source.fetch_audios(songs=songs, override_existing=override_existing)


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


def execute_input(_input: str, search: MetadataSearch) -> bool:
    """
    :returns: True if it should break out of the loop else False
    """
    query_input = _input.strip()
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
    print(search.search_from_query(query_input))


def search_for_metadata():
    search = MetadataSearch()

    while True:
        _input = input("\"help\" for an overview of commands: ")
        if execute_input(_input=_input, search=search):
            break

    print(f"downloading: {search.current_option}")
    return search


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
        fetch_metadata_from_search(search)

    if start_at <= 1 and not only_lyrics:
        logging.info("creating Paths")
        set_targets(genre=genre)

    if start_at <= 2 and not only_lyrics:
        logging.info("Fetching Download Links")
        fetch_sources(cache.get_tracks_without_src())

    if start_at <= 3 and not only_lyrics:
        logging.info("starting to download the mp3's")
        fetch_audios(cache.get_tracks_to_download())

    if start_at <= 4:
        logging.info("starting to fetch the lyrics")
        lyrics.fetch_lyrics(cache.get_tracks_for_lyrics())


def gtk_gui():
    # please maximaly a minimal gui, the fully fleshed out gui should be made externally
    # to avoid ending up with a huge monolyth
    pass
