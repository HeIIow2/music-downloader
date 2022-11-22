import music_kraken as mk
print(mk.__path__)

# mk.cli()

mk.lyrics.fetch_lyrics()
# db = mk.utils.shared.database
# if len(db.get_custom_track([])) == 0:
