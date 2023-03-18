from collections import defaultdict
from enum import Enum
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse

from .metadata import Mapping, Metadata
from .parents import DatabaseObject
from .collection import Collection


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
    BANDCAMP = "bandcamp"
    DEEZER = "deezer"
    SPOTIFY = "spotify"

    # This has nothing to do with audio, but bands can be here
    WIKIPEDIA = "wikipedia"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"     # I will use nitter though lol
    MYSPACE = "myspace"     # Yes somehow this ancient site is linked EVERYWHERE

    @classmethod
    def get_homepage(cls, attribute) -> str:
        homepage_map = {
            cls.YOUTUBE: "https://www.youtube.com/",
            cls.MUSIFY: "https://musify.club/",
            cls.MUSICBRAINZ: "https://musicbrainz.org/",
            cls.ENCYCLOPAEDIA_METALLUM: "https://www.metal-archives.com/",
            cls.GENIUS: "https://genius.com/",
            cls.BANDCAMP: "https://bandcamp.com/",
            cls.DEEZER: "https://www.deezer.com/",
            cls.INSTAGRAM: "https://www.instagram.com/",
            cls.FACEBOOK: "https://www.facebook.com/",
            cls.SPOTIFY: "https://open.spotify.com/",
            cls.TWITTER: "https://twitter.com/",
            cls.MYSPACE: "https://myspace.com/",
            cls.WIKIPEDIA: "https://en.wikipedia.org/wiki/Main_Page"
        }
        return homepage_map[attribute]


class Source(DatabaseObject):
    """
    create somehow like that
    ```python
    # url won't be a valid one due to it being just an example
    Source(src="youtube", url="https://youtu.be/dfnsdajlhkjhsd")
    ```
    """
    COLLECTION_ATTRIBUTES = tuple()
    SIMPLE_ATTRIBUTES = {
        "type_enum": None,
        "page_enum": None,
        "url": None
    }

    def __init__(self, page_enum: SourcePages, url: str, id_: str = None, type_enum=None) -> None:
        DatabaseObject.__init__(self, id_=id_)

        self.type_enum = type_enum
        self.page_enum = page_enum

        self.url = url

    @classmethod
    def match_url(cls, url: str) -> Optional["Source"]:
        """
        this shouldn't be used, unlesse you are not certain what the source is for
        the reason is that it is more inefficient
        """
        parsed = urlparse(url)
        url = parsed.geturl()

        if url.startswith("https://www.youtube"):
            return cls(SourcePages.YOUTUBE, url)

        if url.startswith("https://www.deezer"):
            return cls(SourcePages.DEEZER, url)
        
        if url.startswith("https://open.spotify.com"):
            return cls(SourcePages.SPOTIFY, url)

        if "bandcamp" in url:
            return cls(SourcePages.BANDCAMP, url)

        if "wikipedia" in parsed.netloc:
            return cls(SourcePages.WIKIPEDIA, url)

        if url.startswith("https://www.metal-archives.com/"):
            return cls(SourcePages.ENCYCLOPAEDIA_METALLUM, url)

        # the less important once
        if url.startswith("https://www.facebook"):
            return cls(SourcePages.FACEBOOK, url)

        if url.startswith("https://www.instagram"):
            return cls(SourcePages.INSTAGRAM, url)

        if url.startswith("https://twitter"):
            return cls(SourcePages.TWITTER, url)

        if url.startswith("https://myspace.com"):
            return cls(SourcePages.MYSPACE, url)

    def get_song_metadata(self) -> Metadata:
        return Metadata({
            Mapping.FILE_WEBPAGE_URL: [self.url],
            Mapping.SOURCE_WEBPAGE_URL: [self.homepage]
        })

    def get_artist_metadata(self) -> Metadata:
        return Metadata({
            Mapping.ARTIST_WEBPAGE_URL: [self.url]
        })

    @property
    def metadata(self) -> Metadata:
        if self.type_enum == SourceTypes.SONG:
            return self.get_song_metadata()

        if self.type_enum == SourceTypes.ARTIST:
            return self.get_artist_metadata()

        return super().metadata

    @property
    def indexing_values(self) -> List[Tuple[str, object]]:
        return [
            ('id', self.id),
            ('url', self.url)
        ]

    def __str__(self):
        return self.__repr__()

    def __repr__(self) -> str:
        return f"Src({self.page_enum.value}: {self.url})"

    page_str = property(fget=lambda self: self.page_enum.value)
    type_str = property(fget=lambda self: self.type_enum.value)
    homepage = property(fget=lambda self: SourcePages.get_homepage(self.page_enum))


class SourceCollection(Collection):
    def __init__(self, source_list: List[Source]):
        self._page_to_source_list: Dict[SourcePages, List[Source]] = defaultdict(list)

        super().__init__(data=source_list, element_type=Source)

        
    def map_element(self, source: Source):
        super().map_element(source)

        self._page_to_source_list[source.page_enum].append(source)

    def get_sources_from_page(self, source_page: SourcePages) -> List[Source]:
        """
        getting the sources for a specific page like
        YouTube or musify
        """
        return self._page_to_source_list[source_page].copy()
