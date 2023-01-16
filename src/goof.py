import music_kraken
from music_kraken import (
    Song,
    Lyrics,
    Target,
    Source,
    Album,
    Artist,
    ID3Timestamp
)

from music_kraken.tagging import (
    AudioMetadata,
    write_metadata,
    write_many_metadata
)

import music_kraken.database.new_database as db

import pycountry


def div(msg: str = ""):
    print("-" * 50 + msg + "-" * 50)


cache = music_kraken.database.new_database.Database("test.db")
cache.reset()

main_artist = Artist(
    name="I'm in a coffin"
)

artist_ref = main_artist.reference

split_artist = Artist(
    name="split"
)

feature_artist = Artist(
    name="Ghost"
)

album_input = Album(
    title="One Final Action",
    date=ID3Timestamp(year=1986, month=3, day=1),
    language=pycountry.languages.get(alpha_2="en"),
    label="cum productions"
)
album_input.artists = [
    main_artist,
    split_artist
]

song_input = Song(
    genre="HS Core",
    title="Vein Deep in the Solution",
    length=666,
    isrc="US-S1Z-99-00001",
    tracksort=2,
    target=Target(file="song.mp3", path="~/Music"),
    lyrics=[
        Lyrics(text="these are some depressive lyrics", language="en"),
        Lyrics(text="test", language="en")
    ],
    sources=[
        Source(src="youtube", url="https://youtu.be/dfnsdajlhkjhsd"),
        Source(src="musify", url="https://ln.topdf.de/Music-Kraken/")
    ],
    album=album_input,
    main_artist_list=[main_artist],
    feature_artist_list=[feature_artist],
)

other_song = Song(
    title="this is just another song",
    main_artist_list=[feature_artist],
    feature_artist_list=[main_artist]
)

print(song_input)

additional_song = Song(
    title="A fcking Song",
    album=album_input
)

song_ref = song_input.reference
print(song_ref)

lyrics = Lyrics(text="these are some Lyrics that don't belong to any Song", language="en")

cache.push([album_input, song_input, lyrics, additional_song, other_song])

# getting song by song ref
div()
song_output_list = cache.pull_songs(song_ref=song_ref)
print(len(song_output_list), song_output_list, song_output_list[0].album, sep=" | ")
song = song_output_list[0]
print("tracksort", song_output_list[0].tracksort, sep=": ")
print("ID3", dict(song.metadata))
print(str(song_output_list[0].metadata))
print("--src--")
for source in song.sources:
    print(source)

# try writing metadata
write_metadata(song)

exit()

# getting song  by album ref
div()
song_output_list = cache.pull_songs(album_ref=album_input.reference)
print(len(song_output_list), song_output_list)
for song in song_output_list:
    print(song, song.album)

# getting album
div("album")
album_output_list = cache.pull_albums(album_ref=album_input.reference)
album_output = album_output_list[0]
print(album_output)
print(f"--tracklist-{len(album_output)}--")
for track in album_output.tracklist:
    print(track.tracksort, track)
print("--artist--")
for artist in album_output.artists:
    print(artist)

# getting album by song
div()
album_output_list = cache.pull_albums(song_ref=song_ref)
print(album_output_list)
print("len of album ->", len(album_output_list[0]), album_output_list[0], sep=" | ")

# get artist
div("artist")
artist_output = cache.pull_artists(artist_ref=artist_ref)[0]
print(artist_output)

print("---static---")
print("albums", artist_output.main_albums)
print("main_s", artist_output.main_songs)
print("feat_s", artist_output.feature_songs)

print("---dynamic---")
print("discography", artist_output.discography)
print("songs", artist_output.songs, artist_output.songs.tracklist)
print("features", artist_output.features, artist_output.features.tracklist)
