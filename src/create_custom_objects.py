import music_kraken
from music_kraken import (
    Song,
    Lyrics,
    Target,
    Source,
    Album,
    Artist,
    ID3Timestamp,
    SourcePages,
    SourceTypes
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

def print_song(song_: Song):


    print("tracksort", song_.tracksort, sep=": ")
    # print("ID3", song_.metadata)
    print(str(song_.metadata))
    print("----src----")
    print("song:")
    print(song_.source_list)
    print("album:")
    print(song_.album.source_list)
    print("\n")


song = Song(
    genre="HS Core",
    title="Vein Deep in the Solution",
    length=666,
    isrc="US-S1Z-99-00001",
    tracksort=2,
    target=Target(file="song.mp3", path="~/Music"),
    lyrics=[
        Lyrics(text="these are some depressive lyrics", language="en"),
        Lyrics(text="Dies sind depressive Lyrics", language="de")
    ],
    source_list=[
        Source(SourcePages.YOUTUBE, "https://youtu.be/dfnsdajlhkjhsd"),
        Source(SourcePages.MUSIFY, "https://ln.topdf.de/Music-Kraken/")
    ],
    album=Album(
        title="One Final Action",
        date=ID3Timestamp(year=1986, month=3, day=1),
        language=pycountry.languages.get(alpha_2="en"),
        label="cum productions",
        source_list=[
            Source(SourcePages.ENCYCLOPAEDIA_METALLUM, "https://www.metal-archives.com/albums/I%27m_in_a_Coffin/One_Final_Action/207614")
        ]
    ),
    main_artist_list=[
        Artist(
            name="I'm in a coffin",
            source_list=[
                Source(SourcePages.ENCYCLOPAEDIA_METALLUM, "https://www.metal-archives.com/bands/I%27m_in_a_Coffin/127727")
            ]
        ),
        Artist(name="some_split_artist")
    ],
    feature_artist_list=[Artist(name="Ruffiction")],
)

print_song(song)

exit()

song_ref = song.reference

cache.push([song])



# getting song by song ref
div()
song_list = cache.pull_songs(song_ref=song_ref)
song_from_db = song_list[0]


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
