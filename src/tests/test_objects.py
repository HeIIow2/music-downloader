
import pycountry
import unittest
import sys
import os

# Add the parent directory of the src package to the Python module search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from music_kraken import objects

from music_kraken import metadata


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
        self.collection = objects.collection.Collection(
            title="A collection",
            date=objects.ID3Timestamp(year=1986, month=3, day=1),
            language=pycountry.languages.get(alpha_2="en"),
            label_list=[
                objects.Label(name="a collection label")
            ],
            source_list=[
                objects.Source(objects.SourcePages.ENCYCLOPAEDIA_METALLUM,
                               "https://www.metal-archives.com/collections/I%27m_in_a_Coffin/One_Final_Action/207614")
            ]
        )

    def test_collection_title(self):
        self.assertEqual(self.collection, "A collection")

    def test_collection_date(self):
        self.assertEqual(self.collection.date.year, 1986)
        self.assertEqual(self.collection.date.month, 3)
        self.assertEqual(self.collection.date.day, 1)

    def test_collection_language(self):
        self.assertEqual(self.collection.language.alpha_2, "en")

    def test_collection_label(self):
        self.assertEqual(
            self.collection.label_list[0].name, "a collection label")

    def test_collection_source(self):
        self.assertEqual(
            self.collection.source_list[0].page, objects.SourcePages.ENCYCLOPAEDIA_METALLUM)
        self.assertEqual(
            self.collection.source_list[0].url, "https://www.metal-archives.com/collections/I%27m_in_a_Coffin/One_Final_Action/207614")


class TestFormattedText(unittest.TestCase):
    def setUp(self):
        self.text_markdown = objects.FormattedText(markdown="""
        # This is a test title
        This is a test paragraph
        ## This is a test subtitle
        - This is a test list item
        - This is another test list item
        This is another test paragraph
""")
        self.text_html = objects.FormattedText(html="""
        <h1>This is a test title</h1>
        <p>This is a test paragraph</p>
        <h2>This is a test subtitle</h2>
        <ul>
        <li>This is a test list item</li>
        <li>This is another test list item</li>
        </ul> 
        <p>This is another test paragraph</p>""")

        self.plaintext = objects.FormattedText(plaintext="""
This is a test title
This is a test paragraph
This is a test subtitle
- This is a test list item
- This is another test list item
This is another test paragraph""")

    def test_formatted_text_markdown_to_html(self):
        self.assertEqual(self.text_markdown.get_html(), self.text_html.html)

    def test_formatted_text_html_to_markdown(self):
        self.assertEqual(self.text_html.get_markdown(), self.text_markdown)

    def test_formatted_text_markdown_to_plaintext(self):
        self.assertEqual(self.text_markdown.get_plaintext(), self.plaintext)

    def test_formatted_text_html_to_plaintext(self):
        self.assertEqual(self.text_html.get_plaintext(), self.plaintext)


class TestLyrics(unittest.TestCase):

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
        self.assertEqual(self.lyrics.text,
                         "these are some depressive lyrics")

    def test_lyrics_language(self):
        self.assertEqual(self.lyrics.language.alpha_2, "en")
    
    def test_lyrics_source(self):
        self.assertEqual(len(self.lyrics.source_collection), 2)


class TestMetadata(unittest.TestCase):

    def setUp(self):
        self.timestamp = objects.ID3Timestamp(year=1986, month=3, day=1)
        self.metadata = objects.metadata.Metadata(id3_dict={"date": self.timestamp})

    def test_metadata_id3(self):
        self.assertEqual(self.metadata.get_id3_value("date"), self.timestamp)