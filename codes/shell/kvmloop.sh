#!/bin/bash
set -x

zfsdir="/var/lib/libvirt/images"
tmpdir="/tmp"
guest=$1 ; shift

if [ ! -d /target ];
then
	mkdir -p /target
fi

if [ "$guest" == "" ]; then
    echo "$0 [guest]"
    exit 1
fi

sudo qemu-nbd -f qcow2 -c /dev/nbd0 $zfsdir/$guest/disk01.qcow2
#sudo qemu-nbd -f raw -c /dev/nbd0 $zfsdir/$guest/disk01

if [ $? -ne 0 ]; then
	echo "nbd error"
	exit 1
fi

sudo mount /dev/nbd0p1 /target

sudo mount -o bind /proc /target/proc
sudo mount -o bind /sys /target/sys
sudo mount -o bind /dev /target/dev
sudo mount -o bind /dev/pts /target/dev/pts

echo "entering image"
sudo chroot /target

echo "after image"
sudo su -

sudo umount /target/proc
sudo umount /target/sys
sudo umount /target/dev/pts
sudo umount /target/dev
sudo umount /target

sudo qemu-nbd -d /dev/nbd0
sudo qemu-nbd -d /dev/nbd0
sudo qemu-nbd -d /dev/nbd0
sudo qemu-nbd -d /dev/nbd0
