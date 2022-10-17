import metadata


def search_for_metadata(query: str):
    search = metadata.Search(query=query)

    print(search.options)
    while True:
        input_ = input("q to quit, ok to download, .. for previous options, . for current options, int for this element: ").lower()
        input_.strip()
        if input_ == "q":
            exit(0)
        if input_ == "ok":
            return search
        if input_ == ".":
            print(search.options)
            continue
        if input_ == "..":
            print(search.get_previous_options())
            continue
        if input_.isdigit():
            print(search.choose(int(input_)))
            continue


def cli():
    search = search_for_metadata(query=input("initial query: "))
    search.download()


if __name__ == "__main__":
    cli()
