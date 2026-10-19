r"""
-> cmmcommands
Here are ALL the commands for CMM
Including the dict to call each
Used by the main file to execute each command
"""
# imports
import sys
import time
import ast
import subprocess
import threading
import os
import shutil
import re
from decimal import Decimal
import cmmtools
from cmmerrors import *
_vm = None

def __set__(vm):
    global _vm
    _vm = vm

def noth(*args):
    return None

def _true(*args):
    return True

def _false(*args):
    return False

def _pr(text):
    txt = text[3:-1]
    txttp = cmmtools.seval(txt)
    if txttp is None:
        return
    for char in str(txttp):
        if not char.isprintable():
            raise PrintError("Char non printable")
    _vm.stdout(txttp)

def _txt(text):
    txt = text[4:-1]
    return txt

def _inp(text):
    txt = text[4:-1]
    txttp = cmmtools.seval(txt)
    if txttp is None:
        return
    try:
        temp = _vm.stdin(txttp)
        return temp
    except EOFError:
        raise EOF("EOF when reading an input")

def _dvar(text):
    var = text.split(")ac(")
    var_name = var[0][6:]
    var_content = cmmtools.seval(var[1][:-2])
    if var_name in _vm.vars:
        raise VarExistError("Cannot create a variable that exists")
    if "__" in var_name:
        raise InvalidVarNameError("Variable cannot contain __")
    if var_name.startswith("&"):
        if not var_content in _vm.vars:
            raise VarNotExistError(f"Variable '{var_content}' doesn't exists")
        if "__" in var_content:
            raise PointerError(f"Cannot point to a builtin variable")
        if var_content.startswith("*"):
            raise PointerError(f"Cannot point to a constant")
    _vm.vars[var_name] = var_content

def _nvar(text):
    var = text.split(")ac(")
    var_name = var[0][6:]
    var_content = cmmtools.seval(var[1][:-2])
    if not var_name in _vm.vars:
        raise VarNotExistError(f"NameError Variable '{var_name}' does not exists")
    if "__" in var_name:
        raise VarModifyError("Cannot modify builtin variables")
    if var_name.startswith("*"):
        raise VarModifyError("Cannot modify constants")
    if var_name.startswith("&"):
        if _vm.vars[var_name].startswith("*"):
            raise VarModifyError("Cannot modify builtin variables")
        if "__" in _vm.vars[var_name]:
            raise VarModifyError("Cannot modify constants")
        if var_name in _vm.vars:
            _vm.vars[_vm.vars[var_name]] = var_content
        else:
            raise VarNotExistError(f"Variable '{var_name}' doesn't exists")
        return
    _vm.vars[var_name] = var_content

def _var(text):
    var_name = text[4:-1]
    if var_name not in _vm.vars:
        raise VarNotExistError(f" Variable '{var_name}' does not exists")
    if var_name.startswith("&"):
        return _vm.vars[_vm.vars[var_name]]
    return _vm.vars[var_name]

def _cosh(text):
    text = text[5:-1]
    args = []
    arg = ""
    level = 0
    for c in text:
        if c == "(":
            level += 1
        elif c == ")":
            level -= 1
        if c == "," and level == 0:
            args.append(arg)
            arg = ""
        else:
            arg += c
    args.append(arg)
    arg_bool_r = args[0][1:-1]
    arg_code_r = args[1][1:-1]
    arg_bool = cmmtools.seval(arg_bool_r)
    arg_code = cmmtools.seval(arg_code_r)
    while not arg_bool:
        cmmtools.seval(arg_code)
        arg_bool = cmmtools.seval(arg_bool_r)

def _len(text):
    arg = text[4:-1]
    kk = cmmtools.seval(arg)
    return len(kk)

def _type(text):
    arg = text[5:-1]
    kk = cmmtools.seval(arg)
    kkk = type(kk).__name__
    return kkk

def _sinh(text):
    arg = text[5:-1]
    while True:
        argg = cmmtools.seval(arg)
        if argg == "True":
            break

def _if(text):
    args = text[3:-1]
    parts = cmmtools.split_commands(args)
    condition = cmmtools.seval(parts[0][1:-1])
    if condition:
        cmmtools.seval(parts[1][1:-1])
    elif len(parts) > 2:
        cmmtools.seval(parts[2][1:-1])

def _bool(text):
    cond = text[6:-2]
    args = cond.split("),(")
    left = cmmtools.seval(args[0])
    op = cmmtools.seval(args[1])
    right = cmmtools.seval(args[2])
    if op == "==":
        return left == right
    elif op == "!=":
        return left != right
    elif op == "<":
        return left < right
    elif op == ">":
        return left > right
    elif op == "<=":
        return left <= right
    elif op == ">=":
        return left >= right
    else:
        raise NotABoolError(f"Invalid boolean operator: {op}")

def _totype(text):
    args = cmmtools.split_commands(text[7:-1])
    value = cmmtools.seval(args[0])
    typ = cmmtools.seval(args[1])
    if typ == "int":
        return int(value)
    elif typ == "str":
        return str(value)
    elif typ == "float":
        return float(value)
    elif typ == "bool":
        return bool(value)
    elif typ == "list":
        value = cmmtools.seval(f"list({value})")
        return value
    else:
        raise NotATypeError(f"'{typ}' is not a valid type")

def _exec(text):
    code = text[5:-1]
    return cmmtools.seval(cmmtools.seval(code))

def _goto(text):
    try:
        id = text[5:-1]
        _vm.block = _vm.ids[id] 
    except KeyError:
        raise NotExistError(f"The id '{id}' is not asostied with a block")

def _id(text):
    id = text[3:-1]
    _vm.ids[id] = _vm.block

def _num(text):
    arg = text[4:-1]
    try:
        return int(arg)
    except ValueError:
        raise TypeError("num() only accept integer values")

def _calc(text):
    args = cmmtools.split_commands(text[5:-1])
    calcul = ""
    for arg in args:
        calcul += str(cmmtools.seval(arg))
    if not re.fullmatch(r"[0-9+\-*/%().,\s]+", calcul):
        raise TypeError("calc() only admits numbers and mathematical operators")
    calcul = re.sub(
        r'(?<![\w.])(\d+\.\d+)',
        r'Decimal("\1")',
        calcul
    )
    try:
        return eval(calcul, {"Decimal": Decimal}, {})
    except ZeroDivisionError:
        raise ZeroDivisionError("Cannot divide by zero")

def _for(text):
    args = []
    actual = ""
    level = 0
    content = text[4:-1]
    for c in content:
        if c == "(":
            level += 1
        elif c == ")":
            level -= 1
        if c == "," and level == 0:
            args.append(actual)
            actual = ""
        else:
            actual += c
    args.append(actual)
    var = args[0][1:-1]
    ran = args[1]
    code = args[2][1:-1]
    if ran.startswith("(list("):
        elements = cmmtools.seval(ran[1:-1])
        for element in elements:
            _vm.vars[var] = element
            cmmtools.seval(code)
    else:
        ran = ran.split("to")
        start = cmmtools.seval(ran[0][1:-1])
        ran = ran[1].split("by")
        end = cmmtools.seval(ran[0][1:-1])
        step = cmmtools.seval(ran[1][1:-1])
        counter = start
        while counter < end:
            _vm.vars[var] = counter
            cmmtools.seval(code)
            counter += step
    if var in _vm.vars:
        del _vm.vars[var]

def _delay(text):
    def d(num):
        time.sleep(num)
    k = text[7:-2]
    kk = k.split("),(")
    try:
        num = int(kk[0])
    except ValueError:
        raise TypeError("Time must be an integer base 10")
    lon = kk[1]
    if lon == "ns":
        d(num/1000000000)
    elif lon == "ms":
        d(num/1000)
    elif lon == "s":
        d(num)
    elif lon == "ds":
        d(num*10)
    elif lon == "min":
        d(num*60)
    elif lon == "dmin":
        d(num*600)
    elif lon == "h":
        d(num*3600)
    else:
        raise NotATimeUnitError(f"Invalid time unit: {lon}")

def _be(text):
    if _vm.vars["__safemode__"]:
        raise SafeModeError("Cannot use be in safe mode")
    k = text[3:-1]
    kk = k.split(")ac(")
    program = cmmtools.seval(kk[0])
    cmd_id = kk[1]
    if cmd_id.startswith("cmd1m"):
        if any(char.isdigit() for char in cmd_id[5:]):
            raise NameError("Names for programs cannot have numbers")
        elif " " in cmd_id:
            raise NameError("The program ID cannot have spaces")
        else:
            pass
    else:
        raise NameError("Names for programs must start with 'cmd1m'")
    def create_bee(program, cmd_id):
        process = subprocess.Popen(
            program,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        _vm.bees[cmd_id] = process
    create_bee(program, cmd_id)

def _send(text):
    if _vm.vars["__safemode__"]:
        raise SafeModeError("Cannot use send in safe mode")
    k = text[6:-1]
    args = k.rsplit(")to(", 1)
    msg = args[0]
    cmd_id = args[1].rstrip(")")
    msg = cmmtools.seval(msg)
    if cmd_id not in _vm.bees:
        raise NotExistError(f"'{cmd_id}' does not exist")
    process = _vm.bees[cmd_id]
    process.stdin.write(msg + "\n")
    process.stdin.flush()

def _dec(text):
    arg = text[4:-1]
    if arg == "cmm":
        raise CMMExit()
    elif arg.startswith("cmd1m"):
        if not arg in _vm.bees:
            raise NotExistError(f"'{arg}' does not exist")
        bee = _vm.bees.get(arg)
        if bee:
            bee.kill()
        del _vm.bees[arg]
    else:
        raise SyntaxError("Invalid syntax in dec()")
    
def _try(text):
    code = text[4:-1]
    try:
        return cmmtools.seval(code)
    except CMMExit:
        raise CMMExit() from None
    except Exception as temp:
        err = type(temp).__name__
        return err
    
def _extra(text):
    code = text[6:-1]
    threading.Thread(target=cmmtools.seval, args=(code,)).start()

def _list(text):
    rls = text[5:-1]
    try:
        value = ast.literal_eval(rls)
    except (SyntaxError, ValueError):
        raise SyntaxError(f"'{rls}' is not a valid list literal")
    if not isinstance(value, list) or not isinstance(value, dict):
        raise TypeError(f"T'{rls}' is not a list")
    return value

def _wget(text):
    if _vm.vars["__safemode__"]:
        raise SafeModeError("Cannot use wget in safe mode")
    import urllib.request
    url = cmmtools.seval(text[5:-1])
    try:
        filename = url.split("/")[-1]
        if filename == "":
            raise NameError("File cannot be ''")
        with urllib.request.urlopen(url) as response:
            data = response.read()
            return data
    except Exception as e:
        raise GenericError(e)
    
def _all(text):
    mod = cmmtools.seval(text[4:-1])
    if mod in _vm.modules:
        raise NotExistError(f"Module '{mod}' already loaded")
    if not mod.endswith(".cmm2"):
        raise NameError("CMM modules only uses .cmm2 archives")
    try:
        with open(mod, "r") as cmmc:
            _vm.modules[mod[:-5]] = cmmc.read()
    except FileNotFoundError:
        raise NotExistError(f"Module '{mod}' doesnt exist")
    
def _ell(text):
    txtk = text[5:-2]
    txt = txtk.split("),(")
    mod = cmmtools.seval(txt[0])
    args = txt[1]
    _vm.vars["__ell__"] = str(args)
    cmmtools.seval(_vm.modules[mod])

def _getelem(text):
    txtk = text[9:-2]
    txt = txtk.split("),(")
    elem = cmmtools.seval(txt[0])
    ls = cmmtools.seval(txt[1])
    if not isinstance(ls, list):
        raise TypeError("Cannot get an element from an object which is not a list")
    try:
        return ls[elem-1]
    except IndexError:
        raise IndexError(f"Index '{elem}' is out of range")
    except TypeError:
        raise IndexError(f"Invalid index '{elem}'")
        
def _append(text):
    txtk = text[8:-2]
    txt = txtk.split("),(")
    elem = cmmtools.seval(txt[0])
    ls = cmmtools.seval(txt[1])
    if not isinstance(ls, list):
        raise TypeError("Cannot append an element to an object which is not a list")
    ls.append(elem)

def _setelem(text):
    ktxt = text[9:-2]
    txt = ktxt.split("),(")
    pos = cmmtools.seval(txt[0])
    ls = cmmtools.seval(txt[1])
    val = cmmtools.seval(txt[2])
    if not isinstance(ls, list):
        raise TypeError("Cannot set an element in an object which is not a list")
    try:
        ls[pos-1] = val
    except IndexError:
        raise IndexError(f"Cannot set element '{pos}'")
    
def _delelem(text):
    txtk = text[8:-2]
    txt = txtk.split("),(")
    pos = cmmtools.seval(txt[0])
    ls = cmmtools.seval(txt[1])
    if not isinstance(ls, list):
        raise TypeError("Cannot delete an element from an object which is not a list")
    if not isinstance(pos, int) or pos < 1:
        raise TypeError(f"Invalid index '{pos}'")
    try:
        del ls[pos-1]
    except IndexError:
        raise IndexError(f"Cannot delete element '{pos}'")
    
def _dfunc(text):
    # dfunc((...),(...),(...))
    ktxt = text[6:-1]
    txt = cmmtools.split_commands(ktxt)
    name = txt[0][1:-1]
    vars = txt[1][1:-1]
    code = txt[2][1:-1]
    _vm.func[name] = {
        "code": code,
        "vars": vars
    }

def _func(text):
    # func((...),(...,...))
    ktxt = text[6:-2]
    txt = ktxt.split("),(")
    name = txt[0]
    vars = txt[1].split(",")
    if not name in _vm.func:
        raise FuncNotExistError(f"Function '{name}' doesn't exist")
    if not len(vars) == len(_vm.func[name]["vars"]):
        raise ArgsError("Functions must receive full arguments")
    n = 0
    temp = []
    for i in vars:
        n += 1
        _vm.vars[f"__fv{n}__"] = cmmtools.seval(i)
        temp.append(f"__fv{n}__")
    _vm.vars["__inside_func__"] = True
    cmmtools.seval(_vm.func[name]["code"])
    _vm.vars["__inside_func__"] = False
    for i in temp:
        del _vm.vars[i]

def _none(*args):
    return None

def _save(text):
    args = text[6:-2]
    args = args.split(")ac(")
    path = cmmtools.seval(args[1])
    content = str(cmmtools.seval(args[0]))
    with open(path, "w") as f:
        f.write(content)

def _seefile(text):
    txt = text[8:-1]
    path = cmmtools.seval(txt)
    if not os.path.exists(path):
        raise FileNotFoundError("Directory doesn't exists")
    with open(path, "r") as f:
        kk = f.read()
    return kk

def _savec(text):
    path = cmmtools.seval(text[6:-1])
    os.makedirs(path, exist_ok=True)

def _delc(text):
    if _vm.vars["__safemode__"]:
        raise SafeModeError("Cannot use delc in safe mode")
    path = cmmtools.seval(text[5:-1])
    if not os.path.exists(path):
        raise FileNotFoundError("Directory doesn't exists")
    shutil.rmtree(path)
        

def _move(text):
    if _vm.vars["__safemode__"]:
        raise SafeModeError("Cannot use move in safe mode")
    txt = cmmtools.seval(text[6:-2])
    args = txt.split("),(")
    src = args[0]
    dst = args[1]
    if not os.path.exists(src):
        raise FileNotFoundError("File or directory doesn't exists")
    shutil.move(src, dst)

def _del(text):
    if _vm.vars["__safemode__"]:
        raise SafeModeError("Cannot use del in safe mode")
    path = cmmtools.seval(text[4:-1])
    if not os.path.exists(path):
        raise FileNotFoundError("File doesn't exists")
    os.remove(path)

def _replace(text):
    kk = text[9:-2]
    k = kk.split("),(")
    txt = cmmtools.seval(k[0])
    sr = cmmtools.seval(k[1])
    dr = cmmtools.seval(k[2])
    return txt.replace(sr, dr)

def _exists(text):
    var = cmmtools.seval(text[7:-1])
    return var in _vm.vars

def _split(text):
    ktxt = text[7:-2]
    txt = ktxt.split("),(")
    txtts = cmmtools.seval(txt[0])
    s = cmmtools.seval(txt[1])
    return txtts.split(s)

def _readline(text):
    ktxt = text[10:-2]
    txt = ktxt.split("),(")
    path = cmmtools.seval(txt[0])
    line = cmmtools.seval(txt[1])
    if not os.path.exists(path):
        raise FileNotFoundError("Directory doesn't exists")
    with open(path, "r") as f:
        kk = f.read()
    q = kk.split("\n")
    return q[line]

def _trim(text):
    txt = text[5:-1]
    arg = cmmtools.seval(txt)
    if not isinstance(arg, str):
        raise TypeError("Trim only works with str")
    return arg.replace(" ", "")

def _strip(text):
    ktxt = text[7:-2]
    txt = ktxt.split("),(")
    arg = cmmtools.seval(txt[0])
    arg2 = cmmtools.seval(txt[1])
    if not isinstance(arg, str):
        raise TypeError("Strip only works with str")
    return arg.strip(arg2)

def _upper(text):
    ktk = text[6:-1]
    tkt = cmmtools.seval(ktk)
    if not isinstance(tkt, str):
        raise TypeError("upper only works with str")
    return tkt.upper()

def _lower(text):
    ktk = text[6:-1]
    tkt = cmmtools.seval(ktk)
    if not isinstance(tkt, str):
        raise TypeError("lower only works with str")
    return tkt.lower()

def _elli(text):
    return ...

def _pyexec(text):
    if _vm.vars["__safemode__"]:
        raise SafeModeError("Cannot use pyexec in safe mode")
    code = cmmtools.seval(text[7:-1])
    exec(code, _vm.pyattr, _vm.pyattr)

def _pyeval(text):
    if _vm.vars["__safemode__"]:
        raise SafeModeError("Cannot use pyeval in safe mode")
    code = cmmtools.seval(text[7:-1])
    return eval(code, _vm.pyattr, _vm.pyattr)

def _ret(text):
    return cmmtools.seval(text[4:-1])

def _shell(text):
    if _vm.vars["__safemode__"]:
        raise SafeModeError("Cannot use shell in safe mode")
    return os.system(cmmtools.seval(text[6:-1]))

def _ascii(text):
    char = cmmtools.seval(text[6:-1])
    if isinstance(char, str):
        if len(char) > 1:
            raise EncodeError("ascii use only one number")
        return char
    elif isinstance(char, int):
        if char > 255 or char < 0:
            raise EncodeError("ascii character out of range")
        return chr(char)
    raise EncodeError("ascii requires a number or character")

def _cls(text):
    _vm.stdcls()

commands = {
"pr": _pr,
"txt": _txt,
"inp": _inp,
"dvar": _dvar,
"var": _var,
"nvar": _nvar,
"cosh": _cosh,
"len": _len,
"rem": noth,
"": noth,
"sinh": _sinh,
"True": _true,
"False": _false,
"None": _none,
"type": _type,
"1f": _if,
"bool": _bool,
"totype": _totype,
"exec": _exec,
"goto": _goto,
"1d": _id,
"calc": _calc,
"num": _num,
"for": _for,
"delay": _delay,
"be": _be,
"send": _send,
"dec": _dec,
"try": _try,
"extra": _extra,
"list": _list,
"all": _all,
"ell": _ell,
"getelem": _getelem,
"append": _append,
"setelem": _setelem,
"delelem": _delelem,
"dfunc": _dfunc,
"func": _func,
"save": _save,
"savec": _savec,
"move": _move,
"del": _del,
"delc": _delc,
"seefile": _seefile,
"replace": _replace,
"exists": _exists,
"split": _split,
"readline": _readline,
"wget": _wget,
"trim": _trim,
"strip": _strip,
"upper": _upper,
"lower": _lower,
"...": _elli,
"pyexec": _pyexec,
"pyeval": _pyeval,
"ret": _ret,
"shell": _shell,
"ascii": _ascii,
"cls": _cls
}
