# How to contribute

I am always happy about pull requests.  

If something is missing, like attributes for an object feel free to either add it yourself or open an issue, if you choose to just change it, beware that something may have to change. :3

So here is a List of what you can do:

1. [implement a new page like e.g. Soundcloud](#add-a-new-page)
2. [help securing this programm](#find-a-security-vulnerability)

## Add a new Page

The audio and Metadata Sources all inherit from the class `Page`, which can be found in [abstract.py](src/music_kraken/pages/abstract.py).

You can create a subclass of this class for, for example `YouTube` or `Musify` or whatever. 

1. Just create a new file with the name `your_page.py`
in the [page module](src/music_kraken/pages). 
2. Then you can simply copy the contents of the [preset](src/music_kraken/pages/preset.py) over to your file.
3. All the functions you need to implement, can be found in the [preset](src/music_kraken/pages/preset.py).

### Important notes

- There is no need to check if you for example added a source of a song twice. I do much post-processing to the data you scrape in the page classes. You can see what exactly I do in [abstract.py](src/music_kraken/pages/abstract.py).
- Use the connection class how it is laid out in the preset to make the request. This will take care of retrying requests, rotating proxies, consistent use of tor (if selected in the config). You have:
  - `connection.get()`
  - `connection.post()`
- Look at the code of the pages I already have implemented. Namely:
  - [musify.club](src/music_kraken/pages/musify.py) _(heavily making use of web scraping)_
  - [YouTube](src/music_kraken/pages/youtube.py) _(using both invidious and piped)_
  - [Metal Archives](src/music_kraken/pages/youtube.py)

## Find a security vulnerability

I take security seriously. Really.

If you find a vulnerability that is rather critical, [write me on matrix](https://matrix.to/#/@hellow_2:matrix.org).
Under vulnerability counts:

- If there is a bug, which makes music_kraken ignore a proxy/tor setting.

BUT... There could be more stuff, that falls under security.
