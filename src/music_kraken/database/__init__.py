from . import (
    temp_database,
    song
)

Song = song.Song
Artist = song.Artist
Source = song.Source
Target = song.Target
Metadata = song.Metadata

cache = temp_database.TempDatabase()
