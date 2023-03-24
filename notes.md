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


[Here a comperison of audio coding formats.](https://en.wikipedia.org/wiki/Comparison_of_audio_coding_formats)

The two criterias, which NEED to be met is:
1. open source
2. the encoder as well as the player need to be free to use

## container

[Wikipedia](https://en.wikipedia.org/wiki/Container_format)

A container embeddes the metadata in a file. In this case I am interested in containers regarding audio.

### considerations

Important differences between container, that I need to consider when choosing one, *cuz I only implement this shit once*, are:
1. advanced content, meaning which fields there are, for example title, length, ...
2. popularity *(the more poppular it is, the better will be the support between different software)*
3. support for different [codec features](#audio-codec) *(older codecs might not support newer frames)*
4. overhead *(different file size with different data, though this certainly is less an issue with audio)*
5. support streaming the media

These destinctions are sorted from top to bottom.


## audio codec

[Wikipedia](https://en.wikipedia.org/wiki/Audio_codec)

The audio codec is simply software/hardware, to convert audio from an [audio coding format](#audio-coding-format) to playable audio and vice versa.

# ID3

[ID3](https://en.wikipedia.org/wiki/ID3) is a metadata container format for audio. I am going for [ID3v2.4](https://en.wikipedia.org/wiki/ID3#ID3v2)

An Application can define its own types of frames.

There are standard frames for containing cover art, BPM, copyright and license, lyrics, and arbitrary text and URL data, as well as other things.

Version 2.4 of the specification prescribes that all text fields (the fields that start with a T, except for TXXX) can contain multiple values separated by a null character. The null character varies by [character encoding](https://en.wikipedia.org/wiki/Character_encoding). 

[id3 fields docs](https://docs.puddletag.net/source/id3.html)

[forum](https://hydrogenaud.io/index.php/topic,51504.0.html)
> Hence, for the best possible compatibility I recommend writing ID3v2.3 tags in the ISO 8859 format. 

[ID3 tag mapping](https://wiki.hydrogenaud.io/index.php?title=Foobar2000:ID3_Tag_Mapping)

## Frames

A frame Name is composed from 4 capital letters $XXXX$

The first letter of text frames is $TXXX$

--- 

# TODO

 - Add pprint to the song objects
 - DOCUMENTATION
