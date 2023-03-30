from music_kraken import pages


def cli():
    def next_search(search: pages.Search, query: str):
        query: str = query.strip()
        parsed: str = query.lower()
        
        if parsed == ".":
            return
        if parsed == "..":
            search.goto_previous()
            return
        
        if parsed.isdigit():
            search.choose_index(int(parsed))
            return
        
        page = search.get_page_from_query(parsed)
        if page is not None:
            search.choose_page(page)
            return
        
        # if everything else is not valid search
        search.search(query)
    
    search = pages.Search()

    while True:
        next_search(search, input(">> "))
        print(search)


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
    cli()
