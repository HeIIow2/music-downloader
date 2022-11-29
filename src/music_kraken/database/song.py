from typing import List

from .artist import Artist
from .metadata import Metadata
from .source import Source
from .target import Target

# I don't import cache from the db module because it would lead to circular imports
# from .temp_database import temp_database as cache
# from . import cache



class Song:
    def __init__(self, json_response: dict) -> None:
        """
        id: is not NECESARRILY the musicbrainz id, but is DISTINCT for every song
        mb_id: is the musicbrainz_id
        target: Each Song can have exactly one target which can be either full or empty
        lyrics: There can be multiple lyrics. Each Lyrics object can me added to multiple lyrics
        """
        # attributes
        self.id: str | None = None
        self.mb_id: str | None = None
        self.title: str | None = None
        self.isrc: str | None = None
        self.length: int | None = None

        self.metadata: Metadata = Metadata()
        # joins
        self.artists: List[Artist] = []
        self.lyrics: LyricsContainer = LyricsContainer(parent=self)

        self.sources: List[Source] = []
        self.target: Target = Target()

        self.json_data = json_response

        # initialize the data
        self.id = self.json_data['id']
        self.title = self.json_data['title']
        self.artists = []
        for a in self.json_data['artists']:
            new_artist = Artist(a)
            exists = False
            for existing_artist in self.artists:
                if new_artist == existing_artist:
                    exists = True
                    break
            if not exists:
                self.artists.append(new_artist)
        self.isrc = self.json_data['isrc']

        # initialize the sources
        self.sources: List[Source] = []
        for src in self.json_data['source']:
            if src['src'] is None:
                continue
            self.sources.append(Source(src))

        # initialize the target
        self.target = Target()
        self.target.file = self.json_data['file']
        self.target.path = self.json_data['path']

        # initialize id3 metadata
        self.metadata = Metadata()
        for key, value in self.json_data.items():
            self.metadata[key] = value
        self.metadata['artist'] = self.get_artist_names()

        self.length = self.json_data['length']
        # EasyID3.valid_keys.keys()

        # the lyrics are not in the metadata class because the field isn't supported
        # by easyid3
        self.lyrics: LyricsContainer = LyricsContainer(parent=self)

    def __str__(self) -> str:
        return f"\"{self.title}\" by {', '.join([str(a) for a in self.artists])}"

    def __repr__(self) -> str:
        return self.__str__()

    def get_metadata(self):
        return self.metadata.get_all_metadata()

    def has_isrc(self) -> bool:
        return self.isrc is not None

    def get_artist_names(self) -> List[str]:
        return [a.name for a in self.artists]

    def __getitem__(self, item):
        if item not in self.json_data:
            return None
        return self.json_data[item]

    def __setitem__(self, item, value):
        if item == "file":
            self.target.file = value
            return
        if item == "path":
            self.target.path = value
            return

        self.json_data[item] = value


class Lyrics:
    def __init__(self, text: str, language: str) -> None:
        self.text = text
        self.language = language


class LyricsContainer:
    def __init__(self, parent: Song):
        self.lyrics_list: List[Lyrics] = []

        self.parent = parent

    def append(self, lyrics: Lyrics):
        # due to my db not supporting multiple Lyrics yet, I just use for doing stuff with the lyrics
        # the first element. I know this implementation is junk, but take it or leave it, it is going
        # soon anyway
        if len(self.lyrics_list) >= 1:
            return

        self.lyrics_list.append(lyrics)
        # unfortunately can't do this here directly, because of circular imports. If anyone
        # took the time to get familiar with this codebase... thank you, and if you have any
        # suggestion of resolving this, please open an issue.
        # cache.add_lyrics(track_id=self.parent.id, lyrics=lyrics.text)

    def extend(self, lyrics_list: List[Lyrics]):
        for lyrics in lyrics_list:
            self.append(lyrics)

    is_empty = property(fget=lambda self: len(self.lyrics_list) <= 0)

