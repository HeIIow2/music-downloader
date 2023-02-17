from typing import Union, Set, Optional, Dict, DefaultDict
from collections import defaultdict
import traceback
from peewee import (
    SqliteDatabase,
    MySQLDatabase,
    PostgresqlDatabase,
    Model
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

        self.added_song_ids: Dict[str] = dict()
        self.added_album_ids: Dict[str] = dict()
        self.added_artist_ids: Dict[str] = dict()

        self.db_objects: DefaultDict[data_models.BaseModel, list] = defaultdict(list)

    def __enter__(self, database: Database):
        """
        Enter the context of the database session

        Args:
        database: An instance of a database connection from Peewee

        Returns:
        self: The instance of the session object
        """
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

        self.commit(reset=False)
        return exc_val is None

    def add_source(self, source: objects.Source, connected_to: data_models.Source.ContentTypes) -> data_models.Source:
        db_source = data_models.Source(
            id=source.id,
            page=source.page_str,
            url=source.url,
            content_object=connected_to
        ).use(self.database)

        self.db_objects[data_models.Source].append(db_source)

        return db_source

    def add_lyrics(self, lyrics: objects.Lyrics, song: data_models.Song) -> data_models.Lyrics:
        db_lyrics = data_models.Lyrics(
            id=lyrics.id,
            text=lyrics.text,
            language=lyrics.language,
            song=song
        ).use(self.database)

        self.db_objects[data_models.Lyrics].append(db_lyrics)

        for source in lyrics.source_list:
            self.add_source(source=source, connected_to=db_lyrics)

        return db_lyrics

    def add_target(self, target: objects.Target, song: data_models.Song) -> data_models.Target:
        db_target = data_models.Target(
            id=target.id,
            path=target.path,
            file=target.file,
            song=song
        ).use(self.database)

        self.db_objects[data_models.Target].append(db_target)

        return db_target

    def add_song(self, song: objects.Song) -> Optional[data_models.Song]:
        """
        Add a song object to the session

        Args:
        song: An instance of the Song object
        """
        if song.dynamic:
            return
        if song.id in self.added_song_ids:
            return self.added_song_ids[song.id]

        db_song: data_models.Song = data_models.Song(
            id=song.id,
            name=song.title,
            isrc=song.isrc,
            length=song.length,
            tracksort=song.tracksort,
            genre=song.genre
        ).use(self.database)

        self.db_objects[data_models.Song].append(db_song)
        self.added_song_ids[song.id] = db_song

        for source in song.source_list:
            self.add_source(source=source, connected_to=db_song)

        for target in [song.target]:
            self.add_target(target, db_song)

        for main_artist in song.main_artist_collection:
            db_song_artist = data_models.SongArtist(
                song=db_song,
                artist=self.add_artist(main_artist),
                is_feature=False
            )

        for feature_artist in song.feature_artist_collection:
            db_song_artist = data_models.SongArtist(
                song=db_song,
                artist=self.add_artist(feature_artist),
                is_feature=True
            )

        for album in [song.album]:
            db_album_song = data_models.AlbumSong(
                song=db_song,
                album=self.add_album(album)
            )

        return db_song

    def add_album(self, album: objects.Album) -> Optional[data_models.Album]:
        """
        Add an album object to the session

        Args:
        album: An instance of the Album object
        """
        if album.dynamic:
            return
        if album.id in self.added_album_ids:
            return self.added_album_ids[album.id]

        db_album = data_models.Album().use(self.database)

        self.db_objects[data_models.Album].append(db_album)
        self.added_album_ids.add(album.id)

        return db_album

    def add_artist(self, artist: objects.Artist) -> Optional[data_models.Artist]:
        """
        Add an artist object to the session

        Args:
        artist: An instance of the Artist object
        """
        if artist.dynamic:
            return
        if artist.id in self.added_artist_ids:
            return self.added_artist_ids[artist.id]

        db_artist = data_models.Artist()

        self.db_objects[data_models.Artist].append(db_artist)
        self.added_artist_ids[artist.id] = db_artist

        return db_artist

    def commit(self, reset: bool = True):
        """
        Commit changes to the database
        """

        for model, model_instance_list in self.db_objects.items():
            model.Use(self.database).insert_many(model_instance_list)
        
        if reset:
            self.__init__(self.database)


if __name__ == "__main__":
    with Session(SqliteDatabase(":memory:")) as session:
        session.add_song(objects.Song(title="Hs"))