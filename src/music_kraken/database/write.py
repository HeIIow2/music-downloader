from typing import Union, Optional, Dict, DefaultDict, Type, List
from collections import defaultdict
import json
import traceback
from peewee import (
    SqliteDatabase,
    MySQLDatabase,
    PostgresqlDatabase,
    Model
)

from .. import objects
from . import data_models

# just a Type for type hintung. You can't do anything with it.
Database = Union[SqliteDatabase, PostgresqlDatabase, MySQLDatabase]


class WritingSession:
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
        self.added_label_ids: Dict[str] = dict()

        self.db_objects: DefaultDict[data_models.BaseModel, List[data_models.BaseModel]] = defaultdict(list)

    def __enter__(self) -> Type['WritingSession']:
        """
        Enter the context of the database session

        Args:
        database: An instance of a database connection from Peewee

        Returns:
        self: The instance of the session object
        """
        # self.__init__(database=database)
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
            title=song.title,
            isrc=song.isrc,
            length=song.length,
            tracksort=song.tracksort,
            genre=song.genre
        ).use(self.database)

        self.db_objects[data_models.Song].append(db_song)
        self.added_song_ids[song.id].append(db_song)

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
            
            self.db_objects[data_models.SongArtist].append(db_song_artist)

        for feature_artist in song.feature_artist_collection:
            db_song_artist = data_models.SongArtist(
                song=db_song,
                artist=self.add_artist(feature_artist),
                is_feature=True
            )
            
            self.db_objects[data_models.SongArtist].append(db_song_artist)

        for album in [song.album]:
            db_album_song = data_models.AlbumSong(
                song=db_song,
                album=self.add_album(album)
            )
            
            self.db_objects[data_models.AlbumSong] = db_album_song

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

        db_album = data_models.Album(
            id = album.id,
            title = album.title,
            album_status = album.album_status.value,
            album_type = album.album_type.value,
            language = album.iso_639_2_language,
            date_string = album.date.timestamp,
            date_format = album.date.timeformat,
            barcode = album.barcode,
            albumsort = album.albumsort
        ).use(self.database)

        self.db_objects[data_models.Album].append(db_album)
        self.added_album_ids.add(album.id)
        
        for source in album.source_list:
            self.add_source(source, db_album)

        for song in album.tracklist:
            db_song_album = data_models.AlbumSong(
                id = album.id,
                album = album,
                song = self.add_song(song)
            )
            
            self.db_objects[data_models.AlbumSong].append(db_song_album)

        for artist in album.artist_collection:
            db_album_artist = data_models.ArtistAlbum(
                album = album,
                artist = self.add_artist(artist)
            )
            
            self.db_objects[data_models.Artist].append(db_album_artist)

        for label in album.label_collection:
            self.db_objects[data_models.LabelAlbum].append(
                data_models.LabelAlbum(
                    label = self.add_label(label=label),
                    album = db_album
                )
            )

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

        db_artist = data_models.Artist(
            id = artist.id,
            name = artist.name,
            country = artist.country_string,
            formed_in_date = artist.formed_in.timestamp,
            formed_in_format = artist.formed_in.timestamp,
            general_genre = artist.general_genre
        )

        self.db_objects[data_models.Artist].append(db_artist)
        self.added_artist_ids[artist.id] = db_artist
        
        for source in artist.source_list:
            self.add_source(source, db_artist)
        
        for album in artist.main_albums:
            db_album_artist = data_models.ArtistAlbum(
                artist = artist,
                album = self.add_album(album)
            )
            
            self.db_objects[data_models.ArtistAlbum].append(db_album_artist)
            
        for song in artist.feature_songs:
            db_artist_song = data_models.SongArtist(
                artist = artist,
                song = self.add_song(song),
                is_feature = True
            )
            
            self.db_objects[data_models.SongArtist].append(db_artist_song)

        for label in artist.label_collection:
            self.db_objects[data_models.LabelArtist].append(
                data_models.LabelArtist(
                    artist = db_artist,
                    label = self.add_label(label=label)
                )
            )

        return db_artist

    def add_label(self, label: objects.Label) -> Optional[data_models.Label]:
        if label.dynamic:
            return
        if label.id in self.added_label_ids:
            return self.added_label_ids[label.id]
        
        db_label = data_models.Label(
            id = label.id,
            name = label.name,
            additional_arguments = json.dumps(label.additional_arguments)
        )
        
        self.db_objects[data_models.Label]
        self.add_label[label.id] = db_label
        
        for album in label.album_collection:
            self.db_objects[data_models.LabelAlbum].append(
                data_models.LabelAlbum(
                    album = self.add_album(album=album),
                    label = db_label
                )
            )
            
        for artist in label.current_artist_collection:
            self.db_objects[data_models.LabelArtist].append(
                artist = self.add_artist(artist=artist),
                label = db_label
            )
        
        return db_label

    def commit(self, reset: bool = True):
        """
        Commit changes to the database
        """

        for model, model_instance_list in self.db_objects.items():
            model.Use(self.database).insert_many(model_instance_list)
        
        if reset:
            self.__init__(self.database)


if __name__ == "__main__":
    with WritingSession(SqliteDatabase(":memory:")) as session:
        session.add_song(objects.Song(title="Hs"))