from . import (
    temp_database,
    song
)

Song = song.Song
Artist = song.Artist
Source = song.Source
Target = song.Target
Metadata = song.Metadata
Lyrics = song.Lyrics

cache = temp_database.TempDatabase()
