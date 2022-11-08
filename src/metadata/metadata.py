import logging
import musicbrainzngs

from metadata import options

mb_log = logging.getLogger("musicbrainzngs")
mb_log.setLevel(logging.WARNING)
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
            self.set_options(
                options.Options([musicbrainzngs.search_artists(query), musicbrainzngs.search_releases(query),
                                 musicbrainzngs.search_recordings(query)]))
        elif artist is not None:
            self.set_options(options.Options([musicbrainzngs.search_artists(artist=artist)]))

    def browse_artist(self, artist: dict, limit: int = 25):
        options_sets = [
            {"artist-list": [artist, ], "artist-count": 1},
            musicbrainzngs.browse_releases(artist=artist["id"], limit=limit),
            musicbrainzngs.browse_recordings(artist=artist["id"], limit=limit)
        ]
        return self.set_options(options.Options(options_sets))

    def browse_release(self, release: dict, limit: int = 25):
        options_sets = [
            musicbrainzngs.browse_artists(release=release["id"], limit=limit),
            {"release-list": [release, ], "release-count": 1},
            musicbrainzngs.browse_recordings(release=release["id"], limit=limit)
        ]
        return self.set_options(options.Options(options_sets))

    def browse_track(self, track: dict, limit: int = 25):
        options_sets = [
            musicbrainzngs.browse_artists(recording=track["id"], limit=limit),
            musicbrainzngs.browse_releases(recording=track["id"], limit=limit),
            {"recording-list": [track, ], "recording-count": 1}
        ]
        return self.set_options(options.Options(options_sets))

    def choose(self, index, limit: int = 25, ignore_limit_for_tracklist: bool = True):
        if not self.current_options.choose(index):
            return self.current_options

        self.current_chosen_option = self.current_options.get_current_option(komplex=True)
        kind = self.current_chosen_option['type']
        if kind == 'artist':
            return self.browse_artist(self.current_chosen_option, limit=limit)
        if kind == 'release':
            release_limit = limit if not ignore_limit_for_tracklist else 100
            release_limit = 100
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
        input_ = input(
            "d to download, q to quit, .. for previous options, . for current options, int for this element: ").lower()
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
    search.download_release("1aeb676f-e556-4b17-b45e-64ab69ef0375")
    # for track_ in search.download_artist("c0c720b5-012f-4204-a472-981403f37b12"):
    #     print(track_)
    # res = search.download_track("83a30323-aee1-401a-b767-b3c1bdd026c0")
    # res = search.download_track("5e1ee2c5-502c-44d3-b1bc-22803441d8c6")
    res = search.download_track("86b43bec-eea6-40ae-8624-c1e404204ba1")
    # res = search.download_track("5cc28584-10c6-40e2-b6d4-6891e7e7c575")

    for key in res[0]:
        if res[0][key] is None:
            continue

        print(key, res[0][key])
