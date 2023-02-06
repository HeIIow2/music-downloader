import gc

from typing import List
import musicbrainzngs
import logging
import os

from . import (
    database,
    not_used_anymore,
    target
)


from .utils.shared import (
    MUSIC_DIR,
    NOT_A_GENRE
)

# from .lyrics import lyrics


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
Artist = database.Artist
Source = database.Source
SourceTypes = database.SourceTypes
SourcePages = database.SourcePages
Target = database.Target
Lyrics = database.Lyrics
Album = database.Album

ID3Timestamp = database.ID3Timestamp

cache = database.cache
Database = database.Database



def set_targets(genre: str):
    target.set_target.UrlPath(genre=genre)


def fetch_sources(songs: List[Song], skip_existing_files: bool = True):
    not_used_anymore.fetch_sources(songs=songs, skip_existing_files=skip_existing_files)


def fetch_audios(songs: List[Song], override_existing: bool = False):
    not_used_anymore.fetch_audios(songs=songs, override_existing=override_existing)


def clear_cache():
    cache.init_db(reset_anyways=True)

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
