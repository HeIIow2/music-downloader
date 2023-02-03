# https://github.com/Alir3z4/html2text
import html2text

import pandoc

"""
>>> import html2text
>>>
>>> h = html2text.HTML2Text()
>>> # Ignore converting links from HTML
>>> h.ignore_links = True
>>> print h.handle("<p>Hello, <a href='https://www.google.com/earth/'>world</a>!")
Hello, world!

>>> print(h.handle("<p>Hello, <a href='https://www.google.com/earth/'>world</a>!"))

Hello, world!

>>> # Don't Ignore links anymore, I like links
>>> h.ignore_links = False
>>> print(h.handle("<p>Hello, <a href='https://www.google.com/earth/'>world</a>!"))
Hello, [world](https://www.google.com/earth/)!
"""


class FormattedText:
    _plaintext: str
    _markdown: str
    _html: str

    doc = None

    def __new__(cls, **kwargs):
        self = object.__new__(cls)

        self._plaintext = ""
        self._markdown = ""
        self._html = ""

        return self

    def __init__(
        self,
        plaintext: str = None,
        markdown: str = None,
        html: str = None
        ) -> None:
        self.set_plaintext(plaintext)
        self.set_markdown(markdown)
        self.set_html(html)

    def set_plaintext(self, plaintext: str):
        if plaintext is None:
            return

        self._plaintext = plaintext

    def set_markdown(self, markdown: str):
        if markdown is None:
            return

        self._markdown = markdown

    def set_html(self, html: str):
        if html is None:
            return
        self.doc = pandoc.read(html, format="html")

    def get_markdown(self) -> str:
        if self.doc is None:
            return None
        return pandoc.write(self.doc, format="markdown").strip()

    def get_html(self) -> str:
        if self.doc is None:
            return None
        return pandoc.write(self.doc, format="html").strip()


class NotesAttributes:
    def __init__(self) -> None:
        pass

if __name__ == "__main__":
    markdown = """
# World of Work

1. The right to help out society, and being paied for it
2. **The right to get paied, so you can get along well.**
3. The right for every individual to sell their products to provide for themselfes or for others
4. The right of fair competitions, meaning eg. no monopoles.
5. **The right for a home.**
6. **The right to good healthcare**
7. The right of protections against tragedies, be it personal ones, or global ones.
8. The right to be educated in a way that enables you to work.

## 3 most important ones

1. The right to get paied, so you can get along well.
2. The right for a home.
3. The right for a good healthcare.
    """
    html = """
<b>Contact:</b> <a href="mailto:ghostbath@live.com">ghostbath@live.com</a><br />
<br />
Although the band originally claimed that they were from Chongqing, China, it has been revealed in a 2015 interview with <b>Noisey</b> that they're an American band based in Minot, North Dakota.<br />
<br />
According to the band, "Ghost Bath" refers to "the act of committing suicide by submerging in a body of water."<br />
<br />
<b>Compilation appearance(s):</b><br />
- "Luminescence" on <i>Jericho Vol.36 - Nyctophobia</i> (2018) []
    """

    notes = FormattedText(html=html)
    print(notes.get_html())
    print("-"*30)
    print(notes.get_markdown())