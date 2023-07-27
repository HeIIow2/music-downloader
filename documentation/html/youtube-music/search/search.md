# Search

## Files

what is it | query | file
---|---|---
general search response | `psychonaut 4`, [general-result.json](general-result.json)

## A general search yields

- **Top Result**
  - The top Artist
  - The most popular songs of said artist
- **Songs** (3) excluding the top songs
- Videos (3)
- **Albums** (3)
- Community playlists (3)
- **Artists** (3) excluding the top artist
  - if you search for a artist, it might return simmilar artists in style, not in name

### Different Renderers

#### `runs`

This should be pretty consistently all over the response be parsebal to a list of Music Elements.

`runs` usually is a list. If a element of the list has the key `navigationEndpoint`, it represents a music elements in a following manner:

- `text` the name
- `navigationEndpoint` -> `browseEndpoint`
  - `browseId` the id of the artist/song/album...
  - `browseEndpointContextSupportedConfigs` -> `browseEndpointContextMusicConfig` -> `pageType` the type of the header like element 

#### musicCardShelfRenderer

Used by e.g. the `Top Results`.

Contains:

- One Main-Element (a header like music object) | consists of these keys:
  - `thumbnail` the image of the header
  - `title` -> `runs`
    - for details look [here](#runs).


### Details

You can get the contents (a list of [renderers](#musiccardshelfrenderer)) this way:

```python
data = r.json().get("contents", {}).get("tabbedSearchResultsRenderer", {}).get("tabs", [{}])[0].get("tabRenderer").get("content", {}).get("sectionListRenderer", {}).get("contents", [])
```

Then the list contains following items, in following order:

1. _About these results_ (an infobutton)
2. The **Top result**
3. The **Songs** [_musicShelfRenderer_]
4. ...
