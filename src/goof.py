import music_kraken

artist = music_kraken.Artist(
    name="I'm in a Coffin"
)

song = music_kraken.Song(
    title="Vein Deep in the Solution",
    release="One Final Action",
    artists=[artist]
)

print(song)

music_kraken.fetch_sources([song])
