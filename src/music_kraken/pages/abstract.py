import random
from typing import Optional, Union, Type, Dict, List
from bs4 import BeautifulSoup
import requests
import logging
from dataclasses import dataclass
from copy import copy

from ..utils import shared
from ..objects import (
    Song,
    Source,
    Album,
    Artist,
    Lyrics,
    Target,
    DatabaseObject,
    Options,
    SourcePages,
    Collection,
    Label
)
from ..tagging import write_metadata_to_target
from ..utils.shared import DOWNLOAD_PATH, DOWNLOAD_FILE, DEFAULT_VALUES

LOGGER = logging.getLogger("this shouldn't be used")

@dataclass
class DefaultTarget:
    genre: str = DEFAULT_VALUES["genre"]
    label: str = DEFAULT_VALUES["label"]
    artist: str = DEFAULT_VALUES["artist"]
    album: str = DEFAULT_VALUES["album"]
    song: str = DEFAULT_VALUES["song"]
    
    def __setattr__(self, __name: str, __value: str) -> None:
        if __name in DEFAULT_VALUES:
            if self.__getattribute__(__name) == DEFAULT_VALUES[__name]:
                super().__setattr__(__name, __value)
            return
            
        super().__setattr__(__name, __value)
    
    @property
    def target(self) -> Target:
        return Target(
            relative_to_music_dir=True,
            path=DOWNLOAD_PATH.format(genre=self.genre, label=self.label, artist=self.artist, album=self.album, song=self.song),
            file=DOWNLOAD_FILE.format(genre=self.genre, label=self.label, artist=self.artist, album=self.album, song=self.song)
        )
    

class Page:
    """
    This is an abstract class, laying out the 
    functionality for every other class fetching something
    """
    API_SESSION: requests.Session = requests.Session()
    API_SESSION.proxies = shared.proxies
    TIMEOUT = 5
    TRIES = 5
    
    SOURCE_TYPE: SourcePages

    @classmethod
    def get_request(cls, url: str, stream: bool = False, accepted_response_codes: set = set((200,)), trie: int = 0) -> Optional[
        requests.Response]:
        retry = False
        try:
            r = cls.API_SESSION.get(url, timeout=cls.TIMEOUT, stream=stream)
        except requests.exceptions.Timeout:
            retry = True
        except requests.exceptions.ConnectionError:
            retry = True

        if not retry and r.status_code in accepted_response_codes:
            return r

        if not retry:
            LOGGER.warning(f"{cls.__name__} responded wit {r.status_code} at GET:{url}. ({trie}-{cls.TRIES})")
            LOGGER.debug(r.content)

        if trie >= cls.TRIES:
            LOGGER.warning("to many tries. Aborting.")
            return None

        return cls.get_request(url, accepted_response_codes, trie + 1)

    @classmethod
    def post_request(cls, url: str, json: dict, accepted_response_codes: set = set((200,)), trie: int = 0) -> Optional[
        requests.Response]:
        retry = False
        try:
            r = cls.API_SESSION.post(url, json=json, timeout=cls.TIMEOUT)
        except requests.exceptions.Timeout:
            retry = True
        except requests.exceptions.ConnectionError:
            retry = True

        if not retry and r.status_code in accepted_response_codes:
            return r

        if not retry:
            LOGGER.warning(f"{cls.__name__} responded wit {r.status_code} at POST:{url}. ({trie}-{cls.TRIES})")
            LOGGER.debug(r.content)

        if trie >= cls.TRIES:
            LOGGER.warning("to many tries. Aborting.")
            return None

        return cls.post_request(url, json, accepted_response_codes, trie + 1)

    @classmethod
    def get_soup_from_response(cls, r: requests.Response) -> BeautifulSoup:
        return BeautifulSoup(r.content, "html.parser")

    class Query:
        def __init__(self, query: str):
            self.query = query
            self.is_raw = False

            self.artist = None
            self.album = None
            self.song = None

            self.parse_query(query=query)

        def __str__(self):
            if self.is_raw:
                return self.query
            return f"{self.artist}; {self.album}; {self.song}"

        def parse_query(self, query: str):
            if not '#' in query:
                self.is_raw = True
                return

            query = query.strip()
            parameters = query.split('#')
            parameters.remove('')

            for parameter in parameters:
                splitted = parameter.split(" ")
                type_ = splitted[0]
                input_ = " ".join(splitted[1:]).strip()

                if type_ == "a":
                    self.artist = input_
                    continue
                if type_ == "r":
                    self.album = input_
                    continue
                if type_ == "t":
                    self.song = input_
                    continue

        def get_str(self, string):
            if string is None:
                return ""
            return string

        artist_str = property(fget=lambda self: self.get_str(self.artist))
        album_str = property(fget=lambda self: self.get_str(self.album))
        song_str = property(fget=lambda self: self.get_str(self.song))

    @classmethod
    def search_by_query(cls, query: str) -> Options:
        """
        # The Query
        You can define a new parameter with "#",
        the letter behind it defines the *type* of parameter, followed by a space
        "#a Psychonaut 4 #r Tired, Numb and #t Drop by Drop"
        if no # is in the query it gets treated as "unspecified query"

        # Functionality
        Returns the best matches from this page for the query, passed in.

        :param query:
        :return possible_music_objects:
        """

        return Options()

    @classmethod
    def fetch_details(cls, music_object: Union[Song, Album, Artist, Label], stop_at_level: int = 1) -> DatabaseObject:
        """
        when a music object with laccing data is passed in, it returns
        the SAME object **(no copy)** with more detailed data.
        If you for example put in an album, it fetches the tracklist

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
        
        new_music_object: DatabaseObject = type(music_object)()

        had_sources = False

        source: Source
        for source in music_object.source_collection.get_sources_from_page(cls.SOURCE_TYPE):
            new_music_object.merge(cls._fetch_object_from_source(source=source, obj_type=type(music_object), stop_at_level=stop_at_level))
            had_sources = True
            
        if not had_sources:
            music_object.compile(merge_into=True)
            return music_object

        collections = {
            Label: Collection(element_type=Label),
            Artist: Collection(element_type=Artist),
            Album: Collection(element_type=Album),
            Song: Collection(element_type=Song)
        }

        cls._clean_music_object(new_music_object, collections)
        
        music_object.merge(new_music_object)     
               
        music_object.compile(merge_into=True)

        return music_object
    
    @classmethod
    def fetch_object_from_source(cls, source: Source, stop_at_level: int = 2):
        obj_type = cls._get_type_of_url(source.url)
        if obj_type is None:
            return None
        
        music_object = cls._fetch_object_from_source(source=source, obj_type=obj_type, stop_at_level=stop_at_level)
        
        collections = {
            Label: Collection(element_type=Label),
            Artist: Collection(element_type=Artist),
            Album: Collection(element_type=Album),
            Song: Collection(element_type=Song)
        }

        cls._clean_music_object(music_object, collections)  
        music_object.compile(merge_into=True)
        return music_object
        

    @classmethod
    def _fetch_object_from_source(cls, source: Source, obj_type: Union[Type[Song], Type[Album], Type[Artist], Type[Label]], stop_at_level: int = 1) -> Union[Song, Album, Artist, Label]:
        if obj_type == Artist:
            return cls._fetch_artist_from_source(source=source, stop_at_level=stop_at_level)
        
        if obj_type == Song:
            return cls._fetch_song_from_source(source=source, stop_at_level=stop_at_level)
        
        if obj_type == Album:
            return cls._fetch_album_from_source(source=source, stop_at_level=stop_at_level)
        
        if obj_type == Label:
            return cls._fetch_label_from_source(source=source, stop_at_level=stop_at_level)

    @classmethod
    def _clean_music_object(cls, music_object: Union[Label, Album, Artist, Song], collections: Dict[Union[Type[Song], Type[Album], Type[Artist], Type[Label]], Collection]):
        if type(music_object) == Label:
            return cls._clean_label(label=music_object, collections=collections)
        if type(music_object) == Artist:
            return cls._clean_artist(artist=music_object, collections=collections)
        if type(music_object) == Album:
            return cls._clean_album(album=music_object, collections=collections)
        if type(music_object) == Song:
            return cls._clean_song(song=music_object, collections=collections)

    @classmethod
    def _clean_collection(cls, collection: Collection, collection_dict: Dict[Union[Type[Song], Type[Album], Type[Artist], Type[Label]], Collection]):
        if collection.element_type not in collection_dict:
            return

        for i, element in enumerate(collection):
            r = collection_dict[collection.element_type].append(element)
            if not r.was_in_collection:
                cls._clean_music_object(r.current_element, collection_dict)
                continue

            collection[i] = r.current_element
            cls._clean_music_object(r.current_element, collection_dict)

    @classmethod
    def _clean_label(cls, label: Label, collections: Dict[Union[Type[Song], Type[Album], Type[Artist], Type[Label]], Collection]):
        cls._clean_collection(label.current_artist_collection, collections)
        cls._clean_collection(label.album_collection, collections)

    @classmethod
    def _clean_artist(cls, artist: Artist, collections: Dict[Union[Type[Song], Type[Album], Type[Artist], Type[Label]], Collection]):
        cls._clean_collection(artist.main_album_collection, collections)
        cls._clean_collection(artist.feature_song_collection, collections)
        cls._clean_collection(artist.label_collection, collections)

    @classmethod
    def _clean_album(cls, album: Album, collections: Dict[Union[Type[Song], Type[Album], Type[Artist], Type[Label]], Collection]):
        cls._clean_collection(album.label_collection, collections)
        cls._clean_collection(album.song_collection, collections)
        cls._clean_collection(album.artist_collection, collections)

    @classmethod
    def _clean_song(cls, song: Song, collections: Dict[Union[Type[Song], Type[Album], Type[Artist], Type[Label]], Collection]):
        cls._clean_collection(song.album_collection, collections)
        cls._clean_collection(song.feature_artist_collection, collections)
        cls._clean_collection(song.main_artist_collection, collections)

    @classmethod
    def download(
        cls, 
        music_object: Union[Song, Album, Artist, Label], 
        download_features: bool = True,
        default_target: DefaultTarget = None
    ):
        if default_target is None:
            default_target = DefaultTarget()
        
        if type(music_object) is Song:
            return cls.download_song(music_object, default_target)
        if type(music_object) is Album:
            return cls.download_album(music_object, default_target)
        if type(music_object) is Artist:
            return cls.download_artist(music_object, default_target)
        if type(music_object) is Label:
            return cls.download_label(music_object, download_features=download_features, default_target=default_target)
        
    @classmethod
    def download_label(cls, label: Label, download_features: bool = True, override_existing: bool = False, default_target: DefaultTarget = None):
        if default_target is None:
            default_target = DefaultTarget()
        else:
            default_target = copy(default_target)
        default_target.label = label.name
        
        cls.fetch_details(label)
        for artist in label.current_artist_collection:
            cls.download_artist(artist, download_features=download_features, override_existing=override_existing, default_target=default_target)
        
        for album in label.album_collection:
            cls.download_album(album, override_existing=override_existing, default_target=default_target)

    @classmethod
    def download_artist(cls, artist: Artist, download_features: bool = True, override_existing: bool = False, default_target: DefaultTarget = None):
        if default_target is None:
            default_target = DefaultTarget()
        else:
            default_target = copy(default_target)
        default_target.artist = artist.name
        
        cls.fetch_details(artist)
        for album in artist.main_album_collection:
            cls.download_album(album, override_existing=override_existing, default_target=default_target)
        
        if download_features:
            for song in artist.feature_album.song_collection:
                cls.download_song(song, override_existing=override_existing, default_target=default_target)

    @classmethod
    def download_album(cls, album: Album, override_existing: bool = False, default_target: DefaultTarget = None):
        if default_target is None:
            default_target = DefaultTarget()
        else:
            default_target = copy(default_target)
        default_target.album = album.title
        
        cls.fetch_details(album)
        for song in album.song_collection:
            cls.download_song(song, override_existing=override_existing, default_target=default_target)

    @classmethod
    def download_song(cls, song: Song, override_existing: bool = False, create_target_on_demand: bool = True, default_target: DefaultTarget = None):
        if default_target is None:
            default_target = DefaultTarget()
        else:
            default_target = copy(default_target)
        default_target.song = song.title
        
        cls.fetch_details(song)
        
        if song.target_collection.empty:
            if create_target_on_demand and not song.main_artist_collection.empty and not song.album_collection.empty:
                song.target_collection.append(default_target.target)
            else:
                return
        
        target: Target
        if any(target.exists for target in song.target_collection) and not override_existing:
            existing_target: Target
            for existing_target in song.target_collection:
                if existing_target.exists:
                    break
                
            for target in song.target_collection:
                if target is existing_target:
                    continue
                
                existing_target.copy_content(target)
        
        sources = song.source_collection.get_sources_from_page(cls.SOURCE_TYPE)
        if len(sources) == 0:
            return
        
        print("great")
        
        temp_target: Target = Target(
            path=shared.TEMP_DIR,
            file=str(random.randint(0, 999999))
        )
        
        cls._download_song_to_targets(source=sources[0], target=temp_target)
        cls._post_process_targets(song, temp_target)
    
    @classmethod
    def _post_process_targets(cls, song: Song, temp_target: Target):
        write_metadata_to_target(song.metadata, temp_target)
        
        target: Target
        for target in song.target_collection:
            temp_target.copy_content(target)
        

    @classmethod
    def _fetch_song_from_source(cls, source: Source, stop_at_level: int = 1) -> Song:
        return Song()
    
    @classmethod
    def _fetch_album_from_source(cls, source: Source, stop_at_level: int = 1) -> Album:
        return Album()

    @classmethod
    def _fetch_artist_from_source(cls, source: Source, stop_at_level: int = 1) -> Artist:
        return Artist()

    @classmethod
    def _fetch_label_from_source(cls, source: Source, stop_at_level: int = 1) -> Label:
        return Label()

    @classmethod
    def _get_type_of_url(cls, url: str) -> Optional[Union[Type[Song], Type[Album], Type[Artist], Type[Label]]]:
        return None
    
    @classmethod
    def _download_song_to_targets(cls, source: Source) -> Target:
        return Target()
