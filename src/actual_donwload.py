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
    
def direct_download():
    search = pages.Search()
    
    search.search_url("https://www.metal-archives.com/bands/Ghost_Bath/3540372489")
    print(search)
    
    search.search_url("https://musify.club/artist/ghost-bath-280348")
    print(search)


if __name__ == "__main__":
    music_kraken.cli()
