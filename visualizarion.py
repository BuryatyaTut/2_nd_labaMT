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
    'AMPERSAND': '&',
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

        elif char == '&':
            tokens.append(('AMPERSAND', '&'))
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

    # ======================================
    def parse_type_list(self, parent):
        type_list_node = self.add_node(parent, 'TypeList')
        self.parse_type(type_list_node)
        self.parse_type_tail(type_list_node)

    def parse_type_tail(self, parent):
        while self.current_token and self.current_token[0] == 'AMPERSAND':
            ampersand_node = self.add_node(parent, 'Ampersand')
            self.match('AMPERSAND', ampersand_node)
            self.parse_type(ampersand_node)

    def parse_type(self, parent):
        type_node = self.add_node(parent, 'Type')
        if self.current_token and self.current_token[0] == 'ARRAY':
            self.parse_array_type(type_node)
        else:
            self.match('IDENTIFIER', type_node)

    def parse_array_type(self, parent):
        array_node = self.add_node(parent, 'ArrayType')
        self.match('ARRAY', array_node)
        self.match('LT', array_node)
        self.parse_type_list(array_node)
        self.match('GT', array_node)

    # ==========================================

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


def run_tests():
    test_cases = [
         # Valid Inputs
        ("var a: Array<Int>;", True),
        ("var b: Array<String>", True),
        ("var c: Array<Array<Float>>;", True),
        ("var dhjhj: Array<Array<Array<Boolean>>>", True),
        ("var e : Array < Double >;", True),
        ("var f: Array<CustomType123>;", True),
        ("var g_g: Array<Array<Array<Array<Long>>>>", True),

        # Invalid Inputs
        ("x: Array<Int>;", False),
        ("var i: Array<>;", False),
        ("var j: Array;", False),
        ("var k: Int;", False),
        ("var : Array<String>;", False),
        ("var l: Array_<Int>;", False),
        ("var m: Array<Array<>>;", False),
        ("var n: Array<Int#>;", False),
        ("var o Array<String>;", False),
        ("var p: <Array<Int>>;", False),
        ("Array<Int> var q;", False),
        ("var r: Array<Array<Int> String>;", False),
        ("var s: Array<Array;>", False),
        ("var t: Array<1Int>;", False),
        ("var u: Array<Array_>", False),
        ("var v: ;", False),
        ("var Array<Int> w;", False),

        # AMPERSAND VALID
        ("var x: Array<Int&String&Double>;", True),
        ("var y: Array<Array<Int&Float>>;", True),
        ("var z: Array<Array<Array<String&Int>>>;", True),
        ("var a: Array<CustomType&AnotherType>;", True),
        ("var b: Array<Int&Int>;", True),
        ("var c: Array<Array<Int>&Array<Float>>;", True),
        ("var d: Array<Array<Int&String>>;", True),
        ("var e: Array<Int&Array<String>>;", True),
        ("var f: Array<Array<Int>&String>;", True),
        ("var g: Array<Array<Array <Int&Float> > &    Double>;", True),
        ("var b: Array<Int & Float>;", True),
        ("var f: Array<Int &Array<Float>>;", True),
        ("var g: Array<Int & Array<String> & Double>;", True),

        # AMPERSAND INVALID
        ("var x: Array<&Int&String>;", False),
        ("var y: Array<Int&&Float>;", False),
        ("var z: Array<Int&>;", False),
        ("var a: Array<>&Float>;", False),
        ("&var c: Array<Int&Float>;", False),
        ("var d: Array<>&String&Int>;", False),
        ("var e: Array<Int&String&>;", False),
        ("var x: Array<Arraay<Int>>;", False),
        ("var y: Array<Array<Int>&>;", False),
        ("var z: Array<Int&Float&>;", False),
        ("var a: &Array<Int>;", False),
        ("var b: Array<Array<Int>&Array>; ", False),
        ("var c: Array<Array<>>;", False),
        ("var d: Array<Identifer&>;", False),
        ("var e: Array<>&Array<Int>>;", False),
        ("var f: Array<Int&&&Float>;", False),
        ("var g: Array<Array<Int&String&&Double>>;", False)

    ]

    failed_tests_cnt = 0
    for input, should_pass in test_cases:
        try:
            tokens = tokenize(input)
            parser = Parser(tokens)
            parser.parse()
            if not should_pass:
                print(f"!!!!!!!!!!!!!!!!!!!Test failed (should not pass): {input}")
                failed_tests_cnt += 1
            else:
                print("test success |", input)
        except SyntaxError:
            if should_pass:
                print(f"!!!!!!!!!!!!!!!!!!!Test failed (should pass): {input}")
                failed_tests_cnt += 1
            else:
                print("test success (failing) |", input)

    print(f"{failed_tests_cnt} tests failed")


def main():
    # test_input = "var g: Array<Int & Array<String> & Double>;"
    test_input = "var g: Array<Int & String>"
    tokens = tokenize(test_input)
    print(tokens)
    parser = Parser(tokens)
    parser.parse()
    parser.visualize()


if __name__ == '__main__':
    # run_tests()
    main()
