#!/bin/bash -e

if mountpoint /mnt; then
    umount -f /mnt
fi
[ -e /dev/bcache0 ] && wipefs -a /dev/bcache0
while true; do
    [ -e /sys/class/block/bcache0/bcache/stop ] || break
    bdev_stop=$(ls /sys/class/block/bcache0/bcache/stop )
    if [ -n "${bdev_stop}" -a -e "${bdev_stop}" ]; then
         echo "writing 1 to $bdev_stop"
         echo 1 > $bdev_stop
         udevadm settle
         sleep 1
    else
        break
    fi
done
while true; do
    [ -e /sys/fs/bcache/*-*-*-*/stop ] || break
    cdev_stop=$(ls /sys/fs/bcache/*-*-*-*/stop)
    if [ -n "${cdev_stop}" -a -e "${cdev_stop}" ]; then
         echo "writing 1 to $cdev_stop"
         echo 1 > $cdev_stop
         udevadm settle
         sleep 1
    else
        break
    fi
done
# wipe /dev/vdb and /dev/vdc
for ((x=0; x<50; x++)); do
    wipefs -a /dev/vdc
    dd if=/dev/zero of=/dev/vdc bs=1M count=10
    rc=$?
    [ "$rc" = "0" ] && break;
    udevadm settle
    sleep 1
done
[ "$rc" != "0" ] && exit 3

for ((x=0; x<50; x++)); do
    wipefs -a /dev/vdb
    dd if=/dev/zero of=/dev/vdb bs=1M count=10
    rc=$?
    [ "$rc" = "0" ] && break;
    udevadm settle
    sleep 1
done
[ "$rc" != "0" ] && exit 4
make-bcache --wipe-bcache -C /dev/vdb -B /dev/vdc
udevadm settle
# this is needed before the fix but causes issue after the fix
# (as they are already registered)
set +e
echo /dev/vdc | tee /sys/fs/bcache/register
echo /dev/vdb | tee /sys/fs/bcache/register
set -e
udevadm settle
[ ! -e /dev/bcache0 ] && {
    echo "bcache0 missing"
    exit 1
}
[ ! -e /dev/bcache/by-uuid ] && {
    echo "bcache0 present but /dev/bcache/by-uuid does not exist!"
    exit 1
}
ls -al /dev/bcache/by-uuid/
echo "Creating filesystems on bcache0"
mkfs.ext4 /dev/bcache0 || exit
echo "mounting bcache0 to /mnt"
mount /dev/bcache0 /mnt
udevadm settle --exit-if-exists /dev/bcache0
[ ! -e /dev/bcache/by-uuid ] && {
    echo "bcache0 mounted and /dev/bcache/by-uuid does not exist!"
    exit 2
}
ls -al /dev/bcache/by-uuid/
echo "Everything OK"
exit 0
