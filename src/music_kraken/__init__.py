import gc
import musicbrainzngs
import logging
import re

from . import objects, pages
from .utils.shared import MUSIC_DIR, NOT_A_GENRE, get_random_message


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

URL_REGGEX = 'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
DOWNLOAD_COMMANDS = {
    "ok",
    "download",
    "\d",
    "hs"
}

EXIT_COMMANDS = {
    "exit",
    "quit"
}


def cli():
    def next_search(_search: pages.Search, query: str) -> bool:
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
            r = _search.download_chosen()

            print()
            print(r)
            print()

            return not r.is_mild_failure

        url = re.match(URL_REGGEX, query)
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

    search = pages.Search()

    while True:
        if next_search(search, input(">> ")):
            break
        print(search)

    print()
    print(get_random_message())
