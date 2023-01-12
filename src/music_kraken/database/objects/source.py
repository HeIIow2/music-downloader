from enum import Enum

from .parents import (
    DatabaseObject,
    SongAttribute
)

class sources(Enum):
    YOUTUBE = "youtube"
    MUSIFY  = "musify"

    @classmethod
    def get_homepage(cls, attribute) -> str:
        homepage_map = {
            cls.YOUTUBE:    "https://www.youtube.com/",
            cls.MUSIFY:     "https://musify.club/"
        }
        return homepage_map[attribute]



class Source(DatabaseObject, SongAttribute):
    """
    create somehow like that
    ```python
    # url won't be a valid one due to it being just an example
    Source(src="youtube", url="https://youtu.be/dfnsdajlhkjhsd")
    ```
    """

    def __init__(self, id_: str = None, src: str = None, url: str = None) -> None:
        DatabaseObject.__init__(self, id_=id_)
        SongAttribute.__init__(self)

        self.src = sources(src)
        self.url = url

    def __str__(self):
        return f"{self.src}: {self.url}"

    homepage = property(fget=lambda self: sources.get_homepage(self.src))
