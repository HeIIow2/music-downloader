import music_kraken
from music_kraken import pages
from music_kraken.objects import Song, Target, Source, SourcePages, Album


def search_pages():
    search = pages.Search()
    print("metadata", search.pages)
    print("audio", search.audio_pages)

    print()
    print(search)

    search.choose_page(pages.Musify)

    print()
    print(search)

    search.choose_index(0)
    print(search)


def direct_download():
    search = pages.Search()

    search.search_url("https://www.metal-archives.com/bands/Ghost_Bath/3540372489")
    print(search)

    search.search_url("https://musify.club/artist/ghost-bath-280348")
    print(search)


def download_audio():
    song = Song(
        source_list=[
            Source(SourcePages.MUSIFY, "https://musify.club/track/im-in-a-coffin-life-never-was-waste-of-skin-16360302")
        ],
        target_list=[
            Target(relative_to_music_dir=True, path="example", file="waste_of_skin_1"),
            Target(relative_to_music_dir=True, path="example", file="waste_of_skin_2")
        ]
    )

    pages.Musify.download_song(song)


def real_download():
    search = pages.Search()
    search.search_url("https://musify.club/release/children-of-the-night-2018-1079829")
    search.download_chosen()


if __name__ == "__main__":
    music_kraken.cli(genre="dsbm")
