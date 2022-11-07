import logging
import musicbrainzngs

try:
    from object_handeling import get_elem_from_obj, parse_music_brainz_date

except ModuleNotFoundError:
    from metadata.object_handeling import get_elem_from_obj, parse_music_brainz_date


mb_log = logging.getLogger("musicbrainzngs")
mb_log.setLevel(logging.WARNING)
musicbrainzngs.set_useragent("metadata receiver", "0.1", "https://github.com/HeIIow2/music-downloader")


OPTION_TYPES = ['artist', 'release_group', 'release', 'recording']

class Option:
    def __init__(self, type_: str, id: str, name: str, additional_info: str = "") -> None:
        if type_ not in OPTION_TYPES:
            raise ValueError(f"type: {type_} doesn't exist. Leagal Values: {OPTION_TYPES}")
        self.type = type_
        self.name = name
        self.id = str

        self.additional_info = additional_info

    def __repr__(self) -> str:
        type_repr = {
            'artist': 'artist\t\t',
            'release_group': 'release group\t', 
            'release': 'release\t\t', 
            'recording': 'recording\t'
        }
        return f"{type_repr[self.type]}: \"{self.name}\"{self.additional_info}"


class Search:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

        self.options_history = []

    def search_recording_from_text(self, artist: str = None, release_group: str = None, recording: str = None):
        result = musicbrainzngs.search_recordings(artist=artist, release=release_group, recording=recording)
        recording_list = get_elem_from_obj(result, ['recording-list'], return_if_none=[])
        print(recording_list[0])
        resulting_options = [Option("recording", get_elem_from_obj(recording_, ['id']), get_elem_from_obj(recording_, ['title']), additional_info=f"") for recording_ in recording_list]
        return resulting_options

    def search_release_group_from_text(self, artist: str = None, release_group: str = None):
        result = musicbrainzngs.search_release_groups(artist=artist, releasegroup=release_group)
        release_group_list = get_elem_from_obj(result, ['release-group-list'], return_if_none=[])
        
        resulting_options = [Option("release_group", get_elem_from_obj(release_group_, ['id']), get_elem_from_obj(release_group_, ['title']), additional_info=f" by {get_elem_from_obj(release_group_, ['artist-credit', 0, 'name'])}") for release_group_ in release_group_list]
        return resulting_options

    def search_artist_from_text(self, artist: str = None):
        result = musicbrainzngs.search_artists(artist=artist)
        artist_list = get_elem_from_obj(result, ['artist-list'], return_if_none=[])

        print(artist_list[0])

        resulting_options = [Option("artist", get_elem_from_obj(artist_, ['id']), get_elem_from_obj(artist_, ['name']), additional_info=f": {', '.join([i['name'] for i in get_elem_from_obj(artist_, ['tag-list'], return_if_none=[])])}") for artist_ in artist_list]
        return resulting_options


    def search_from_text(self, artist: str = None, release_group: str = None, recording: str = None):
        if artist is None and release_group is None and recording is None:
            self.logger.error("either artist, release group or recording has to be set")
            return -1

        results = []
        if recording is not None:
            results = self.search_recording_from_text(artist=artist, release_group=release_group, recording=recording)
        elif release_group is not None:
            results = self.search_release_group_from_text(artist=artist, release_group=release_group)
        else:
            results = self.search_artist_from_text(artist=artist)

        for res in results:
            print(res)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger_ = logging.getLogger("test")

    search = Search(logger=logger_)
    # search.search_from_text(artist="I Prevail")
    # search.search_from_text(artist="I Prevail", release_group="TRAUMA")
    search.search_from_text(artist="I Prevail", release_group="TRAUMA", recording="breaking down")
