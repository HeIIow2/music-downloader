# Music Kraken

![](https://github.com/HeIIow2/music-downloader/blob/master/assets/logo_cropped.jpg?raw=true)

## Installation

You can find and get this project from either [PyPI](https://pypi.org/project/music-kraken/) as Python-Package 
or simply the source code from [GitHub](https://github.com/HeIIow2/music-downloader). Note that even though
everything **SHOULD** work cross Plattform, I only tested it on Ubuntu.
If you enjoy this project, feel free to give it a Star on GitHub.

```sh
# install it with
pip install music-kraken

# and simply run it like this:
music-kraken
```

## Quick-Guide

**Genre:** First the cli asks you to input a gere you want to download to. The options it gives you (if it gives you any) are all the folders you got in the music directory. You also can just input a new one.

**What to download:** After that it prompts you for a search. Here are a couple examples how you can search:

```
> #a Psychonaut 4
searches for the artist "Psychonaut 4"

> #a Crystal F #r das Leben dannach
searches for the release (album) "das Leben dannach" by the artist "Crystal F"

> #r Death Pierce Me #t sterile nails and thunderbowels
searches for the track "sterile nails and thunderbowels" from the release "Death Pierce Me"
```

After searching with this syntax it prompts you with multiple results. You can either choose one of those by inputing its id `int` or you can search for a new query.

After you chose either an artist, a release group, a release or a track by its id, download it by inputing the string `ok`. My downloader will download it automatically for you.

---

## Programming interface

If you want to use this project, or parts from it in youre own projects from it, 
make sure to be familiar with [Python Modules](https://docs.python.org/3/tutorial/modules.html).
Further and better documentation including code examples are yet to come, so here is the rough
module structure for now. (should be up-to-date but no guarantee)

### Modules

- utils
  - shared (equivalent to global variables and constants)
  - config
  - database
  - some static methods that are in general useful for me
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

---

## Metadata

First the metadata has to be downloaded. The best api to do so is undeniably [Musicbrainz](musicbrainz.org/). This is a result of them being a website with a large Database spanning over all Genres.

### Musicbrainz

![Musicbrainz Data Scheme](https://wiki.musicbrainz.org/-/images/9/9e/pymb3-model-core.png)

To fetch from [Musicbrainz](musicbrainz.org/) we first have to know what to fetch. A good start is to get an input querry, which can be just put into the MB-Api. It then returns a list of possible artists, releases and recordings.

If the following chosen element is an artist, its discography + a couple tracks are printed, if a release is chosen, the artists + tracklist + release is outputted, If a track is chosen its artists and releases are shown.

Up to now it doesn't if the discography or tracklist is chosen.

### Metadata to fetch

I orient on which metadata to download on the keys in `mutagen.EasyID3` . Following I fetch and thus tag the MP3 with:
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

This is the **international standart release code**. With this a track can be identified 99% of the time, if it is known and the website has a search api for that. Obviously this will get important later.

## Download

Now that the metadata is downloaded and cached, download sources need to be sound, because one can't listen to metadata. Granted it would be amazing if that would be possible. 

### Musify

The quickest source to get download links from is to my knowledge [musify](https://musify.club/). Its a russian music downloading page, where many many songs are available to stream and to download. Due to me not wanting to stress the server to much, I abuse a handy feature nearly every page where you can search suff has. The autocomplete api for the search input. Those always are quite limited in the number of results it returns, but it is optimized to be quick. Thus with the http header `Connection` set to `keep-alive` the bottleneck defently is not at the speed of those requests.

For musify the endpoint is following: [https://musify.club/search/suggestions?term={title}](https://musify.club/search/suggestions?term=LornaShore) If the http headers are set correctly, then searching for example for "Lorna Shore" yields following result:

```json
[
    {
        "id":"Lorna Shore",
        "label":"Lorna Shore",
        "value":"Lorna Shore",
        "category":"Исполнители",
        "image":"https://39s.musify.club/img/68/9561484/25159224.jpg",
        "url":"/artist/lorna-shore-59611"       
    },
    {"id":"Immortal","label":"Lorna Shore - Immortal (2020)","value":"Immortal","category":"Релизы","image":"https://39s-a.musify.club/img/70/20335517/52174338.jpg","url":"/release/lorna-shore-immortal-2020-1241300"},
    {"id":"Immortal","label":"Lorna Shore - Immortal","value":"Immortal","category":"Треки","image":"","url":"/track/lorna-shore-immortal-12475071"}
]
```

This is a shortened example for the response the api gives. The results are very Limited, but it is also very efficient to parse. The steps I take are:

- call the api with the query being the track name
- parse the json response to an object
- look at how different the title and artist are on every element from the category `Треки`, translated roughly to track or release.
- If they match get the download links and cache them.

### Youtube

Herte the **isrc** plays a huge role. You probably know it, when you search on youtube for a song, and the music videos has a long intro or the first result is a live version. I don't want those in my music collection, only if the tracks are like this in the official release. Well how can you get around that?

Turns out if you search for the **isrc** on youtube the results contain the music, like it is on the official release and some japanese meme videos. The tracks I wan't just have the title of the released track, so one can just compare those two.

For searching, as well as for downloading I use the programm `youtube-dl`, which also has a programming interface for python.

There are two bottlenecks with this approach though:
1. `youtube-dl` is just slow. Actually it has to be, to not get blocked by youtube.
2. Ofthen musicbrainz just doesn't give the isrc for some songs.


## Lyrics

To get the Lyrics, I scrape them, and put those in the USLT ID3 Tags of for example mp3 files. Unfortunately some players, like the one I use, Rhythmbox don't support USLT Lyrics. So I created an Plugin for Rhythmbox. You can find it here: [https://github.com/HeIIow2/rythmbox-id3-lyrics-support](https://github.com/HeIIow2/rythmbox-id3-lyrics-support).

### Genius

For the lyrics source the page [https://genius.com/](https://genius.com/) is easily sufficient. It has most songs. Some songs are not present though, but that is fine, because the lyrics are optional anyways.
