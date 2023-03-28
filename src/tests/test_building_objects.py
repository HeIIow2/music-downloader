from mutagen import id3
import pycountry
import unittest
import sys
import os
from pathlib import Path

# Add the parent directory of the src package to the Python module search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from music_kraken import objects


class TestSong(unittest.TestCase):

    def setUp(self):
        self.album_list = [
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
            ]
        
        self.artist_list = []
        
        self.main_artist_list=[
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
        ]
        feature_artist_list=[
                objects.Artist(
                    name="Ruffiction",
                    label_list=[
                        objects.Label(name="Ruffiction Productions")
                    ]
                )
            ]
        
        self.artist_list.extend(self.main_artist_list)
        self.artist_list.extend(feature_artist_list)
        
        self.song = objects.Song(
            genre="HS Core",
            title="Vein Deep in the Solution",
            length=666,
            isrc="US-S1Z-99-00001",
            tracksort=2,
            target_list=[
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
            album_list=self.album_list,
            main_artist_list=self.main_artist_list,
            feature_artist_list=feature_artist_list,
        )
        
        self.song.compile()

    def test_album(self):
        for artist in self.song.main_artist_collection:
            for artist_album in artist.main_album_collection:
                self.assertIn(artist_album, self.song.album_collection)
    
    def test_artist(self):
        for album in self.song.album_collection:
            for album_artist in album.artist_collection:
                self.assertIn(album_artist, self.song.main_artist_collection)

