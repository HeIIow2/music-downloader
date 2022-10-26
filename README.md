# music-downloader
This programm will first get the metadata of various songs from metadata provider like musicbrainz, and then search for download links on pages like bandcamp. Then it will download the song and edit the metadata according.

## Metadata

First the metadata has to be downloaded. The best api to do so is undeniably [Musicbrainz](musicbrainz.org/). This is a result of them being a website with a large Database spanning over all Genres.

### Musicbrainz

![Musicbrainz Data Scheme](https://wiki.musicbrainz.org/-/images/9/9e/pymb3-model-core.png)

To fetch from [Musicbrainz](musicbrainz.org/) we first have to know what to fetch. A good start is to get an input querry, which can be just put into the MB-Api. It then returns a list of possible artists, releases and recordings.

Then we can output them in the Terminal and ask for further input. Following can be inputed afterwards:

- `q` to quit
- `ok` to download
- `..` for previous options 
- `.` for current options
- `an integer` for this element

If the following chosen element is an artist, its discography + a couple tracks are outputed, if a release is chosen, the artists + tracklist + release is outputted, If a track is chosen its artists and releases are shown.

**TO DO**

- Schow always the whole tracklist of an release if it is chosen
- Show always the whole discography of an artist if it is chosen

Up to now it doesn't if the discography or tracklist is chosen.

### Metadata to fetch

I orient on which metadata to download on the keys in `mutagen.EasyID3` . Following I fatch and thus tag the MP3 with:
- title
- artist
- albumartist
- tracknumber
- albumsort can sort albums cronological
- titlesort is just set to the tracknumber to sort by track order to sort correctly
- isrc
- musicbrainz_artistid
- musicbrainz_albumid
- musicbrainz_albumartistid
- musicbrainz_albumstatus
- language
- musicbrainz_albumtype
- releasecountry
- barcode

#### albumsort/titlesort

Those Tags are for the musicplayer to not sort for Example the albums of a band alphabetically, but in another way. I set it just to chronological order

#### isrc

This is the **international standart release code**. With this a track can be identified 100% percicely all of the time, if it is known and the website has a search api for that. Obviously this will get important later.



## Download

### Musify

### Youtube
