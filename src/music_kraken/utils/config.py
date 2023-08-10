from dynaconf import Dynaconf

from .path_manager import LOCATIONS

"""
https://www.dynaconf.com/settings_files/

This file is there to load the settings.
How I will structure this programm exactly is in the stars.

The concept is that I package a config file, with this programm, and then load it.
Then I check if there is a config file at the LOCATIONS.CONFIG_FILE, and if yes they get merged
"""

settings = Dynaconf(
    settings_files=[str(LOCATIONS.CONFIG_FILE)],
)
