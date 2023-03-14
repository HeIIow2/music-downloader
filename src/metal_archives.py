from music_kraken import objects


from music_kraken.pages import (
    EncyclopaediaMetallum
)


results = EncyclopaediaMetallum.search_by_query("#a Happy Days")

artist = results[0]
artist: objects.Artist = EncyclopaediaMetallum.fetch_details(artist)

artist.compile()
print(artist.options)
print()
