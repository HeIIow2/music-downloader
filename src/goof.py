import music_kraken
from music_kraken import (
    Song,
    Lyrics,
    Target,
    Source,
    Album,
    Artist
)

import music_kraken.database.new_database as db

def div():
    print("-"*100)


cache = music_kraken.database.new_database.Database("test.db")
cache.reset()

main_artist = Artist(
    name="I'm in a coffin"
)

split_artist = Artist(
    name="split"
)

feature_artist = Artist(
    name="Ghost"
)

album_input = Album(
    title="One Final Action"
)

song_input = Song(
    title="Vein Deep in the Solution",
    length=666,
    tracksort=2,
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
    album = album_input,
    main_artist_list = [main_artist],
    feature_artist_list = [feature_artist]
)

print(song_input)

additional_song = Song(
    title="A fcking Song",
    album=album_input
)

song_ref = song_input.reference
print(song_ref)

lyrics = Lyrics(text="these are some Lyrics that don't belong to any Song", language="en")

cache.push([album_input, song_input, lyrics, additional_song])

# getting song by song ref
div()
song_output_list = cache.pull_songs(song_ref=song_ref)
print(len(song_output_list), song_output_list, song_output_list[0].album, sep=" | ")
print("tracksort", song_output_list[0].tracksort, sep=": ")

# getting song  by album ref
div()
song_output_list = cache.pull_songs(album_ref=album_input.reference)
print(len(song_output_list), song_output_list)
for song in song_output_list:
    print(song, song.album)

# getting album
div()
album_output_list = cache.pull_albums(album_ref=album_input.reference)
album_output = album_output_list[0]
print(album_output)
for track in album_output.tracklist:
    print(track.tracksort, track)

# getting album by song
div()
album_output_list = cache.pull_albums(song_ref=song_ref)
print(album_output_list)
print("len of album ->", len(album_output_list[0]), album_output_list[0], sep=" | ")
