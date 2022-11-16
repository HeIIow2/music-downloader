# TO DO
- be able to select multiple things at once (eg "0, 3, 5, 6") and then download this selection with ok
- add the file system as audio source
- add complete search of musify (scraping of artist page etc.) as last resort
- add a check if the songs truly are the same with non changebal attributes (length etc.)
- get additional ISRCs
- add Deezer as additional source
- add a config file where you should be able to set:
  - folder structure (genre/artist/release/track.mp3 eg.) 
  - proxies (maybe a boolean if tor should be enabled)
  - toggling of audio sources and sorting priorities of audio sources

# Which "Modules" do I have
## Overview
- fetching of metadata
- creating the target paths/filenames
- fetching of the download sourced
- downloading of the mp3
- fetching of the lyrics

## Naming and Structure of Modules
- utils
  - shared (equivalent to global variables and constants)
  - config
  - database
  - some static methods that are in general usefull for me
- tagging
  - song (within a class Song used to get and set the metadata of mp3 files)
- metadata
  - search
  - fetch
- something with target
- audio_source 
  - fetch_source
  - fetch_audio
  - sources
    - musify
    - youtube
- lyrics

# Wrong Audio
- Crystal F - Hanging Man

# Did not found whole release
- Crystal F - Trail Mix 2 (Vollmond)
- Crystal F - Was ist blos mit Hauke los
- Psychonaut 4 - Neurasthenia (Sweet Decadence)
