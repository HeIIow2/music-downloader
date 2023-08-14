from .sections.logging import LOGGING_SECTION
from .sections.audio import AUDIO_SECTION
from .sections.connection import CONNECTION_SECTION
from .sections.misc import MISC_SECTION
from .sections.paths import PATHS_SECTION

from .sections.paths import LOCATIONS
from .config import Config


config = Config()


def read_config():
    if not LOCATIONS.CONFIG_FILE.is_file():
        write_config()
    config.read_from_config_file(LOCATIONS.CONFIG_FILE)


def write_config():
    config.write_to_config_file(LOCATIONS.CONFIG_FILE)

set_name_to_value = config.set_name_to_value

read_config()