from typing import List, Union, Type
from peewee import (
    SqliteDatabase,
    PostgresqlDatabase,
    MySQLDatabase,
    Model,
    CharField,
    IntegerField,
    BooleanField,
    ForeignKeyField,
    TextField
)


class Album(Model):
    """A class representing an album in the music database."""

    title: str = CharField()
    label: str = CharField()
    album_status: str = CharField()
    language: str = CharField()
    date: str = CharField()
    date_format: str = CharField()
    country: str = CharField()
    barcode: str = CharField()
    albumsort: int = IntegerField()
    is_split: bool = BooleanField(default=False)


class Artist(Model):
    """A class representing an artist in the music database."""

    name: str = CharField()


class Song(Model):
    """A class representing a song in the music database."""

    name: str = CharField()
    isrc: str = CharField()
    length: int = IntegerField()
    tracksort: int = IntegerField()
    genre: str = CharField()
    album: ForeignKeyField = ForeignKeyField(Album, backref='songs')


class Source(Model):
    """A class representing a source of a song in the music database."""

    type: str = CharField()
    src: str = CharField()
    url: str = CharField()

    content_type: str = CharField()
    content_id: int = IntegerField()
    content: ForeignKeyField = ForeignKeyField('self', backref='content_items', null=True)

    @property
    def content_object(self) -> Union[Song, Album, Artist, None]:
        """Get the content associated with the source as an object."""
        if self.content_type == 'Song':
            return Song.get(Song.id == self.content_id)
        elif self.content_type == 'Album':
            return Album.get(Album.id == self.content_id)
        elif self.content_type == 'Artist':
            return Artist.get(Artist.id == self.content_id)
        else:
            return None

    @content_object.setter
    def content_object(self, value: Union[Song, Album, Artist]) -> None:
        """Set the content associated with the source as an object."""
        self.content_type = value.__class__.__name__
        self.content_id = value.id


class Target(Model):
    """A class representing a target of a song in the music database."""

    file: str = CharField()
    path: str = CharField()
    song = ForeignKeyField(Song, backref='targets')


class Lyrics(Model):
    """A class representing lyrics of a song in the music database."""

    text: str = TextField()
    language: str = CharField()
    song = ForeignKeyField(Song, backref='lyrics')


class SongArtist(Model):
    """A class representing the relationship between a song and an artist."""

    song: ForeignKeyField = ForeignKeyField(Song, backref='song_artists')
    artist: ForeignKeyField = ForeignKeyField(Artist, backref='song_artists')
    is_feature: bool = BooleanField(default=False)


class AlbumArtist(Model):
    """A class representing the relationship between an album and an artist."""

    album: ForeignKeyField = ForeignKeyField(Album, backref='album_artists')
    artist: ForeignKeyField = ForeignKeyField(Artist, backref='album_artists')


class Models:
    def __init__(self, database: Union[SqliteDatabase, PostgresqlDatabase, MySQLDatabase]):
        self.database: Union[SqliteDatabase, PostgresqlDatabase, MySQLDatabase] = database

    def get_obj(self, _model: Model):
        _model._meta.database = self.database
