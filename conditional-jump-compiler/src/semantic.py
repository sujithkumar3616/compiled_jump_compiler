# ── Semantic Analysis: symbol table + label checks ──────────────────

def analyse(ast):
    symbols       = {}   # name -> {type, line}
    defined_labels = set()
    used_labels    = set()
    warnings       = []

    def scan_labels(nodes):
        for n in nodes:
            if n['kind'] == 'label':
                defined_labels.add(n['name'])
            if n['kind'] in ('cjump', 'goto'):
                used_labels.add(n['target'])
            if 'body' in n:
                scan_labels(n['body'])

    def visit(nodes):
        for n in nodes:
            if n['kind'] == 'assign':
                symbols[n['lhs']] = {'type': 'int', 'line': n['line']}
                if isinstance(n['rhs'], dict):
                    for v in (n['rhs']['a'], n['rhs']['b']):
                        if not v.lstrip('-').isnumeric() and v not in symbols:
                            symbols[v] = {'type': 'int', 'line': n['line']}
                elif not n['rhs'].lstrip('-').isnumeric() and n['rhs'] not in symbols:
                    symbols[n['rhs']] = {'type': 'int', 'line': n['line']}

            if n['kind'] in ('cjump', 'if', 'while'):
                for v in (n['lhs'], n['rhs']):
                    if not v.lstrip('-').isnumeric() and v not in symbols:
                        symbols[v] = {'type': 'int', 'line': n['line']}

            if 'body' in n:
                visit(n['body'])

    scan_labels(ast)
    visit(ast)

    for lbl in used_labels:
        if lbl not in defined_labels:
            warnings.append(f"Warning: label '{lbl}' used but never defined")

    return {
        'symbols':        symbols,
        'defined_labels': defined_labels,
        'used_labels':    used_labels,
        'warnings':       warnings,
    }