import logging
import re
from pathlib import Path
from typing import List

import gc
import musicbrainzngs

from . import objects, pages
from .utils import exception, shared, path_manager
from .utils.config import config, read, write, PATHS_SECTION
from .utils.shared import MUSIC_DIR, MODIFY_GC, NOT_A_GENRE_REGEX, get_random_message
from .utils.string_processing import fit_to_file_system


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


def exit_message():
    print()
    print_cute_message()
    print("See you soon! :3")


def paths():
    print(f"Temp dir:\t{shared.TEMP_DIR}\n"
          f"Music dir:\t{shared.MUSIC_DIR}\n"
          f"Log file:\t{shared.LOG_PATH}"
          f"Config file:\t{shared.CONFIG_FILE}")
    print()
    print_cute_message()
    print()


def settings(
        name: str = None,
        value: str = None,
):
    def modify_setting(_name: str, _value: str, invalid_ok: bool = True) -> bool:
        try:
            config.set_name_to_value(_name, _value)
        except exception.config.SettingException as e:
            if invalid_ok:
                print(e)
                return False
            else:
                raise e

        write()
        return True

    def print_settings():
        for i, attribute in enumerate(config):
            print(f"{i:0>2}: {attribute.name}={attribute.value}")

    def modify_setting_by_index(index: int) -> bool:
        attribute = list(config)[index]

        print()
        print(attribute)

        input__ = input(f"{attribute.name}=")
        if not modify_setting(attribute.name, input__.strip()):
            return modify_setting_by_index(index)

        return True

    if name is not None and value is not None:
        modify_setting(name, value, invalid_ok=True)

        print()
        print_cute_message()
        print()
        return

    while True:
        print_settings()

        input_ = input("Id of setting to modify: ")
        print()
        if input_.isdigit() and int(input_) < len(config):
            if modify_setting_by_index(int(input_)):
                print()
                print_cute_message()
                print()
                return
        else:
            print("Please input a valid ID.")
            print()


def cli(
        genre: str = None,
        download_all: bool = False,
        direct_download_url: str = None,
        command_list: List[str] = None
):
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

    # directly download url
    if direct_download_url is not None:
        if search.search_url(direct_download_url):
            r = search.download_chosen(genre=genre, download_all=download_all)
            print()
            print(r)
            print()
        else:
            print(f"Sorry, could not download the url: {direct_download_url}")

        exit_message()
        return

    # run one command after another from the command list
    if command_list is not None:
        for command in command_list:
            print(f">> {command}")
            if next_search(search, command):
                break
            print(search)

        exit_message()
        return

    # the actual cli
    while True:
        if next_search(search, input(">> ")):
            break
        print(search)

    exit_message()
