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

class Query:
    def __init__(self) -> None:
        pass

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
        :return detailed_music_object:
        """

        raise NotImplementedError
