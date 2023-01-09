from enum import Enum
import mutagen
from mutagen.id3 import ID3

import logging


logger = logging.Logger("hs")



class Mapping(Enum):
    DATE = "TYER"
    UNSYNCED_LYRICS = "USLT"
    TRACKNUMBER = "TRCK"
    TOTALTRACKS = "TRCK" # Stored in the same frame with TRACKNUMBER, separated by '/': e.g. '4/9'.
    TITLE = "TIT2"
    TITLESORTORDER = "TSOT"
    ENCODING_SETTINGS = "TSSE"
    SUBTITLE = "TIT3"
    SET_SUBTITLE = "TSST"
    RELEASE_DATE = "TDRL"
    RECORDING_DATES = "TXXX"
    PUBLISHER_URL = "WPUB"
    PUBLISHER = "TPUB"
    RATING = "POPM"
    PAYMEMT_URL = "WPAY"
    DISCNUMBER = "TPOS"
    MOVEMENT_COUNT = "MVIN"
    TOTALDISCS = "TPOS"
    ORIGINAL_RELEASE_DATE = "TDOR"
    ORIGINAL_ARTIST = "TOPE"
    ORIGINAL_ALBUM = "TOAL"
    INTERNET_RADIO_WEBPAGE_URL = "WORS"
    SOURCE_WEBPAGE_URL = "WOAS"
    FILE_WEBPAGE_URL = "WOAF"
    ARTIST_WEBPAGE_URL = "WOAR"
    MOVEMENT_INDEX = "MVIN"
    MOVEMENT_NAME = "MVNM"
    MEDIA_TYPE = "TMED"
    LYRICIST = "TEXT"
    WRITER = "TEXT"
    ARTIST = "TPE1"
    LANGUAGE = "TLAN"
    ITUNESCOMPILATION = "TCMP"
    ISRC = "TSRC"
    REMIXED_BY = "TPE4"
    RADIO_STATION_OWNER = "TRSO"
    RADIO_STATION = "TRSN"
    INITIAL_KEY = "TKEY"
    OWNER = "TOWN"
    ENCODED_BY = "TENC"
    COPYRIGHT_URL = "WCOP"
    COPYRIGHT = "TCOP"
    GENRE = "TCON"
    GROUPING = "TIT1"
    CONDUCTOR = "TPE3"
    COMPOSERSORTORDER = "TSOC"
    COMPOSER = "TCOM"
    COMMERCIAL_INFORMATION_URL = "WCOM"
    COMMENT = "COMM"
    BPM = "TBPM"
    ALBUM_ARTIST = "TPE2"
    BAND = "TPE2"
    ARTISTSORTORDER = "TSOP"
    ALBUM = "TALB"
    ALBUMSORTORDER = "TSOA"
    ALBUMARTISTSORTORDER = "TSO2"


class AudioMetadata:
    def __init__(self, file_location: str = None) -> None:
        self.file_location = file_location

        self.frames: ID3 = ID3()
        if self.file_location is not None:
            # try loading the data from the given file. if it doesn't succeed the frame remains empty
            try:
                self.frames.load(self.file_location)
            except mutagen.MutagenError:
                logger.warning(f"couldn't find any metadata at: \"{self.file_location}\"")

    def save(self, file_location: str = None):
        if file_location is not None:
            self.file_location = file_location

        if self.file_location is None:
            raise Exception("no file target provided to save the data to")
        self.frames.save(filething=self.file_location)


if __name__ == "__main__":
    print("called directly")
    filepath = "/home/lars/Music/deathcore/Archspire/Bleed the Future/Bleed the Future.mp3"

    audio_metadata = AudioMetadata(file_location=filepath)
    print(audio_metadata.frames.pprint())
