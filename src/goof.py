import music_kraken as mk
print(mk.__file__)

song_list = mk.cache.get_custom_track([])

print(mk.cache, len(song_list))
print(song_list)

for song in song_list:
    print()
    print(song)
    print(song.json_data)
