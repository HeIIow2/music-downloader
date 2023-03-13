from typing import (
    List
)

from ..objects import (
    Song,
    Source,
    Album,
    Artist,
    Lyrics,
    Target,
    MusicObject,
    Options
)


class Page:
    """
    This is an abstract class, laying out the 
    functionality for every other class fetching something
    """

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
    def fetch_details(cls, music_object: MusicObject, flat: bool = False) -> MusicObject:
        """
        when a music object with laccing data is passed in, it returns
        the SAME object **(no copy)** with more detailed data.
        If you for example put in an album, it fetches the tracklist

        :param music_object:
        :param flat: 
        if it is true it fetches only the most important information (only one level)
        if an Artist is passed in, it fetches only the discography of the artist, and not the
        tracklist of every album of the artist.
        :return detailed_music_object: IT MODIFIES THE INPUT OBJ
        """

        if type(music_object) == Song:
            return cls.fetch_song_details(music_object, flat=flat)
        
        if type(music_object) == Album:
            return cls.fetch_album_details(music_object, flat=flat)

        if type(music_object) == Artist:
            return cls.fetch_artist_details(music_object, flat=flat)

        raise NotImplementedError(f"MusicObject {type(music_object)} has not been implemented yet")

    @classmethod
    def fetch_song_details(cls, song: Song, flat: bool = False) -> Song:
        """
        for a general description check cls.fetch_details

        :param song: song without much data
        :param flat: 
        when True it only fetches the artist and the album, and the attributes of those,
        who can be gotten with one api request
        when False it fetches everything including, but not limited to:
         - Lyrics
         - Album + Tracklist (for tracksort)
        
        :return detailed_song: it modifies the input song
        """

        return song

    @classmethod
    def fetch_album_details(cls, album: Album, flat: bool = False) -> Album:
        """
        for a general description check cls.fetch_details

        :param album: album without much data
        :param flat: 
        when True it only fetches the artist and the tracklist, and the attributes of those,
        which can be gotten with one api request
        when False it fetches everything including, but not limited to:
         - Lyrics of every song
         - Artist, Album, Tracklist
         - every attribute of those
        
        :return detailed_artist: it modifies the input artist
        """

        return album

    @classmethod
    def fetch_artist_details(cls, artist: Artist, flat: bool = False) -> Artist:
        """
        for a general description check cls.fetch_details

        :param artist: artist without much data
        :param flat: 
        when True it only fetches the discographie, meaning every album, but not every tracklist
        when False it fetches everything including, but not limited to:
         - the whole discography
         - the tracklist of every album in the discography
        
        :return detailed_artist: it modifies the input artist
        """

        return artist
