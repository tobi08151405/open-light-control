#!/usr/bin/env python3

from subprocess import getoutput as go

files = go("ls")
files_used = []

for i in files.split('\n'):
    if ".ps" in i:
        files_used.append(i)

for i in files_used:
    go("ps2pdf "+i)

files = go("ls")
files_used = []

for i in files.split('\n'):
    if (".pdf" in i) and not ("ges" in i):
        files_used.append(i)

go("pdfjoin -o gesamt.pdf "+" ".join(files_used))
go("rm 0*.pdf")
