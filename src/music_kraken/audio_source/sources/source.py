from typing import Tuple

"""
The class "Source" is the superclass every class for specific audio
sources inherits from. This gives the advantage of a consistent
calling of the functions do search for a song and to download it.
"""


class Source:
    def __init__(self):
        pass

    def get_source(self, row) -> Tuple[str, str]:
        return "", ""
