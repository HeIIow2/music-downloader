import music_kraken as mk
print(mk.__file__)

mk.clear_cache()
song_list = mk.cache.get_custom_track([])
print(mk.cache, len(song_list))
id_="694bfd3c-9d2d-4d67-9bfc-cee5bf77166e"
id_="5cc28584-10c6-40e2-b6d4-6891e7e7c575"
mk.fetch_metadata(id_=id_, type_="recording")

song = mk.cache.get_track_metadata(musicbrainz_releasetrackid=id_)
print(song)
print(song.length)
mk.set_targets(genre="test")

song = mk.cache.get_track_metadata(musicbrainz_releasetrackid=id_)
mk.fetch_sources([song])
