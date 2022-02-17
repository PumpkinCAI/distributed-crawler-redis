import os
import sys
import pkgutil
sys.path.append('../')
pkgpath = os.path.dirname(__file__)
pkgname = os.path.basename(pkgpath)
for _, file, _ in pkgutil.iter_modules([pkgpath]):
    abfile = os.path.join(pkgpath, file)
    __import__(pkgname+'.'+file)

