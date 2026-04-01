# ── Parser: builds AST from tokens ─────────────────────────────────

from lexer import tokenize

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos    = 0

    def cur(self):
        return self.tokens[self.pos]

    def eat(self, kind):
        tok = self.cur()
        if tok[0] != kind:
            raise SyntaxError(f'Line {tok[2]}: expected {kind}, got {tok[0]} ({tok[1]!r})')
        self.pos += 1
        return tok

    def skip_newlines(self):
        while self.cur()[0] == 'NEWLINE':
            self.pos += 1

    def parse(self):
        stmts = []
        while self.cur()[0] != 'EOF':
            self.skip_newlines()
            if self.cur()[0] == 'EOF':
                break
            s = self.parse_stmt()
            if s:
                stmts.append(s)
        return stmts

    def parse_stmt(self):
        tok = self.cur()

        # label definition  e.g. L1:
        if tok[0] == 'ID' and self.pos + 1 < len(self.tokens) and self.tokens[self.pos+1][0] == 'COLON':
            name = tok[1]
            self.pos += 2          # skip ID and COLON
            self.skip_newlines()
            return {'kind': 'label', 'name': name, 'line': tok[2]}

        # if x == 0 goto L1  OR  if x == 0 \n ... end
        if tok[0] == 'IF':
            self.pos += 1
            lhs = self.eat('ID')[1]
            op  = self.cur()[1]; self.pos += 1
            rhs = self.cur()[1]; self.pos += 1
            if self.cur()[0] == 'GOTO':
                self.pos += 1
                target = self.cur()[1]; self.pos += 1
                self.skip_newlines()
                return {'kind': 'cjump', 'lhs': lhs, 'op': op, 'rhs': rhs,
                        'target': target, 'line': tok[2]}
            else:
                self.skip_newlines()
                body = []
                while self.cur()[0] not in ('END', 'EOF'):
                    self.skip_newlines()
                    s = self.parse_stmt()
                    if s: body.append(s)
                if self.cur()[0] == 'END': self.pos += 1
                self.skip_newlines()
                return {'kind': 'if', 'lhs': lhs, 'op': op, 'rhs': rhs,
                        'body': body, 'line': tok[2]}

        # while x < 10
        if tok[0] == 'WHILE':
            self.pos += 1
            lhs = self.eat('ID')[1]
            op  = self.cur()[1]; self.pos += 1
            rhs = self.cur()[1]; self.pos += 1
            self.skip_newlines()
            body = []
            while self.cur()[0] not in ('END', 'EOF'):
                self.skip_newlines()
                s = self.parse_stmt()
                if s: body.append(s)
            if self.cur()[0] == 'END': self.pos += 1
            self.skip_newlines()
            return {'kind': 'while', 'lhs': lhs, 'op': op, 'rhs': rhs,
                    'body': body, 'line': tok[2]}

        # goto L1
        if tok[0] == 'GOTO':
            self.pos += 1
            target = self.cur()[1]; self.pos += 1
            self.skip_newlines()
            return {'kind': 'goto', 'target': target, 'line': tok[2]}

        # assignment  x = y + 1
        if tok[0] == 'ID' and self.pos+1 < len(self.tokens) and self.tokens[self.pos+1][0] == 'ASSIGN':
            lhs = tok[1]; self.pos += 2
            a   = self.cur()[1]; self.pos += 1
            if self.cur()[0] in ('PLUS','MINUS','MUL','DIV'):
                bop = self.cur()[1]; self.pos += 1
                b   = self.cur()[1]; self.pos += 1
                self.skip_newlines()
                return {'kind': 'assign', 'lhs': lhs,
                        'rhs': {'op': bop, 'a': a, 'b': b}, 'line': tok[2]}
            self.skip_newlines()
            return {'kind': 'assign', 'lhs': lhs, 'rhs': a, 'line': tok[2]}

        # skip unknown token
        self.pos += 1
        return None


def parse(source):
    tokens = tokenize(source)
    return Parser(tokens).parse()