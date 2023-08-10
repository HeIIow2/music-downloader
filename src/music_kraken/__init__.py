import logging

import gc
import musicbrainzngs

from .utils.old_config import read_config
from .utils.shared import MODIFY_GC
from . import cli

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
