class Source:
    def __init__(self, src_data) -> None:
        self.src_data = src_data

        self.src = self.src_data['src']
        self.url = self.src_data['url']
