from dynaconf import Dynaconf
from dynaconf import settings
from dynaconf.utils import object_merge

# from .path_manager import LOCATIONS

"""
https://www.dynaconf.com/settings_files/

This file is there to load the settings.
How I will structure this programm exactly is in the stars.

The concept is that I package a config file, with this programm, and then load it.
Then I check if there is a config file at the LOCATIONS.CONFIG_FILE, and if yes they get merged
"""

settings.happy_message = [
        "Support the artist.",
        "Star Me: https://github.com/HeIIow2/music-downloader",
        "🏳️‍⚧️🏳️‍⚧️ Trans rights are human rights. 🏳️‍⚧️🏳️‍⚧️",
        "🏳️‍⚧️🏳️‍⚧️ Trans women are women, trans men are men, and enbies are enbies. 🏳️‍⚧️🏳️‍⚧️",
        "🏴‍☠️🏴‍☠️ Unite under one flag, fck borders. 🏴‍☠️🏴‍☠️",
        "Join my Matrix Space: https://matrix.to/#/#music-kraken:matrix.org",
        "Gotta love the BPJM ;-;",
        "🏳️‍⚧️🏳️‍⚧️ Protect trans youth. 🏳️‍⚧️🏳️‍⚧️",
        "Nonstop Progressive Marxism.",
    ]


dynacont_object = Dynaconf(
    settings_files=[str(LOCATIONS.CONFIG_FILE)]
)



class Settings:
    def __init__(self) -> None:
        


