class Artist:
    def __init__(self, artist_data) -> None:
        self.artist_data = artist_data

        self.id = self.artist_data['id']
        self.name = self.artist_data['name']

    def __eq__(self, __o: object) -> bool:
        if type(__o) != type(self):
            return False
        return self.id == __o.id

    def __str__(self) -> str:
        return self.name

