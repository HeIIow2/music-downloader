from mutagen import id3
import pycountry
import unittest
import sys
import os
from pathlib import Path

# Add the parent directory of the src package to the Python module search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from music_kraken import objects

"""
Testing the Formatted text is barely possible cuz one false character and it fails.
Not worth the trouble
"""


class TestSong(unittest.TestCase):

    def setUp(self):
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
        self.assertEqual(self.song.target_collection[0].file_path, Path("example", "song.mp3"))

    def test_song_lyrics(self):
        self.assertEqual(len(self.song.lyrics_collection), 2)
        # the other stuff will be tested in the Lyrics test

    def test_song_source(self):
        self.assertEqual(len(self.song.source_collection), 2)
        # again the other stuff will be tested in dedicaded stuff


class TestAlbum(unittest.TestCase):

    def setUp(self):
        self.album = objects.Album(
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
        )

    def test_album_title(self):
        self.assertEqual(self.album.title, "One Final Action")

    def test_album_date(self):
        self.assertEqual(self.album.date.year, 1986)
        self.assertEqual(self.album.date.month, 3)
        self.assertEqual(self.album.date.day, 1)

    def test_album_language(self):
        self.assertEqual(self.album.language.alpha_2, "en")

    def test_album_label(self):
        self.assertEqual(self.album.label_collection[0].name, "an album label")

    def test_album_source(self):
        sp = self.album.source_collection.get_sources_from_page(objects.SourcePages.ENCYCLOPAEDIA_METALLUM)[0]

        self.assertEqual(
            sp.page_enum, objects.SourcePages.ENCYCLOPAEDIA_METALLUM)
        self.assertEqual(
            sp.url, "https://www.metal-archives.com/albums/I%27m_in_a_Coffin/One_Final_Action/207614")


class TestCollection(unittest.TestCase):
    def setUp(self):
        self.song_list: objects.song = [
            objects.Song(title="hasskrank"),
            objects.Song(title="HaSSkrank"),
            objects.Song(title="Suicideseason", isrc="uniqueID"),
            objects.Song(title="same isrc different title", isrc="uniqueID")
        ]
        self.unified_titels = set(song.unified_title for song in self.song_list)
        
        self.collection = objects.Collection(
            element_type=objects.Song, 
            data=self.song_list
        )
        
    def test_length(self):
        # hasskrank gets merged into HaSSkrank
        self.assertEqual(len(self.collection), 2)
        
    def test_data(self):
        """
        tests if the every unified name existed
        """
        song: objects.Song
        for song in self.collection:
            self.assertIn(song.unified_title, self.unified_titels)

    def test_appending(self):
        collection = objects.Collection(
            element_type=objects.Song
        )

        res = collection.append(self.song_list[0])
        self.assertEqual(res.was_in_collection, False)
        self.assertEqual(res.current_element, self.song_list[0])

        res = collection.append(self.song_list[1])
        self.assertEqual(res.was_in_collection, True)
        self.assertEqual(res.current_element, self.song_list[0])

        res = collection.append(self.song_list[2])
        self.assertEqual(res.was_in_collection, False)
        self.assertEqual(res.current_element, self.song_list[2])

        res = collection.append(self.song_list[3], merge_into_existing=False)
        self.assertEqual(res.was_in_collection, True)
        self.assertEqual(res.current_element, self.song_list[3])









class TestLyrics(unittest.TestCase):
    """
    TODO
    I NEED TO REWRITE LYRICS TAKING FORMATTED TEXT INSTEAD OF JUST STRINGS
    """

    def setUp(self):
        self.lyrics = objects.Lyrics(
            text="these are some depressive lyrics",
            language=pycountry.languages.get(alpha_2="en"),
            source_list=[
                objects.Source(objects.SourcePages.ENCYCLOPAEDIA_METALLUM,
                               "https://www.metal-archives.com/lyrics/I%27m_in_a_Coffin/One_Final_Action/207614"),
                objects.Source(objects.SourcePages.MUSIFY,
                               "https://www.musify.com/lyrics/I%27m_in_a_Coffin/One_Final_Action/207614")
            ]
        )

    def test_lyrics_text(self):
        self.assertEqual(self.lyrics.text, "these are some depressive lyrics")

    def test_lyrics_language(self):
        self.assertEqual(self.lyrics.language.alpha_2, "en")
    
    def test_lyrics_source(self):
        self.assertEqual(len(self.lyrics.source_collection), 2)


class TestMetadata(unittest.TestCase):
    
    
    def setUp(self):
        self.title = "some title"
        
        self.song = objects.Song(
            title=self.title
        )

    def test_song_metadata(self):
        self.assertEqual(self.song.metadata[objects.ID3Mapping.TITLE], id3.Frames[objects.ID3Mapping.TITLE.value](encoding=3, text=self.title))