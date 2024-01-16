import logging
import gc
import sys

from .utils.shared import DEBUG, DEBUG_LOGGING
from .utils.config import logging_settings, main_settings, read_config
read_config()
from . import cli


if DEBUG:
    import sys
    sys.setrecursionlimit(100)


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = logging_settings['logging_format']

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


stream_handler = logging.StreamHandler()
stream_handler.setFormatter(CustomFormatter())

# configure logger default
logging.basicConfig(
    level=logging_settings['log_level'] if not DEBUG_LOGGING else logging.DEBUG,
    format=logging_settings['logging_format'],
    handlers=[
        logging.FileHandler(main_settings['log_file']),
        stream_handler
    ]
)

if main_settings['modify_gc']:
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
