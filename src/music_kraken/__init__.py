import logging

import gc
import musicbrainzngs

from .utils.shared import DEBUG
from .utils.config import logging_settings, main_settings, read_config
read_config()
from . import cli


# configure logger default
logging.basicConfig(
    level=logging_settings['log_level'] if not DEBUG else logging.DEBUG,
    format=logging_settings['logging_format'],
    handlers=[
        logging.FileHandler(main_settings['log_file']),
        logging.StreamHandler()
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
