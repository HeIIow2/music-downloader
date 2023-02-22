from . import (
    song,
    metadata,
    source,
    parents,
    formatted_text,
    album
)

MusicObject = parents.DatabaseObject

ID3Mapping = metadata.Mapping
ID3Timestamp = metadata.ID3Timestamp

SourceTypes = source.SourceTypes
SourcePages = source.SourcePages
SourceAttribute = source.SourceAttribute

Song = song.Song
Artist = song.Artist
Source = source.Source
Target = song.Target
Lyrics = song.Lyrics

AlbumType = album.AlbumType
AlbumStatus = album.AlbumStatus
Album = song.Album

FormattedText = formatted_text.FormattedText
