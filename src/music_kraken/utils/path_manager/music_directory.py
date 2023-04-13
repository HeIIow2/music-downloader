from pathlib import Path
from sys import platform
import logging
from os.path import expandvars

import configparser

DEFAULT_MUSIC_DIRECTORY = Path(Path.home(), "Music")


def get_xdg_music_directory() -> Path:
    """
    gets the xdg music directory, for all the linux or bsd folks!
    Thanks to Distant Thunder, as well as Kevin Gruber for making that pull request:
    https://github.com/HeIIow2/music-downloader/pull/6

    :return:
    """

    # XDG_USER_DIRS_FILE reference: https://freedesktop.org/wiki/Software/xdg-user-dirs/
    xdg_user_dirs_file = Path(Path.home(), ".config", "user-dirs.dirs")

    try:
        with open(xdg_user_dirs_file, 'r') as f:
            data = "[XDG_USER_DIRS]\n" + f.read()
        config = configparser.ConfigParser(allow_no_value=True)
        config.read_string(data)
        xdg_config = config['XDG_USER_DIRS']
        return Path(expandvars(xdg_config['xdg_music_dir'].strip('"')))

    except (FileNotFoundError, KeyError) as e:
        logging.warning(
            f"Missing file or No entry found for \"xdg_music_dir\" in: \"{xdg_user_dirs_file}\".\n"
            f"Will fallback on default \"$HOME/Music\"."
        )
        logging.debug(str(e))

    return DEFAULT_MUSIC_DIRECTORY


def get_music_directory() -> Path:
    if platform != "linux":
        return DEFAULT_MUSIC_DIRECTORY

    return get_xdg_music_directory()
