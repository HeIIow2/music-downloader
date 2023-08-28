from .sections.logging import LOGGING_SECTION
from .sections.audio import AUDIO_SECTION
from .sections.connection import CONNECTION_SECTION
from .sections.misc import MISC_SECTION
from .sections.paths import PATHS_SECTION

from .sections.paths import LOCATIONS
from .config import Config

from .settings import read_config, write_config, load, set_name_to_value


load()
