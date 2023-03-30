import gc

from typing import List
import musicbrainzngs
import logging
import re

from . import (
    objects,
    pages
)


from .utils.shared import (
    MUSIC_DIR,
    NOT_A_GENRE
)


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


def cli():
    def next_search(search: pages.Search, query: str):
        query: str = query.strip()
        parsed: str = query.lower()
        
        if parsed == ".":
            return
        if parsed == "..":
            search.goto_previous()
            return
        
        if parsed.isdigit():
            search.choose_index(int(parsed))
            return
        
        url = re.match(URL_REGGEX, query)
        if url is not None:
            if not search.search_url(url.string):
                print("The given url couldn't be downloaded")
            return
        
        page = search.get_page_from_query(parsed)
        if page is not None:
            search.choose_page(page)
            return
        
        # if everything else is not valid search
        search.search(query)
    
    search = pages.Search()

    while True:
        next_search(search, input(">> "))
        print(search)
        