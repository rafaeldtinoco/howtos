#!/usr/bin/python3 -B

import sys
import os

from myfunctions import *

sys.path.append(os.path.abspath("/home/inaddy/work/codes/scripts"))

library="pool/var_lib_libvirt_images"

def syntax():
    print("%s [vms|snapshots]" % sys.argv[0])
    sys.exit(1)

if __name__ == '__main__':

    try:
        option = sys.argv[1]

    except IndexError:
        option = "vms"

    if option not in ["vms", "snapshots"]:
        syntax

    tipo = "-t filesystem"
    lugar = library

    if option == "snapshots":
        tipo = "-t snapshot"

    ret = executa("sudo zfs list %s -r %s" % (tipo, lugar))
    ret = [r.split(' ')[0].split('/')[-1] for r in ret.split("\n") if ("%s/" % lugar) in r]
    print("\n".join(ret))
