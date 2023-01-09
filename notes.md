# TO DO
- Create a super class for audio_source, from which yet to come classes like Musify or Youtube inherit.
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
- target
- audio_source 
  - fetch_source
  - fetch_audio
  - sources
    - musify
    - youtube
- lyrics
  - lyrics
  - genius (will eventually be moved in a folder with lyric sources)

# Wrong Audio
- Crystal F - Hanging Man

# Did not found whole release
- Crystal F - Trail Mix 2 (Vollmond)
- Crystal F - Was ist blos mit Hauke los
- Psychonaut 4 - Neurasthenia (Sweet Decadence)

# Audio Formats

[Wikipedia](https://en.wikipedia.org/wiki/Audio_file_format)

> It is important to distinguish between the audio coding format, the container containing the raw audio data, and an audio codec. 

## audio coding format

[Wikipedia](https://en.wikipedia.org/wiki/Audio_coding_format)

The audio coding format is a format, which tries to store audio in a minimal space, while still allowing a decent quality.

There are two types:
 1. lossless compression
 2. lossy compression

## container

[Wikipedia](https://en.wikipedia.org/wiki/Container_format)

## audio codec

[Wikipedia](https://en.wikipedia.org/wiki/Audio_codec)

The audio codec is simply software/hardware, to convert audio from an [audio coding format](#audio-coding-format) to playable audio and vice versa.
