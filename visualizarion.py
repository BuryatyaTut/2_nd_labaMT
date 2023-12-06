from graphviz import Digraph

# Define token regex patterns
TOKENS = {
    'VAR': r'var',
    'IDENTIFIER': r'[a-zA-Z_][a-zA-Z0-9_]*',  # Variable names
    'COLON': r':',
    'ARRAY': r'Array',
    'LT': r'<',
    'GT': r'>',
    'SEMICOLON': r';',
    'WHITESPACE': r'[ \t\n]+',  # To be skipped
    'UNKNOWN': r'.',  # Any other character
}


def tokenize(code):
    tokens = []
    i = 0
    while i < len(code):
        char = code[i]

        # Skipping whitespaces
        if char in ' \t\n':
            i += 1
            continue

        # Tokenizing 'var'
        elif char == 'v' and code[i:i + 3] == 'var':
            tokens.append(('VAR', 'var'))
            i += 3

        # Tokenizing 'Array'
        elif char == 'A' and code[i:i + 5] == 'Array':
            tokens.append(('ARRAY', 'Array'))
            i += 5

        # Tokenizing identifiers (variable names and types)
        elif char.isalpha() or char == '_':
            start = i
            while i < len(code) and (code[i].isalnum() or code[i] == '_'):
                i += 1
            tokens.append(('IDENTIFIER', code[start:i]))

        # Tokenizing single character tokens
        elif char == ':':
            tokens.append(('COLON', ':'))
            i += 1
        elif char == '<':
            tokens.append(('LT', '<'))
            i += 1
        elif char == '>':
            tokens.append(('GT', '>'))
            i += 1
        elif char == ';':
            tokens.append(('SEMICOLON', ';'))
            i += 1

        # Handling unknown characters
        else:
            raise SyntaxError(f"Unknown character: {char}")

    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.next_token()
        self.tree = Digraph()
        self.node_count = 0

    def next_token(self):
        self.current_token = self.tokens.pop(0) if self.tokens else None

    def match(self, token_type, parent):
        content = f"{token_type}: {self.current_token[1]}"
        node_id = self.add_node(parent, content, is_terminal=True)
        if not self.current_token or self.current_token[0] != token_type:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token}")
        self.next_token()
        return node_id

    def add_node(self, parent, label, is_terminal=False):
        node_id = f'node{self.node_count}'
        if is_terminal:
            self.tree.node(node_id, label, style='filled', color='lightblue')
        else:
            self.tree.node(node_id, label)
        if parent is not None:
            self.tree.edge(parent, node_id)
        self.node_count += 1
        return node_id

    def parse_array_type(self, parent):
        array_node = self.add_node(parent, 'ArrayType')
        self.match('ARRAY', array_node)
        self.match('LT', array_node)
        self.parse_type(array_node)
        self.match('GT', array_node)

    def parse_type(self, parent):
        type_node = self.add_node(parent, 'Type')
        if self.current_token and self.current_token[0] == 'ARRAY':
            self.parse_array_type(type_node)
        else:
            self.match('IDENTIFIER', type_node)

    def parse(self):
        root = self.add_node(None, 'S')
        self.match('VAR', root)
        self.match('IDENTIFIER', root)
        self.match('COLON', root)
        self.parse_array_type(root)
        if self.current_token and self.current_token[0] == 'SEMICOLON':
            self.match('SEMICOLON', root)

    def visualize(self, filename='parse_tree'):
        self.tree.render(filename, format='png', view=True)


test_input = "var g_g: Array<Array<Array<Array<Long>>>>;"
tokens = tokenize(test_input)
parser = Parser(tokens)
parser.parse()
parser.visualize()
