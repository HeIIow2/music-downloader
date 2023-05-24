import logging
import random
from copy import copy
from typing import Optional, Union, Type, Dict, Set, List
import threading

import requests
from bs4 import BeautifulSoup

from ..connection import Connection
from ..objects import (
    Song,
    Source,
    Album,
    Artist,
    Target,
    DatabaseObject,
    Options,
    Collection,
    Label,
)
from ..utils.enums.source import SourcePages
from ..utils.enums.album import AlbumType
from ..audio import write_metadata_to_target, correct_codec
from ..utils import shared
from ..utils.support_classes import Query, DownloadResult, DefaultTarget


INDEPENDENT_DB_OBJECTS = Union[Label, Album, Artist, Song]
INDEPENDENT_DB_TYPES = Union[Type[Song], Type[Album], Type[Artist], Type[Label]]


def _clean_music_object(music_object: INDEPENDENT_DB_OBJECTS, collections: Dict[INDEPENDENT_DB_TYPES, Collection]):
    if type(music_object) == Label:
        return _clean_label(label=music_object, collections=collections)
    if type(music_object) == Artist:
        return _clean_artist(artist=music_object, collections=collections)
    if type(music_object) == Album:
        return _clean_album(album=music_object, collections=collections)
    if type(music_object) == Song:
        return _clean_song(song=music_object, collections=collections)


def _clean_collection(collection: Collection, collection_dict: Dict[INDEPENDENT_DB_TYPES, Collection]):
    if collection.element_type not in collection_dict:
        return

    for i, element in enumerate(collection):
        r = collection_dict[collection.element_type].append(element, merge_into_existing=True)
        collection[i] = r.current_element

        if not r.was_the_same:
            _clean_music_object(r.current_element, collection_dict)


def _clean_label(label: Label, collections: Dict[INDEPENDENT_DB_TYPES, Collection]):
    _clean_collection(label.current_artist_collection, collections)
    _clean_collection(label.album_collection, collections)


def _clean_artist(artist: Artist, collections: Dict[INDEPENDENT_DB_TYPES, Collection]):
    _clean_collection(artist.main_album_collection, collections)
    _clean_collection(artist.feature_song_collection, collections)
    _clean_collection(artist.label_collection, collections)


def _clean_album(album: Album, collections: Dict[INDEPENDENT_DB_TYPES, Collection]):
    _clean_collection(album.label_collection, collections)
    _clean_collection(album.song_collection, collections)
    _clean_collection(album.artist_collection, collections)


def _clean_song(song: Song, collections: Dict[INDEPENDENT_DB_TYPES, Collection]):
    _clean_collection(song.album_collection, collections)
    _clean_collection(song.feature_artist_collection, collections)
    _clean_collection(song.main_artist_collection, collections)

def clean_object(dirty_object: DatabaseObject) -> DatabaseObject:
    if isinstance(dirty_object, INDEPENDENT_DB_OBJECTS):
        collections = {
            Label: Collection(element_type=Label),
            Artist: Collection(element_type=Artist),
            Album: Collection(element_type=Album),
            Song: Collection(element_type=Song)
        }

        return _clean_music_object(dirty_object, collections)
    
def build_new_object(new_object: DatabaseObject) -> DatabaseObject:
    new_object = clean_object(new_object)
    new_object.compile(merge_into=False)
    
    return new_object

def merge_together(old_object: DatabaseObject, new_object: DatabaseObject) -> DatabaseObject:
    new_object = clean_object(new_object)
    
    old_object.merge(new_object)
    old_object.compile(merge_into=False)
    
    return old_object


class Page(threading.Thread):
    """
    This is an abstract class, laying out the 
    functionality for every other class fetching something
    """

    SOURCE_TYPE: SourcePages
    LOGGER = logging.getLogger("this shouldn't be used")
    
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self) -> None:
        pass
    
    def get_source_type(self, source: Source) -> Optional[INDEPENDENT_DB_TYPES]:
        return None
      
    def get_soup_from_response(self, r: requests.Response) -> BeautifulSoup:
        return BeautifulSoup(r.content, "html.parser")

    # to search stuff
    def search(self, query: Query) -> List[DatabaseObject]:
        music_object = query.music_object
        
        search_functions = {
            Song: self.song_search,
            Album: self.album_search,
            Artist: self.artist_search,
            Label: self.label_search
        }
        
        if type(music_object) in search_functions:
            r = search_functions[type(music_object)](music_object)
            if len(r) > 0:
                return r
            
        r = []
        for default_query in query.default_search:
            r.extend(self.general_search(default_query))
        
        return r
    
    def general_search(self, search_query: str) -> List[DatabaseObject]:
        return []
    
    def label_search(self, label: Label) -> List[Label]:
        return []
    
    def artist_search(self, artist: Artist) -> List[Artist]:
        return []
    
    def album_search(self, album: Album) -> List[Album]:
        return []
    
    def song_search(self, song: Song) -> List[Song]:
        return []
    

    def fetch_details(self, music_object: DatabaseObject, stop_at_level: int = 1) -> DatabaseObject:
        """
        when a music object with lacking data is passed in, it returns
        the SAME object **(no copy)** with more detailed data.
        If you for example put in, an album, it fetches the tracklist

        :param music_object:
        :param stop_at_level: 
        This says the depth of the level the scraper will recurse to.
        If this is for example set to 2, then the levels could be:
        1. Level: the album
        2. Level: every song of the album + every artist of the album
        If no additional requests are needed to get the data one level below the supposed stop level
        this gets ignored
        :return detailed_music_object: IT MODIFIES THE INPUT OBJ
        """

        # creating a new object, of the same type
        new_music_object: DatabaseObject = type(music_object)()

        # only certain database objects, have a source list
        if isinstance(music_object, INDEPENDENT_DB_OBJECTS):
            source: Source
            for source in music_object.source_collection.get_sources_from_page(self.SOURCE_TYPE):
                new_music_object.merge(
                    self.fetch_object_from_source(source=source, enforce_type=type(music_object), stop_at_level=stop_at_level, post_process=False))

        return merge_together(music_object, new_music_object)

    def fetch_object_from_source(self, source: Source, stop_at_level: int = 2, enforce_type: Type[DatabaseObject] = None, post_process: bool = True) -> Optional[DatabaseObject]:
        obj_type = self.get_source_type(source)
        
        if obj_type is None:
            return None
        if enforce_type != obj_type and enforce_type is not None:
            self.LOGGER.warning(f"Object type isn't type to enforce: {enforce_type}, {obj_type}")
            return None
        
        music_object: DatabaseObject = None
        
        fetch_map = {
            Song: self.fetch_song,
            Album: self.fetch_album,
            Artist: self.fetch_artist,
            Label: self.fetch_label
        }
        
        if obj_type in fetch_map:
            music_object = fetch_map[obj_type](source, stop_at_level)
        else:
            self.LOGGER.warning(f"Can't fetch details of type: {obj_type}")
            return None

        if post_process and music_object:
            return build_new_object(music_object)

        return music_object
    
    def fetch_song(self, source: Source, stop_at_level: int = 1) -> Song:
        return Song()

    def fetch_album(self, source: Source, stop_at_level: int = 1) -> Album:
        return Album()

    def fetch_artist(self, source: Source, stop_at_level: int = 1) -> Artist:
        return Artist()

    def fetch_label(self, source: Source, stop_at_level: int = 1) -> Label:
        return Label()

    @classmethod
    def download(
            cls,
            music_object: Union[Song, Album, Artist, Label],
            download_features: bool = True,
            default_target: DefaultTarget = None,
            genre: str = None,
            override_existing: bool = False,
            create_target_on_demand: bool = True,
            download_all: bool = False,
            exclude_album_type: Set[AlbumType] = shared.ALBUM_TYPE_BLACKLIST
    ) -> DownloadResult:
        """

        :param genre: The downloader will download to THIS folder (set the value of default_target.genre to genre)
        :param music_object:
        :param download_features:
        :param default_target:
        :param override_existing:
        :param create_target_on_demand:
        :param download_all:
        :param exclude_album_type:
        :return total downloads, failed_downloads:
        """
        if default_target is None:
            default_target = DefaultTarget()

        if download_all:
            exclude_album_type: Set[AlbumType] = set()
        elif exclude_album_type is None:
            exclude_album_type = {
                AlbumType.COMPILATION_ALBUM,
                AlbumType.LIVE_ALBUM,
                AlbumType.MIXTAPE
            }

        if type(music_object) is Song:
            return cls.download_song(
                music_object,
                override_existing=override_existing,
                create_target_on_demand=create_target_on_demand,
                genre=genre
            )
        if type(music_object) is Album:
            return cls.download_album(
                music_object,
                default_target=default_target,
                override_existing=override_existing,
                genre=genre
            )
        if type(music_object) is Artist:
            return cls.download_artist(
                music_object,
                default_target=default_target,
                download_features=download_features,
                exclude_album_type=exclude_album_type,
                genre=genre
            )
        if type(music_object) is Label:
            return cls.download_label(
                music_object,
                download_features=download_features,
                default_target=default_target,
                exclude_album_type=exclude_album_type,
                genre=genre
            )

        return DownloadResult(error_message=f"{type(music_object)} can't be downloaded.")

    @classmethod
    def download_label(
            cls,
            label: Label,
            exclude_album_type: Set[AlbumType],
            download_features: bool = True,
            override_existing: bool = False,
            default_target: DefaultTarget = None,
            genre: str = None
    ) -> DownloadResult:

        default_target = DefaultTarget() if default_target is None else copy(default_target)
        default_target.label_object(label)

        r = DownloadResult()

        cls.fetch_details(label)
        for artist in label.current_artist_collection:
            r.merge(cls.download_artist(
                artist,
                download_features=download_features,
                override_existing=override_existing,
                default_target=default_target,
                exclude_album_type=exclude_album_type,
                genre=genre
            ))

        album: Album
        for album in label.album_collection:
            if album.album_type == AlbumType.OTHER:
                cls.fetch_details(album)

            if album.album_type in exclude_album_type:
                cls.LOGGER.info(f"Skipping {album.option_string} due to the filter. ({album.album_type})")
                continue
            
            r.merge(cls.download_album(
                album,
                override_existing=override_existing,
                default_target=default_target,
                genre=genre
            ))

        return r

    @classmethod
    def download_artist(
            cls,
            artist: Artist,
            exclude_album_type: Set[AlbumType],
            download_features: bool = True,
            override_existing: bool = False,
            default_target: DefaultTarget = None,
            genre: str = None
    ) -> DownloadResult:

        default_target = DefaultTarget() if default_target is None else copy(default_target)
        default_target.artist_object(artist)

        r = DownloadResult()

        cls.fetch_details(artist)

        album: Album
        for album in artist.main_album_collection:
            if album.album_type in exclude_album_type:
                cls.LOGGER.info(f"Skipping {album.option_string} due to the filter. ({album.album_type})")
                continue
            
            r.merge(cls.download_album(
                album,
                override_existing=override_existing,
                default_target=default_target,
                genre=genre
            ))

        if download_features:
            for song in artist.feature_album.song_collection:
                r.merge(cls.download_song(
                    song,
                    override_existing=override_existing,
                    default_target=default_target,
                    genre=genre
                ))

        return r

    @classmethod
    def download_album(
            cls,
            album: Album,
            override_existing: bool = False,
            default_target: DefaultTarget = None,
            genre: str = None
       ) -> DownloadResult:

        default_target = DefaultTarget() if default_target is None else copy(default_target)
        default_target.album_object(album)

        r = DownloadResult()

        cls.fetch_details(album)

        album.update_tracksort()

        cls.LOGGER.info(f"downloading album: {album.title}")
        for song in album.song_collection:
            r.merge(cls.download_song(
                song,
                override_existing=override_existing,
                default_target=default_target,
                genre=genre
            ))

        return r

    @classmethod
    def download_song(
            cls,
            song: Song,
            override_existing: bool = False,
            create_target_on_demand: bool = True,
            default_target: DefaultTarget = None,
            genre: str = None
    ) -> DownloadResult:
        cls.LOGGER.debug(f"Setting genre of {song.option_string} to {genre}")
        song.genre = genre

        default_target = DefaultTarget() if default_target is None else copy(default_target)
        default_target.song_object(song)

        cls.fetch_details(song)

        if song.target_collection.empty:
            if create_target_on_demand and not song.main_artist_collection.empty and not song.album_collection.empty:
                song.target_collection.append(default_target.target)
            else:
                return DownloadResult(error_message=f"No target exists for {song.title}, but create_target_on_demand is False.")

        target: Target
        if any(target.exists for target in song.target_collection) and not override_existing:
            r = DownloadResult(total=1, fail=0)
            
            existing_target: Target
            for existing_target in song.target_collection:
                if existing_target.exists:
                    r.merge(cls._post_process_targets(song=song, temp_target=existing_target))
                    break
  
            return r

        sources = song.source_collection.get_sources_from_page(cls.SOURCE_TYPE)
        if len(sources) == 0:
            return DownloadResult(error_message=f"No source found for {song.title} as {cls.__name__}.")

        temp_target: Target = Target(
            path=shared.TEMP_DIR,
            file=str(random.randint(0, 999999))
        )

        r = cls._download_song_to_targets(source=sources[0], target=temp_target, desc=song.title)

        if not r.is_fatal_error:
            r.merge(cls._post_process_targets(song, temp_target))

        return r

    @classmethod
    def _post_process_targets(cls, song: Song, temp_target: Target) -> DownloadResult:
        correct_codec(temp_target)
        write_metadata_to_target(song.metadata, temp_target)

        r = DownloadResult()

        target: Target
        for target in song.target_collection:
            if temp_target is not target:
                temp_target.copy_content(target)
            r.add_target(target)
        
        return r

    @classmethod
    def _download_song_to_targets(cls, source: Source, target: Target, desc: str = None) -> DownloadResult:
        return DownloadResult()
