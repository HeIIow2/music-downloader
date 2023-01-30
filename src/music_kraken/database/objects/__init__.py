from . import (
    song,
    metadata,
    source,
    parents
)

MusicObject = parents.DatabaseObject

ID3Mapping = metadata.Mapping
ID3Timestamp = metadata.ID3Timestamp

SourceTypes = source.SourceTypes
SourcePages = source.SourcePages

Song = song.Song
Artist = song.Artist
Source = source.Source
Target = song.Target
Lyrics = song.Lyrics

Album = song.Album
