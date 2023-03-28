from music_kraken import objects
from music_kraken.pages import EncyclopaediaMetallum


def search():
    results = EncyclopaediaMetallum.search_by_query("#a Ghost Bath")
    print(results)
    print(results[0].source_collection)


def fetch_artist():
    artist = objects.Artist(
        source_list=[
            objects.Source(objects.SourcePages.MUSIFY, "https://musify.club/artist/psychonaut-4-83193"),
            objects.Source(objects.SourcePages.ENCYCLOPAEDIA_METALLUM, "https://www.metal-archives.com/bands/Ghost_Bath/3540372489")
        ]
    )

    artist: objects.Artist = EncyclopaediaMetallum.fetch_details(artist)
    print(artist.options)


def fetch_album():
    album = objects.Album(
        source_list=[objects.Source(objects.SourcePages.MUSIFY,
                                    "https://musify.club/release/linkin-park-hybrid-theory-2000-188")]
    )

    album: objects.Album = EncyclopaediaMetallum.fetch_details(album)
    print(album.options)

    song: objects.Song
    for artist in album.artist_collection:
        print(artist.id, artist.name)
    for song in album.song_collection:
        for artist in song.main_artist_collection:
            print(artist.id, artist.name)


if __name__ == "__main__":
    fetch_artist()
