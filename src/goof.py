import music_kraken
from music_kraken import (
    Song,
    Lyrics,
    Target,
    Source
)

import music_kraken.database.new_database as db


cache = music_kraken.database.new_database.Database("test.db")
cache.reset()

song = Song(
    title="Vein Deep in the Solution",
    release_name="One Final Action",
    length=666,
    target=Target(file="~/Music/genre/artist/album/song.mp3", path="~/Music/genre/artist/album"),
    metadata={
        "album": "One Final Action"
    },
    lyrics=[
        Lyrics(text="these are some depressive lyrics", language="en"),
        Lyrics(text="test", language="en")
    ],
    sources=[
        Source(src="youtube", url="https://youtu.be/dfnsdajlhkjhsd"),
        Source(src="musify", url="https://ln.topdf.de/Music-Kraken/")
    ]
)

song_ref = song.reference
print(song_ref)

lyrics = Lyrics(text="these are some Lyrics that don't belong to any Song", language="en")

cache.push([song, lyrics])

cache.pull_single_song(song_ref=song_ref)
