from ..utils.enums import album
from . import (
    song,
    metadata,
    source,
    parents,
    formatted_text,
    option,
    collection
)

DatabaseObject = parents.DatabaseObject

Metadata = metadata.Metadata
ID3Mapping = metadata.Mapping
ID3Timestamp = metadata.ID3Timestamp

Source = source.Source

Song = song.Song
Artist = song.Artist
Source = source.Source
Target = song.Target
Lyrics = song.Lyrics
Label = song.Label

Album = song.Album

FormattedText = formatted_text.FormattedText

Options = option.Options
Collection = collection.Collection
