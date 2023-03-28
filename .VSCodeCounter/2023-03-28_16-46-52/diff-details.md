# Diff Details

Date : 2023-03-28 16:46:52

Directory /home/lars/Projects/music-downloader/src

Total : 40 files,  523 codes, 22 comments, 130 blanks, all 675 lines

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [src/create_custom_objects.py](/src/create_custom_objects.py) | Python | -22 | -3 | -12 | -37 |
| [src/donwload.py](/src/donwload.py) | Python | 9 | 0 | 6 | 15 |
| [src/metal_archives.py](/src/metal_archives.py) | Python | -18 | -4 | -3 | -25 |
| [src/music_kraken/__init__.py](/src/music_kraken/__init__.py) | Python | -33 | -1 | -11 | -45 |
| [src/music_kraken/database/__init__.py](/src/music_kraken/database/__init__.py) | Python | -18 | 0 | -4 | -22 |
| [src/music_kraken/database/data_models.py](/src/music_kraken/database/data_models.py) | Python | -1 | 1 | 0 | 0 |
| [src/music_kraken/database/database.py](/src/music_kraken/database/database.py) | Python | 20 | -1 | 12 | 31 |
| [src/music_kraken/database/object_cache.py](/src/music_kraken/database/object_cache.py) | Python | -35 | -56 | -16 | -107 |
| [src/music_kraken/database/old_database.py](/src/music_kraken/database/old_database.py) | Python | -432 | -154 | -115 | -701 |
| [src/music_kraken/database/read.py](/src/music_kraken/database/read.py) | Python | 0 | 0 | -1 | -1 |
| [src/music_kraken/database/temp_database.py](/src/music_kraken/database/temp_database.py) | Python | -12 | 0 | -8 | -20 |
| [src/music_kraken/database/write.py](/src/music_kraken/database/write.py) | Python | -210 | -62 | -63 | -335 |
| [src/music_kraken/objects/__init__.py](/src/music_kraken/objects/__init__.py) | Python | 4 | 0 | 1 | 5 |
| [src/music_kraken/objects/album.py](/src/music_kraken/objects/album.py) | Python | 1 | 0 | 0 | 1 |
| [src/music_kraken/objects/artist.py](/src/music_kraken/objects/artist.py) | Python | -18 | 0 | -5 | -23 |
| [src/music_kraken/objects/cache.py](/src/music_kraken/objects/cache.py) | Python | 37 | 56 | 18 | 111 |
| [src/music_kraken/objects/collection.py](/src/music_kraken/objects/collection.py) | Python | 33 | 15 | 13 | 61 |
| [src/music_kraken/objects/formatted_text.py](/src/music_kraken/objects/formatted_text.py) | Python | -3 | -47 | -1 | -51 |
| [src/music_kraken/objects/lyrics.py](/src/music_kraken/objects/lyrics.py) | Python | 4 | 0 | 0 | 4 |
| [src/music_kraken/objects/metadata.py](/src/music_kraken/objects/metadata.py) | Python | -3 | -6 | -3 | -12 |
| [src/music_kraken/objects/option.py](/src/music_kraken/objects/option.py) | Python | 23 | 0 | 11 | 34 |
| [src/music_kraken/objects/parents.py](/src/music_kraken/objects/parents.py) | Python | 44 | 16 | 19 | 79 |
| [src/music_kraken/objects/song.py](/src/music_kraken/objects/song.py) | Python | 108 | 2 | 5 | 115 |
| [src/music_kraken/objects/source.py](/src/music_kraken/objects/source.py) | Python | 2 | -21 | -1 | -20 |
| [src/music_kraken/objects/target.py](/src/music_kraken/objects/target.py) | Python | 7 | 0 | 2 | 9 |
| [src/music_kraken/pages/__init__.py](/src/music_kraken/pages/__init__.py) | Python | -1 | 0 | 0 | -1 |
| [src/music_kraken/pages/abstract.py](/src/music_kraken/pages/abstract.py) | Python | 107 | -36 | 26 | 97 |
| [src/music_kraken/pages/download_center/__init__.py](/src/music_kraken/pages/download_center/__init__.py) | Python | 2 | 0 | 2 | 4 |
| [src/music_kraken/pages/download_center/page_attributes.py](/src/music_kraken/pages/download_center/page_attributes.py) | Python | 14 | 0 | 6 | 20 |
| [src/music_kraken/pages/download_center/search.py](/src/music_kraken/pages/download_center/search.py) | Python | 98 | 8 | 42 | 148 |
| [src/music_kraken/pages/encyclopaedia_metallum.py](/src/music_kraken/pages/encyclopaedia_metallum.py) | Python | 100 | 20 | 20 | 140 |
| [src/music_kraken/pages/musify.py](/src/music_kraken/pages/musify.py) | Python | 500 | 248 | 135 | 883 |
| [src/music_kraken/target/__init__.py](/src/music_kraken/target/__init__.py) | Python | -4 | 0 | -2 | -6 |
| [src/music_kraken/target/set_target.py](/src/music_kraken/target/set_target.py) | Python | -37 | -7 | -18 | -62 |
| [src/musify_search.py](/src/musify_search.py) | Python | 26 | 0 | 11 | 37 |
| [src/python.py](/src/python.py) | Python | 12 | 43 | 6 | 61 |
| [src/test.py](/src/test.py) | Python | 1 | 0 | 0 | 1 |
| [src/tests/example_data_objects.py](/src/tests/example_data_objects.py) | Python | -36 | -5 | -6 | -47 |
| [src/tests/test_building_objects.py](/src/tests/test_building_objects.py) | Python | 81 | 1 | 13 | 95 |
| [src/tests/test_objects.py](/src/tests/test_objects.py) | Python | 173 | 15 | 51 | 239 |

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details