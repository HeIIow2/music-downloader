import music_kraken as mk
print(mk.__path__)

# if you simply wan't to run the buildin minimal cli just do this:
# mk.cli()

# SEARCH

"""
The whole programm takes the data it processes further from the cache, a sqlite database.
So bevore you can do anything, you will need to fill it with the songs you
wan't to download.
For now the base of everything is musicbrainz, so you need to get the
musicbrainz id and the type the id corresponds to (artist/release group/release/track).
To get this you first have to initialize a search object (music_kraken.metadata.metadata_search.Search).
"""

search_object = mk.metadata.metadata_search.Search()

"""
Then you need an initial "text search" to get some options you can choose from. For
this you can either specify artists releases and whatever directly with:
 - Search.search_from_text(self, artist: str = None, release_group: str = None, recording: str = None)
Or you can search with a text Querry like in the default cli:
 - Search.search_from_query(self, query: str)
"""

multiple_objects = search_object.search_from_text(artist=input("input the name of the artist: "))

"""
both possible methods return an instance of MultipleOptions. It can just be
printed or converted to a string.
"""

print(multiple_objects)

"""
After the first "text search" you can either again search again with the same function,
or you can further explore one of the options from the previous search.
For this simply call Search.choose(self, index: int).
The index represents the number in the previously returned instance of MultipleOptions. Thus
you **NEED TO BEFORHAND DO A "TEX SEARCH"**. Else it will not work.
"""

"""
All the data can be gotten from the temporary database / cache.
You can get the database object like this:
"""

cache = mk.database.temp_database.temp_database
print(cache)

"""
When fetching any song data from the cache, you will get it as Song
object (music_kraken.database.song.Song). There are multiple methods
to get different sets of Songs. The names explain the methods pretty
well:
 - get_track_metadata(id: str)
 - get_tracks_to_download()
 - get_tracks_without_src()
 - get_tracks_without_isrc()
 - get_tracks_without_filepath()

the id always is a musicbrainz id and distinct for every track
"""
