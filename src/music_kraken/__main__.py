import music_kraken
# from .audio_source.sources.musify import Musify
from .audio_source.sources.youtube import Youtube


if __name__ == "__main__":
    music_kraken.cli()
    # Youtube.fetch_audio({'title': 'dfas', '': '', 'isrc': ''})
    # Youtube.fetch_audio({'title': 'dfas', 'url': '', 'file': 'dasf', 'isrc': ''})
