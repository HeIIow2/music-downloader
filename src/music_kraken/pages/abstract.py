import logging
import random
from copy import copy
from typing import Optional, Union, Type, Dict, Set, List, Tuple
from string import Formatter

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
from ..utils.config import main_settings
from ..utils.support_classes import Query, DownloadResult
from ..utils.string_processing import fit_to_file_system


INDEPENDENT_DB_OBJECTS = Union[Label, Album, Artist, Song]
INDEPENDENT_DB_TYPES = Union[Type[Song], Type[Album], Type[Artist], Type[Label]]


class NamingDict(dict):
    CUSTOM_KEYS: Dict[str, str] = {
        "label": "label.name",
        "artist": "artist.name",
        "song": "song.title",
        "isrc": "song.isrc",
        "album": "album.title",
        "album_type": "album.album_type_string"
    }
    
    def __init__(self, values: dict, object_mappings: Dict[str, DatabaseObject] = None):
        self.object_mappings: Dict[str, DatabaseObject] = object_mappings or dict()
        
        super().__init__(values)
        self["audio_format"] = main_settings["audio_format"]
        
    def add_object(self, music_object: DatabaseObject):
        self.object_mappings[type(music_object).__name__.lower()] = music_object
    
    def copy(self) -> dict:
        return type(self)(super().copy(), self.object_mappings.copy())
    
    def __getitem__(self, key: str) -> str:
        return fit_to_file_system(super().__getitem__(key))
    
    def default_value_for_name(self, name: str) -> str:
        return f'Various {name.replace("_", " ").title()}'

    def __missing__(self, key: str) -> str:
        if "." not in key:
            if key not in self.CUSTOM_KEYS:
                return self.default_value_for_name(key)

            key = self.CUSTOM_KEYS[key]
        
        frag_list = key.split(".")
        
        object_name = frag_list[0].strip().lower()
        attribute_name = frag_list[-1].strip().lower()

        if object_name not in self.object_mappings:
            return self.default_value_for_name(attribute_name)
        
        music_object = self.object_mappings[object_name]
        try:
            value = getattr(music_object, attribute_name)
            if value is None:
                return self.default_value_for_name(attribute_name)
        
            return str(value)
        
        except AttributeError:
            return self.default_value_for_name(attribute_name)


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

def merge_together(old_object: DatabaseObject, new_object: DatabaseObject, do_compile: bool = True) -> DatabaseObject:
    new_object = clean_object(new_object)
    
    old_object.merge(new_object)
    if do_compile:
        old_object.compile(merge_into=False)
    
    return old_object


class Page:
    """
    This is an abstract class, laying out the 
    functionality for every other class fetching something
    """
    
    SOURCE_TYPE: SourcePages
    LOGGER = logging.getLogger("this shouldn't be used")
    
    # set this to true, if all song details can also be fetched by fetching album details
    NO_ADDITIONAL_DATA_FROM_SONG = False
    
        
    def __init__(self):
        super().__init__()
    
    """
    CODE I NEED WHEN I START WITH MULTITHREADING
    
    def __init__(self, end_event: EndThread, search_queue: Queue, search_result_queue: Queue):
        self.end_event = end_event
        
        self.search_queue = search_queue
        self.search_result_queue = search_result_queue
        
        super().__init__()
        
    @property
    def _empty_working_queues(self):
        return self.search_queue.empty()

    def run(self) -> None:
        while bool(self.end_event) and self._empty_working_queues:
            if not self.search_queue.empty():
                self.search(self.search_queue.get())
                self.search_result_queue.put(FinishedSearch())
                continue
    """
    
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
            if r is not None and len(r) > 0:
                return r
            
        r = []
        for default_query in query.default_search:
            for single_option in self.general_search(default_query):
                r.append(single_option)
        
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
    

    def fetch_details(self, music_object: DatabaseObject, stop_at_level: int = 1, post_process: bool = True) -> DatabaseObject:
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
                new_music_object.merge(self.fetch_object_from_source(
                    source=source, 
                    enforce_type=type(music_object), 
                    stop_at_level=stop_at_level, 
                    post_process=False
                ))

        return merge_together(music_object, new_music_object, do_compile=post_process)

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

        if stop_at_level > 1:
            collection: Collection
            for collection_str in music_object.DOWNWARDS_COLLECTION_ATTRIBUTES:
                collection = music_object.__getattribute__(collection_str)

                for sub_element in collection:
                    sub_element.merge(self.fetch_details(sub_element, stop_at_level=stop_at_level-1, post_process=False))

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

    def download(self, music_object: DatabaseObject, genre: str, download_all: bool = False, process_metadata_anyway: bool = False) -> DownloadResult:
        naming_dict: NamingDict = NamingDict({"genre": genre})
          
        def fill_naming_objects(naming_music_object: DatabaseObject):
            nonlocal naming_dict
            
            for collection_name in naming_music_object.UPWARDS_COLLECTION_ATTRIBUTES:
                collection: Collection = getattr(naming_music_object, collection_name)
                
                if collection.empty:
                    continue
                
                dom_ordered_music_object: DatabaseObject = collection[0]
                naming_dict.add_object(dom_ordered_music_object)
                return fill_naming_objects(dom_ordered_music_object)
          
        fill_naming_objects(music_object)
          
        return self._download(music_object, naming_dict, download_all, process_metadata_anyway=process_metadata_anyway)


    def _download(self, music_object: DatabaseObject, naming_dict: NamingDict, download_all: bool = False, skip_details: bool = False, process_metadata_anyway: bool = False) -> DownloadResult:
        skip_next_details = skip_details
        
        # Skips all releases, that are defined in shared.ALBUM_TYPE_BLACKLIST, if download_all is False
        if isinstance(music_object, Album):
            if self.NO_ADDITIONAL_DATA_FROM_SONG:
                skip_next_details = True
            
            if not download_all and music_object.album_type.value in main_settings["album_type_blacklist"]:
                return DownloadResult()

        if not isinstance(music_object, Song) or not self.NO_ADDITIONAL_DATA_FROM_SONG:
            self.fetch_details(music_object=music_object, stop_at_level=2)
            
        naming_dict.add_object(music_object)

        if isinstance(music_object, Song):
            return self._download_song(music_object, naming_dict, process_metadata_anyway=process_metadata_anyway)

        download_result: DownloadResult = DownloadResult()

        for collection_name in music_object.DOWNWARDS_COLLECTION_ATTRIBUTES:
            collection: Collection = getattr(music_object, collection_name)

            sub_ordered_music_object: DatabaseObject
            for sub_ordered_music_object in collection:
                download_result.merge(self._download(sub_ordered_music_object, naming_dict.copy(), download_all, skip_details=skip_next_details, process_metadata_anyway=process_metadata_anyway))

        return download_result

    def _download_song(self, song: Song, naming_dict: NamingDict, process_metadata_anyway: bool = False):
        if "genre" not in naming_dict and song.genre is not None:
            naming_dict["genre"] = song.genre

        if song.genre is None:
            song.genre = naming_dict["genre"]

        path_parts = Formatter().parse(main_settings["download_path"])
        file_parts = Formatter().parse(main_settings["download_file"])
        new_target = Target(
            relative_to_music_dir=True,
            path=main_settings["download_path"].format(**{part[1]: naming_dict[part[1]] for part in path_parts}),
            file=main_settings["download_file"].format(**{part[1]: naming_dict[part[1]] for part in file_parts})
        )


        if song.target_collection.empty:
            song.target_collection.append(new_target)

        sources = song.source_collection.get_sources_from_page(self.SOURCE_TYPE)
        if len(sources) == 0:
            return DownloadResult(error_message=f"No source found for {song.title} as {self.__class__.__name__}.")

        temp_target: Target = Target(
            path=main_settings["temp_directory"],
            file=str(random.randint(0, 999999))
        )
        
        r = DownloadResult(1)

        found_on_disc = False
        target: Target
        for target in song.target_collection:
            if target.exists:
                if process_metadata_anyway:
                    target.copy_content(temp_target)
                found_on_disc = True
                
                r.found_on_disk += 1
                r.add_target(target)
        
        if found_on_disc and not process_metadata_anyway:
            self.LOGGER.info(f"{song.option_string} already exists, thus not downloading again.")
            return r

        source = sources[0]

        if not found_on_disc:
            r = self.download_song_to_target(source=source, target=temp_target, desc=song.title)
                    

        if not r.is_fatal_error:
            r.merge(self._post_process_targets(song, temp_target, [] if found_on_disc else self.get_skip_intervals(song, source)))

        return r
    
    def _post_process_targets(self, song: Song, temp_target: Target, interval_list: List) -> DownloadResult:
        correct_codec(temp_target, interval_list=interval_list)
        
        self.post_process_hook(song, temp_target)
        
        write_metadata_to_target(song.metadata, temp_target)

        r = DownloadResult()

        target: Target
        for target in song.target_collection:
            if temp_target is not target:
                temp_target.copy_content(target)
            r.add_target(target)
            
        temp_target.delete()
        r.sponsor_segments += len(interval_list)
        
        return r
    
    def get_skip_intervals(self, song: Song, source: Source) -> List[Tuple[float, float]]:
        return []
    
    def post_process_hook(self, song: Song, temp_target: Target, **kwargs):
        pass
    
    def download_song_to_target(self, source: Source, target: Target, desc: str = None) -> DownloadResult:
        return DownloadResult()
