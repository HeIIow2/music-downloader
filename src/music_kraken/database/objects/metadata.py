from enum import Enum
from typing import List, Dict, Tuple
from mutagen import id3

from .parents import (
    ID3Metadata
)


class Mapping(Enum):
    """
    These frames belong to the id3 standart
    """
    # Textframes
    TITLE = "TIT2"
    ISRC = "TSRC"
    LENGTH = "TLEN"
    DATE = "TYER"
    TRACKNUMBER = "TRCK"
    TOTALTRACKS = "TRCK"  # Stored in the same frame with TRACKNUMBER, separated by '/': e.g. '4/9'.
    TITLESORTORDER = "TSOT"
    ENCODING_SETTINGS = "TSSE"
    SUBTITLE = "TIT3"
    SET_SUBTITLE = "TSST"
    RELEASE_DATE = "TDRL"
    RECORDING_DATES = "TXXX"
    PUBLISHER_URL = "WPUB"
    PUBLISHER = "TPUB"
    RATING = "POPM"
    DISCNUMBER = "TPOS"
    MOVEMENT_COUNT = "MVIN"
    TOTALDISCS = "TPOS"
    ORIGINAL_RELEASE_DATE = "TDOR"
    ORIGINAL_ARTIST = "TOPE"
    ORIGINAL_ALBUM = "TOAL"
    MEDIA_TYPE = "TMED"
    LYRICIST = "TEXT"
    WRITER = "TEXT"
    ARTIST = "TPE1"
    LANGUAGE = "TLAN"
    ITUNESCOMPILATION = "TCMP"
    REMIXED_BY = "TPE4"
    RADIO_STATION_OWNER = "TRSO"
    RADIO_STATION = "TRSN"
    INITIAL_KEY = "TKEY"
    OWNER = "TOWN"
    ENCODED_BY = "TENC"
    COPYRIGHT = "TCOP"
    GENRE = "TCON"
    GROUPING = "TIT1"
    CONDUCTOR = "TPE3"
    COMPOSERSORTORDER = "TSOC"
    COMPOSER = "TCOM"
    BPM = "TBPM"
    ALBUM_ARTIST = "TPE2"
    BAND = "TPE2"
    ARTISTSORTORDER = "TSOP"
    ALBUM = "TALB"
    ALBUMSORTORDER = "TSOA"
    ALBUMARTISTSORTORDER = "TSO2"

    SOURCE_WEBPAGE_URL = "WOAS"
    FILE_WEBPAGE_URL = "WOAF"
    INTERNET_RADIO_WEBPAGE_URL = "WORS"
    ARTIST_WEBPAGE_URL = "WOAR"
    COPYRIGHT_URL = "WCOP"
    COMMERCIAL_INFORMATION_URL = "WCOM"
    PAYMEMT_URL = "WPAY"

    MOVEMENT_INDEX = "MVIN"
    MOVEMENT_NAME = "MVNM"

    UNSYNCED_LYRICS = "USLT"
    COMMENT = "COMM"

    @classmethod
    def get_text_instance(cls, key: str, value: str):
        return id3.Frames[key](encoding=3, text=value)

    @classmethod
    def get_url_instance(cls, key: str, url: str):
        return id3.Frames[key](encoding=3, url=url)

    @classmethod
    def get_mutagen_instance(cls, attribute, value):
        key = attribute.value

        if key[0] == 'T':
            # a text fiel
            return cls.get_text_instance(key, value)
        if key[0] == "W":
            # an url field
            return cls.get_url_instance(key, value)


class Metadata:
    """
    Shall only be read or edited via the Song object.
    call it like a dict to read/write values
    """
    class FrameValue:
        def __init__(self, values: list, modified_by: str) -> None:
            """
            Parameters:
                values (list): the values.
            """
            pass

    def __init__(self, data: dict = {}) -> None:
        # this is pretty self-explanatory
        # the key is a 4 letter key from the id3 standards like TITL

        self.id3_attributes: Dict[str, list] = {}

        # its a null byte for the later concatenation of text frames
        self.null_byte = "\x00"

    def get_all_metadata(self):
        return list(self.id3_attributes.items())

    def __setitem__(self, key: str, value: list, override_existing: bool = True):
        if len(value) == 0:
            return
        if type(value) != list:
            raise ValueError(f"can only set attribute to list, not {type(value)}")

        if override_existing:
            new_val = []
            for elem in value:
                if elem is not None:
                    new_val.append(elem)
            if len(new_val) > 0:
                self.id3_attributes[key] = new_val
        else:
            if key not in self.id3_attributes:
                self.id3_attributes[key] = value
                return
            self.id3_attributes[key].extend(value)

    def __getitem__(self, key):
        if key not in self.id3_attributes:
            return None
        return self.id3_attributes[key]

    def add_id3_metadata_obj(self, id3_metadata: ID3Metadata, override_existing: bool = True):
        metadata_dict = id3_metadata.get_id3_dict()
        for field_enum, value in metadata_dict.items():
            self.__setitem__(field_enum.value, value, override_existing=override_existing)

    def add_many_id3_metadata_obj(self, id3_metadata_list: List[ID3Metadata], override_existing: bool = False):
        for id3_metadata in id3_metadata_list:
            self.add_id3_metadata_obj(id3_metadata, override_existing=override_existing)

    def delete_item(self, key: str):
        if key in self.id3_attributes:
            return self.id3_attributes.pop(key)

    def get_id3_value(self, key: str):
        if key not in self.id3_attributes:
            return None

        list_data = self.id3_attributes[key]

        """
        Version 2.4 of the specification prescribes that all text fields (the fields that start with a T, except for TXXX) can contain multiple values separated by a null character. 
        Thus if above conditions are met, I concatenate the list,
        else I take the first element
        """
        if key[0].upper() == "T" and key.upper() != "TXXX":
            return self.null_byte.join(list_data)

        return list_data[0]

    def get_mutagen_object(self, key: str):
        return Mapping.get_mutagen_instance(Mapping(key), self.get_id3_value(key))

    def __iter__(self):
        for key in self.id3_attributes:
            yield key, self.get_mutagen_object(key)

    def __str__(self) -> str:
        rows = []
        for key, value in self.id3_attributes.items():
            rows.append(f"{key} - {str(value)}")
        return "\n".join(rows)
