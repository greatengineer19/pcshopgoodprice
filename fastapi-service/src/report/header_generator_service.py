class HeaderGeneratorService:
    def __init__(self):
        self.builder = []

    def call(self, text_headers):
        for text_header in text_headers:
            self.builder.append({ 'text': text_header })

        return self.builder