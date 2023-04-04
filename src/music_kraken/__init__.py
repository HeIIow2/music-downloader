import gc
import musicbrainzngs
import logging
import re
import os

from . import objects, pages
from .utils.shared import MUSIC_DIR, NOT_A_GENRE, MODIFY_GC, get_random_message

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


def cli():
    def get_genre():
        def get_existing_genre():
            valid_directories = []
            for elem in os.listdir(MUSIC_DIR):
                if elem not in NOT_A_GENRE:
                    valid_directories.append(elem)

            return valid_directories

        existing_genres = get_existing_genre()
        print("Available genres:")
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

    def next_search(_search: pages.Search, query: str, genre: str) -> bool:
        """
        :param _search:
        :param query:
        :return exit in the next step:
        """
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
            r = _search.download_chosen(genre=genre)

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

    genre = get_genre()
    print(f"Selected: {genre}\n")

    search = pages.Search()

    while True:
        if next_search(search, input(">> "), genre):
            break
        print(search)

    print()
    print(get_random_message())
