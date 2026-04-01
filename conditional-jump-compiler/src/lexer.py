# ── Lexer: breaks source code into tokens ──────────────────────────

TOKEN_TYPES = [
    ('IF',       r'if'),
    ('WHILE',    r'while'),
    ('GOTO',     r'goto'),
    ('END',      r'end'),
    ('ID',       r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('NUM',      r'[0-9]+'),
    ('EQ',       r'=='),
    ('NEQ',      r'!='),
    ('LTE',      r'<='),
    ('GTE',      r'>='),
    ('LT',       r'<'),
    ('GT',       r'>'),
    ('ASSIGN',   r'='),
    ('PLUS',     r'\+'),
    ('MINUS',    r'-'),
    ('MUL',      r'\*'),
    ('DIV',      r'/'),
    ('COLON',    r':'),
    ('NEWLINE',  r'\n'),
    ('SKIP',     r'[ \t]+'),
    ('MISMATCH', r'.'),
]

import re

KEYWORDS = {'if', 'while', 'goto', 'end'}

def tokenize(source):
    tokens = []
    master = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_TYPES)
    for line_num, line in enumerate(source.splitlines(), 1):
        for mo in re.finditer(master, line):
            kind  = mo.lastgroup
            value = mo.group()
            if kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise SyntaxError(f'Line {line_num}: unexpected character {value!r}')
            else:
                # check for label  e.g.  L1:
                if kind == 'ID' and value in KEYWORDS:
                    kind = value.upper()
                tokens.append((kind, value, line_num))
        tokens.append(('NEWLINE', '\\n', line_num))
    tokens.append(('EOF', '', 0))
    return tokens