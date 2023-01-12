from enum import Enum

from .id3_mapping import Mapping
from .parents import (
    DatabaseObject,
    SongAttribute,
    ID3Metadata
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



class Source(DatabaseObject, SongAttribute, ID3Metadata):
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

    def get_id3_dict(self) -> dict:
        return {
            Mapping.FILE_WEBPAGE_URL: [self.url],
            Mapping.SOURCE_WEBPAGE_URL: [self.homepage]
        }

    def __str__(self):
        return f"{self.src}: {self.url}"

    type_str = property(fget=lambda self: self.src.value)
    homepage = property(fget=lambda self: sources.get_homepage(self.src))
