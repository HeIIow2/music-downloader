from music_kraken import objects
from music_kraken.pages import Musify


def search():
    results = Musify.search_by_query("#a Ghost Bath")
    print(results)


def fetch_artist():
    artist = objects.Artist(
        name="Ghost Bath",
        source_list=[objects.Source(objects.SourcePages.MUSIFY, "https://musify.club/artist/psychonaut-4-83193")]
    )
    
    artist = Musify.fetch_details(artist)
    print(artist.options)

if __name__ == "__main__":
    fetch_artist()
