import music_kraken

music_kraken.clear_cache()

artist = music_kraken.Artist(
    name="I'm in a Coffin"
)

song = Song(
    title="Vein Deep in the Solution",
    release_name="One Final Action",
    target=Target(file="~/Music/genre/artist/album/song.mp3", path="~/Music/genre/artist/album"),
    metadata={
        "album": "One Final Action"
    },
    lyrics=[
        Lyrics(text="these are some depressive lyrics", language="en")
    ],
    sources=[
        Source(src="youtube", url="https://youtu.be/dfnsdajlhkjhsd")
    ]
)


print(song)
print(song.id)

# music_kraken.fetch_sources([song])
