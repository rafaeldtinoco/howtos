#!/bin/bash -e

#
# this script updates a debian located inside an ext4 qcow2 file
#

ARG0=$(basename $0)
MACHINE=$1
ARGUMENT=$2
LIBVIRTDIR=/var/lib/libvirt/images
LXCDIR=/var/lib/lxc
DISKNAME=disk01.ext4.qcow2
LOGFILE=/tmp/qcowxxx.log
MACHINEDIR=$LIBVIRTDIR/$MACHINE
QCOWFILE=$LIBVIRTDIR/$MACHINE/$DISKNAME
OLDDIR=$PWD
MAINDIR=$(dirname $0)
[ "$MAINDIR" == "." ] && MAINDIR=$(pwd)

echo -n > $LOGFILE
RANDMAC=$(printf '52:54:00:%02X:%02X:%02X\n' $[RANDOM%256] $[RANDOM%256] $[RANDOM%256])

getout() {
    echo ERROR: $@
    cd $OLDDIR
    exit 1
}

[ ! $(which sudo) ] && getout "no sudo found"
SUDO=$(which sudo)

# /var/lib/lxc/lxc$$/
# /var/lib/lxc/lxc$$/config
# /var/lib/lxc/lxc$$/rootfs
# /var/lib/lxc/lxc$$/lxc$$.log

TDIR=$LXCDIR/lxc$$
TARGET=$TDIR/rootfs

$SUDO mkdir -p $TARGET

# begin

cd $MAINDIR

[ "$MACHINE" == "list" ] && sudo ls -1 $LIBVIRTDIR && exit 0

[ ! $MACHINE ] && getout "tell me the machine!"
[ ! -d $MACHINEDIR ] && getout "tell me the machine!"
[ ! -f $QCOWFILE ] && getout "where is the file $QCOWFILE ?"

[ ! $(which chroot) ] && getout "no chroot found"
[ ! $(which lxc-start) ] && getout "no lxc-start found"
[ ! $(which fsck.ext4) ] && getout "no fsck.ext4 found"

cat << EOF | sudo tee $TDIR/config 2>&1 > $LOGFILE 2>&1
lxc.include = /usr/share/lxc/config/debian.common.conf
lxc.arch = linux64

lxc.net.0.type = veth
lxc.net.0.link = bridge0
lxc.net.0.flags = up
lxc.net.0.hwaddr = $RANDMAC
lxc.mount.entry = / mnt none bind 0 0
lxc.mount.entry = $HOME ${HOME:1} none bind 0 0
lxc.mount.entry = $HOME mnt/${HOME:1} none bind 0 0
lxc.rootfs.path = $TARGET
lxc.uts.name = lxc$$
EOF

MOUNT=$(which mount)
FSCK=$(which fsck.ext4)
UMOUNT=$(which umount)
CHROOT=$(which chroot)
QEMUNBD=$(which qemu-nbd)

set +e

for i in $(seq 1 20); do
    $SUDO umount /dev/nbd10 2>&1 > $LOGFILE 2>&1
    $SUDO $QEMUNBD -d /dev/nbd10 2>&1 > $LOGFILE 2>&1
done

set -e

$SUDO $QEMUNBD --connect=/dev/nbd10 $QCOWFILE

$SUDO $FSCK /dev/nbd10 -y 2>&1 > $LOGFILE 2>&1

$SUDO $MOUNT /dev/nbd10 $TARGET

# $SUDO $MOUNT -o bind /dev $TARGET/dev
# $SUDO $MOUNT -o bind /proc $TARGET/proc
# $SUDO $MOUNT -o bind /sys $TARGET/sys
# $SUDO $MOUNT -o bind / $TARGET/mnt
# $SUDO $MOUNT -t tmpfs -o size=1G tmpfs $TARGET/tmp

set +e

if   [ x$ARG0 == x"qcowshell.sh" ]; then
    # lxc container of a qcow2 image

    $SUDO -- lxc-start -n lxc$$ -F

elif [ x$ARG0 == x"qcowcmd.sh"  ]; then

    $SUDO -- lxc-start -n lxc$$
    sleep 7
    $SUDO lxc-attach -n lxc$$ -- $ARGUMENT
    sleep 3
    $SUDO -- lxc-stop -n lxc$$

elif [ x$ARG0 == x"qcowvmlinuz.sh" ]; then
    # bring kernel image + ramdisk to host

    if [ $ARGUMENT ]; then
        VMLINUZ=$(sudo ls -1tr $TARGET/boot/ | grep vmlinuz | grep -i $ARGUMENT | tail -1)
        INITRD=$(sudo ls -1tr $TARGET/boot/ | grep initrd | grep -i $ARGUMENT | tail -1)
    fi

    if [ ! $VMLINUZ ] || [ ! $INITRD ]; then
        VMLINUZ=$(sudo ls -1tr $TARGET/boot/ | grep vmlinuz | tail -1)
        INITRD=$(sudo ls -1tr $TARGET/boot/ | grep initrd | tail -1)
    fi

    echo vmlinuz=$VMLINUZ
    echo initrd=$INITRD

    if [ -d $MACHINEDIR ]; then
        echo "bringing lxc$$ ($MACHINE) kernel/ramdisk to host"
        sudo cp $TARGET/boot/$VMLINUZ $MACHINEDIR/vmlinuz
        sudo cp $TARGET/boot/$INITRD $MACHINEDIR/initrd.img
    fi

elif [ x$ARG0 == x"qcowkerninst.sh" ]; then
    # install kernel pkgs into qcow2 image

    cd $OLDDIR

    ls -1 *.deb 2>&1 > /dev/null 2>&1
    if [ $? != 0 ]; then
        echo "no .deb pkgs found in $(pwd)"
    else
        $SUDO -- lxc-start -n lxc$$
        sleep 1

        for pkg in *.deb; do
            $SUDO lxc-attach -n lxc$$ -- dpkg -i /mnt/$(pwd)/$pkg
        done

        sleep 1
        $SUDO -- lxc-stop -n lxc$$
    fi

    cd $MAINDIR

fi

set -e

# $SUDO $UMOUNT $TARGET/tmp
# $SUDO $UMOUNT $TARGET/mnt
# $SUDO $UMOUNT $TARGET/sys
# $SUDO $UMOUNT $TARGET/proc
# $SUDO $UMOUNT $TARGET/dev

$SUDO $UMOUNT $TARGET

$SUDO rmdir $TARGET || getout "could NOT clean temp mount dir"
$SUDO rm -f $TDIR/config
$SUDO rm -f $TDIR/*.log
$SUDO rmdir $TDIR || getout "could not clean temp dir"

for i in $(seq 1 20); do
    $SUDO $QEMUNBD -d /dev/nbd10 2>&1 > $LOGFILE 2>&1
done

cd $OLDDIR
