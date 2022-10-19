import os.path
from tkinter.messagebox import NO


import musicbrainzngs
import pandas as pd

musicbrainzngs.set_useragent("metadata receiver", "0.1", "https://github.com/HeIIow2/music-downloader")

KNOWN_KIND_OF_OPTIONS = ["artist", "release", "track"]


class Search:
    def __init__(self, query: str = None, artist: str = None, temp: str = "temp"):
        if query is None and artist is None:
            raise ValueError("no query provided")

        self.options_history = []
        self.current_options = None
        self.current_chosen_option = None

        self.temp = temp

        # initial search
        if query is not None:
            self.set_options(self.Options([musicbrainzngs.search_artists(query), musicbrainzngs.search_releases(query),
                                           musicbrainzngs.search_recordings(query)]))
        elif artist is not None:
            self.set_options(self.Options([musicbrainzngs.search_artists(artist=artist)]))

    def download(self, file: str = ".cache1.csv"):
        kind = self.current_chosen_option['kind']
        mb_id = self.current_chosen_option['id']

        metadata_list = []
        if kind == "artist":
            metadata_list = self.download_artist(mb_id)
        elif kind == "release":
            metadata_list = self.download_release(mb_id)
        elif kind == "track":
            metadata_list = self.download_track(mb_id)

        metadata_df = pd.DataFrame(metadata_list)
        metadata_df.to_csv(os.path.join(self.temp, file))

        return metadata_df

    def download_artist(self, mb_id):
        """
        Available includes: recordings, releases, release-groups, works, various-artists, discids, media, isrcs,
        aliases, annotation, area-rels, artist-rels, label-rels, place-rels, event-rels, recording-rels,
        release-rels, release-group-rels, series-rels, url-rels, work-rels, instrument-rels, tags, user-tags,
        ratings, user-ratings
        """
        metadata_list = []
        result = musicbrainzngs.get_artist_by_id(mb_id, includes=["releases"])
        for release in result["artist"]["release-list"]:
            metadata_list.extend(self.download_release(release["id"]))

        return metadata_list

    def download_release(self, mb_id):
        """
        Available includes: artists, labels, recordings, release-groups, media, artist-credits, discids, isrcs,
        recording-level-rels, work-level-rels, annotation, aliases, tags, user-tags, area-rels, artist-rels,
        label-rels, place-rels, event-rels, recording-rels, release-rels, release-group-rels, series-rels, url-rels,
        work-rels, instrument-rels
        """
        result = musicbrainzngs.get_release_by_id(mb_id, includes=["artists", "recordings"])

        tracklist_metadata = []

        is_various_artist = len(result['release']['artist-credit']) > 1
        tracklist = result['release']['medium-list'][0]['track-list']
        track_count = len(tracklist)
        this_track = 0
        for track in tracklist:
            track_id = track["recording"]["id"]
            this_track = track["position"]

            tracklist_metadata.extend(self.download_track(track_id, is_various_artist=is_various_artist, track=this_track, total_tracks=track_count))
        
        return tracklist_metadata

    def download_track(self, mb_id, is_various_artist: bool = None, track: int = None, total_tracks: int = None, album_sort: int = None):
        """
        TODO
        bpm     its kind of possible via the AcousticBrainz API. however, the data may not be of very good
                quality and AB is scheduled to go away in some time.

        compilation     Field that is used by iTunes to mark albums as compilation.
                        Either enter the value 1 or delete the field. https://en.wikipedia.org/wiki/Compilation_album
                        How should I get it? I don't fucking know

        composer, copyright, discsubtitle

        language

        DONE

        album
        title
        artist
        albumartist
        tracknumber
        !!!albumsort can sort albums cronological
        titlesort is just set to the tracknumber to sort by track order to sort correctly
        isrc

        Album Art
        """
        """Available includes: artists, releases, discids, media, artist-credits, isrcs, work-level-rels, annotation, 
        aliases, tags, user-tags, ratings, user-ratings, area-rels, artist-rels, label-rels, place-rels, event-rels, 
        recording-rels, release-rels, release-group-rels, series-rels, url-rels, work-rels, instrument-rels """

        result = musicbrainzngs.get_recording_by_id(mb_id, includes=["artists", "releases", "recording-rels", "isrcs", "work-level-rels"])
        recording_data = result['recording']
        print(result)

        isrc = None if 'isrc-list' not in recording_data else recording_data['isrc-list'][0]
        print(isrc)

        release_data = recording_data['release-list'][0]
        mb_release_id = release_data['id']

        title = recording_data['title']
        artist = [artist_['artist']['name'] for artist_ in recording_data['artist-credit']]
        mb_artist_ids = [artist_['artist']['id'] for artist_ in recording_data['artist-credit']]
        
        def get_additional_artist_info(mb_id_):
            r = musicbrainzngs.get_artist_by_id(mb_id_, includes=["releases"])

            album_sort = 0
            for i, release in enumerate(r["artist"]["release-list"]):
                id_ = release["id"]
                if id_ == mb_release_id:
                    album_sort = i
                    break

            return album_sort

        def get_additional_release_info(mb_id_):
            r = musicbrainzngs.get_release_by_id(mb_id_, includes=["artists", "recordings", "recording-rels"])
            is_various_artist_ = len(r['release']['artist-credit']) > 1
            tracklist = r['release']['medium-list'][0]['track-list']
            track_count_ = len(tracklist)
            this_track_ = 0
            for track in tracklist:
                if track["recording"]["id"] == mb_id:
                    this_track_ = track["position"]

            return is_various_artist_, this_track_, track_count_

        album_id = release_data['id']
        album = release_data['title']
        year = release_data['date'].split("-")[0]
        date = release_data['date']
        if is_various_artist is None or track is None or total_tracks is None:
            is_various_artist, track, total_tracks = get_additional_release_info(album_id)
        if album_sort is None:
            album_sort = get_additional_artist_info(mb_artist_ids[0])
        album_artist = "Various Artists" if is_various_artist else artist[0]

        return [{
            'album': album,
            'title': title,
            'artist': artist,
            'album_artist': album_artist,
            'tracknumber': track,
            'albumsort': album_sort,
            'titlesort': track,
            'isrc': isrc,
            'date': date,
            'year': year,
            'total_tracks': total_tracks
        }]

    def browse_artist(self, artist: dict, limit: int = 25):
        options_sets = [
            {"artist-list": [artist, ], "artist-count": 1},
            musicbrainzngs.browse_releases(artist=artist["id"], limit=limit),
            musicbrainzngs.browse_recordings(artist=artist["id"], limit=limit)
        ]
        return self.set_options(self.Options(options_sets))

    def browse_release(self, release: dict, limit: int = 25):
        options_sets = [
            musicbrainzngs.browse_artists(release=release["id"], limit=limit),
            {"release-list": [release, ], "release-count": 1},
            musicbrainzngs.browse_recordings(release=release["id"], limit=limit)
        ]
        return self.set_options(self.Options(options_sets))

    def browse_track(self, track: dict, limit: int = 25):
        options_sets = [
            musicbrainzngs.browse_artists(recording=track["id"], limit=limit),
            musicbrainzngs.browse_releases(recording=track["id"], limit=limit),
            {"recording-list": [track, ], "recording-count": 1}
        ]
        return self.set_options(self.Options(options_sets))

    def choose(self, index, limit: int = 25, ignore_limit_for_tracklist: bool = True):
        if not self.current_options.choose(index):
            return self.current_options

        self.current_chosen_option = self.current_options.get_current_option()
        kind = self.current_chosen_option['kind']
        if kind == 'artist':
            return self.browse_artist(self.current_chosen_option, limit=limit)
        if kind == 'release':
            release_limit = limit if not ignore_limit_for_tracklist else 100
            return self.browse_release(self.current_chosen_option, limit=release_limit)
        if kind == 'track':
            track_limit = limit if not ignore_limit_for_tracklist else 100
            return self.browse_track(self.current_chosen_option, limit=track_limit)

        return self.current_options

    def get_options(self):
        return self.current_options

    def set_options(self, option_instance):
        self.options_history.append(option_instance)
        self.current_options = option_instance

        return option_instance

    def get_previous_options(self):
        self.options_history.pop(-1)
        self.current_options = self.options_history[-1]
        return self.current_options

    options = property(fget=get_options)

    class Options:
        def __init__(self, results: list):
            self.results = results

            self.artist_count = 0
            self.release_count = 0
            self.track_count = 0
            self.result_list = []
            self.set_options_values()

            self.current_option_ind = None

        def get_current_option(self):
            if self.current_option_ind is None:
                raise Exception("It must first be chosen, which option to get, before getting it")

            return self.result_list[self.current_option_ind]

        def choose(self, index: int) -> bool:
            if len(self.result_list) <= index - 1:
                return False
            self.current_option_ind = index
            return True

        def get_string_for_artist(self, artist: dict) -> str:
            string = f"'{artist['name']}'"
            if "country" in artist:
                string += f" from {artist['country']}"
            if 'disambiguation' in artist:
                string += f", '{artist['disambiguation']}'"
            return string + "\n"

        def get_string_for_release(self, release: dict) -> str:
            string = ""
            if "type" in release:
                string += f"the {release['type']} titled "
            string += f"'{release['title']}'"
            if "artist-credit-phrase" in release:
                string += f" by: {release['artist-credit-phrase']}"

            return string + "\n"

        def get_string_for_tracks(self, tracks: dict) -> str:
            # I know it's not the best practice but whatever
            return self.get_string_for_release(tracks)

        def get_string_for_option(self, option: dict) -> str:
            kind = option['kind']
            if kind == "artist":
                return self.get_string_for_artist(option)
            if kind == "release":
                return self.get_string_for_release(option)
            if kind == "track":
                return self.get_string_for_tracks(option)
            return "Error\n"

        def __str__(self) -> str:
            string = f"artists: {self.artist_count}; releases {self.release_count}; tracks {self.track_count}\n"
            for i, option in enumerate(self.result_list):
                string += f"{i})\t{option['kind']}:\t" + self.get_string_for_option(option)
            return string

        def set_options_values(self):
            for option_set in self.results:
                if "artist-list" in option_set:
                    self.set_artist_values(option_set)
                    continue
                if "release-list" in option_set:
                    self.set_release_values(option_set)
                    continue
                if "recording-list" in option_set:
                    self.set_track_values(option_set)
                    continue

        def set_artist_values(self, option_set: dict):
            self.artist_count += option_set['artist-count']
            for artist in option_set['artist-list']:
                artist['kind'] = "artist"
                self.result_list.append(artist)

        def set_release_values(self, option_set: dict):
            self.release_count += option_set['release-count']
            for release in option_set['release-list']:
                release['kind'] = "release"
                self.result_list.append(release)

        def set_track_values(self, option_set: dict):
            self.track_count += option_set['recording-count']
            for track in option_set['recording-list']:
                track['kind'] = "track"
                self.result_list.append(track)


def automated_demo():
    search = Search(query="psychonaut 4")
    print(search.options)
    print(search.choose(0))
    search.download()
    print(search.choose(2))
    search.download()
    print(search.choose(4))
    print(search.download())


def interactive_demo():
    search = Search(query=input("initial query: "))
    print(search.options)
    while True:
        input_ = input("d to download, q to quit, .. for previous options, . for current options, int for this element: ").lower()
        input_.strip()
        if input_ == "q":
            break
        if input_ == ".":
            print(search.options)
            continue
        if input_ == "..":
            print(search.get_previous_options())
            continue
        if input_.isdigit():
            print(search.choose(int(input_)))
            continue
        if input_ == "d":
            search.download()
            break


if __name__ == "__main__":
    # interactive_demo()
    # automated_demo()
    search = Search(query="psychonaut 4")
    # search.download_release("27f00fb8-983c-4d5c-950f-51418aac55dc")
    # for track_ in search.download_artist("c0c720b5-012f-4204-a472-981403f37b12"):
    #     print(track_)
    #search.download_track("83a30323-aee1-401a-b767-b3c1bdd026c0")
    search.download_track("5cc28584-10c6-40e2-b6d4-6891e7e7c575")
