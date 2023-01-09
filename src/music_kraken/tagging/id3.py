import mutagen
from mutagen.id3 import ID3

import logging


logger = logging.Logger("hs")


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
