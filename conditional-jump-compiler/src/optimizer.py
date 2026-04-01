# ── Optimizer: eliminates redundant jump instructions ───────────────

def optimize(ir):
    code    = [dict(ins, elim=False, reason='') for ins in ir]
    changes = []

    # Pass 1: goto L where next instruction is L (fall-through)
    for i in range(len(code) - 1):
        if not code[i]['elim'] and code[i]['op'] == 'JMP':
            if code[i+1]['op'] == 'LABEL' and code[i+1]['a'] == code[i]['a']:
                code[i]['elim']   = True
                code[i]['reason'] = 'fall-through'
                changes.append(
                    f"Instr {i+1}: JMP {code[i]['a']} removed — target is next instruction")

    # Pass 2: duplicate conditional jumps to the same label
    seen = {}
    for i, ins in enumerate(code):
        if ins['elim']:
            continue
        if ins['op'] in ('LABEL', 'JMP'):
            seen.clear()
            continue
        if ins['op'].startswith('JMP_'):
            key = ins['op'] + '_' + ins['a']
            if key in seen:
                code[i]['elim']   = True
                code[i]['reason'] = 'duplicate cjump'
                changes.append(
                    f"Instr {i+1}: duplicate {ins['op']} {ins['a']} removed")
            else:
                seen[key] = i

    # Pass 3: consecutive unconditional gotos to same target
    for i in range(len(code) - 1):
        if (not code[i]['elim'] and not code[i+1]['elim']
                and code[i]['op'] == 'JMP' and code[i+1]['op'] == 'JMP'
                and code[i]['a'] == code[i+1]['a']):
            code[i+1]['elim']   = True
            code[i+1]['reason'] = 'consecutive goto'
            changes.append(
                f"Instr {i+2}: consecutive JMP {code[i+1]['a']} removed")

    removed = sum(1 for ins in code if ins['elim'])
    return {'optimized': code, 'changes': changes, 'removed': removed}