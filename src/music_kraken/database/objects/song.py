import os
from typing import List, Tuple, Dict
import datetime
import pycountry

from .metadata import (
    Mapping as ID3_MAPPING,
    Metadata,
    ID3Timestamp
)
from ...utils.shared import (
    MUSIC_DIR,
    DATABASE_LOGGER as logger
)
from .parents import (
    DatabaseObject,
    Reference,
    SongAttribute,
    ID3Metadata
)
from .source import Source

"""
All Objects dependent 
"""


class Target(DatabaseObject, SongAttribute):
    """
    create somehow like that
    ```python
    # I know path is pointless, and I will change that (don't worry about backwards compatibility there)
    Target(file="~/Music/genre/artist/album/song.mp3", path="~/Music/genre/artist/album")
    ```
    """

    def __init__(self, id_: str = None, file: str = None, path: str = None) -> None:
        DatabaseObject.__init__(self, id_=id_)
        SongAttribute.__init__(self)
        self._file = file
        self._path = path

    def set_file(self, _file: str):
        self._file = _file

    def get_file(self) -> str | None:
        if self._file is None:
            return None
        return os.path.join(MUSIC_DIR, self._file)

    def set_path(self, _path: str):
        self._path = _path

    def get_path(self) -> str | None:
        if self._path is None:
            return None
        return os.path.join(MUSIC_DIR, self._path)

    def get_exists_on_disc(self) -> bool:
        """
        returns True when file can be found on disc
        returns False when file can't be found on disc or no filepath is set
        """
        if not self.is_set():
            return False

        return os.path.exists(self.file)

    def is_set(self) -> bool:
        return not (self._file is None or self._path is None)

    file = property(fget=get_file, fset=set_file)
    path = property(fget=get_path, fset=set_path)

    exists_on_disc = property(fget=get_exists_on_disc)


class Lyrics(DatabaseObject, SongAttribute):
    def __init__(self, text: str, language: str, id_: str = None) -> None:
        DatabaseObject.__init__(self, id_=id_)
        SongAttribute.__init__(self)
        self.text = text
        self.language = language


class Song(DatabaseObject, ID3Metadata):
    def __init__(
            self,
            id_: str = None,
            mb_id: str = None,
            title: str = None,
            album_name: str = None,
            isrc: str = None,
            length: int = None,
            tracksort: int = None,
            genre: str = None,
            sources: List[Source] = None,
            target: Target = None,
            lyrics: List[Lyrics] = None,
            album=None,
            main_artist_list: list = None,
            feature_artist_list: list = None
    ) -> None:
        """
        id: is not NECESARRILY the musicbrainz id, but is DISTINCT for every song
        mb_id: is the musicbrainz_id
        target: Each Song can have exactly one target which can be either full or empty
        lyrics: There can be multiple lyrics. Each Lyrics object can me added to multiple lyrics
        """
        super().__init__(id_=id_)
        # attributes
        # *private* attributes
        self.title: str = title
        self.isrc: str = isrc
        self.length: int = length
        self.mb_id: str | None = mb_id
        self.album_name: str | None = album_name
        self.tracksort: int | None = tracksort
        self.genre: str = genre
        
        self.sources: List[Source] = []
        if sources is not None:
            self.sources = sources

        self.album = album

        self.target = Target()
        if target is not None:
            self.target = target
        self.target.add_song(self)

        self.lyrics = []
        if lyrics is not None:
            self.lyrics = lyrics

        self.album = album

        self.main_artist_list = []
        if main_artist_list is not None:
            self.main_artist_list = main_artist_list

        self.feature_artist_list = []
        if feature_artist_list is not None:
            self.feature_artist_list = feature_artist_list

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.id == other.id

    def get_artist_credits(self) -> str:
        feature_str = ""
        if len(self.feature_artist_list) > 0:
            feature_str = " feat. " + ", ".join([artist.name for artist in self.feature_artist_list])
        return ", ".join([artist.name for artist in self.main_artist_list]) + feature_str

    def __str__(self) -> str:
        artist_credit_str = ""
        artist_credits = self.get_artist_credits()
        if artist_credits != "":
            artist_credit_str = f" by {artist_credits}"

        return f"\"{self.title}\"{artist_credit_str}"

    def __repr__(self) -> str:
        return self.__str__()

    def has_isrc(self) -> bool:
        return self.isrc is not None

    def get_album_id(self):
        if self.album is None:
            return None
        return self.album.id

    def get_id3_dict(self) -> dict:
        return {
            ID3_MAPPING.TITLE: [self.title],
            ID3_MAPPING.ISRC: [self.isrc],
            ID3_MAPPING.LENGTH: [str(self.length)],
            ID3_MAPPING.GENRE: [self.genre]
        }
    
    def get_metadata(self) -> Metadata:
        metadata = Metadata(self.get_id3_dict())

        metadata.add_many_metadata_dict([source.get_id3_dict() for source in self.sources])
        if self.album is not None:
            metadata.add_metadata_dict(self.album.get_id3_dict())
        metadata.add_many_metadata_dict([artist.get_id3_dict() for artist in self.main_artist_list])
        metadata.add_many_metadata_dict([artist.get_id3_dict() for artist in self.feature_artist_list])

        return metadata

    metadata = property(fget=get_metadata)


"""
All objects dependent on Album
"""


class Album(DatabaseObject, ID3Metadata):
    """
    -------DB-FIELDS-------
    title           TEXT, 
    copyright       TEXT,
    album_status    TEXT,
    language        TEXT,
    year            TEXT,
    date            TEXT,
    country         TEXT,
    barcode         TEXT,
    song_id         BIGINT,
    is_split        BOOLEAN NOT NULL DEFAULT 0
    """

    def __init__(
            self,
            id_: str = None,
            title: str = None,
            label: str = None,
            album_status: str = None,
            language: pycountry.Languages = None,
            date: ID3Timestamp = None,
            country: str = None,
            barcode: str = None,
            is_split: bool = False,
            albumsort: int = None,
            dynamic: bool = False
    ) -> None:
        DatabaseObject.__init__(self, id_=id_, dynamic=dynamic)
        self.title: str = title
        self.album_status: str = album_status
        self.label = label
        self.language: pycountry.Languages = language
        self.date: ID3Timestamp = date
        self.country: str = country
        """
        TODO
        find out the id3 tag for barcode and implement it
        maybee look at how mutagen does it with easy_id3
        """
        self.barcode: str = barcode
        self.is_split: bool = is_split
        self.albumsort: int | None = albumsort

        self.tracklist: List[Song] = []
        self.artists: List[Artist] = []

    def __str__(self) -> str:
        return f"Album: \"{self.title}\""

    def __repr__(self):
        return self.__str__()

    def __len__(self) -> int:
        return len(self.tracklist)

    def set_tracklist(self, tracklist: List[Song]):
        self.tracklist = tracklist

        for i, track in enumerate(self.tracklist):
            track.tracksort = i + 1

    def add_song(self, song: Song):
        for existing_song in self.tracklist:
            if existing_song == song:
                return

        song.tracksort = len(self.tracklist)
        self.tracklist.append(song)

    def get_id3_dict(self) -> dict:
        return {
            ID3_MAPPING.ALBUM: [self.title],
            ID3_MAPPING.COPYRIGHT: [self.copyright],
            ID3_MAPPING.LANGUAGE: [self.iso_639_2_language],
            ID3_MAPPING.ALBUM_ARTIST: [a.name for a in self.artists],
            ID3_MAPPING.DATE: [self.date.timestamp]
        }

    def get_copyright(self) -> str:
        if self.date.year == 1 or self.label is None:
            return None

        return f"{self.date.year} {self.label}"

    def get_iso_639_2_lang(self) -> str:
        if self.language is None:
            return None

        return self.language.alpha_3

    copyright = property(fget=get_copyright)
    iso_639_2_language = property(fget=get_iso_639_2_lang)



"""
All objects dependent on Artist
"""


class Artist(DatabaseObject, ID3Metadata):
    """
    main_songs
    feature_song

    albums
    """

    def __init__(
            self,
            id_: str = None,
            name: str = None,
            main_songs: List[Song] = None,
            feature_songs: List[Song] = None,
            main_albums: List[Album] = None
    ):
        DatabaseObject.__init__(self, id_=id_)

        if main_albums is None:
            main_albums = []
        if feature_songs is None:
            feature_songs = []
        if main_songs is None:
            main_songs = []

        self.name: str | None = name

        self.main_songs = main_songs
        self.feature_songs = feature_songs

        self.main_albums = main_albums

    def __str__(self):
        return self.name or ""

    def __repr__(self):
        return self.__str__()

    def get_features(self) -> Album:
        feature_release = Album(
            title="features",
            copyright_=self.name,
            album_status="dynamic",
            is_split=True,
            albumsort=666,
            dynamic=True
        )
        for feature in self.feature_songs:
            feature_release.add_song(feature)

        return feature_release

    def get_songs(self) -> Album:
        song_release = Album(
            title="song collection",
            copyright_=self.name,
            album_status="dynamic",
            is_split=False,
            albumsort=666,
            dynamic=True
        )
        for song in self.main_songs:
            song_release.add_song(song)
        for song in self.feature_songs:
            song_release.add_song(song)
        return song_release

    def get_discography(self) -> List[Album]:
        flat_copy_discography = self.main_albums.copy()
        flat_copy_discography.append(self.get_features())

        return flat_copy_discography

    def get_id3_dict(self) -> dict:
        return {
            ID3_MAPPING.ARTIST: [self.name]
        }

    discography: List[Album] = property(fget=get_discography)
    features: Album = property(fget=get_features)
    songs: Album = property(fget=get_songs)
