from . import (
    temp_database,
    old_database
)
from .. import objects

MusicObject = objects.MusicObject

ID3Timestamp = objects.ID3Timestamp
SourceTypes = objects.SourceTypes
SourcePages = objects.SourcePages
Song = objects.Song
Source = objects.Source
Target = objects.Target
Lyrics = objects.Lyrics
Album = objects.Album
Artist = objects.Artist

FormattedText = objects.FormattedText

Database = database.Database
cache = temp_database.TempDatabase()
