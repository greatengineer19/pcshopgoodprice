class RowBuilder:
    def __init__(self):
        self.builder = []

    def append_text(self, text):
        self.builder.append({ 'text': text, 'cell_type': 'text' })   

        return self
    
    def append_quantity(self, text):
        self.builder.append({ 'text': text, 'cell_type': 'quantity' })   

        return self
    
    def append_money(self, text):
        self.builder.append({ 'text': text, 'cell_type': 'money' })   

        return self

    def build(self):
        return self.builder