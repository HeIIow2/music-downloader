import sys
import os
import unittest

# Add the parent directory of the src package to the Python module search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from music_kraken import pages
from music_kraken.pages import download_center
from music_kraken.pages.download_center import page_attributes

class TestPageSelection(unittest.TestCase):
    def test_no_shady_pages(self):
        search = download_center.Download(
            exclude_shady=True
        )
        
        for page in search.pages:
            self.assertNotIn(page, page_attributes.SHADY_PAGES)
    
    def test_excluding(self):
        search = download_center.Download(
            exclude_pages=set((pages.EncyclopaediaMetallum,))
        )
        
        for page in search.pages:
            self.assertNotEqual(page, pages.EncyclopaediaMetallum)
        
        
    def test_audio_one(self):
        search = download_center.Download(
            exclude_shady=True
        )
        
        for audio_page in search.audio_pages:
            self.assertIn(audio_page, page_attributes.AUDIO_PAGES)        

    def test_audio_two(self):
        search = download_center.Download()
        
        for audio_page in search.audio_pages:
            self.assertIn(audio_page, page_attributes.AUDIO_PAGES)        

        