class Artist:
    def __init__(self, artist_data) -> None:
        self.artist_data

        self.id = self.artist_data['id']
        self.name = self.artist_data['name']


class Song:
    def __init__(self, json_response) -> None:
        self.json_data = json_response

        self.artists = [Artist(a) for a in self.json_data['artists']]
        """
        artist
        source
        """

    def get_artist_names(self):
        return [a.name for a in self.aritsts]

    def __getitem__(self, item):
        print(item)
        print(self.json_data)
        if item not in self.json_data:
            return None
        return self.json_data[item]

    def __setitem__(self, item, value):
        print(item, value)
        self.json_data[item] = value
