# How to contribute

I am always happy about pull requests.  
If you wanna contribute, this is for you. Some options will follow:

## Add an audio/metadata source

The audio and Metadata Sources all inherint the class `Page` in [abstract.py](src/music_kraken/pages/abstract.py)

You can create a subclass of this class for for example youtube or musify or whatever.  
I documented the function it should have in the docstrings of [abstract.py](src/music_kraken/pages/abstract.py). If you are unsure about how it works, look at either the doccumentation *(will get more detailed soon)* or an [example](src/music_kraken/pages/encyclopaedia_metallum.py). For trying you're class you can make a skript simmilar to [this one](src/metal_archives.py). Make sure it is in the same directory though.

> Read the part of the documentation, I already have written. 
