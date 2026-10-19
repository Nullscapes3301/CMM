r"""
-> cmmtools
very important tools for CMM like
cmmtools.split_commands() -> split commands of CMM using commas(,)
cmmtools.get_cmm_code() -> transform a raw text to normal CMM instruccions
cmmtools.seval() -> the heart of CMM
"""
import cmmcommands
import cmmerrors
import copy

def split_commands(text):
    result = []
    current = []
    depth = 0
    text = str(text)
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            if depth > 0:
                depth -= 1
        if char == "," and depth == 0:
            result.append("".join(current))
            current = []
        else:
            current.append(char)
    if current:
        result.append("".join(current))
    return result

def get_cmm_code(prompt):
    prompt = str(prompt)
    if not prompt.startswith("cmm-"):
        raise cmmerrors.SyntaxError("Invalid syntax: CMM scripts must start with 'cmm-'")
    if not prompt.endswith("."):
        raise cmmerrors.SyntaxError("Invalid syntax: CMM scripts must finish with '.'")
    cm = prompt[4:-1]
    cm = cm.replace("\n", "")
    if len(cm) == 0:
        raise Exception("Invalid syntax: CMM scripts cannot be null")
    return split_commands(cm)

coms = copy.deepcopy(cmmcommands.commands)

def seval(code):
    code = str(code)
    code = split_commands(code)
    codex = []
    for i in code:
        kk = i.split("(")
        k = kk[0]
        codex.append(coms[k](i))
    if len(codex) == 1:
        return codex[0]
    codez = ""
    for i in codex:
        codez += str(i)
    return codez
