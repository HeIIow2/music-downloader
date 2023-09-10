from typing import TypedDict, List
from datetime import datetime
from urllib.parse import ParseResult
from logging import Logger
from pathlib import Path

from ...path_manager import LOCATIONS
from ..config import Config
from ..attributes.attribute import Attribute, EmptyLine, Description
from ..attributes.special_attributes import (
    SelectAttribute, 
    PathAttribute, 
    AudioFormatAttribute,
)

config = Config([
    Description(f"""IMPORTANT: If you modify this file, the changes for the actual setting, will be kept as is.
The changes you make to the comments, will be discarded, next time you run music-kraken. Have fun!

Latest reset: {datetime.now()}

_________           __           
\\_   ___ \\  __ __ _/  |_   ____  
/    \\  \\/ |  |  \\\\   __\\_/ __ \\ 
\\     \\____|  |  / |  |  \\  ___/ 
 \\______  /|____/  |__|   \\___  >
        \\/                    \\/ 
"""),

    Attribute(name="hasnt_yet_started", default_value=False, description="This will be set automatically, to look if it needs to run the scripts that run on start."),
    Attribute(name="bitrate", default_value=125, description="Streams the audio with given bitrate [kB/s]. Can't stream with a higher Bitrate, than the audio source provides."),
    AudioFormatAttribute(name="audio_format", default_value="mp3", description="""Music Kraken will stream the audio into this format.
You can use Audio formats which support ID3.2 and ID3.1,
but you will have cleaner Metadata using ID3.2."""),

    Attribute(name="result_history", default_value=False, description="""If enabled, you can go back to the previous results.
The consequence is a higher meory consumption, because every result is saved."""),
    Attribute(name="history_length", default_value=8, description="""You can choose how far back you can go in the result history.
The further you choose to be able to go back, the higher the memory usage.
'-1' removes the Limit entirely."""),

    EmptyLine(),

    Attribute(name="sort_by_date", default_value=True, description="If this is set to true, it will set the albumsort attribute such that,\nthe albums are sorted by date"),
    Attribute(name="sort_album_by_type", default_value=True, description="""If this is set to true, it will set the albumsort attribute such that,
the albums are put into categories before being sorted.
This means for example, the Studio Albums and EP's are always in front of Singles, and Compilations are in the back."""),
    Attribute(name="download_path", default_value="{genre}/{artist}/{album}", description="""There are multiple fields, you can use for the path and file name:
- genre
- label
- artist
- album
- song
- album_type
The folder music kraken should put the songs into."""),
    Attribute(name="download_file", default_value="{song}.{audio_format}", description="The filename of the audio file."),
    SelectAttribute(name="album_type_blacklist", default_value=[
        "Compilation Album",
        "Live Album",
        "Mixtape"
    ], options=("Studio Album", "EP (Extended Play)", "Single", "Live Album", "Compilation Album", "Mixtape", "Demo", "Other"), description="""Music Kraken ignores all albums of those types.
Following album types exist in the programm:"""),

    EmptyLine(),

    Attribute(name="proxies", default_value=[], description="This is a dictionary."),
    Attribute(name="tor", default_value=False, description="""Route ALL traffic through Tor.
If you use Tor, make sure the Tor browser is installed, and running.I can't guarantee maximum security though!"""),
    Attribute(name="tor_port", default_value=9150, description="The port, tor is listening. If tor is already working, don't change it."),

    Attribute(name="chunk_size", default_value=1024, description="Size of the chunks that are streamed.\nHere could be some room for improvement."),
    Attribute(name="show_download_errors_threshold", default_value=0.3, description="""If the percentage of failed downloads goes over this threshold,
all the error messages are shown."""),

    EmptyLine(),

    PathAttribute(name="music_directory", default_value=LOCATIONS.MUSIC_DIRECTORY, description="The directory, all the music will be downloaded to."),
    PathAttribute(name="temp_directory", default_value=LOCATIONS.TEMP_DIRECTORY, description="All temporary stuff is gonna be dumped in this directory."),
    PathAttribute(name="log_file", default_value=LOCATIONS.get_log_file("download_logs.log")),
    PathAttribute(name="ffmpeg_binary", default_value=LOCATIONS.FFMPEG_BIN, description="Set the path to the ffmpeg binary."),
    Attribute(
        name="not_a_genre_regex",
        description="These regular expressions tell music-kraken, which sub-folders of the music-directory\n"
                    "it should ignore, and not count to genres",
        default_value=[
            r'^\.'  # is hidden/starts with a "."
        ]
    ),

    EmptyLine(),

    Attribute(name="happy_messages", default_value=[
        "Support the artist.",
        "Star Me: https://github.com/HeIIow2/music-downloader",
        "🏳️‍⚧️🏳️‍⚧️ Trans rights are human rights. 🏳️‍⚧️🏳️‍⚧️",
        "🏳️‍⚧️🏳️‍⚧️ Trans women are women, trans men are men, and enbies are enbies. 🏳️‍⚧️🏳️‍⚧️",
        "🏴‍☠️🏴‍☠️ Unite under one flag, fck borders. 🏴‍☠️🏴‍☠️",
        "Join my Matrix Space: https://matrix.to/#/#music-kraken:matrix.org",
        "BPJM does cencorship.",
        "🏳️‍⚧️🏳️‍⚧️ Protect trans youth. 🏳️‍⚧️🏳️‍⚧️",
        "Klassenkampf",
        "Rise Proletarians!!"
    ], description="""Just some nice and wholesome messages.
If your mindset has traits of a [file corruption], you might not agree.
But anyways... Freedom of thought, so go ahead and change the messages."""),
    Attribute(name="id_bits", default_value=64, description="I really dunno why I even made this a setting.. Modifying this is a REALLY dumb idea."),
    Description("🏳️‍⚧️🏳️‍⚧️ Protect trans youth. 🏳️‍⚧️🏳️‍⚧️\n"),

], LOCATIONS.get_config_file("main"))


class SettingsStructure(TypedDict):
    hasnt_yet_started: bool
    result_history: bool
    history_length: int
    happy_messages: List[str]
    modify_gc: bool
    id_bits: int

    # audio
    bitrate: int
    audio_format: str
    sort_by_date: bool
    sort_album_by_type: bool
    download_path: str
    download_file: str
    album_type_blacklist: List[str]

    # connection
    proxies: List[dict[str, str]]
    tor: bool
    tor_port: int
    chunk_size: int
    show_download_errors_threshold: float

    # paths
    music_directory: Path
    temp_directory: Path
    log_file: Path
    not_a_genre_regex: List[str]
    ffmpeg_binary: Path

