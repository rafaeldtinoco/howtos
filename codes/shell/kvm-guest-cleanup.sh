#!/bin/bash

if [ $UID -ne 0 ]
then
    sudo $0 $@
    exit 0
fi

IMGDIR="/var/lib/libvirt/images"
TARGET="/target"
NBDDEV="/dev/nbd7"

for n in 1 2 3; do
    umount $TARGET/dev/pts
    umount $TARGET/dev/
    umount $TARGET/sys
    umount $TARGET/proc
    umount $TARGET
done

for n in 1 2 3 4 5 6 7 8; do
    qemu-nbd -d $NBDDEV
done
