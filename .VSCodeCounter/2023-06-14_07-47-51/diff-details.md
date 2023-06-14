# Diff Details

Date : 2023-06-14 07:47:51

Directory /home/lars/Projects/music-downloader/src

Total : 44 files,  -709 codes, -5 comments, -155 blanks, all -869 lines

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [src/actual_donwload.py](/src/actual_donwload.py) | Python | -27 | -2 | -12 | -41 |
| [src/music_kraken/__init__.py](/src/music_kraken/__init__.py) | Python | -77 | -15 | -27 | -119 |
| [src/music_kraken/__main__.py](/src/music_kraken/__main__.py) | Python | 10 | 0 | 2 | 12 |
| [src/music_kraken/cli/__init__.py](/src/music_kraken/cli/__init__.py) | Python | 2 | 0 | 0 | 2 |
| [src/music_kraken/cli/download/__init__.py](/src/music_kraken/cli/download/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/music_kraken/cli/download/shell.py](/src/music_kraken/cli/download/shell.py) | Python | 199 | 86 | 78 | 363 |
| [src/music_kraken/cli/options/__init__.py](/src/music_kraken/cli/options/__init__.py) | Python | 3 | 0 | 1 | 4 |
| [src/music_kraken/cli/options/invidious/__init__.py](/src/music_kraken/cli/options/invidious/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/music_kraken/cli/options/invidious/shell.py](/src/music_kraken/cli/options/invidious/shell.py) | Python | 66 | 7 | 28 | 101 |
| [src/music_kraken/connection/connection.py](/src/music_kraken/connection/connection.py) | Python | 6 | 0 | 0 | 6 |
| [src/music_kraken/download/__init__.py](/src/music_kraken/download/__init__.py) | Python | -1 | 0 | 0 | -1 |
| [src/music_kraken/download/download.py](/src/music_kraken/download/download.py) | Python | -35 | 0 | -14 | -49 |
| [src/music_kraken/download/page_attributes.py](/src/music_kraken/download/page_attributes.py) | Python | 46 | 0 | 19 | 65 |
| [src/music_kraken/download/results.py](/src/music_kraken/download/results.py) | Python | 62 | 7 | 26 | 95 |
| [src/music_kraken/download/search.py](/src/music_kraken/download/search.py) | Python | -6 | 0 | 0 | -6 |
| [src/music_kraken/not_used_anymore/__init__.py](/src/music_kraken/not_used_anymore/__init__.py) | Python | 0 | 0 | -3 | -3 |
| [src/music_kraken/not_used_anymore/fetch_audio.py](/src/music_kraken/not_used_anymore/fetch_audio.py) | Python | -75 | -12 | -20 | -107 |
| [src/music_kraken/not_used_anymore/fetch_source.py](/src/music_kraken/not_used_anymore/fetch_source.py) | Python | -54 | -1 | -16 | -71 |
| [src/music_kraken/not_used_anymore/metadata/__init__.py](/src/music_kraken/not_used_anymore/metadata/__init__.py) | Python | -6 | 0 | -2 | -8 |
| [src/music_kraken/not_used_anymore/metadata/metadata_fetch.py](/src/music_kraken/not_used_anymore/metadata/metadata_fetch.py) | Python | -257 | -24 | -65 | -346 |
| [src/music_kraken/not_used_anymore/metadata/metadata_search.py](/src/music_kraken/not_used_anymore/metadata/metadata_search.py) | Python | -253 | -40 | -72 | -365 |
| [src/music_kraken/not_used_anymore/metadata/sources/__init__.py](/src/music_kraken/not_used_anymore/metadata/sources/__init__.py) | Python | -3 | 0 | -2 | -5 |
| [src/music_kraken/not_used_anymore/metadata/sources/musicbrainz.py](/src/music_kraken/not_used_anymore/metadata/sources/musicbrainz.py) | Python | -42 | -6 | -12 | -60 |
| [src/music_kraken/not_used_anymore/sources/__init__.py](/src/music_kraken/not_used_anymore/sources/__init__.py) | Python | 0 | 0 | -1 | -1 |
| [src/music_kraken/not_used_anymore/sources/genius.py](/src/music_kraken/not_used_anymore/sources/genius.py) | Python | -115 | -16 | -42 | -173 |
| [src/music_kraken/not_used_anymore/sources/local_files.py](/src/music_kraken/not_used_anymore/sources/local_files.py) | Python | -40 | 0 | -18 | -58 |
| [src/music_kraken/not_used_anymore/sources/musify.py](/src/music_kraken/not_used_anymore/sources/musify.py) | Python | -136 | -9 | -37 | -182 |
| [src/music_kraken/not_used_anymore/sources/source.py](/src/music_kraken/not_used_anymore/sources/source.py) | Python | -11 | -5 | -8 | -24 |
| [src/music_kraken/not_used_anymore/sources/youtube.py](/src/music_kraken/not_used_anymore/sources/youtube.py) | Python | -71 | -4 | -24 | -99 |
| [src/music_kraken/objects/metadata.py](/src/music_kraken/objects/metadata.py) | Python | 11 | 0 | 2 | 13 |
| [src/music_kraken/objects/parents.py](/src/music_kraken/objects/parents.py) | Python | 6 | 2 | 2 | 10 |
| [src/music_kraken/objects/song.py](/src/music_kraken/objects/song.py) | Python | 7 | 0 | 5 | 12 |
| [src/music_kraken/objects/source.py](/src/music_kraken/objects/source.py) | Python | 3 | 0 | 1 | 4 |
| [src/music_kraken/objects/target.py](/src/music_kraken/objects/target.py) | Python | 2 | 0 | 1 | 3 |
| [src/music_kraken/pages/__init__.py](/src/music_kraken/pages/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [src/music_kraken/pages/abstract.py](/src/music_kraken/pages/abstract.py) | Python | -123 | 12 | -10 | -121 |
| [src/music_kraken/pages/musify.py](/src/music_kraken/pages/musify.py) | Python | -53 | -14 | -21 | -88 |
| [src/music_kraken/pages/preset.py](/src/music_kraken/pages/preset.py) | Python | 4 | 0 | 1 | 5 |
| [src/music_kraken/pages/youtube.py](/src/music_kraken/pages/youtube.py) | Python | 229 | 29 | 73 | 331 |
| [src/music_kraken/utils/config/connection.py](/src/music_kraken/utils/config/connection.py) | Python | -1 | 0 | 0 | -1 |
| [src/music_kraken/utils/exception/download.py](/src/music_kraken/utils/exception/download.py) | Python | 8 | 0 | 4 | 12 |
| [src/music_kraken/utils/shared.py](/src/music_kraken/utils/shared.py) | Python | 3 | 0 | 1 | 4 |
| [src/music_kraken/utils/support_classes/__init__.py](/src/music_kraken/utils/support_classes/__init__.py) | Python | 1 | 0 | 0 | 1 |
| [src/music_kraken/utils/support_classes/thread_classes.py](/src/music_kraken/utils/support_classes/thread_classes.py) | Python | 8 | 0 | 4 | 12 |

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details