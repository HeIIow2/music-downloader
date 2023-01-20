from enum import Enum

from .metadata import Mapping
from .parents import (
    DatabaseObject,
    SongAttribute,
    ID3Metadata
)

class source_types(Enum):
    SONG = "song"
    ALBUM = "album"
    ARTIST = "artist"
    LYRICS = "lyrics"

class sources(Enum):
    YOUTUBE = "youtube"
    MUSIFY  = "musify"
    GENIUS = "genius"
    MUSICBRAINZ = "musicbrainz"
    ENCYCLOPAEDIA_METALLUM = "encyclopaedia metallum"

    @classmethod
    def get_homepage(cls, attribute) -> str:
        homepage_map = {
            cls.YOUTUBE:    "https://www.youtube.com/",
            cls.MUSIFY:     "https://musify.club/",
            cls.MUSICBRAINZ:"https://musicbrainz.org/",
            cls.ENCYCLOPAEDIA_METALLUM: "https://www.metal-archives.com/",
            cls.GENIUS:     "https://genius.com/"
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

    def __init__(self, type_enum, id_: str = None, src: str = None, url: str = None) -> None:
        DatabaseObject.__init__(self, id_=id_)
        SongAttribute.__init__(self)

        self.type_enum = type_enum
        self.src = sources(src)
        self.url = url

    def get_id3_dict(self) -> dict:
        if self.type_enum == source_types.SONG:
            return {
                Mapping.FILE_WEBPAGE_URL: [self.url],
                Mapping.SOURCE_WEBPAGE_URL: [self.homepage]
            }
        
        if self.type_enum == source_types.ARTIST:
            return {
                Mapping.ARTIST_WEBPAGE_URL: [self.url]
            }

        return {}

    def __str__(self):
        return f"{self.src}: {self.url}"

    site_str = property(fget=lambda self: self.src.value)
    type_str = property(fget=lambda self: self.type_enum.value)
    homepage = property(fget=lambda self: sources.get_homepage(self.src))
