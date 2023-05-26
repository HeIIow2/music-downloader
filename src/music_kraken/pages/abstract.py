import logging
import random
from copy import copy
from typing import Optional, Union, Type, Dict, Set, List
import threading
from queue import Queue

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
from ..utils.shared import DEFAULT_VALUES, DOWNLOAD_PATH, DOWNLOAD_FILE, THREADED
from ..utils.support_classes import Query, DownloadResult, DefaultTarget, EndThread, FinishedSearch


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

        _clean_music_object(dirty_object, collections)
    return dirty_object
    
def build_new_object(new_object: DatabaseObject) -> DatabaseObject:
    new_object = clean_object(new_object)
    new_object.compile(merge_into=False)
    
    return new_object

def merge_together(old_object: DatabaseObject, new_object: DatabaseObject) -> DatabaseObject:
    new_object = clean_object(new_object)
    
    old_object.merge(new_object)
    old_object.compile(merge_into=False)
    
    return old_object


class LoreIpsum:
    pass


Parent = threading.Thread if THREADED else LoreIpsum


class Page(Parent):
    """
    This is an abstract class, laying out the 
    functionality for every other class fetching something
    """
    
    SOURCE_TYPE: SourcePages
    LOGGER = logging.getLogger("this shouldn't be used")
    
    def __init__(self, end_event: EndThread, search_queue: Queue, search_result_queue: Queue):
        self.end_event = end_event
        
        self.search_queue = search_queue
        self.search_result_queue = search_result_queue
        
        Parent.__init__(self)

    @property
    def _empty_working_queues(self):
        return self.search_queue.empty()

    def run(self) -> None:
        while bool(self.end_event) and self._empty_working_queues:
            if not self.search_queue.empty():
                self.search(self.search_queue.get())
                self.search_result_queue.put(FinishedSearch())
                continue
    
    def get_source_type(self, source: Source) -> Optional[Type[DatabaseObject]]:
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
            for single_option in self.general_search(default_query):
                r.append(single_option)
                self.search_result_queue.put(single_option)
        
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
                    self.fetch_object_from_source(
                        source=source, 
                        enforce_type=type(music_object), 
                        stop_at_level=stop_at_level, 
                        post_process=False
                    )
                )

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

    def download(self, music_object: DatabaseObject, genre: str, download_all: bool = False) -> DownloadResult:
        naming_objects = {"genre": genre}
        
        def fill_naming_objects(naming_music_object: DatabaseObject):
            nonlocal naming_objects
            
            for collection_name in naming_music_object.UPWARDS_COLLECTION_ATTRIBUTES:
                collection: Collection = getattr(self, collection_name)
                
                if collection.empty():
                    continue
                if collection.element_type in naming_objects:
                    continue
                
                dom_ordered_music_object: DatabaseObject = collection[0]
                return fill_naming_objects(dom_ordered_music_object)
          
        fill_naming_objects(music_object)
          
        return self._download(music_object, {}, genre, download_all)


    def _download(self, music_object: DatabaseObject, naming_objects: Dict[Type[DatabaseObject], DatabaseObject], download_all: bool = False) -> list:
        # Skips all releases, that are defined in shared.ALBUM_TYPE_BLACKLIST, if download_all is False
        if isinstance(music_object, Album):
            if not download_all and music_object.album_type in shared.ALBUM_TYPE_BLACKLIST:
                return DownloadResult()

        self.fetch_details(music_object=music_object, stop_at_level=2)
        naming_objects[type(music_object)] = music_object

        if isinstance(music_object, Song):
            return self._download_song(music_object, naming_objects)

        download_result: DownloadResult = DownloadResult()

        for collection_name in music_object.DOWNWARDS_COLLECTION_ATTRIBUTES:
            collection: Collection = getattr(self, collection_name)

            sub_ordered_music_object: DatabaseObject
            for sub_ordered_music_object in collection:
                download_result.merge(self._download(sub_ordered_music_object, naming_objects.copy(), download_all))

        return download_result

    def _download_song(self, song: Song, naming_objects: Dict[Type[DatabaseObject], DatabaseObject]):
        name_attribute = DEFAULT_VALUES.copy()
        
        # song
        name_attribute["genre"] = naming_objects["genre"]
        name_attribute["song"] = song.title
        
        if Album in naming_objects:
            album: Album = naming_objects[Album]
            name_attribute["album"] = album.title
            name_attribute["album_type"] = album.album_type.value
        
        if Artist in naming_objects:
            artist: Artist = naming_objects[Artist]
            naming_objects["artist"] = artist.name
        
        if Label in naming_objects:
            label: Label = naming_objects[Label]
            naming_objects["label"] = label.name
        
        new_target = Target(
            relative_to_music_dir=True,
            path=DOWNLOAD_PATH.format(**name_attribute),
            file=DOWNLOAD_FILE.format(**name_attribute)
        )
        
        if song.target_collection.empty:
            song.target_collection.append(new_target)
        
        sources = song.source_collection.get_sources_from_page(self.SOURCE_TYPE)
        if len(sources) == 0:
            return DownloadResult(error_message=f"No source found for {song.title} as {self.__class__.__name__}.")

        temp_target: Target = Target(
            path=shared.TEMP_DIR,
            file=str(random.randint(0, 999999))
        )
        
        r = self._download_song_to_targets(source=sources[0], target=temp_target, desc=song.title)

        if not r.is_fatal_error:
            r.merge(self._post_process_targets(song, temp_target))

        return r
    
    def _post_process_targets(self, song: Song, temp_target: Target) -> DownloadResult:
        correct_codec(temp_target)
        write_metadata_to_target(song.metadata, temp_target)

        r = DownloadResult()

        target: Target
        for target in song.target_collection:
            if temp_target is not target:
                temp_target.copy_content(target)
            r.add_target(target)
            
        temp_target.delete()
        
        return r
    
    def download_song_to_target(self, source: Source, target: Target, desc: str = None) -> DownloadResult:
        return DownloadResult()
