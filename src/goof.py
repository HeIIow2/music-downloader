from music_kraken import (
    Song,
    Database,
    Artist
)

from music_kraken.pages import (
    EncyclopaediaMetallum
)


test_db = Database("test.db")
# test_db.reset()

def print_song(song_: Song):
    print(str(song_.metadata))
    print("----album--")
    print(song_.album)
    print("----src----")
    print("song:")
    print(song_.source_list)
    print("album:")
    print(song_.album.source_list)
    print("artist:")
    print([a.source_list for a in song_.main_artist_list])
    print([a.source_list for a in song_.feature_artist_list])
    print("\n")

def print_artist(artist: Artist):
    print(artist)
    print("---discography---")
    for album in artist.discography:
        print(album)


# only_smile = EncyclopaediaMetallum.search_by_query("only smile")
# print(EncyclopaediaMetallum.search_by_query("#a Ghost Bath"))
# print(EncyclopaediaMetallum.search_by_query("#a Ghost Bath #r Self Loather"))

songs_in_db = test_db.pull_songs()
song: Song

if len(songs_in_db) <= 0:
    print("didn't find song in db.... downloading")
    song: Song = EncyclopaediaMetallum.search_by_query("#a Ghost Bath #r Self Loather #t hide from the sun")[0]
    test_db.push_song(song)
else:
    print("found song in database")
    song = songs_in_db[0]

print_song(song)

artist = song.main_artist_list[0]
artist = EncyclopaediaMetallum.fetch_artist_details(artist)

print_artist(artist)

# print(only_smile)
