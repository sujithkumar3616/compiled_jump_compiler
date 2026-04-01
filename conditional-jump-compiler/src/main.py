# ── Main: runs all compiler phases ──────────────────────────────────

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from lexer    import tokenize
from parser   import parse
from semantic import analyse
from ir_gen   import generate
from optimizer import optimize
from codegen  import generate_code

DIVIDER = '-' * 45

def run(source):
    print(DIVIDER)
    print('PHASE 1 — LEXER')
    print(DIVIDER)
    tokens = tokenize(source)
    for tok in tokens:
        if tok[0] not in ('NEWLINE', 'EOF'):
            print(f'  {tok[0]:<12} {tok[1]}')

    print()
    print(DIVIDER)
    print('PHASE 2 — PARSER (AST)')
    print(DIVIDER)
    ast = parse(source)
    for node in ast:
        print(' ', node)

    print()
    print(DIVIDER)
    print('PHASE 3 — SEMANTIC ANALYSIS')
    print(DIVIDER)
    sem = analyse(ast)
    print('  Symbols:')
    for name, info in sem['symbols'].items():
        print(f'    {name:<12} type={info["type"]}  line={info["line"]}')
    print('  Defined labels:', sem['defined_labels'])
    print('  Used labels:   ', sem['used_labels'])
    for w in sem['warnings']:
        print(' ', w)

    print()
    print(DIVIDER)
    print('PHASE 4 — INTERMEDIATE REPRESENTATION (IR)')
    print(DIVIDER)
    ir = generate(ast)
    for i, ins in enumerate(ir, 1):
        print(f'  {i:>3}  {ins["op"]:<10} {ins["a"]:<10} {ins["b"]:<6} {ins["c"]}')

    print()
    print(DIVIDER)
    print('PHASE 5 — OPTIMIZATION')
    print(DIVIDER)
    opt = optimize(ir)
    print(f'  Instructions before : {len(opt["optimized"])}')
    print(f'  Jumps eliminated    : {opt["removed"]}')
    for c in opt['changes']:
        print(' ', c)

    print()
    print(DIVIDER)
    print('PHASE 6 — CODE GENERATION (OUTPUT)')
    print(DIVIDER)
    asm = generate_code(opt['optimized'])
    for line in asm:
        print(line)
    print()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            source = f.read()
    else:
        source = """\
if x == 0 goto L1
if y != 5 goto L2
while z < 10
  z = z + 1
end
L1: x = 1
L2: y = 2
"""
    run(source)




