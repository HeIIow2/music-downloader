from typing import List

from .artist import Artist
from .metadata import Metadata
from .source import Source
from .target import Target


class Artist:
    def __init__(self, id_: str = None, name: str = None) -> None:
        self.id = id_
        self.name = name

    def __eq__(self, __o: object) -> bool:
        if type(__o) != type(self):
            return False
        return self.id == __o.id

    def __str__(self) -> str:
        return self.name


class Lyrics:
    def __init__(self, text: str, language: str) -> None:
        self.text = text
        self.language = language


class LyricsContainer:
    def __init__(self):
        self.lyrics_list: List[Lyrics] = []

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


class Song:
    def __init__(
        self, 
        id_: str = None,
        mb_id: str = None,
        title: str = None,
        release: str = None,
        isrc: str = None,
        length: int = None,
        artists: List[Artist] = None,
        metadata: Metadata = None,
        sources: List[Source] = None,
        target: Target = None,
        lyrics: LyricsContainer = None
        ) -> None:
        """
        id: is not NECESARRILY the musicbrainz id, but is DISTINCT for every song
        mb_id: is the musicbrainz_id
        target: Each Song can have exactly one target which can be either full or empty
        lyrics: There can be multiple lyrics. Each Lyrics object can me added to multiple lyrics
        """
        # attributes
        self.id: str | None = id_
        self.mb_id: str | None = mb_id
        self.title: str | None = title
        self.release: str | None = release
        self.isrc: str | None = isrc
        self.length: int | None = length

        if metadata is None:
            metadata = Metadata()
        self.metadata: Metadata = metadata
        
        # joins
        if artists is None:
            artists = []
        self.artists: List[Artist] = artists

        if sources is None:
            sources = []
        self.sources: List[Source] = sources
        
        if target is None:
            target = Target()
        self.target: Target = target

        if lyrics is None:
            lyrics = LyricsContainer()
        self.lyrics: LyricsContainer = lyrics


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
