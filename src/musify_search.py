from music_kraken import objects
from music_kraken.pages import Musify


results = Musify.search_by_query("#a Ghost Bath")
print(results)
exit()

artist = results[0]
artist: objects.Artist = Musify.fetch_details(artist)

print(artist.options)
print()
