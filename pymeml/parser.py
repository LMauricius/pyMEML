import re
from typing import Union, List, Dict, Tuple

# === Data Types ===
class Keyword(str):
    """Represents a keyword distinct from a string."""
    def __repr__(self):
        return f"Keyword({super().__repr__()})"

Value = Union['DictType', 'ListType', float, str, Keyword]
TupleType = Tuple
DictType = Dict[str, TupleType]
ListType = List[TupleType]

# === Tokenization ===
TOKEN_REGEX = re.compile(
    r"""
    [ \t\n]*(
        \n # Newlines
    ) |
    [ \t]*(
        \# [^\n]* |             # Comments
        [{\[\]}:] |          # Braces, brackets, colon
        "[^"\\]*(?:\\.[^"\\]*)*" |  # Double-quoted strings
        '[^'\\]*(?:\\.[^'\\]*)*' |  # Single-quoted strings
        [-+]?\d+\.\d+ |      # Floats
        [-+]?\d+ |           # Integers
        [A-Za-z_][A-Za-z0-9_]*  # Identifiers (keywords)
    )
""",
    re.VERBOSE,
)

def tokenize(text: str) -> List[str]:
    tokens = []
    for match in TOKEN_REGEX.finditer(text):
        token = match.group(1)
        if token is None:
            token = match.group(2)
        if token.startswith('#'):
            continue  # skip comments
        tokens.append(token)
    return tokens

# === Parser ===
class Parser:
    def __init__(self, tokens: List[str]):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected=None):
        token = self.current()
        if expected and token != expected:
            raise SyntaxError(f"Expected '{expected}', got '{token}'")
        self.pos += 1
        return token

    def parse(self) -> DictType:
        return self.parse_dict()

    def parse_dict(self) -> DictType:
        result = {}
        self.consume('{')
        self.consume("\n")
        while self.current() and self.current() != '}':
            key = self.consume()
            self.consume(':')
            tuple_values = self.parse_tuple(until={'\n', None})
            result[key] = tuple_values
            self.consume("\n")
        self.consume('}')
        return result

    def parse_list(self) -> ListType:
        items = []
        self.consume("[")
        self.consume("\n")
        while self.current() and self.current() != ']':
            items.append(self.parse_tuple(until={"\n", None}))
            self.consume("\n")
        self.consume(']')
        return items

    def parse_tuple(self, until: set) -> TupleType:
        values = []
        while self.current() and self.current() not in until and self.current() != ':':
            token = self.current()
            if token == '{':
                values.append(self.parse_dict())
            elif token == '[':
                values.append(self.parse_list())
            else:
                values.append(self.parse_value(token))
                self.pos += 1
        return tuple(values)

    def parse_value(self, token: str) -> Value:
        if re.fullmatch(r'"[^"]*"|\'[^\']*\'', token):
            return token[1:-1]
        elif re.fullmatch(r'-?\d+\.\d+', token):
            return float(token)
        elif re.fullmatch(r'-?\d+', token):
            return int(token)
        elif re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', token):
            return Keyword(token)
        else:
            raise ValueError(f"Invalid token: {token}")