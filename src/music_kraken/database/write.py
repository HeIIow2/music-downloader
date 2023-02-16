from typing import Union, Set
import traceback
from peewee import (
    SqliteDatabase,
    MySQLDatabase,
    PostgresqlDatabase,
)

from . import objects
from . import data_models

# just a Type for type hintung. You can't do anything with it.
Database = Union[SqliteDatabase, PostgresqlDatabase, MySQLDatabase]

class Session:
    """
    Context manager for a database session

    Usage:
    with Session(database) as session:
        # Perform database operations using session object

    Args:
    database: An instance of a database connection from Peewee

    Attributes:
    database: An instance of a database connection from Peewee
    """
    def __init__(self, database: Database) -> None:
        """
        Initialize a database session

        Args:
        database: An instance of a database connection from Peewee
        """
        self.database = database
        
        self.added_song_ids: Set[str] = set()
        self.added_album_ids: Set[str] = set()
        self.added_artist_ids: Set[str] = set()

    def __enter__(self, database: Database):
        """
        Enter the context of the database session

        Args:
        database: An instance of a database connection from Peewee

        Returns:
        self: The instance of the session object
        """
        print('Entering the context')
        self.__init__(database=database)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context of the database session

        Args:
        exc_type: The type of the raised exception
        exc_val: The value of the raised exception
        exc_tb: The traceback of the raised exception

        Returns:
        bool: True if no exception was raised, False otherwise
        """
        if exc_val is not None:
            traceback.print_tb(exc_tb)
            print(f"Exception of type {exc_type} occurred with message: {exc_val}")

        self.commit()
        return exc_val is None
    
    def add_source(self, source: objects.Source, connected_to: data_models.Source.ContentTypes) -> data_models.Source:
        db_source = data_models.Source(
            page=source.page_str,
            url=source.url,
            content_object=connected_to
        ).use(self.database)

        return db_source

    def add_song(self, song: objects.Song) -> data_models.Song:
        """
        Add a song object to the session

        Args:
        song: An instance of the Song object
        """
        if song.dynamic:
            return
        if song.id in self.added_song_ids:
            return
        self.added_song_ids.add(song.id)

        db_song: data_models.Song = data_models.Song(
            id=song.id,
            name=song.title,
            isrc=song.isrc,
            length=song.length,
            tracksort=song.tracksort,
            genre=song.genre
        ).use(self.database)

        for source in song.source_list:
            self.add_source(source=source, connected_to=db_song)

        return db_song

    def add_album(self, album: objects.Album):
        """
        Add an album object to the session

        Args:
        album: An instance of the Album object
        """
        if album.dynamic:
            return
        if album.id in self.added_album_ids:
            return
        self.added_album_ids.add(album.id)

    def add_artist(self, artist: objects.Artist):
        """
        Add an artist object to the session

        Args:
        artist: An instance of the Artist object
        """
        if artist.dynamic:
            return
        if artist.id in self.added_artist_ids:
            return
        self.added_artist_ids.add(artist.id)

    def commit(self):
        """
        Commit changes to the database
        """
        pass