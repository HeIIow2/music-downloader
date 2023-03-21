from . import (
    song,
    metadata,
    source,
    parents,
    formatted_text,
    album,
    option,
    collection
)

MusicObject = parents.DatabaseObject

ID3Mapping = metadata.Mapping
ID3Timestamp = metadata.ID3Timestamp

Source = source.Source
SourceTypes = source.SourceTypes
SourcePages = source.SourcePages

Song = song.Song
Artist = song.Artist
Source = source.Source
Target = song.Target
Lyrics = song.Lyrics
Label = song.Label

AlbumType = album.AlbumType
AlbumStatus = album.AlbumStatus
Album = song.Album

FormattedText = formatted_text.FormattedText

Options = option.Options
Collection = collection.Collection
