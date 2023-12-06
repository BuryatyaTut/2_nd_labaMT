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

    def next_token(self):
        self.current_token = self.tokens.pop(0) if self.tokens else None

    def match(self, token_type):
        if not self.current_token or self.current_token[0] != token_type:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token}")
        self.next_token()

    def parse_array_type(self):
        # ArrayType -> 'Array' '<' Type '>'
        self.match('ARRAY')
        self.match('LT')
        self.parse_type()
        self.match('GT')

    def parse_type(self):
        # Type -> IDENTIFIER | ArrayType
        if self.current_token and self.current_token[0] == 'ARRAY':
            self.parse_array_type()
        else:
            self.match('IDENTIFIER')

    def parse_optional_semicolon(self):
        if self.current_token and self.current_token[0] == 'SEMICOLON':
            self.match('SEMICOLON')

    def parse(self):
        # S -> 'var' IDENTIFIER ':' ArrayType
        self.match('VAR')
        self.match('IDENTIFIER')
        self.match('COLON')
        self.parse_array_type()
        self.parse_optional_semicolon()

        if self.current_token:
            raise SyntaxError("Unexpected input after array declaration")


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
        ("var h: Array< List <String> >;", False),

        # Invalid Inputs
        ("x: Array<Int>;", False),
        ("var i: Array<>;", False),
        ("var j: Array;", False),
        ("var k: Int;", False),
        ("var : Array<String>;", False),
        ("var l: Array<Int> extra;", False),
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
        ("var Array<Int> w;", False)
    ]

    for input, should_pass in test_cases:
        try:
            tokens = tokenize(input)
            parser = Parser(tokens)
            parser.parse()
            if not should_pass:
                print(f"Test failed (should not pass): {input}")
        except SyntaxError:
            if should_pass:
                print(f"Test failed (should pass): {input}")



def main():
    # Test the lexer
    code = "var      Aboba_heh:Array<Int>"
    tokens = tokenize(code)
    print(tokens)

    # Test the updated parser with and without semicolon
    test_inputs = [
        "var x: Array  <Int>;",  # With semicolon
        "var x: Array<Int>",  # Without semicolon
        "var x: Array<Array<Int>>;",
        ""
    ]
    test_results = []
    for input_str in test_inputs:
        tokens = tokenize(input_str)
        parser = Parser(tokens)
        try:
            parser.parse()
            test_results.append(f"Input accepted: {input_str}")
        except SyntaxError as e:
            test_results.append(f"Syntax error in '{input_str}': {str(e)}")
    print(test_results)


if __name__ == '__main__':
    run_tests()
