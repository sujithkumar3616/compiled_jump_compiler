# ── Code Generator: emits final assembly-like instructions ──────────

def generate_code(opt_ir):
    lines = []

    JMP_MNEM = {
        'JMP_JE':  'JE',  'JMP_JNE': 'JNE',
        'JMP_JL':  'JL',  'JMP_JLE': 'JLE',
        'JMP_JG':  'JG',  'JMP_JGE': 'JGE',
    }

    for ins in opt_ir:
        if ins['elim']:
            continue

        op = ins['op']

        if op == 'LABEL':
            lines.append(f"{ins['a']}:")

        elif op == 'MOV':
            lines.append(f"    MOV  {ins['a']}, {ins['b']}")

        elif op in ('ADD', 'SUB', 'MUL', 'DIV'):
            lines.append(f"    {op}  {ins['a']}, {ins['b']}, {ins['c']}")

        elif op == 'CMP':
            lines.append(f"    CMP  {ins['a']}, {ins['c']}   ; {ins['a']} {ins['b']} {ins['c']}")

        elif op == 'JMP':
            lines.append(f"    JMP  {ins['a']}")

        elif op in JMP_MNEM:
            lines.append(f"    {JMP_MNEM[op]:<4} {ins['a']}")

    return lines