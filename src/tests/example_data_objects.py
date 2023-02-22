import pycountry

from ..music_kraken.objects import (
    Song,
    Source,
    SourcePages,
    Target,
    Lyrics,
    Album
)

"""
TODO
create enums for Album.album_status
move country from Album to Artist, and use pycountry.Countries
"""

song = Song(
    title="title",
    isrc="isrc",
    length=666,
    tracksort=1,
    genre="horrorcore",
    source_list=[
        Source(SourcePages.YOUTUBE, "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        Source(SourcePages.SPOTIFY, "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"),
        Source(SourcePages.BANDCAMP, "https://metalband.bandcamp.com/track/song1")
    ],
    target=Target(file="song.mp3", path="~/Music"),
    lyrics_list=[
        Lyrics(text="some song lyrics", language="en")
    ],
    album=Album(
        title="some album",
        label="braindead",
        album_status="official",
        language=pycountry.languages.get(alpha_2='de'),
    )
)


song1_sources = [
    Source(SourcePages.YOUTUBE, "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
    Source(SourcePages.SPOTIFY, "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"),
    Source(SourcePages.BANDCAMP, "https://metalband.bandcamp.com/track/song1")
]
