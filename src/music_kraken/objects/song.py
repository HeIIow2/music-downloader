import random
from collections import defaultdict
from typing import List, Optional, Dict, Tuple

import pycountry

from ..utils.enums.album import AlbumType, AlbumStatus
from .collection import Collection
from .formatted_text import FormattedText
from .lyrics import Lyrics
from .metadata import (
    Mapping as id3Mapping,
    ID3Timestamp,
    Metadata
)
from .option import Options
from .parents import MainObject
from .source import Source, SourceCollection
from .target import Target
from ..utils.string_processing import unify
from ..utils.shared import SORT_BY_ALBUM_TYPE, SORT_BY_DATE

"""
All Objects dependent 
"""

CountryTyping = type(list(pycountry.countries)[0])
OPTION_STRING_DELIMITER = " | "


class Song(MainObject):
    """
    Class representing a song object, with attributes id, mb_id, title, album_name, isrc, length,
    tracksort, genre, source_list, target, lyrics_list, album, main_artist_list, and feature_artist_list.
    """

    COLLECTION_ATTRIBUTES = (
        "lyrics_collection", "album_collection", "main_artist_collection", "feature_artist_collection",
        "source_collection")
    SIMPLE_ATTRIBUTES = {
        "title": None,
        "unified_title": None,
        "isrc": None,
        "length": None,
        "tracksort": 0,
        "genre": None,
        "notes": FormattedText()
    }

    def __init__(
            self,
            _id: int = None,
            dynamic: bool = False,
            title: str = None,
            unified_title: str = None,
            isrc: str = None,
            length: int = None,
            tracksort: int = None,
            genre: str = None,
            source_list: List[Source] = None,
            target_list: List[Target] = None,
            lyrics_list: List[Lyrics] = None,
            album_list: List['Album'] = None,
            main_artist_list: List['Artist'] = None,
            feature_artist_list: List['Artist'] = None,
            notes: FormattedText = None,
            **kwargs
    ) -> None:
        MainObject.__init__(self, _id=_id, dynamic=dynamic, **kwargs)
        # attributes
        self.title: str = title
        self.unified_title: str = unified_title
        if unified_title is None and title is not None:
            self.unified_title = unify(title)

        self.isrc: str = isrc
        self.length: int = length
        self.tracksort: int = tracksort or 0
        self.genre: str = genre
        self.notes: FormattedText = notes or FormattedText()

        self.source_collection: SourceCollection = SourceCollection(source_list)
        self.target_collection: Collection = Collection(data=target_list, element_type=Target)
        self.lyrics_collection: Collection = Collection(data=lyrics_list, element_type=Lyrics)
        self.album_collection: Collection = Collection(data=album_list, element_type=Album)
        self.main_artist_collection = Collection(data=main_artist_list, element_type=Artist)
        self.feature_artist_collection = Collection(data=feature_artist_list, element_type=Artist)

    def _build_recursive_structures(self, build_version: int, merge: bool):
        if build_version == self.build_version:
            return
        self.build_version = build_version

        album: Album
        for album in self.album_collection:
            album.song_collection.append(self, merge_on_conflict=merge, merge_into_existing=False)
            album._build_recursive_structures(build_version=build_version, merge=merge)

        artist: Artist
        for artist in self.feature_artist_collection:
            artist.feature_song_collection.append(self, merge_on_conflict=merge, merge_into_existing=False)
            artist._build_recursive_structures(build_version=build_version, merge=merge)

        for artist in self.main_artist_collection:
            for album in self.album_collection:
                artist.main_album_collection.append(album, merge_on_conflict=merge, merge_into_existing=False)
                artist._build_recursive_structures(build_version=build_version, merge=merge)

    @property
    def indexing_values(self) -> List[Tuple[str, object]]:
        return [
            ('id', self.id),
            ('title', self.unified_title),
            ('isrc', self.isrc),
            *[('url', source.url) for source in self.source_collection]
        ]

    @property
    def metadata(self) -> Metadata:
        metadata = Metadata({
            id3Mapping.TITLE: [self.title],
            id3Mapping.ISRC: [self.isrc],
            id3Mapping.LENGTH: [self.length],
            id3Mapping.GENRE: [self.genre],
            id3Mapping.TRACKNUMBER: [self.tracksort_str]
        })

        # metadata.merge_many([s.get_song_metadata() for s in self.source_collection])  album sources have no relevant metadata for id3
        metadata.merge_many([a.metadata for a in self.album_collection])
        metadata.merge_many([a.metadata for a in self.main_artist_collection])
        metadata.merge_many([a.metadata for a in self.feature_artist_collection])
        metadata.merge_many([lyrics.metadata for lyrics in self.lyrics_collection])

        return metadata

    def get_artist_credits(self) -> str:
        main_artists = ", ".join([artist.name for artist in self.main_artist_collection])
        feature_artists = ", ".join([artist.name for artist in self.feature_artist_collection])

        if len(feature_artists) == 0:
            return main_artists
        return f"{main_artists} feat. {feature_artists}"

    def __str__(self) -> str:
        artist_credit_str = ""
        artist_credits = self.get_artist_credits()
        if artist_credits != "":
            artist_credit_str = f" by {artist_credits}"

        return f"\"{self.title}\"{artist_credit_str}"

    def __repr__(self) -> str:
        return f"Song(\"{self.title}\")"

    @property
    def option_string(self) -> str:
        return f"{self.__repr__()} " \
               f"from Album({OPTION_STRING_DELIMITER.join(album.title for album in self.album_collection)}) " \
               f"by Artist({OPTION_STRING_DELIMITER.join(artist.name for artist in self.main_artist_collection)}) " \
               f"feat. Artist({OPTION_STRING_DELIMITER.join(artist.name for artist in self.feature_artist_collection)})"

    @property
    def options(self) -> Options:
        """
        Return a list of related objects including the song object, album object, main artist objects, and
        feature artist objects.

        :return: a list of objects that are related to the Song object
        """
        options = self.main_artist_collection.shallow_list
        options.extend(self.feature_artist_collection)
        options.extend(self.album_collection)
        options.append(self)
        return Options(options)

    @property
    def tracksort_str(self) -> str:
        """
        if the album tracklist is empty, it sets it length to 1, this song has to be on the Album
        :returns id3_tracksort: {song_position}/{album.length_of_tracklist} 
        """
        if len(self.album_collection) == 0:
            return f"{self.tracksort}"

        return f"{self.tracksort}/{len(self.album_collection[0].song_collection) or 1}"


"""
All objects dependent on Album
"""


class Album(MainObject):
    COLLECTION_ATTRIBUTES = ("label_collection", "artist_collection", "song_collection")
    SIMPLE_ATTRIBUTES = {
        "title": None,
        "unified_title": None,
        "album_status": None,
        "album_type": AlbumType.OTHER,
        "language": None,
        "date": ID3Timestamp(),
        "barcode": None,
        "albumsort": None,
        "notes": FormattedText()
    }

    def __init__(
            self,
            _id: int = None,
            title: str = None,
            unified_title: str = None,
            language: pycountry.Languages = None,
            date: ID3Timestamp = None,
            barcode: str = None,
            albumsort: int = None,
            dynamic: bool = False,
            source_list: List[Source] = None,
            artist_list: List['Artist'] = None,
            song_list: List[Song] = None,
            album_status: AlbumStatus = None,
            album_type: AlbumType = None,
            label_list: List['Label'] = None,
            notes: FormattedText = None,
            **kwargs
    ) -> None:
        MainObject.__init__(self, _id=_id, dynamic=dynamic, **kwargs)

        self.title: str = title
        self.unified_title: str = unified_title
        if unified_title is None and title is not None:
            self.unified_title = unify(title)

        self.album_status: AlbumStatus = album_status
        self.album_type: AlbumType = album_type or AlbumType.OTHER
        self.language: pycountry.Languages = language
        self.date: ID3Timestamp = date or ID3Timestamp()

        """
        TODO
        find out the id3 tag for barcode and implement it
        maybe look at how mutagen does it with easy_id3
        """
        self.barcode: str = barcode
        """
        TODO
        implement a function in the Artist class,
        to set albumsort with help of the release year
        """
        self.albumsort: Optional[int] = albumsort
        self.notes = notes or FormattedText()

        self.source_collection: SourceCollection = SourceCollection(source_list)
        self.song_collection: Collection = Collection(data=song_list, element_type=Song)
        self.artist_collection: Collection = Collection(data=artist_list, element_type=Artist)
        self.label_collection: Collection = Collection(data=label_list, element_type=Label)

    def _build_recursive_structures(self, build_version: int, merge: bool):
        if build_version == self.build_version:
            return
        self.build_version = build_version

        song: Song
        for song in self.song_collection:
            song.album_collection.append(self, merge_on_conflict=merge, merge_into_existing=False)
            song._build_recursive_structures(build_version=build_version, merge=merge)

        artist: Artist
        for artist in self.artist_collection:
            artist.main_album_collection.append(self, merge_on_conflict=merge, merge_into_existing=False)
            artist._build_recursive_structures(build_version=build_version, merge=merge)

        label: Label
        for label in self.label_collection:
            label.album_collection.append(self, merge_on_conflict=merge, merge_into_existing=False)
            label._build_recursive_structures(build_version=build_version, merge=merge)

    @property
    def indexing_values(self) -> List[Tuple[str, object]]:
        return [
            ('id', self.id),
            ('title', self.unified_title),
            ('barcode', self.barcode),
            *[('url', source.url) for source in self.source_collection]
        ]

    @property
    def metadata(self) -> Metadata:
        return Metadata({
            id3Mapping.ALBUM: [self.title],
            id3Mapping.COPYRIGHT: [self.copyright],
            id3Mapping.LANGUAGE: [self.iso_639_2_lang],
            id3Mapping.ALBUM_ARTIST: [a.name for a in self.artist_collection],
            id3Mapping.DATE: [self.date.timestamp],
            id3Mapping.ALBUMSORTORDER: [str(self.albumsort)] if self.albumsort is not None else []
        })

    def __repr__(self):
        return f"Album(\"{self.title}\")"

    @property
    def option_string(self) -> str:
        return f"{self.__repr__()} " \
               f"by Artist({OPTION_STRING_DELIMITER.join([artist.name for artist in self.artist_collection])}) " \
               f"under Label({OPTION_STRING_DELIMITER.join([label.name for label in self.label_collection])})"

    @property
    def options(self) -> Options:
        options = self.artist_collection.shallow_list
        options.append(self)
        options.extend(self.song_collection)

        return Options(options)

    def update_tracksort(self):
        """
        This updates the tracksort attributes, of the songs in
        `self.song_collection`, and sorts the songs, if possible.

        It is advised to only call this function, once all the tracks are
        added to the songs.

        :return:
        """

        if self.song_collection.empty:
            return

        tracksort_map: Dict[int, Song] = {
            song.tracksort: song for song in self.song_collection if song.tracksort is not None
        }

        # place the songs, with set tracksort attribute according to it
        for tracksort, song in tracksort_map.items():
            index = tracksort - 1

            """
            I ONLY modify the `Collection._data` attribute directly, 
            to bypass the mapping of the attributes, because I will add the item in the next step
            """

            """
            but for some reason, neither 
            `self.song_collection._data.index(song)`
            `self.song_collection._data.remove(song)`
            get the right object.
            
            I have NO FUCKING CLUE why xD
            But I just implemented it myself.
            """
            for old_index, temp_song in enumerate(self.song_collection._data):
                if song is temp_song:
                    break

            # the list can't be empty
            del self.song_collection._data[old_index]
            self.song_collection._data.insert(index, song)

        # fill in the empty tracksort attributes
        for i, song in enumerate(self.song_collection):
            if song.tracksort is not None:
                continue
            song.tracksort = i + 1

    def compile(self, merge_into: bool = False):
        """
        compiles the recursive structures,
        and does depending on the object some other stuff.

        no need to override if only the recursive structure should be built.
        override self.build_recursive_structures() instead
        """

        self.update_tracksort()
        self._build_recursive_structures(build_version=random.randint(0, 99999), merge=merge_into)

    @property
    def copyright(self) -> str:
        if self.date is None:
            return ""
        if self.date.has_year or len(self.label_collection) == 0:
            return ""

        return f"{self.date.year} {self.label_collection[0].name}"

    @property
    def iso_639_2_lang(self) -> Optional[str]:
        if self.language is None:
            return None

        return self.language.alpha_3

    @property
    def is_split(self) -> bool:
        """
        A split Album is an Album from more than one Artists
        usually half the songs are made by one Artist, the other half by the other one.
        In this case split means either that or one artist featured by all songs.
        :return:
        """
        return len(self.artist_collection) > 1


"""
All objects dependent on Artist
"""


class Artist(MainObject):
    COLLECTION_ATTRIBUTES = (
        "feature_song_collection",
        "main_album_collection",
        "label_collection",
        "source_collection"
    )
    SIMPLE_ATTRIBUTES = {
        "name": None,
        "unified_name": None,
        "country": None,
        "formed_in": ID3Timestamp(),
        "notes": FormattedText(),
        "lyrical_themes": [],
        "general_genre": ""
    }

    def __init__(
            self,
            _id: int = None,
            dynamic: bool = False,
            name: str = None,
            unified_name: str = None,
            source_list: List[Source] = None,
            feature_song_list: List[Song] = None,
            main_album_list: List[Album] = None,
            notes: FormattedText = None,
            lyrical_themes: List[str] = None,
            general_genre: str = "",
            country: CountryTyping = None,
            formed_in: ID3Timestamp = None,
            label_list: List['Label'] = None,
            **kwargs
    ):
        MainObject.__init__(self, _id=_id, dynamic=dynamic, **kwargs)

        self.name: str = name
        self.unified_name: str = unified_name
        if unified_name is None and name is not None:
            self.unified_name = unify(name)

        """
        TODO implement album type and notes
        """
        self.country: CountryTyping = country
        self.formed_in: ID3Timestamp = formed_in
        """
        notes, general genre, lyrics themes are attributes
        which are meant to only use in outputs to describe the object
        i mean do as you want but there is no strict rule about em so good luck
        """
        self.notes: FormattedText = notes or FormattedText()
        """
        TODO
        implement in db
        """
        self.lyrical_themes: List[str] = lyrical_themes or []
        self.general_genre = general_genre

        self.source_collection: SourceCollection = SourceCollection(source_list)
        self.feature_song_collection: Collection = Collection(data=feature_song_list, element_type=Song)
        self.main_album_collection: Collection = Collection(data=main_album_list, element_type=Album)
        self.label_collection: Collection = Collection(data=label_list, element_type=Label)

    def compile(self, merge_into: bool = False):
        """
        compiles the recursive structures,
        and does depending on the object some other stuff.

        no need to override if only the recursive structure should be built.
        override self.build_recursive_structures() instead
        """

        self.update_albumsort()
        self._build_recursive_structures(build_version=random.randint(0, 99999), merge=merge_into)

    def update_albumsort(self):
        """
        This updates the albumsort attributes, of the albums in
        `self.main_album_collection`, and sorts the albums, if possible.

        It is advised to only call this function, once all the albums are
        added to the artist.

        :return:
        """
        if len(self.main_album_collection) <= 0:
            return

        type_section: Dict[AlbumType] = defaultdict(lambda: 2, {
            AlbumType.OTHER: 0,  # if I don't know it, I add it to the first section
            AlbumType.STUDIO_ALBUM: 0,
            AlbumType.EP: 0,
            AlbumType.SINGLE: 1
        }) if SORT_BY_ALBUM_TYPE else defaultdict(lambda: 0)

        sections = defaultdict(list)

        # order albums in the previously defined section
        album: Album
        for album in self.main_album_collection:
            sections[type_section[album.album_type]].append(album)

        def sort_section(_section: List[Album], last_albumsort: int) -> int:
            # album is just a value used in loops
            nonlocal album

            if SORT_BY_DATE:
                _section.sort(key=lambda _album: _album.date, reverse=True)

            new_last_albumsort = last_albumsort

            for album_index, album in enumerate(_section):
                if album.albumsort is None:
                    album.albumsort = new_last_albumsort = album_index + 1 + last_albumsort

            _section.sort(key=lambda _album: _album.albumsort)

            return new_last_albumsort

        # sort the sections individually
        _last_albumsort = 1
        for section_index in sorted(sections):
            _last_albumsort = sort_section(sections[section_index], _last_albumsort)

        # merge all sections again
        album_list = []
        for section_index in sorted(sections):
            album_list.extend(sections[section_index])

        # replace the old collection with the new one
        self.main_album_collection: Collection = Collection(data=album_list, element_type=Album)


    def _build_recursive_structures(self, build_version: int, merge: False):
        if build_version == self.build_version:
            return
        self.build_version = build_version

        song: Song
        for song in self.feature_song_collection:
            song.feature_artist_collection.append(self, merge_on_conflict=merge, merge_into_existing=False)
            song._build_recursive_structures(build_version=build_version, merge=merge)

        album: Album
        for album in self.main_album_collection:
            album.artist_collection.append(self, merge_on_conflict=merge, merge_into_existing=False)
            album._build_recursive_structures(build_version=build_version, merge=merge)

        label: Label
        for label in self.label_collection:
            label.current_artist_collection.append(self, merge_on_conflict=merge, merge_into_existing=False)
            label._build_recursive_structures(build_version=build_version, merge=merge)

    @property
    def indexing_values(self) -> List[Tuple[str, object]]:
        return [
            ('id', self.id),
            ('name', self.unified_name),
            *[('url', source.url) for source in self.source_collection]
        ]

    @property
    def metadata(self) -> Metadata:
        metadata = Metadata({
            id3Mapping.ARTIST: [self.name]
        })
        metadata.merge_many([s.get_artist_metadata() for s in self.source_collection])

        return metadata

    def __str__(self):
        string = self.name or ""
        plaintext_notes = self.notes.get_plaintext()
        if plaintext_notes is not None:
            string += "\n" + plaintext_notes
        return string

    def __repr__(self):
        return f"Artist(\"{self.name}\")"

    @property
    def option_string(self) -> str:
        return f"{self.__repr__()} " \
               f"under Label({OPTION_STRING_DELIMITER.join([label.name for label in self.label_collection])})"

    @property
    def options(self) -> Options:
        options = [self]
        options.extend(self.main_album_collection)
        options.extend(self.feature_song_collection)
        return Options(options)

    @property
    def country_string(self):
        return self.country.alpha_3

    @property
    def feature_album(self) -> Album:
        return Album(
            title="features",
            album_status=AlbumStatus.UNRELEASED,
            album_type=AlbumType.COMPILATION_ALBUM,
            is_split=True,
            albumsort=666,
            dynamic=True,
            song_list=self.feature_song_collection.shallow_list
        )

    def get_all_songs(self) -> List[Song]:
        """
        returns a list of all Songs.
        probably not that useful, because it is unsorted
        """
        collection = self.feature_song_collection.copy()
        for album in self.discography:
            collection.extend(album.song_collection)

        return collection

    @property
    def discography(self) -> List[Album]:
        flat_copy_discography = self.main_album_collection.copy()
        flat_copy_discography.append(self.feature_album)

        return flat_copy_discography


"""
Label
"""


class Label(MainObject):
    COLLECTION_ATTRIBUTES = ("album_collection", "current_artist_collection")
    SIMPLE_ATTRIBUTES = {
        "name": None,
        "unified_name": None,
        "notes": FormattedText()
    }

    def __init__(
            self,
            _id: int = None,
            dynamic: bool = False,
            name: str = None,
            unified_name: str = None,
            notes: FormattedText = None,
            album_list: List[Album] = None,
            current_artist_list: List[Artist] = None,
            source_list: List[Source] = None,
            **kwargs
    ):
        MainObject.__init__(self, _id=_id, dynamic=dynamic, **kwargs)

        self.name: str = name
        self.unified_name: str = unified_name
        if unified_name is None and name is not None:
            self.unified_name = unify(name)
        self.notes = notes or FormattedText()

        self.source_collection: SourceCollection = SourceCollection(source_list)
        self.album_collection: Collection = Collection(data=album_list, element_type=Album)
        self.current_artist_collection: Collection = Collection(data=current_artist_list, element_type=Artist)

    def _build_recursive_structures(self, build_version: int, merge: False):
        if build_version == self.build_version:
            return
        self.build_version = build_version

        album: Album
        for album in self.album_collection:
            album.label_collection.append(self, merge_on_conflict=merge, merge_into_existing=False)
            album._build_recursive_structures(build_version=build_version, merge=merge)

        artist: Artist
        for artist in self.current_artist_collection:
            artist.label_collection.append(self, merge_on_conflict=merge, merge_into_existing=False)
            artist._build_recursive_structures(build_version=build_version, merge=merge)

    @property
    def indexing_values(self) -> List[Tuple[str, object]]:
        return [
            ('id', self.id),
            ('name', self.unified_name),
            *[('url', source.url) for source in self.source_collection]
        ]

    @property
    def options(self) -> Options:
        options = [self]
        options.extend(self.current_artist_collection.shallow_list)
        options.extend(self.album_collection.shallow_list)
