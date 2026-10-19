r"""
-> cmmvars
The default vars of CMM
"""
import platform
import sys
vars = {
    "__name__": "CMM",
    "__prompt__": "",
    "__blocks__": "",
    "__argv__": sys.argv,
    "__ell__": "",
    "__block__": 0,
    "__version__": 2,
    "__platform__": platform.system(),
    "__language__": "CMM",
    "__safemode__": False,
    "__session__": 0,
    "__encoding__": "utf-8",
    "__newline__": "\n",
    "__inside_func__": False,
    "__filename__": "",
    "__filepath__": "",
    "__lp__": "(",
    "__rp__": ")"
}
