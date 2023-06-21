# Diff Details

Date : 2023-05-24 11:17:57

Directory /home/lars/Projects/music-downloader/src

Total : 61 files,  1280 codes, 157 comments, 437 blanks, all 1874 lines

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [src/actual_donwload.py](/src/actual_donwload.py) | Python | 6 | 2 | 1 | 9 |
| [src/music_kraken/__init__.py](/src/music_kraken/__init__.py) | Python | 103 | 9 | 32 | 144 |
| [src/music_kraken/__main__.py](/src/music_kraken/__main__.py) | Python | 85 | 3 | 18 | 106 |
| [src/music_kraken/audio/__init__.py](/src/music_kraken/audio/__init__.py) | Python | 7 | 0 | 3 | 10 |
| [src/music_kraken/audio/codec.py](/src/music_kraken/audio/codec.py) | Python | 25 | 0 | 8 | 33 |
| [src/music_kraken/audio/metadata.py](/src/music_kraken/audio/metadata.py) | Python | 60 | 4 | 24 | 88 |
| [src/music_kraken/connection/__init__.py](/src/music_kraken/connection/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [src/music_kraken/connection/connection.py](/src/music_kraken/connection/connection.py) | Python | 162 | 1 | 30 | 193 |
| [src/music_kraken/connection/rotating.py](/src/music_kraken/connection/rotating.py) | Python | 27 | 3 | 14 | 44 |
| [src/music_kraken/download/__init__.py](/src/music_kraken/download/__init__.py) | Python | 2 | 0 | 1 | 3 |
| [src/music_kraken/download/download.py](/src/music_kraken/download/download.py) | Python | 35 | 0 | 14 | 49 |
| [src/music_kraken/download/multiple_options.py](/src/music_kraken/download/multiple_options.py) | Python | 69 | 0 | 31 | 100 |
| [src/music_kraken/download/page_attributes.py](/src/music_kraken/download/page_attributes.py) | Python | 21 | 1 | 10 | 32 |
| [src/music_kraken/download/search.py](/src/music_kraken/download/search.py) | Python | 130 | 24 | 56 | 210 |
| [src/music_kraken/objects/__init__.py](/src/music_kraken/objects/__init__.py) | Python | -15 | 0 | -3 | -18 |
| [src/music_kraken/objects/album.py](/src/music_kraken/objects/album.py) | Python | -16 | -6 | -5 | -27 |
| [src/music_kraken/objects/option.py](/src/music_kraken/objects/option.py) | Python | 5 | 0 | 2 | 7 |
| [src/music_kraken/objects/parents.py](/src/music_kraken/objects/parents.py) | Python | 3 | 2 | 2 | 7 |
| [src/music_kraken/objects/song.py](/src/music_kraken/objects/song.py) | Python | 37 | 20 | 16 | 73 |
| [src/music_kraken/objects/source.py](/src/music_kraken/objects/source.py) | Python | -30 | -1 | -9 | -40 |
| [src/music_kraken/objects/target.py](/src/music_kraken/objects/target.py) | Python | 5 | 4 | 2 | 11 |
| [src/music_kraken/pages/__init__.py](/src/music_kraken/pages/__init__.py) | Python | -3 | 0 | -4 | -7 |
| [src/music_kraken/pages/abstract.py](/src/music_kraken/pages/abstract.py) | Python | -71 | -10 | 0 | -81 |
| [src/music_kraken/pages/download_center/__init__.py](/src/music_kraken/pages/download_center/__init__.py) | Python | -4 | 0 | -2 | -6 |
| [src/music_kraken/pages/download_center/download.py](/src/music_kraken/pages/download_center/download.py) | Python | -33 | 0 | -13 | -46 |
| [src/music_kraken/pages/download_center/multiple_options.py](/src/music_kraken/pages/download_center/multiple_options.py) | Python | -69 | 0 | -31 | -100 |
| [src/music_kraken/pages/download_center/page_attributes.py](/src/music_kraken/pages/download_center/page_attributes.py) | Python | -24 | -1 | -9 | -34 |
| [src/music_kraken/pages/download_center/search.py](/src/music_kraken/pages/download_center/search.py) | Python | -85 | -23 | -38 | -146 |
| [src/music_kraken/pages/encyclopaedia_metallum.py](/src/music_kraken/pages/encyclopaedia_metallum.py) | Python | -19 | 7 | 10 | -2 |
| [src/music_kraken/pages/musify.py](/src/music_kraken/pages/musify.py) | Python | 65 | 30 | 32 | 127 |
| [src/music_kraken/pages/preset.py](/src/music_kraken/pages/preset.py) | Python | 43 | 1 | 16 | 60 |
| [src/music_kraken/pages/support_classes/__init__.py](/src/music_kraken/pages/support_classes/__init__.py) | Python | 0 | 0 | -1 | -1 |
| [src/music_kraken/pages/support_classes/default_target.py](/src/music_kraken/pages/support_classes/default_target.py) | Python | -55 | 0 | -15 | -70 |
| [src/music_kraken/pages/support_classes/download_result.py](/src/music_kraken/pages/support_classes/download_result.py) | Python | -51 | 0 | -15 | -66 |
| [src/music_kraken/tagging/__init__.py](/src/music_kraken/tagging/__init__.py) | Python | -5 | 0 | -2 | -7 |
| [src/music_kraken/tagging/id3.py](/src/music_kraken/tagging/id3.py) | Python | -60 | -4 | -24 | -88 |
| [src/music_kraken/utils/__init__.py](/src/music_kraken/utils/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [src/music_kraken/utils/config/__init__.py](/src/music_kraken/utils/config/__init__.py) | Python | 7 | 0 | 4 | 11 |
| [src/music_kraken/utils/config/audio.py](/src/music_kraken/utils/config/audio.py) | Python | 152 | 15 | 28 | 195 |
| [src/music_kraken/utils/config/base_classes.py](/src/music_kraken/utils/config/base_classes.py) | Python | 136 | 35 | 61 | 232 |
| [src/music_kraken/utils/config/config.py](/src/music_kraken/utils/config/config.py) | Python | 92 | 16 | 30 | 138 |
| [src/music_kraken/utils/config/connection.py](/src/music_kraken/utils/config/connection.py) | Python | 81 | 2 | 15 | 98 |
| [src/music_kraken/utils/config/logging.py](/src/music_kraken/utils/config/logging.py) | Python | 104 | 4 | 17 | 125 |
| [src/music_kraken/utils/config/misc.py](/src/music_kraken/utils/config/misc.py) | Python | 40 | 0 | 9 | 49 |
| [src/music_kraken/utils/config/paths.py](/src/music_kraken/utils/config/paths.py) | Python | 40 | 0 | 13 | 53 |
| [src/music_kraken/utils/enums/__init__.py](/src/music_kraken/utils/enums/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/music_kraken/utils/enums/album.py](/src/music_kraken/utils/enums/album.py) | Python | 16 | 6 | 5 | 27 |
| [src/music_kraken/utils/enums/source.py](/src/music_kraken/utils/enums/source.py) | Python | 40 | 1 | 8 | 49 |
| [src/music_kraken/utils/exception/__init__.py](/src/music_kraken/utils/exception/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [src/music_kraken/utils/exception/config.py](/src/music_kraken/utils/exception/config.py) | Python | 14 | 8 | 7 | 29 |
| [src/music_kraken/utils/path_manager/__init__.py](/src/music_kraken/utils/path_manager/__init__.py) | Python | 2 | 0 | 2 | 4 |
| [src/music_kraken/utils/path_manager/config_directory.py](/src/music_kraken/utils/path_manager/config_directory.py) | Python | 4 | 0 | 4 | 8 |
| [src/music_kraken/utils/path_manager/locations.py](/src/music_kraken/utils/path_manager/locations.py) | Python | 16 | 0 | 9 | 25 |
| [src/music_kraken/utils/path_manager/music_directory.py](/src/music_kraken/utils/path_manager/music_directory.py) | Python | 36 | 9 | 14 | 59 |
| [src/music_kraken/utils/regex.py](/src/music_kraken/utils/regex.py) | Python | 1 | 0 | 2 | 3 |
| [src/music_kraken/utils/shared.py](/src/music_kraken/utils/shared.py) | Python | -12 | -5 | 4 | -13 |
| [src/music_kraken/utils/string_processing.py](/src/music_kraken/utils/string_processing.py) | Python | 6 | 0 | 4 | 10 |
| [src/music_kraken/utils/support_classes/__init__.py](/src/music_kraken/utils/support_classes/__init__.py) | Python | 3 | 0 | 1 | 4 |
| [src/music_kraken/utils/support_classes/default_target.py](/src/music_kraken/utils/support_classes/default_target.py) | Python | 56 | 0 | 15 | 71 |
| [src/music_kraken/utils/support_classes/download_result.py](/src/music_kraken/utils/support_classes/download_result.py) | Python | 69 | 0 | 21 | 90 |
| [src/music_kraken/utils/support_classes/query.py](/src/music_kraken/utils/support_classes/query.py) | Python | 24 | 0 | 9 | 33 |

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details