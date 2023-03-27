from music_kraken import objects
from music_kraken.pages import Musify


def search():
    results = Musify.search_by_query("#a Ghost Bath")
    print(results)


def fetch_artist():
    artist = objects.Artist(
        source_list=[objects.Source(objects.SourcePages.MUSIFY, "https://musify.club/artist/psychonaut-4-83193")]
    )

    artist = Musify.fetch_details(artist)
    print(artist.options)


def fetch_album():
    album = objects.Album(
        source_list=[objects.Source(objects.SourcePages.MUSIFY,
                                    "https://musify.club/release/linkin-park-hybrid-theory-2000-188")]
    )

    album: objects.Album = Musify.fetch_details(album)
    print(album.options)

    song: objects.Song
    for artist in album.artist_collection:
        print(artist.id, artist.name)
    for song in album.song_collection:
        for artist in song.main_artist_collection:
            print(artist.id, artist.name)

if __name__ == "__main__":
    search()
