#!/usr/bin/python3 -B

import sys
import os

from myfunctions import *

sys.path.append(os.path.abspath("/home/inaddy/work/codes/scripts"))

library="pool/var_lib_libvirt_images"

def syntax():
    print("%s [template] [name] [amd64|arm64]" % sys.argv[0])
    sys.exit(1)

if __name__ == '__main__':

    inicio(debug=True)

    if len(sys.argv) < 4:
        syntax()

    template = sys.argv[1]
    name = sys.argv[2]
    arch = sys.argv[3]

    cmd = []
    outp = []

    rtemplate = template.replace("@", "").replace("-", "")

    cmd.append("sudo zfs snapshot %s/%s@%s" % (library, rtemplate, name))
    cmd.append("sudo zfs clone %s/%s@%s %s/%s" % (library, rtemplate, name, library, name))
    cmd.append("sleep 3")

    if("arm64" in arch):
        virtclone="sudo virt-clone --check path_in_use=off --original \"%s\" --name %s --preserve-data --file /var/lib/libvirt/images/%s/disk01 --nvram /var/lib/libvirt/images/%s/flash1.img" % (template, name, name, name)
    elif ("amd64" in arch):
        virtclone="sudo virt-clone --check path_in_use=off --original \"%s\" --name %s --preserve-data --file /var/lib/libvirt/images/%s/disk01 --file /var/lib/libvirt/images/guest/disk01" % (template, name, name)
    else:
        sys.exit(1)

    cmd.append(virtclone)

    for c in cmd:
        outp.append(executa(c))

    for out in outp:
        if len(out) > 0:
            print(out)
