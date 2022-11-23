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

multiple_options = search_object.search_from_text(artist=input("input the name of the artist: "))

"""
both possible methods return an instance of MultipleOptions. It can just be
printed or converted to a string.
"""

print(multiple_options)

"""
After the first "text search" you can either again search again with the same function,
or you can further explore one of the options from the previous search.
For this simply call Search.choose(self, index: int).
The index represents the number in the previously returned instance of MultipleOptions. 
The element which has been chosen with `choose(i)` will be selectend,
and can be downloaded with following steps

Thus this has to be done **after either search_from_text or search_from_query**
"""

# choosing the best matching band
multiple_options = search_object.choose(0)
# choosing the first ever release group of this band
multiple_options = search_object.choose(1)
# printing out the current options
print(multiple_options)

"""
This process can be repeated indefenetly (until you run out of memory). 
A search history is kept in the Search instance. You could go back to 
the previous search like this:

multiple_options = search.get_previous_options()
"""

# DOWNLOADING METADATA / FILLING UP THE CACHE DB

"""
If you selected the Option you want with `Search.choose(i)`, you can
finally download the metadata of either:
 - an artist (the whole discography)
 - a release group
 - a release
 - a track/recording
To download you need the selected Option Object (`music_kraken.metadata.metadata_search.Option`)
it is simply stored in Search.current_option.

If you already know what you wan't to download you can skip all the steps above and just create
a dictionary like this and use it later (*might change and break after I add multiple metadata sources which I will*):
```python
{
    'type': option_type,
    'id': musicbrainz_id
}
```
The option type is a string (I'm sorry for not making it an enum I know its a bad pratice), which can
have following values:
 - 'artist'
 - 'release_group'
 - 'release'
 - 'recording'
**PAY ATTENTION TO TYPOS, ITS CASE SENSITIVE**

The musicbrainz id is just the id of the object from musicbrainz.
"""

# in this example I will choose the previous selected option.
option_to_download = search_object.current_option
print(option_to_download)

"""
If you got the Option instance you want to download, then downloading the metadata is really straight
forward so I just show the code.
"""

# I am aware of abstrackt classes
metadata_downloader = mk.metadata.metadata_fetch.MetadataDownloader()
metadata_downloader.download({'type': option_to_download.type, 'id': option_to_download.id})

"""
This will add the requested songs to the cache database.
"""


# CACHE / TEMPORARY DATABASE
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
