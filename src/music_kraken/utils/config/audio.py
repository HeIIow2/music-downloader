import logging

from .base_classes import (
    SingleAttribute,
    FloatAttribute,
    StringAttribute,
    Section,
    Description,
    EmptyLine,
    BoolAttribute,
    ListAttribute
)
from ...utils.enums.album import AlbumType
from ...utils.exception.config import SettingValueError

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
    def validate(self, value: str):
        v = self.value.strip().lower()
        if v not in ID3_1_FILE_FORMATS and v not in ID3_2_FILE_FORMATS:
            raise SettingValueError(
                setting_name=self.name,
                setting_value=value,
                rule="has to be a valid audio format, supporting id3 metadata"
            )
    
    @property
    def object_from_value(self) -> str:
        v = self.value.strip().lower()
        if v in ID3_2_FILE_FORMATS:
            return v
        if v in ID3_1_FILE_FORMATS:
            logging.debug(f"setting audio format to a format that only supports ID3.1: {v}")
            return v

        raise ValueError(f"Invalid Audio Format: {v}")


class AlbumTypeListAttribute(ListAttribute):
    def validate(self, value: str):
        try:
            AlbumType(value.strip())
        except ValueError:
            raise SettingValueError(
                setting_name=self.name,
                setting_value=value,
                rule="has to be an existing album type"
            )
    
    def single_object_from_element(self, value: str) -> AlbumType:
        return AlbumType(value)


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

        self.SORT_BY_DATE = BoolAttribute(
            name="sort_by_date",
            description="If this is set to true, it will set the albumsort attribute such that,\n"
                        "the albums are sorted by date.",
            value="true"
        )

        self.SORT_BY_ALBUM_TYPE = BoolAttribute(
            name="sort_album_by_type",
            description="If this is set to true, it will set the albumsort attribute such that,\n"
                        "the albums are put into categories before being sorted.\n"
                        "This means for example, the Studio Albums and EP's are always in front of Singles, "
                        "and Compilations are in the back.",
            value="true"
        )

        self.DOWNLOAD_PATH = StringAttribute(
            name="download_path",
            value="{genre}/{artist}/{album}",
            description="The folder music kraken should put the songs into."
        )

        self.DOWNLOAD_FILE = StringAttribute(
            name="download_file",
            value="{song}.{audio_format}",
            description="The filename of the audio file."
        )


        self.ALBUM_TYPE_BLACKLIST = AlbumTypeListAttribute(
            name="album_type_blacklist",
            description="Music Kraken ignores all albums of those types.\n"
                        "Following album types exist in the programm:\n"
                        f"{', '.join(album.value for album in AlbumType)}",
            value=[
                AlbumType.COMPILATION_ALBUM.value,
                AlbumType.LIVE_ALBUM.value,
                AlbumType.MIXTAPE.value
            ]
        )

        self.attribute_list = [
            self.BITRATE,
            self.AUDIO_FORMAT,
            EmptyLine(),
            self.SORT_BY_DATE,
            self.SORT_BY_ALBUM_TYPE,
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
            self.ALBUM_TYPE_BLACKLIST,
        ]
        super().__init__()


AUDIO_SECTION = AudioSection()
