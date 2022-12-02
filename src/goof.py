import music_kraken

import music_kraken.database.new_database as db

cache = music_kraken.database.new_database.Database("test.db")
cache.reset()

artist = music_kraken.Artist(
    name="I'm in a Coffin"
)

song = music_kraken.Song(
    title="Vein Deep in the Solution",
    release="One Final Action",
    artists=[artist]
)

cache.push([artist, song])

"""
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
"""
