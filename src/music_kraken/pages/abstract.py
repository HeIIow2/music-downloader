from typing import (
    List
)

from ..database import (
    Song,
    Source,
    Album,
    Metadata,
    Artist,
    Lyrics,
    Target,
    MusicObject
)


class Page:
    """
    This is an abstract class, laying out the 
    functionality for every other class fetching something
    """

    @classmethod
    def search_by_query(cls, query: str) -> List[MusicObject]:        
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

        raise NotImplementedError()

    @classmethod
    def fetch_details(cls, music_object: MusicObject, simple: bool = False) -> MusicObject:
        """
        when a music object with laccing data is passed in, it returns
        the SAME object **(no copy)** with more detailed data.
        If you for example put in an album, it fetches the tracklist

        :param music_object:
        :param simple: 
        if it is true it fetches only the most important information (only one level)
        if an Artist is passed in, it fetches only the discography of the artist, and not the
        tracklist of every album of the artist.
        :return detailed_music_object: IT MODIFIES THE INPUT OBJ
        """

        if type(music_object) == Song:
            return cls.fetch_song_details(music_object, simple=simple)
        
        if type(music_object) == Album:
            return cls.fetch_album_details(music_object, simple=simple)

        if type(music_object) == Artist:
            return cls.fetch_artist_details(music_object, simple=simple)

        raise NotImplementedError(f"MusicObject {type(music_object)} has not been implemented yet")

    def fetch_song_details(cls, song: Song, simple: bool = False) -> Song:
        """
        for a general description check cls.fetch_details

        :param song: song without much data
        :param simple: 
        when True it only fetches the artist and the album, and the attributes of those,
        who can be gotten with one api request
        when False it fetches everything including, but not limited to:
         - Lyrics
         - Album + Tracklist (for tracksort)
        
        :return detailed_song: it modifies the input song
        """

        raise NotImplementedError()

    def fetch_album_details(cls, album: Album, simple: bool = False) -> Album:
        """
        for a general description check cls.fetch_details

        :param album: album without much data
        :param simple: 
        when True it only fetches the artist and the tracklist, and the attributes of those,
        which can be gotten with one api request
        when False it fetches everything including, but not limited to:
         - Lyrics of every song
         - Artist, Album, Tracklist
         - every attribute of those
        
        :return detailed_artist: it modifies the input artist
        """

        raise NotImplementedError()

    def fetch_artist_details(cls, artist: Artist, simple: bool = False) -> Artist:
        """
        for a general description check cls.fetch_details

        :param artist: artist without much data
        :param simple: 
        when True it only fetches the discographie, meaning every album, but not every tracklist
        when False it fetches everything including, but not limited to:
         - the whole discography
         - the tracklist of every album in the discography
        
        :return detailed_artist: it modifies the input artist
        """

        raise NotImplementedError()
