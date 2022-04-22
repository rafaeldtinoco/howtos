#!/usr/bin/python3 -B

import sys
import os

from myfunctions import *

sys.path.append(os.path.abspath("/home/inaddy/work/codes/scripts/"))

library="pool/var_lib_libvirt_images"

def syntax():
    print("%s [name]" % sys.argv[0])
    sys.exit(1)

if __name__ == '__main__':

    inicio(debug=True)

    if len(sys.argv) < 2:
        syntax()

    name = sys.argv[1]

    cmd = []
    outp = []

    ret = executa("sudo zfs list -t snapshot -r %s" % library)
    ret = ret.split("\n")
    ret = [r for r in ret if ("@%s " % name) in r]

    if len(ret) > 0:
        ret = ret[0]
        snapshot = ret.split(" ")[0]
        cmd.append("sudo zfs destroy %s/%s" % (library, name))
        cmd.append("sudo zfs destroy %s" % snapshot)

    cmd.append("sudo virsh undefine %s" % name)

    for c in cmd:
        outp.append(executa(c))

    for out in outp:
        if len(out) > 0:
            print(out)
