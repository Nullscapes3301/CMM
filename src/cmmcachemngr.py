r"""
-> cmmcachemngr
Manager of CMM cache
"""
import json
import os
import cmmvars

def getdefault():
    return {
        "file": "",
        "session": 1,
        "cmm-version": cmmvars.vars["__version__"],
        "errors": [],
    }

def getcachepath(filename):
    if filename is None:
        return None
    cache_dir = ".cmmcache"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return os.path.join(cache_dir, f"CMMcache.{filename}.json")

def mkcache(filename):
    if filename is None:
        return
    with open(getcachepath(filename), "w") as cc:
        json.dump(getdefault(), cc, indent=4)

def getcache(filename, data):
    if filename is None:
        return
    with open(getcachepath(filename), "r") as arh:
        dat = json.load(arh)
    return dat[data]

def setcache(filename, cache, newdata):
    if filename is None:
        return
    with open(getcachepath(filename), "r") as arh:
        dat = json.load(arh)
    dat[cache] = newdata
    with open(getcachepath(filename), "w") as arh:
        json.dump(dat, arh, indent=4)
