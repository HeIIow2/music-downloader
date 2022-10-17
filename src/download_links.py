from turtle import down
import pandas as pd
import requests

# https://musify.club/search/suggestions?term=happy days

class Download:
    def __init__(self, metadata_csv: str = ".cache.csv", session: requests.Session = requests.Session()) -> None:
        self.session = session
        self.session.headers = {
            "Connection": "keep-alive",
            "Referer": "https://musify.club/"
        }

        self.metadata = pd.read_csv(metadata_csv, index_col=0)
        print(self.metadata)

        self.check_musify()

    def check_musify_track(self, row):
        artist = row['artist']
        track = row['title']

        url = f"https://musify.club/search/suggestions?term={track}"

        r = self.session.get(url=url)
        if r.status_code == 200:
            autocomplete = r.json()
            for row in autocomplete:
                print(artist, row['label'], artist in row['label'])
                if artist in row['label']:
                    print(row)
                    break

    def check_musify(self):
        for idx, row in self.metadata.iterrows():
            url = self.check_musify_track(row)
            break
            

if __name__ == "__main__":
    download = Download()
