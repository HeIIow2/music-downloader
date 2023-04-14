import logging

from .base_classes import SingleAttribute, FloatAttribute, StringAttribute, IntAttribute, Section, Description, EmptyLine

# Only the formats with id3 metadata can be used
# https://www.audioranger.com/audio-formats.php
# https://web.archive.org/web/20230322234434/https://www.audioranger.com/audio-formats.php
ID3_2_FILE_FORMATS = frozenset((
    "mp3", "mp2", "mp1",    # MPEG-1                ID3.2
    "wav", "wave", "rmi",   # RIFF (including WAV)  ID3.2
    "aiff", "aif", "aifc",  # AIFF                  ID3.2
    "aac", "aacp",          # Raw AAC	            ID3.2
    "tta",                  # True Audio            ID3.2
))
_sorted_id3_2_formats = sorted(ID3_2_FILE_FORMATS)

ID3_1_FILE_FORMATS = frozenset((
    "ape",                  # Monkey's Audio        ID3.1
    "mpc", "mpp", "mp+",    # MusePack              ID3.1
    "wv",                   # WavPack               ID3.1
    "ofr", "ofs"            # OptimFrog             ID3.1
))
_sorted_id3_1_formats = sorted(ID3_1_FILE_FORMATS)


class AudioFormatAttribute(SingleAttribute):
    @property
    def object_from_value(self) -> str:
        v = self.value.strip().lower()
        if v in ID3_2_FILE_FORMATS:
            return v
        if v in ID3_1_FILE_FORMATS:
            logging.debug(f"setting audio format to a format that only supports ID3.1: {v}")
            return v

        raise ValueError(f"Invalid Audio Format: {v}")


class AudioSection(Section):
    def __init__(self):
        self.BITRATE = FloatAttribute(
            name="bitrate",
            description="Streams the audio with given bitrate [kB/s]. "
                        "Can't stream with a higher Bitrate, than the audio source provides.",
            value="125"
        )

        self.AUDIO_FORMAT = AudioFormatAttribute(name="audio_format", value="mp3", description=f"""
Music Kraken will stream the audio into this format.
You can use Audio formats which support ID3.2 and ID3.1,
but you will have cleaner Metadata using ID3.2.
ID3.2: {', '.join(_sorted_id3_2_formats)}
ID3.1: {', '.join(_sorted_id3_1_formats)}
        """.strip())

        self.DOWNLOAD_PATH = StringAttribute(
            name="download_path",
            value="{genre}/{artist}/{album_type}/{album}",
            description="The folder music kraken should put the songs into."
        )

        self.DOWNLOAD_FILE = StringAttribute(
            name="download_file",
            value="{song}.{audio_format}",
            description="The filename of the audio file."
        )

        self.DEFAULT_GENRE = StringAttribute(
            name="default_genre",
            value="Various Genre",
            description="The default value for the genre field."
        )

        self.DEFAULT_LABEL = StringAttribute(
            name="default_label",
            value="Various Labels",
            description="The Label refers to a lable that signs artists."
        )

        self.DEFAULT_ARTIST = StringAttribute(
            name="default_artist",
            value="Various Artists",
            description="You know Various Artist."
        )

        self.DEFAULT_ALBUM = StringAttribute(
            name="default_album",
            value="Various Album",
            description="This value will hopefully not be used."
        )

        self.DEFAULT_SONG = StringAttribute(
            name="default_song",
            value="Various Song",
            description="If it has to fall back to this value, something did go really wrong."
        )

        self.DEFAULT_ALBUM_TYPE = StringAttribute(
            name="default_album_type",
            value="Other",
            description="Weirdly enough I barely see this used in file systems."
        )

        self.attribute_list = [
            self.BITRATE,
            self.AUDIO_FORMAT,
            EmptyLine(),
            Description("""
There are multiple fields, you can use for the path and file name:
- genre
- label
- artist
- album
- song
- album_type
            """.strip()),
            self.DOWNLOAD_PATH,
            self.DOWNLOAD_FILE,
            self.DEFAULT_ALBUM_TYPE,
            self.DEFAULT_ARTIST,
            self.DEFAULT_GENRE,
            self.DEFAULT_LABEL,
            self.DEFAULT_SONG
        ]


AUDIO_SECTION = AudioSection()
