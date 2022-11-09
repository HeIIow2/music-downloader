from mutagen.id3 import ID3, USLT

"""
https://cweiske.de/tagebuch/rhythmbox-lyrics.htm
Rythmbox, my music player doesn't support ID3 lyrics (USLT) yet, so I have to find something else
Lyrics in MP3 ID3 tags (SYLT/USLT) is still missing, because GStreamer does not support that yet.

One possible sollution would be to use ogg/vorbis files. Those lyrics are supported in rythmbox
'So, the next Rhythmbox release (3.5.0 or 3.4.2) will read lyrics directly from ogg/vorbis files, using the LYRICS and SYNCLYRICS tags.'
Another possible sollution (probaply the better one cuz I dont need to refactor whole metadata AGAIN)
would be to write a Rhythmbox plugin that fetches lyrics from ID3 USLT
"""

# https://www.programcreek.com/python/example/63462/mutagen.mp3.EasyMP3
# https://code.activestate.com/recipes/577138-embed-lyrics-into-mp3-files-using-mutagen-uslt-tag/

MP3_PATH = "/home/lars/Music/deathcore/Brand of Sacrifice/The Interstice/Eclipse.mp3"
LYRICS_BREAKING_DOWN = """
[Chorus: Brian Burkheiser]
I think, I think too much
I'm a little bit paranoid, I think I’m breaking
Maybe it's in my blood
Got a pain that I can't avoid, I think I’m breaking down

[Verse 1: Brian Burkheiser]
Hate every single second, minute, hour every day
Person in the mirror, they won't let me feel a thing
Keep me focused on my problems, I'm addicted to the pain
Everybody's out to get you
[Pre-Chorus: Eric Vanlerberghe]
I guess I never noticed how it came creeping in
My enemy emotion, but I can't sink or swim
I say I'm feeling hopeless, they give me medicine
They give me medicine, they give me medicine

[Chorus: Brian Burkheiser & Eric Vanlerberghe]
I think I think too much (Too much)
I'm a little bit paranoid, I think I'm breaking
Maybe it’s in my blood (My blood)
Got a pain that I can’t avoid, I think I'm breaking
Down, I think I’m breaking
Down, I think I'm breaking
I think I think too much (Too much)
I'm a little bit paranoid, I think I'm breaking down

[Verse 2: Brian Burkheiser]
Lies, every time they ask me, I just tell ’em that I'm fine
Try to hide my demons, but they only multiply
Keep me running from the voices on repeat inside my mind
Everybody fucking hates you

[Pre-Chorus: Eric Vanlerberghe]
I guess I never noticed how it came creeping in
My enemy emotion, but I can't sink or swim
I say I'm feeling hopeless, but no one's listening
But no one's listening, but no one's listening
You might also like
DOA
I Prevail
Rise Above It
I Prevail
Bow Down
I Prevail
[Chorus: Brian Burkheiser & Eric Vanlerberghe]
I think I think too much (Too much)
I'm a little bit paranoid, I think I'm breaking
Maybe it's in my blood (My blood)
Got a pain that I can't avoid, I think I'm breaking
Down, I think I'm breaking
Down, I think I'm breaking
I think I think too much (Too much)
I'm a little bit paranoid, I think I'm breaking down

[Outro: Brian Burkheiser]
I don't really like myself
I don't really like myself
I don't really like myself
I don't really like myself
I think I'm breaking down
"""
LYRICS_ECLIPSE = """
Your offerings have consecrated
They are marked by the brand
The sun has seen it's fifth death
For the red lake to flow again

He will
Feel their pain in order to
Complete the final transformation
A name new and old

Your offerings have been consecrated by the laws of Causality
Falcon of Darkness
Send us into an age of abyss
Blinded by beauty
With stacks of bodies as high as the eye can see
Feast, apostles, feast

The one chosen by the hand of God
The master of the sinful black sheep
And the king of the faithful blind

Welcome to the new age
Welcome to the new age
We are the branded ones"""


def add_lyrics(file_name, lyrics=""):
    tags = ID3(file_name)
    uslt_output = USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics)
    tags["USLT::'eng'"] = uslt_output

    tags.save(file_name)

def get_lyrics(file_name):
    tags = ID3(file_name)
    return tags.getall("USLT")

if __name__ == "__main__":
    add_lyrics(MP3_PATH, lyrics=LYRICS_ECLIPSE)
    print(get_lyrics(MP3_PATH))
