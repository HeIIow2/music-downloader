import music_kraken
from music_kraken import pages


def search_pages():
    search = pages.Search()
    print("metadata", search.pages)
    print("audio", search.audio_pages)

    print()
    print(search)

    search.choose(pages.Musify)

    print()
    print(search)

    search.choose(0)
    print(search)


if __name__ == "__main__":
    music_kraken.cli()
