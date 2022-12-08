import music_kraken
from music_kraken import (
    Song,
    Lyrics,
    Target,
    Source,
    Album
)

import music_kraken.database.new_database as db


cache = music_kraken.database.new_database.Database("test.db")
cache.reset()

album_input = Album(
    title="One Final Action"
)

song_input = Song(
    title="Vein Deep in the Solution",
    album_name=album_input.title,
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
    ],
    album_ref=album_input.reference
)

additional_song = Song(
    title="A fcking Song",
    album_ref=album_input.reference
)

song_ref = song_input.reference
print(song_ref)

lyrics = Lyrics(text="these are some Lyrics that don't belong to any Song", language="en")

cache.push([album_input, song_input, lyrics, additional_song])

# getting song by song ref
song_output_list = cache.pull_songs(song_ref=song_ref)
print(len(song_output_list), song_output_list)
# song_output = song_output_list[0]
# print(song_output)
# print("album id", song_output.album_ref)

# getting song  by album ref
song_output_list = cache.pull_songs(album_ref=album_input.reference)
print(len(song_output_list), song_output_list)

# getting album
album_output_list = cache.pull_albums(album_ref=album_input.ref)
print(album_output_list[0])
