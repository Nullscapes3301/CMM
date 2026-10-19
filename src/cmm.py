import cmmtools
import cmmcommands
import cmmvars
import sys
import os
import cmmcachemngr
import cmmerrors
import copy

class CMM:
    def __init__(
            self,
            file=None,
            prompt=None,
            safemode=False,
            stdout=print,
            stdin=input,
            stdcls=lambda: os.system("cls" if os.name == "nt" else "clear"),
            cache=True
            ):
        self.mngcache = cache 
        self.vars = copy.deepcopy(cmmvars.vars)
        self.stdin = stdin
        self.stdout = stdout
        if file is None:
            self.prompt = prompt
            self.filepath = None
            self.filename = None
            self.mngcache = False
            self.vars["__session__"] = 0
        else:
            self.filepath = os.path.abspath(file)
            self.filename = os.path.basename(self.filepath)
            if self.mngcache:
                try:
                    cmmcachemngr.setcache(self.filename,"session", cmmcachemngr.getcache(self.filename,"session")+1)
                    self.vars["__session__"] = cmmcachemngr.getcache(self.filename,"session")  
                except FileNotFoundError:
                    try:
                        cmmcachemngr.mkcache(self.filename)
                        self.vars["__session__"] = 1
                    except Exception as e:
                        self.stdout("Something happened while creating cache")
                        self.stdout(e)
                        return
                finally:
                    try:
                        with open(self.filepath, "r", encoding="utf-8") as f:
                            self.prompt = f.read()
                        cmmcachemngr.setcache(self.filename,"file", self.filename)
                    except FileNotFoundError:
                        self.stdout(f"File '{self.filepath}' not founded")
                        sys.exit()
        self.vars["__filename__"] = self.filename
        self.vars["__filepath__"] = self.filepath
        self.vars["__safemode__"] = safemode
        self.vars["__prompt__"] = self.prompt
        if not self.filename is None:
            if self.mngcache and cmmcachemngr.getcache(self.filename,"cmm-version") != self.vars["__version__"]:
                self.stdout("<-------------------- CMM warning")
                self.stdout("(!) Interpreter version is different from file version(cache data)")
                self.stdout("(!) This can cause errors")
                self.stdout(">-------------------- CMM warning")
                self.stdout()
        self.commands = copy.deepcopy(cmmcommands.commands)
        self.modules = {}
        self.func = {}
        self.bees = {}
        self.ids = {}
        self.blocks = []
        self.block = 0
        self.pyattr = {
            "print": self.stdout,
            "input": self.stdin
        }
        temp = []
        for line in self.prompt.split("\n"):
            temp.append(line.strip())
        self.prompt = "".join(temp)

    def __call__(self):
        cmmcommands.__set__(self)
        try:
            try:
                self.blocks = cmmtools.get_cmm_code(self.prompt)
            except cmmerrors.SyntaxError as err:
                if "cmm-" in str(err):
                    self.blocks = [self.prompt[:4]]
                else:
                    self.blocks = [self.prompt[-1:]]
                self.block = 0
                raise cmmerrors.SyntaxError(err) from None
            while True:
                self.vars["__block__"] = self.block+1
                com2=self.blocks[self.block].split("(")
                com=com2[0]
                self.commands[com](self.blocks[self.block])
                self.block += 1
                if self.block == len(self.blocks):
                    break
            return 0
        except KeyError as e:
            self.stdout("<-------------------- CMM error")
            self.stdout(f"Command not recognized: {e.args[0]}")
            self.stdout(f"In block {self.block+1}")
            block = self.blocks[self.block]
            self.stdout(block)
            self.stdout("^"+"~"*max(0,len(block)-1))
            if self.filename and self.mngcache:
                ek = cmmcachemngr.getcache(self.filename, "errors")
                ek.append(str(e))
                cmmcachemngr.setcache(self.filename, "errors", ek)
            return 1
        except (cmmerrors.CMMExit, SystemExit) as e:
            return 2
        except KeyboardInterrupt:
            return 3
        except cmmerrors.CMMError as e:
            self.stdout("<-------------------- CMM error")
            self.stdout(f"{type(e).__name__}: {e.args[0]}")
            self.stdout(f"In block {self.block+1}")
            block = self.blocks[self.block]
            self.stdout(block)
            self.stdout("^"+"~"*max(0,len(block)-1))
            if self.filename and self.mngcache:
                ek = cmmcachemngr.getcache(self.filename, "errors")
                ek.append(str(e))
                cmmcachemngr.setcache(self.filename, "errors", ek)
            return 1
        else:
            return 0

if __name__ == "__main__":
    f = None
    p = None
    intr = False
    if len(sys.argv) >= 2:
        f = sys.argv[1]
    else:
        p = input("CMM >>> ")
        intr = True
    while True:
        if intr:
            vm = CMM(prompt=p)
            code = vm()
            print()
            print( "    [DONE]")
            print(f"    CMM code exited with code={code}")
            del vm
            if code == 2:
                break
            p = input("CMM >>> ")
        else:
            vm = CMM(file=f)
            vm()
            break
