#!/usr/bin/env python3

import sys,os
import traceback

fl = sys.argv[1]
fl2 = sys.argv[2]

try:
    with open(fl,"r") as f:
        lines= f.readlines()
except Exception as e:
    print ("Error when opening the file",fl)
    print(traceback.format_exc())
    sys.exit(0)

try:
    with open(fl2,"r") as f:
        lines2= f.readlines()
except Exception as e:
    print ("Error when opening the file",fl2)
    print(traceback.format_exc())
    sys.exit(0)

for indx,ln in enumerate(lines2[1:]):
    cmd = ln
    lines.insert(indx + 1 ,cmd)

with open(fl,"w") as f:
    f.writelines(lines)
