import music_kraken as mk
print(mk.__file__)

"""
from music_kraken.audio_source import (
    fetch_sources,
    fetch_audios
)
print(fetch_sources)

from music_kraken.database import (
    cache
)
"""

print(mk.cache, len(mk.cache.get_tracks_without_src()))

mk.fetch_sources(mk.cache.get_tracks_without_src(), skip_existing_files=False)
mk.fetch_audios(mk.cache.get_tracks_to_download(), override_existing=True)
