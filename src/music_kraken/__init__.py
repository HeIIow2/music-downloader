import gc
import musicbrainzngs
import logging
import re
import os
from pathlib import Path
from typing import List

from . import objects, pages
from .utils.string_processing import fit_to_file_system
from .utils.shared import MUSIC_DIR, MODIFY_GC, NOT_A_GENRE_REGEX, get_random_message

if MODIFY_GC:
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

URL_REGEX = 'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
DOWNLOAD_COMMANDS = {
    "ok",
    "download",
    "\\d",
    "hs"
}

EXIT_COMMANDS = {
    "exit",
    "quit"
}


def print_cute_message():
    message = get_random_message()
    try:
        print(message)
    except UnicodeEncodeError:
        message = str(c for c in message if 0 < ord(c) < 127)
        print(message)


def cli(genre: str = None, download_all: bool = False):
    def get_existing_genre() -> List[str]:
        """
        gets the name of all subdirectories of shared.MUSIC_DIR,
        but filters out all directories, where the name matches with any patern
        from shared.NOT_A_GENRE_REGEX.
        """
        existing_genres: List[str] = []

        # get all subdirectories of MUSIC_DIR, not the files in the dir.
        existing_subdirectories: List[Path] = [f for f in MUSIC_DIR.iterdir() if f.is_dir()]

        for subdirectory in existing_subdirectories:
            name: str = subdirectory.name

            if not any(re.match(regex_pattern, name) for regex_pattern in NOT_A_GENRE_REGEX):
                existing_genres.append(name)

        existing_genres.sort()

        return existing_genres

    def get_genre():
        existing_genres = get_existing_genre()
        for i, genre_option in enumerate(existing_genres):
            print(f"{i + 1:0>2}: {genre_option}")

        while True:
            genre = input("Id or new genre: ")

            if genre.isdigit():
                genre_id = int(genre) - 1
                if genre_id >= len(existing_genres):
                    print(f"No genre under the id {genre_id + 1}.")
                    continue

                return existing_genres[genre_id]

            new_genre = fit_to_file_system(genre)

            agree_inputs = {"y", "yes", "ok"}
            verification = input(f"create new genre \"{new_genre}\"? (Y/N): ").lower()
            if verification in agree_inputs:
                return new_genre

    def next_search(_search: pages.Search, query: str) -> bool:
        """
        :param _search:
        :param query:
        :return exit in the next step:
        """
        nonlocal genre
        nonlocal download_all

        query: str = query.strip()
        parsed: str = query.lower()

        if parsed in EXIT_COMMANDS:
            return True

        if parsed == ".":
            return False
        if parsed == "..":
            _search.goto_previous()
            return False

        if parsed.isdigit():
            _search.choose_index(int(parsed))
            return False

        if parsed in DOWNLOAD_COMMANDS:
            r = _search.download_chosen(genre=genre, download_all=download_all)

            print()
            print(r)
            print()

            return not r.is_mild_failure

        url = re.match(URL_REGEX, query)
        if url is not None:
            if not _search.search_url(url.string):
                print("The given url couldn't be found.")
            return False

        page = _search.get_page_from_query(parsed)
        if page is not None:
            _search.choose_page(page)
            return False

        # if everything else is not valid search
        _search.search(query)
        return False

    if genre is None:
        genre = get_genre()
        print()

    print_cute_message()
    print()
    print(f"Downloading to: \"{genre}\"")
    print()

    search = pages.Search()

    while True:
        if next_search(search, input(">> ")):
            break
        print(search)

    print()
    print_cute_message()
    print("Have fun with your music. :3")
