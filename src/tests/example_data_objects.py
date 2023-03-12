import pycountry
import unittest
import sys
import os

# Add the parent directory of the src package to the Python module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from music_kraken import objects

class TestSong(unittest.TestCase):

    def setUp(self):
        self.song = objects.Song(
            genre="HS Core",
            title="Vein Deep in the Solution",
            length=666,
            isrc="US-S1Z-99-00001",
            tracksort=2,
            target=[
                objects.Target(file="song.mp3", path="example")
            ],
            lyrics_list=[
                objects.Lyrics(
                    text="these are some depressive lyrics", language="en"),
                objects.Lyrics(
                    text="Dies sind depressive Lyrics", language="de")
            ],
            source_list=[
                objects.Source(objects.SourcePages.YOUTUBE,
                               "https://youtu.be/dfnsdajlhkjhsd"),
                objects.Source(objects.SourcePages.MUSIFY,
                               "https://ln.topdf.de/Music-Kraken/")
            ],
            album_list=[
                objects.Album(
                    title="One Final Action",
                    date=objects.ID3Timestamp(year=1986, month=3, day=1),
                    language=pycountry.languages.get(alpha_2="en"),
                    label_list=[
                        objects.Label(name="an album label")
                    ],
                    source_list=[
                        objects.Source(objects.SourcePages.ENCYCLOPAEDIA_METALLUM,
                                       "https://www.metal-archives.com/albums/I%27m_in_a_Coffin/One_Final_Action/207614")
                    ]
                ),
            ],
            main_artist_list=[
                objects.Artist(
                    name="I'm in a coffin",
                    source_list=[
                        objects.Source(
                            objects.SourcePages.ENCYCLOPAEDIA_METALLUM,
                            "https://www.metal-archives.com/bands/I%27m_in_a_Coffin/127727"
                        )
                    ]
                ),
                objects.Artist(name="some_split_artist")
            ],
            feature_artist_list=[
                objects.Artist(
                    name="Ruffiction",
                    label_list=[
                        objects.Label(name="Ruffiction Productions")
                    ]
                )
            ],
        )

    def test_song_genre(self):
        self.assertEqual(self.song.genre, "HS Core")

    def test_song_title(self):
        self.assertEqual(self.song.title, "Vein Deep in the Solution")

    def test_song_length(self):
        self.assertEqual(self.song.length, 666)

    def test_song_isrc(self):
        self.assertEqual(self.song.isrc, "US-S1Z-99-00001")

    def test_song_tracksort(self):
        self.assertEqual(self.song.tracksort, 2)

    def test_song_target(self):
        self.assertEqual(self.song.target[0].file, "song.mp3")
        self.assertEqual(self.song.target[0].path, "example")

    def test_song_lyrics(self):
        self.assertEqual(len(self.song.lyrics_list), 2)
        self.assertEqual(
            self.song.lyrics_list[0].text, "these are some depressive lyrics")
        self.assertEqual(self.song.lyrics_list[0].language, "en")
        self.assertEqual(
            self.song.lyrics_list[1].text, "Dies sind depressive Lyrics")
        self.assertEqual(self.song.lyrics_list[1].language, "de")

    def test_song_source(self):
        self.assertEqual(len(self.song.source_list), 2)
        self.assertEqual(
            self.song.source_list[0].page, objects.SourcePages.YOUTUBE)
        self.assertEqual(
            self.song.source_list[0].url, "https://youtu.be/dfnsdajlhkjhsd")
        self.assertEqual(
            self.song.source_list[1].page, objects.SourcePages.MUSIFY)

"""
print(song.option_string)
for album in song.album_collection:
    print(album.option_string)
for artist in song.main_artist_collection:
    print(artist.option_string)
"""