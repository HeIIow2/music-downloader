from music_kraken import pages


def search_pages():
    search = pages.Search("#a Happy Days")
    print("metadata", search.pages)
    print("audio", search.audio_pages)
    
    print()
    print(search)
    
    search.choose(1)
    print(search)


if __name__ == "__main__":
    search_pages()
