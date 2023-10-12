from ..utils import cli_function

from ...utils.path_manager import LOCATIONS
from ...utils import shared
from ...utils.config import main_settings


def all_paths():
    return {
        "Temp dir": main_settings["temp_directory"],
        "Music dir": main_settings["music_directory"],
        "Log file": main_settings["log_file"],
        "Conf dir": LOCATIONS.CONFIG_DIRECTORY,
        "FFMPEG bin": main_settings["ffmpeg_binary"],
    }


@cli_function
def print_paths():
    for name, path in all_paths().items():
        print(f"{name}:\t{path}")