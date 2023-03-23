from music_kraken import objects, recurse

import pycountry


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
            label_list=[
                objects.Label(name="an album label")
            ],
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
            ],
            label_list=[
                objects.Label(name="Depressive records")
            ]
        ),
        objects.Artist(name="some_split_artist")
    ],
    feature_artist_list=[
        objects.Artist(
            name="Ruffiction",
            label_list=[
                objects.Label(name="Ruffiction Productions")
            ]
        )
    ],
)

song.compile()

print(song.options)
