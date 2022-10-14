import metadata


def test():
    passed = 0
    failed = 0

    # testing search
    metadata.Search(artist="Psychonaut")
    passed += 1
    metadata.Search(query="Psychonaut")
    passed += 1
    try:
        metadata.Search()
        failed += 1
    except ValueError:
        print("throwing error on not giving metadata search a query works")
        passed += 1

    return passed, failed

if __name__ == "__main__":
    p,f = test()
    print(f"{p}-{f}")
