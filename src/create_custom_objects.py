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
    cache
)

from music_kraken.tagging import (
    AudioMetadata,
    write_metadata,
    write_many_metadata
)

import music_kraken.database.database as db

import pycountry
import logging

logging.disable()


def div(msg: str = ""):
    print("-" * 50 + msg + "-" * 50)


cache.reset()


def print_song(song_: Song):
    print(str(song_.metadata))
    print("----album--")
    print(song_.album)
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
            Source(SourcePages.ENCYCLOPAEDIA_METALLUM,
                   "https://www.metal-archives.com/albums/I%27m_in_a_Coffin/One_Final_Action/207614")
        ]
    ),
    main_artist_list=[
        Artist(
            name="I'm in a coffin",
            source_list=[
                Source(SourcePages.ENCYCLOPAEDIA_METALLUM,
                       "https://www.metal-archives.com/bands/I%27m_in_a_Coffin/127727")
            ]
        ),
        Artist(name="some_split_artist")
    ],
    feature_artist_list=[Artist(name="Ruffiction")],
)

print_song(song)

div()
song_ref = song.reference
cache.push([song])

# getting song by song ref
song_list = cache.pull_songs(song_ref=song_ref)
song_from_db = song_list[0]

print_song(song_from_db)

# try writing metadata
write_metadata(song)

# getting song  by album ref
div()