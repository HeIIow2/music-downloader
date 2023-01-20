from enum import Enum

from .metadata import Mapping
from .parents import (
    DatabaseObject,
    SongAttribute,
    ID3Metadata
)


class SourceTypes(Enum):
    SONG = "song"
    ALBUM = "album"
    ARTIST = "artist"
    LYRICS = "lyrics"


class SourcePages(Enum):
    YOUTUBE = "youtube"
    MUSIFY = "musify"
    GENIUS = "genius"
    MUSICBRAINZ = "musicbrainz"
    ENCYCLOPAEDIA_METALLUM = "encyclopaedia metallum"

    @classmethod
    def get_homepage(cls, attribute) -> str:
        homepage_map = {
            cls.YOUTUBE: "https://www.youtube.com/",
            cls.MUSIFY: "https://musify.club/",
            cls.MUSICBRAINZ: "https://musicbrainz.org/",
            cls.ENCYCLOPAEDIA_METALLUM: "https://www.metal-archives.com/",
            cls.GENIUS: "https://genius.com/"
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

    def __init__(self, page_enum, url: str, id_: str = None, type_enum=None) -> None:
        DatabaseObject.__init__(self, id_=id_)
        SongAttribute.__init__(self)

        self.type_enum = type_enum
        self.page_enum = page_enum

        self.url = url

    def get_id3_dict(self) -> dict:
        if self.type_enum == SourceTypes.SONG:
            return {
                Mapping.FILE_WEBPAGE_URL: [self.url],
                Mapping.SOURCE_WEBPAGE_URL: [self.homepage]
            }

        if self.type_enum == SourceTypes.ARTIST:
            return {
                Mapping.ARTIST_WEBPAGE_URL: [self.url]
            }

        return {}

    def __str__(self):
        return f"{self.page_enum}: {self.url}"

    page_str = property(fget=lambda self: self.page_enum.value)
    type_str = property(fget=lambda self: self.type_enum.value)
    homepage = property(fget=lambda self: SourcePages.get_homepage(self.page_enum))
