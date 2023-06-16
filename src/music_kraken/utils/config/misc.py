from .base_classes import Section, IntAttribute, ListAttribute, BoolAttribute


class MiscSection(Section):
    def __init__(self):
        self.ENABLE_RESULT_HISTORY = BoolAttribute(
            name="result_history",
            description="If enabled, you can go back to the previous results.\n"
                        "The consequence is a higher meory consumption, because every result is saved.",
            value="false"
        )
        
        self.HISTORY_LENGTH = IntAttribute(
            name="history_length",
            description="You can choose how far back you can go in the result history.\n"
                        "The further you choose to be able to go back, the higher the memory usage.\n"
                        "'-1' removes the Limit entirely.",
            value="8"
        )
        
        self.HAPPY_MESSAGES = ListAttribute(
            name="happy_messages",
            description="Just some nice and wholesome messages.\n"
                        "If your mindset has traits of a [file corruption], you might not agree.\n"
                        "But anyways... Freedom of thought, so go ahead and change the messages.",
            value=[
                "Support the artist.",
                "Star Me: https://github.com/HeIIow2/music-downloader",
                "🏳️‍⚧️🏳️‍⚧️ Trans rights are human rights. 🏳️‍⚧️🏳️‍⚧️",
                "🏳️‍⚧️🏳️‍⚧️ Trans women are women, trans men are men, and enbies are enbies. 🏳️‍⚧️🏳️‍⚧️",
                "🏴‍☠️🏴‍☠️ Unite under one flag, fck borders. 🏴‍☠️🏴‍☠️",
                "Join my Matrix Space: https://matrix.to/#/#music-kraken:matrix.org",
                "Gotta love the BPJM ;-;",
                "🏳️‍⚧️🏳️‍⚧️ Protect trans youth. 🏳️‍⚧️🏳️‍⚧️",
            ]
        )

        self.MODIFY_GC = BoolAttribute(
            name="modify_gc",
            description="If set to true, it will modify the gc for the sake of performance.\n"
                        "This should not drive up ram usage, but if it is, then turn it of.\n"
                        "Here a blog post about that matter:\n"
                        "https://mkennedy.codes/posts/python-gc-settings-change-this-and-make-your-app-go-20pc-faster/\n"
                        "https://web.archive.org/web/20221124122222/https://mkennedy.codes/posts/python-gc-settings-change-this-and-make-your-app-go-20pc-faster/",
            value="true"
        )

        self.ID_BITS = IntAttribute(
            name="id_bits",
            description="I really dunno why I even made this a setting.. Modifying this is a REALLY dumb idea.",
            value="64"
        )

        self.attribute_list = [
            self.ENABLE_RESULT_HISTORY,
            self.HISTORY_LENGTH,
            self.HAPPY_MESSAGES,
            self.MODIFY_GC,
            self.ID_BITS
        ]

        super().__init__()


MISC_SECTION = MiscSection()
