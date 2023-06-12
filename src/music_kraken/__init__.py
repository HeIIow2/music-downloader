import logging
import re
from pathlib import Path
from typing import List

import gc
import musicbrainzngs

from .cli import Shell
from . import objects, pages, download
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
          f"Log file:\t{shared.LOG_PATH}")
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
    shell = Shell(genre=genre)
    
    if command_list is not None:
        for command in command_list:
            shell.process_input(command)
        return

    if direct_download_url is not None:
        if shell.download(direct_download_url, download_all=download_all):
            exit_message()
            return
        
    shell.mainloop()
    
    exit_message()
