import music_kraken
from music_kraken import pages
from music_kraken.download import Search
from music_kraken.utils.enums.source import SourcePages
from music_kraken.objects import Song, Target, Source, Album


if __name__ == "__main__":
    music_kraken.cli(genre="test", command_list=[
        # "https://musify.club/release/molchat-doma-etazhi-2018-1092949",
        # "https://musify.club/release/ghost-bath-self-loather-2021-1554266",
        "s: #a Ghost Bath",

    ])
