from ..utils import cli_function

from ...utils.path_manager import LOCATIONS
from ...utils import shared


def all_paths():
    return {
        "Temp dir": LOCATIONS.TEMP_DIRECTORY,
        "Music dir": LOCATIONS.MUSIC_DIRECTORY,
        "Log file": shared.LOG_PATH,
        "Conf dir": LOCATIONS.CONFIG_DIRECTORY,
        "Conf file": LOCATIONS.CONFIG_FILE
    }


@cli_function
def print_paths():
    for name, path in all_paths().items():
        print(f"{name}:\t{path}")