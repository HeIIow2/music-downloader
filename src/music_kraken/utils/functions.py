import os
from datetime import datetime
import guppy
from guppy.heapy import Path


hp = guppy.hpy()

def replace_all_refs(replace_with, replace):
    """
    NO
    I have a very good reason to use this here
    DONT use this anywhere else...

    This replaces **ALL** references to replace with a reference to replace_with.

    https://benkurtovic.com/2015/01/28/python-object-replacement.html 
    """
    for path in hp.iso(replace).pathsin:
        relation = path.path[1]
        if isinstance(relation, Path.R_INDEXVAL):
            path.src.theone[relation.r] = replace_with


def clear_console():
    os.system('cls' if os.name in ('nt', 'dos') else 'clear')


def get_current_millis() -> int:
    dt = datetime.now()
    return int(dt.microsecond / 1_000)
