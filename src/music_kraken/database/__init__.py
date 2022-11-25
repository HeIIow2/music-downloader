from . import (
    temp_database,
    song,
    artist,
    metadata,
    source,
    target,
    lyrics
)

Song = song.Song
Artist = artist.Artist
Source = source.Source
Target = target.Target
Metadata = metadata.Metadata
Lyrics = lyrics.Lyrics

cache = temp_database.TempDatabase()
