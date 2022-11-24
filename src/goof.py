import music_kraken as mk
print(mk.__file__)

from music_kraken.audio_source import (
    fetch_sources,
    fetch_audios
)
print(fetch_sources)

cache = mk.database.temp_database.temp_database
print(cache, len(cache.get_tracks_without_src()))

fetch_sources(cache.get_tracks_without_src(), skip_existing_files=False)
fetch_audios(cache.get_tracks_to_download(), override_existing=True)
