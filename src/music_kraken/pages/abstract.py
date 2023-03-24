from typing import Optional, Union, Type
import requests
import logging

LOGGER = logging.getLogger("this shouldn't be used")

from ..utils import shared

from ..objects import (
    Song,
    Source,
    Album,
    Artist,
    Lyrics,
    Target,
    MusicObject,
    Options,
    SourcePages,
    Collection,
    Label
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
    def get_request(cls, url: str, accepted_response_codes: set = set((200,)), trie: int = 0) -> Optional[
        requests.Request]:
        try:
            r = cls.API_SESSION.get(url, timeout=cls.TIMEOUT)
        except requests.exceptions.Timeout:
            return None

        if r.status_code in accepted_response_codes:
            return r

        LOGGER.warning(f"{cls.__name__} responded wit {r.status_code} at {url}. ({trie}-{cls.TRIES})")
        LOGGER.debug(r.content)

        if trie <= cls.TRIES:
            LOGGER.warning("to many tries. Aborting.")

        return cls.get_request(url, accepted_response_codes, trie + 1)

    @classmethod
    def post_request(cls, url: str, json: dict, accepted_response_codes: set = set((200,)), trie: int = 0) -> Optional[
        requests.Request]:
        try:
            r = cls.API_SESSION.post(url, json=json, timeout=cls.TIMEOUT)
        except requests.exceptions.Timeout:
            return None

        if r.status_code in accepted_response_codes:
            return r

        LOGGER.warning(f"{cls.__name__} responded wit {r.status_code} at {url}. ({trie}-{cls.TRIES})")
        LOGGER.debug(r.content)

        if trie <= cls.TRIES:
            LOGGER.warning("to many tries. Aborting.")

        return cls.post_request(url, accepted_response_codes, trie + 1)

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
    def fetch_details(cls, music_object: Union[Song, Album, Artist, Label], stop_at_level: int = 1) -> MusicObject:
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
        
        new_music_object: MusicObject = type(music_object).__init__()
        
        source: Source
        for source in music_object.source_collection:
            new_music_object.merge(cls.fetch_object_from_source(source=source, obj_type=type(music_object), stop_at_level=stop_at_level))


        
        music_object.merge(new_music_object)            
        music_object.compile()

        return music_object

    @classmethod
    def fetch_object_from_source(cls, source: Source, obj_type: Union[Type[Song], Type[Album], Type[Artist], Type[Label]], stop_at_level: int = 1):
        if obj_type == Artist:
            return cls.fetch_artist_from_source(source=source, stop_at_level=stop_at_level)
        
        if obj_type == Song:
            return cls.fetch_song_from_source(source=source, stop_at_level=stop_at_level)
        
        if obj_type == Album:
            return cls.fetch_album_from_source(source=source, stop_at_level=stop_at_level)
        
        if obj_type == Label:
            return cls.fetch_label_from_source(source=source, stop_at_level=stop_at_level)

    @classmethod
    def fetch_song_from_source(cls, source: Source, stop_at_level: int = 1) -> Song:
        return Song()

    @classmethod
    def fetch_album_from_source(cls, source: Source, stop_at_level: int = 1) -> Album:
        return Album()


    @classmethod
    def fetch_artist_from_source(cls, source: Source, stop_at_level: int = 1) -> Artist:
        return Artist()
    
    def fetch_label_from_source(source: Source, stop_at_level: int = 1) -> Label:
        return Label()
