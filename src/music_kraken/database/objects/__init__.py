from . import (
    song,
    metadata,
    source
)

ID3_MAPPING = metadata.Mapping
ID3Timestamp = metadata.ID3Timestamp

source_types = source.source_types

Song = song.Song
Artist = song.Artist
Source = source.Source
Target = song.Target
Metadata = song.Metadata
Lyrics = song.Lyrics

Album = song.Album
