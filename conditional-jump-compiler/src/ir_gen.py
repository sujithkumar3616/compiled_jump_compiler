# ── IR Generator: produces 3-address code ───────────────────────────

_counter = 0

def _tmp():
    global _counter
    _counter += 1
    return f't{_counter}'

_lbl_counter = 100

def _lbl():
    global _lbl_counter
    _lbl_counter += 1
    return f'__L{_lbl_counter}'

NEG_OP = {'>': '<=', '<': '>=', '>=': '<', '<=': '>',
          '==': '!=', '!=': '=='}

OP_JMP = {'>': 'JG', '<': 'JL', '>=': 'JGE', '<=': 'JLE',
          '==': 'JE', '!=': 'JNE'}

def generate(ast):
    global _counter, _lbl_counter
    _counter = 0
    _lbl_counter = 100
    code = []

    def emit(op, a='', b='', c=''):
        code.append({'op': op, 'a': a, 'b': b, 'c': c})

    def compile_expr(e):
        if isinstance(e, dict):
            la = compile_expr(e['a'])
            lb = compile_expr(e['b'])
            t  = _tmp()
            op_map = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}
            emit(op_map[e['op']], t, la, lb)
            return t
        return str(e)

    def visit(nodes):
        for n in nodes:
            if n['kind'] == 'label':
                emit('LABEL', n['name'])

            elif n['kind'] == 'cjump':
                emit('CMP', n['lhs'], n['op'], n['rhs'])
                emit('JMP_' + OP_JMP[n['op']], n['target'])

            elif n['kind'] == 'goto':
                emit('JMP', n['target'])

            elif n['kind'] == 'assign':
                r = compile_expr(n['rhs'])
                emit('MOV', n['lhs'], r)

            elif n['kind'] == 'if':
                else_lbl = _lbl()
                end_lbl  = _lbl()
                emit('CMP', n['lhs'], n['op'], n['rhs'])
                emit('JMP_' + OP_JMP[NEG_OP[n['op']]], else_lbl)
                visit(n['body'])
                emit('JMP', end_lbl)
                emit('LABEL', else_lbl)
                emit('LABEL', end_lbl)

            elif n['kind'] == 'while':
                start_lbl = _lbl()
                end_lbl   = _lbl()
                emit('LABEL', start_lbl)
                emit('CMP', n['lhs'], n['op'], n['rhs'])
                emit('JMP_' + OP_JMP[NEG_OP[n['op']]], end_lbl)
                visit(n['body'])
                emit('JMP', start_lbl)
                emit('LABEL', end_lbl)

    visit(ast)
    return code