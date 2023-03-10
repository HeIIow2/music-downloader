from music_kraken import objects

import pycountry
import logging

logging.disable()


def div(msg: str = ""):
    print("-" * 50 + msg + "-" * 50)


def print_song(song_: objects.Song):
    print(str(song_.metadata))
    print("----album--")
    print(song_.album)
    print("----src----")
    print("song:")
    print(song_.source_list)
    print("album:")
    print(song_.album.source_list)
    print("\n")


song = objects.Song(
    genre="HS Core",
    title="Vein Deep in the Solution",
    length=666,
    isrc="US-S1Z-99-00001",
    tracksort=2,
    target=[
        objects.Target(file="song.mp3", path="example")
    ],
    lyrics_list=[
        objects.Lyrics(text="these are some depressive lyrics", language="en"),
        objects.Lyrics(text="Dies sind depressive Lyrics", language="de")
    ],
    source_list=[
        objects.Source(objects.SourcePages.YOUTUBE, "https://youtu.be/dfnsdajlhkjhsd"),
        objects.Source(objects.SourcePages.MUSIFY, "https://ln.topdf.de/Music-Kraken/")
    ],
    album_list=[
        objects.Album(
        title="One Final Action",
        date=objects.ID3Timestamp(year=1986, month=3, day=1),
        language=pycountry.languages.get(alpha_2="en"),
        label="cum productions",
        source_list=[
                objects.Source(objects.SourcePages.ENCYCLOPAEDIA_METALLUM, "https://www.metal-archives.com/albums/I%27m_in_a_Coffin/One_Final_Action/207614")
            ]
        ),
    ],
    main_artist_list=[
        objects.Artist(
            name="I'm in a coffin",
            source_list=[
                objects.Source(
                    objects.SourcePages.ENCYCLOPAEDIA_METALLUM,
                    "https://www.metal-archives.com/bands/I%27m_in_a_Coffin/127727"
                    )
            ]
        ),
        objects.Artist(name="some_split_artist")
    ],
    feature_artist_list=[objects.Artist(name="Ruffiction")],
)

print(song)

exit()

div()
song_ref = song.reference


# getting song by song ref
song_list = cache.pull_songs(song_ref=song_ref)
song_from_db = song_list[0]

print_song(song_from_db)

# try writing metadata
write_metadata(song)

# getting song  by album ref
div()