import gc

from typing import List
import musicbrainzngs
import logging
import os

from . import (
    objects,
    database,
    pages
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


def get_options_from_query(query: str) -> List[objects.DatabaseObject]:
    options = []
    for MetadataPage in pages.MetadataPages:
        options.extend(MetadataPage.search_by_query(query=query))
    return options

def get_options_from_option(option: objects.DatabaseObject) -> List[objects.DatabaseObject]:
    for MetadataPage in pages.MetadataPages:
        option = MetadataPage.fetch_details(option, flat=False)
    return option.get_options()

def print_options(options: List[objects.DatabaseObject]):
    print("\n".join([f"{str(j).zfill(2)}: {i.get_option_string()}" for j, i in enumerate(options)]))

def cli():
    options = []

    while True:
        command: str = input(">> ").strip()

        if command.isdigit():
            option_index = int(command)

            if option_index >= len(options):
                print(f"option {option_index} doesn't exist")
                continue

            options = get_options_from_option(options[option_index])

        else:
            options = get_options_from_query(command)

        print_options(options)


