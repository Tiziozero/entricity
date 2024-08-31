import re

class ParserError(Exception):
    pass

class Tokenizer:
    def __init__(self, text):
        text = re.sub(r'\s+', '', text)
        print(text)
        self.tokens = re.findall(r'\b\w+\b|{|}|\(|\)|,|;|\".*?\"', text)
        print(self.tokens)
        self.index = 0

    def next_token(self):
        if self.index < len(self.tokens):
            token = self.tokens[self.index]
            self.index += 1
            return token
        return None

    def peek_token(self):
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        return None

class Node:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self):
        return f'{self.type}({self.value}, {self.children})'

class Parser:
    def __init__(self, text):
        self.tokenizer = Tokenizer(text)

    def parse(self):
        return self.parse_canvas()

    def parse_canvas(self):
        if self.tokenizer.next_token() != 'Canvas':
            raise ParserError('Expected "Canvas"')
        if self.tokenizer.next_token() != '(':
            raise ParserError('Expected "("')
        
        width = self.tokenizer.next_token()
        if not width.isdigit():
            raise ParserError('Expected width')
        
        if self.tokenizer.next_token() != ',':
            raise ParserError('Expected ","')
        
        height = self.tokenizer.next_token()
        if not height.isdigit():
            raise ParserError('Expected height')

        if self.tokenizer.next_token() != ')':
            raise ParserError('Expected ")"')
        
        if self.tokenizer.next_token() != '{':
            raise ParserError('Expected "{"')

        canvas_node = Node('Canvas', (int(width), int(height)))

        while self.tokenizer.peek_token() != '}':
            canvas_node.add_child(self.parse_div())

        if self.tokenizer.next_token() != '}':
            raise ParserError('Expected "}"')

        return canvas_node

    def parse_div(self):
        if self.tokenizer.next_token() != 'Div':
            raise ParserError('Expected "Div"')
        if self.tokenizer.next_token() != '(':
            raise ParserError('Expected "("')
        
        x = self.tokenizer.next_token()
        if not x.isdigit():
            raise ParserError('Expected x')
        
        if self.tokenizer.next_token() != ',':
            raise ParserError('Expected ","')

        y = self.tokenizer.next_token()
        if not y.isdigit():
            raise ParserError('Expected y')
        
        if self.tokenizer.next_token() != ',':
            raise ParserError('Expected ","')

        width = self.tokenizer.next_token()
        if not width.isdigit():
            raise ParserError('Expected width')
        
        if self.tokenizer.next_token() != ',':
            raise ParserError('Expected ","')

        height = self.tokenizer.next_token()
        if not height.isdigit():
            raise ParserError('Expected height')

        if self.tokenizer.next_token() != ')':
            raise ParserError('Expected ")"')
        
        if self.tokenizer.next_token() != '{':
            raise ParserError('Expected "{"')

        div_node = Node('Div', (int(x), int(y), int(width), int(height)))

        while self.tokenizer.peek_token() != '}':
            token = self.tokenizer.peek_token()
            if token == 'Img':
                div_node.add_child(self.parse_img())
            elif token == 'Text':
                div_node.add_child(self.parse_text())
            else:
                raise ParserError(f'Unexpected token: {token}')

        if self.tokenizer.next_token() != '}':
            raise ParserError('Expected "}"')

        return div_node

    def parse_img(self):
        if self.tokenizer.next_token() != 'Img':
            raise ParserError('Expected "Img"')
        if self.tokenizer.next_token() != '(':
            raise ParserError('Expected "("')

        src = self.tokenizer.next_token()

        if self.tokenizer.next_token() != ',':
            raise ParserError('Expected ","')

        width = self.tokenizer.next_token()
        if not width.isdigit():
            raise ParserError('Expected width')
        
        if self.tokenizer.next_token() != ',':
            raise ParserError('Expected ","')

        height = self.tokenizer.next_token()
        if not height.isdigit():
            raise ParserError('Expected height')

        if self.tokenizer.next_token() != ')':
            raise ParserError('Expected ")"')

        if self.tokenizer.next_token() != ';':
            raise ParserError('Expected ";"')

        img_node = Node('Img', (src, int(width), int(height)))

        return img_node

    def parse_text(self):
        if self.tokenizer.next_token() != 'Text':
            raise ParserError('Expected "Text"')
        if self.tokenizer.next_token() != '(':
            raise ParserError('Expected "("')

        text = self.tokenizer.next_token()

        if self.tokenizer.next_token() != ')':
            raise ParserError('Expected ")"')

        if self.tokenizer.next_token() != ';':
            raise ParserError('Expected ";"')

        text_node = Node('Text', text)

        return text_node

def parse(text):
    parser = Parser(text)
    return parser.parse()
