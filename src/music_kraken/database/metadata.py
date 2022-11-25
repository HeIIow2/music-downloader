from mutagen.easyid3 import EasyID3

class Metadata:
    def __init__(self) -> None:
        self.data = {}

    def get_all_metadata(self):
        return list(self.data.items())

    def __setitem__(self, item, value):
        if item in EasyID3.valid_keys.keys():
            self.data[item] = value

    def __getitem__(self, item):
        if item not in self.data:
            return None
        return self.data[item]
