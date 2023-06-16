from typing import List, Optional, Type, Tuple
from urllib.parse import urlparse, urlunparse, parse_qs
from enum import Enum

import sponsorblock
from sponsorblock.errors import HTTPException, NotFoundException

from ..objects import Source, DatabaseObject, Song, Target
from .abstract import Page
from ..objects import (
    Artist,
    Source,
    SourcePages,
    Song,
    Album,
    Label,
    Target,
    FormattedText,
    ID3Timestamp
)
from ..connection import Connection
from ..utils.support_classes import DownloadResult
from ..utils.shared import YOUTUBE_LOGGER, INVIDIOUS_INSTANCE, BITRATE, ENABLE_SPONSOR_BLOCK


"""
- https://yt.artemislena.eu/api/v1/search?q=Zombiez+-+Topic&page=1&date=none&type=channel&duration=none&sort=relevance
- https://yt.artemislena.eu/api/v1/channels/playlists/UCV0Ntl3lVR7xDXKoCU6uUXA
- https://yt.artemislena.eu/api/v1/playlists/OLAK5uy_kcUBiDv5ATbl-R20OjNaZ5G28XFanQOmM
- https://yt.artemislena.eu/api/v1/videos/SULFl39UjgY
"""


def get_invidious_url(path: str = "", params: str = "", query: str = "", fragment: str = "") -> str:
    return urlunparse((INVIDIOUS_INSTANCE.scheme, INVIDIOUS_INSTANCE.netloc, path, params, query, fragment))


class YouTubeUrlType(Enum):
    CHANNEL = "channel"
    PLAYLIST = "playlist"
    VIDEO = "watch"
    NONE = ""


class YouTubeUrl:
    """
    Artist
    https://yt.artemislena.eu/channel/UCV0Ntl3lVR7xDXKoCU6uUXA
    https://www.youtube.com/channel/UCV0Ntl3lVR7xDXKoCU6uUXA
    
    Release
    https://yt.artemislena.eu/playlist?list=OLAK5uy_nEg5joAyFjHBPwnS_ADHYtgSqAjFMQKLw
    https://www.youtube.com/playlist?list=OLAK5uy_nEg5joAyFjHBPwnS_ADHYtgSqAjFMQKLw
    
    Track
    https://yt.artemislena.eu/watch?v=SULFl39UjgY&list=OLAK5uy_nEg5joAyFjHBPwnS_ADHYtgSqAjFMQKLw&index=1
    https://www.youtube.com/watch?v=SULFl39UjgY
    """
    
    def __init__(self, url: str) -> None:
        """
        Raises Index exception for wrong url, and value error for not found enum type
        """
        self.id = ""
        parsed = urlparse(url=url)
        
        self.url_type: YouTubeUrlType
        
        type_frag_list = parsed.path.split("/")
        if len(type_frag_list) < 2:
            self.url_type = YouTubeUrlType.NONE
        else:
            try:
                self.url_type = YouTubeUrlType(type_frag_list[1].strip())
            except ValueError:
                self.url_type = YouTubeUrlType.NONE
                
        if self.url_type == YouTubeUrlType.CHANNEL:
            if len(type_frag_list) < 3:
                self.couldnt_find_id(url)
            else:
                self.id = type_frag_list[2]
        
        elif self.url_type == YouTubeUrlType.PLAYLIST:
            query_stuff = parse_qs(parsed.query)
            if "list" not in query_stuff:
                self.couldnt_find_id(url)
            else:
                self.id = query_stuff["list"][0]
        
        elif self.url_type == YouTubeUrlType.VIDEO:
            query_stuff = parse_qs(parsed.query)
            if "v" not in query_stuff:
                self.couldnt_find_id(url)
            else:
                self.id = query_stuff["v"][0]
            
        
    def couldnt_find_id(self, url: str):
        YOUTUBE_LOGGER.warning(f"The id is missing: {url}")
        self.url_type = YouTubeUrlType.NONE
        
    @property
    def api(self) -> str:
        if self.url_type == YouTubeUrlType.CHANNEL:
            return get_invidious_url(path=f"/api/v1/channels/playlists/{self.id}")
        
        if self.url_type == YouTubeUrlType.PLAYLIST:
            return get_invidious_url(path=f"/api/v1/playlists/{id}")
        
        if self.url_type == YouTubeUrlType.VIDEO:
            return get_invidious_url(path=f"/api/v1/videos/{self.id}")
        
        return get_invidious_url()
            
    @property
    def normal(self) -> str:
        if self.url_type.CHANNEL:
            return get_invidious_url(path=f"/channel/{self.id}")
        
        if self.url_type.PLAYLIST:
            return get_invidious_url(path="/playlist", query=f"list={self.id}")
        
        if self.url_type.VIDEO:
            return get_invidious_url(path="/watch", query=f"v={self.id}")


class YouTube(Page):
    # CHANGE
    SOURCE_TYPE = SourcePages.YOUTUBE
    LOGGER = YOUTUBE_LOGGER

    NO_ADDITIONAL_DATA_FROM_SONG = True

    def __init__(self, *args, **kwargs):
        self.connection: Connection = Connection(
            host=get_invidious_url(),
            logger=self.LOGGER
        )

        self.download_connection: Connection = Connection(
            host="https://www.youtube.com/",
            logger=self.LOGGER
        )
        
        # the stuff with the connection is, to ensure sponsorblock uses the proxies, my programm does
        _sponsorblock_connection: Connection = Connection(host="https://sponsor.ajay.app/")
        self.sponsorblock_client = sponsorblock.Client(session=_sponsorblock_connection.session)

        super().__init__(*args, **kwargs)

    def get_source_type(self, source: Source) -> Optional[Type[DatabaseObject]]:
        _url_type = {
            YouTubeUrlType.CHANNEL: Artist,
            YouTubeUrlType.PLAYLIST: Album,
            YouTubeUrlType.VIDEO: Song,
        }
        
        parsed = YouTubeUrl(source.url)
        if parsed.url_type in _url_type:
            return _url_type[parsed.url_type]

    def general_search(self, search_query: str) -> List[DatabaseObject]:
        return self.artist_search(Artist(name=search_query, dynamic=True))
    
    def _json_to_artist(self, artist_json: dict) -> Artist:#
        return Artist(
            name=artist_json["author"].replace(" - Topic", ""),
            source_list=[
                Source(self.SOURCE_TYPE, get_invidious_url(path=artist_json["authorUrl"]))
            ]
        )

    def artist_search(self, artist: Artist) -> List[Artist]:
        # https://yt.artemislena.eu/api/v1/search?q=Zombiez+-+Topic&page=1&date=none&type=channel&duration=none&sort=relevance
        endpoint = get_invidious_url(path="/api/v1/search", query=f"q={artist.name.replace(' ', '+')}+-+Topic&page=1&date=none&type=channel&duration=none&sort=relevance")
        
        artist_list = []
        
        r = self.connection.get(endpoint)
        if r is None:
            return []

        for search_result in r.json():
            if search_result["type"] != "channel":
                continue
            author: str = search_result["author"]
            if not author.endswith(" - Topic"):
                continue
            
            artist_list.append(self._json_to_artist(search_result))
            
        return artist_list

    def _fetch_song_from_id(self, youtube_id: str) -> Tuple[Song, Optional[int]]:
        # https://yt.artemislena.eu/api/v1/videos/SULFl39UjgY
        r = self.connection.get(get_invidious_url(path=f"/api/v1/videos/{youtube_id}"))
        if r is None:
            return Song(), None

        data = r.json()
        if data["genre"] != "Music":
            self.LOGGER.warning(f"Genre has to be music, trying anyways")

        title = data["title"]
        license_str = None

        artist_list: List[Artist] = []

        _author: str = data["author"]
        if _author.endswith(" - Topic"):
            artist_list.append(Artist(
                name=_author.replace(" - Topic", ""),
                source_list=[Source(
                    self.SOURCE_TYPE, get_invidious_url(path=f"/channel/{data['authorId']}")
                )]
            ))

        else:
            for music_track in data.get("musicTracks", []):
                title = music_track["song"]
                license_str = music_track["license"]

                for artist_name in music_track["artist"].split(" x "):
                    artist_list.append(Artist(name=artist_name))

        return Song(
            title=title,
            source_list=[Source(
                self.SOURCE_TYPE, get_invidious_url(path="/watch", query=f"v={data['videoId']}")
            )],
            notes=FormattedText(html=data["descriptionHtml"] + f"\n<p>{license_str}</ p>" ),
            main_artist_list=artist_list
        ), int(data["published"])

    def fetch_song(self, source: Source, stop_at_level: int = 1) -> Song:
        parsed = YouTubeUrl(source.url)
        if parsed.url_type != YouTubeUrlType.VIDEO:
            return Song()

        song, _ = self._fetch_song_from_id(parsed.id)
        return song

    def fetch_album(self, source: Source, stop_at_level: int = 1) -> Album:
        parsed = YouTubeUrl(source.url)
        if parsed.url_type != YouTubeUrlType.PLAYLIST:
            return Album()

        title = None
        source_list = [source]
        notes = None
        song_list = []

        # https://yt.artemislena.eu/api/v1/playlists/OLAK5uy_kcUBiDv5ATbl-R20OjNaZ5G28XFanQOmM
        r = self.connection.get(get_invidious_url(path=f"/api/v1/playlists/{parsed.id}"))
        if r is None:
            return Album()

        data = r.json()
        if data["type"] != "playlist":
            return Album()

        title = data["title"]
        notes = FormattedText(html=data["descriptionHtml"])

        timestamps: List[int] = []

        """
        TODO
        fetch the song and don't get it from there
        """
        for video in data["videos"]:
            other_song = Song(
                source_list=[
                    Source(
                        self.SOURCE_TYPE, get_invidious_url(path="/watch", query=f"v={video['videoId']}")
                    )
                ],
                tracksort=video["index"]+1
            )

            song, utc_timestamp = self._fetch_song_from_id(video["videoId"])
            song.merge(other_song)

            if utc_timestamp is not None:
                timestamps.append(utc_timestamp)
            song_list.append(song)

        return Album(
            title=title,
            source_list=source_list,
            notes=notes,
            song_list=song_list,
            date=ID3Timestamp.fromtimestamp(round(sum(timestamps) / len(timestamps)))
        )

    def fetch_artist(self, source: Source, stop_at_level: int = 1) -> Artist:
        parsed = YouTubeUrl(source.url)
        if parsed.url_type != YouTubeUrlType.CHANNEL:
            return Artist(source_list=[source])
        
        artist_name = None
        album_list = []
        
        # playlist
        # https://yt.artemislena.eu/api/v1/channels/playlists/UCV0Ntl3lVR7xDXKoCU6uUXA
        r = self.connection.get(get_invidious_url(f"/api/v1/channels/playlists/{parsed.id}"))
        if r is None:
            return Artist()

        for playlist_json in r.json()["playlists"]:
            if playlist_json["type"] != "playlist":
                continue
            
            artist_name = playlist_json["author"].replace(" - Topic", "")
            
            # /playlist?list=OLAK5uy_nbvQeskr8nbIuzeLxoceNLuCL_KjAmzVw
            album_list.append(Album(
                title=playlist_json["title"],
                source_list=[Source(
                    self.SOURCE_TYPE, get_invidious_url(path="/playlist", query=f"list={playlist_json['playlistId']}")
                )],
                artist_list=[Artist(
                    name=artist_name,
                    source_list=[
                        Source(self.SOURCE_TYPE, get_invidious_url(path=playlist_json["authorUrl"]))
                    ]
                )]
            ))
        
        return Artist(name=artist_name, main_album_list=album_list, source_list=[source])

    def download_song_to_target(self, source: Source, target: Target, desc: str = None) -> DownloadResult:
        """
        1. getting the optimal source
        Only audio sources allowed
        not a bitrate that is smaller than the selected bitrate, but not one that is wayyy huger

        2. download it

        :param source:
        :param target:
        :param desc:
        :return:
        """
        r = self.connection.get(YouTubeUrl(source.url).api)
        if r is None:
            return DownloadResult(error_message="Api didn't even respond, maybe try another invidious Instance")

        audio_format = None
        best_bitrate = 0

        for possible_format in r.json()["adaptiveFormats"]:
            format_type: str = possible_format["type"]
            if not format_type.startswith("audio"):
                continue

            bitrate = int(possible_format.get("bitrate", 0))

            if bitrate >= BITRATE:
                best_bitrate = bitrate
                audio_format = possible_format
                break

            if bitrate > best_bitrate:
                best_bitrate = bitrate
                audio_format = possible_format

        if audio_format is None:
            return DownloadResult(error_message="Couldn't find the download link.")

        endpoint = audio_format["url"]

        self.download_connection.stream_into(endpoint, target, description=desc, raw_url=True)

        if self.download_connection.get(endpoint, stream=True, raw_url=True):
            return DownloadResult(total=1)
        return DownloadResult(error_message=f"Streaming to the file went wrong: {endpoint}, {str(target.file_path)}")

    def get_skip_intervals(self, song: Song, source: Source) -> List[Tuple[float, float]]:
        if not ENABLE_SPONSOR_BLOCK:
            return []
        
        parsed = YouTubeUrl(source.url)
        if parsed.url_type != YouTubeUrlType.VIDEO:
            self.LOGGER.warning(f"{source.url} is no video url.")
            return []
        
        segments = []
        try:
            segments = self.sponsorblock_client.get_skip_segments(parsed.id)
        except NotFoundException:
            self.LOGGER.debug(f"No sponsor found for the video {parsed.id}.")
        except HTTPException as e:
            self.LOGGER.warning(f"{e}")

        return [(segment.start, segment.end) for segment in segments]
