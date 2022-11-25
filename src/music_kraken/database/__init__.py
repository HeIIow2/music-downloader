from . import (
    temp_database,
    song,
    artist,
    metadata,
    source,
    target
)

Song = song.Song
Artist = artist.Artist
Source = source.Source
Target = target.Target
Metadata = metadata.Metadata

cache = temp_database.TempDatabase()
