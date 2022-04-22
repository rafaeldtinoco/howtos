#!/bin/bash

ARGS=$@
ARG0=$0
ARG1=$1
ARG2=$2

LIBVIRTDIR=/var/lib/libvirt/images

[ ! $(which sudo) ] && getout "sudo not found"

if [ "$ARG1" == "list" ]; then
    sudo ls -1 $LIBVIRTDIR
    exit 0
fi

if [ $UID -ne 0 ]; then
    sudo $ARG0 $ARGS
    exit 0
fi

getout() {
    echo ERROR: $@
    exit 1
}

ARG0=$(basename $ARG0)
MACHINE=$ARG1
CLONE=$ARG2
OLDDIR=$PWD

MACHINEDIR=$LIBVIRTDIR/$MACHINE
CLONEDIR=$LIBVIRTDIR/$CLONE

[ ! $(which qemu-img) ] && getout "no qemu-img found"
[ ! $(which virt-clone) ] && getout "no virt-clone found"
[ ! $(which virsh) ] && getout "no virsh found"

[ ! $MACHINE ] && getout "machine not informed"

[ ! -d $LIBVIRTDIR ] && getout "libvirt dir not found"
[ ! -d $MACHINEDIR ] && getout "vm dir not found"

[[ ! "$MACHINE" =~ win ]] && {
    [ ! -f $MACHINEDIR/vmlinuz ] && getout "vmlinuz not found"
    [ ! -f $MACHINEDIR/initrd.img ] && getout "initrd.img not found"
}

[ ! -f $MACHINEDIR/disk01.ext4.qcow2 ] && getout "disk not found"

if [[ "$ARG0" == "virtcopy.sh" || "$ARG0" == "virtclone.sh" ]]; then

    [ ! $CLONE ] && getout "dest not informed"
    [ -d $CLONEDIR ] && getout "dest already exists"

    mkdir $CLONEDIR
    [ ! -d $CLONEDIR ] && getout "dest dir could not be created"

    [[ ! "$MACHINE" =~ win ]] && {
        cp $MACHINEDIR/vmlinuz $CLONEDIR/vmlinuz
        cp $MACHINEDIR/initrd.img $CLONEDIR/initrd.img
    }

    if [ "$ARG0" == "virtcopy.sh" ]; then
        cp $MACHINEDIR/disk01.ext4.qcow2 $CLONEDIR/disk01.ext4.qcow2

        virt-clone --check path_in_use=off --preserve-data \
            --connect qemu:///system --original $MACHINE --name $CLONE \
            --file $CLONEDIR/disk01.ext4.qcow2
    fi

    if [ "$ARG0" == "virtclone.sh" ]; then
        sudo qemu-img create -f qcow2 -b $MACHINEDIR/disk01.ext4.qcow2 \
            $CLONEDIR/disk01.ext4.qcow2

        virt-clone --check path_in_use=off --preserve-data \
            --connect qemu:///system --original $MACHINE --name $CLONE \
            --file $CLONEDIR/disk01.ext4.qcow2
    fi

    virsh dumpxml $CLONE > /tmp/$$.xml

    [[ ! "$MACHINE" =~ win ]] && {
        sed -i "s:.*<kernel>.*:<kernel>$CLONEDIR/vmlinuz</kernel>:g" /tmp/$$.xml
        sed -i "s:.*<initrd>.*:<initrd>$CLONEDIR/initrd.img</initrd>:g" /tmp/$$.xml
    }

    virsh define /tmp/$$.xml
    rm /tmp/$$.xml

elif [ "$ARG0" == "virtdel.sh" ]; then

    [ ! -d $MACHINEDIR ] && getout "clone dir could not be found"

    virsh undefine $MACHINE 2>&1

    rm -f $MACHINEDIR/vmlinuz
    rm -f $MACHINEDIR/initrd.img
    rm -f $MACHINEDIR/disk01.ext4.qcow2
    rmdir $MACHINEDIR

fi
