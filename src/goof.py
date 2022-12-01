import music_kraken

music_kraken.clear_cache()

artist = music_kraken.Artist(
    name="I'm in a Coffin"
)

song = music_kraken.Song(
    title="Vein Deep in the Solution",
    release="One Final Action",
    artists=[artist]
)

print(song)
print(song.id)

# music_kraken.fetch_sources([song])
