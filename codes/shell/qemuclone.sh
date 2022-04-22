#!/bin/bash

basedir=$PWD

trap cleanup INT

gitclean() {
    git clean -f
    git reset --hard
    git clean -f
}

cleanup() {
    cd $basedir
}

zfspool="pool/var_lib_libvirt_images"
zfsmount="/var/lib/libvirt/images"

checkvirtclone() {
    which virt-clone > /dev/null
    if [ $? -ne 0 ]; then
        echo "no virt-clone"
        exit 1
    fi
}

checkexists() {
    newone=$1
    sudo virsh list --name --all | grep -q $newone
    if [ $? -eq 0 ]; then
        echo a vm with name $newone has been found
        exit 1
    fi
}

gettemplates() {
    templates=$(sudo virsh list --all | awk '{print $2}' | egrep -E '(sid|stretch)')
}

listtemplates() {
    for t in $templates; do printf "  $t\n"; done
}

checktemplate() {
    found=0
    for template in $templates; do [ "$1" == "$template" ] && found=1; done
    if [ "$found" -ne "1" ]; then echo "available templates:"; listtemplates; exit 1; fi
}

zfssnap() {
    oldone=$1
    newone=$2

    if [ "$1" == "" ]; then echo "zfssnap had no template arg"; exit 1; fi
    if [ "$2" == "" ]; then echo "zfssnap had no newvm arg"; exit 1; fi
    from=$(sudo zfs list | grep $zfspool/$oldone | awk '{print $1}' | head -1)
    if [ "$from" == "" ]; then echo "no pool to snapshot from"; exit 1; fi
    sudo zfs snapshot $from@$newone && echo "zfs snapshot created"
    sudo zfs clone $from@$newone $zfspool/$newone && echo "zfs clone created"
}

virtclone() {
    oldone=$1
    newone=$2

    sudo virt-clone --check path_in_use=off \
            --original=$oldone \
            --name $newone\
            --preserve-data \
            --file $zfsmount/$newone/disk01.ext4 \
            > /dev/null 2>&1 \
            && echo "vm was cloned"
}

fixxml() {
    newone=$1
    sudo virsh dumpxml $newone | sed "s:$zfsmount/$oldone/:$zfsmount/$newone/:g" > /tmp/$newone.$$
    echo "compressing libvirt xmls by precaution =)"
    sudo tar cvfz /tmp/libvirt_qemu.tar.gz.$$ /etc/libvirt/qemu/ 2>&1 > /dev/null 2>&1
    sudo mv /tmp/$newone.$$ /etc/libvirt/qemu/$newone.xml

    sudo systemctl stop libvirtd
    sudo systemctl stop virtlogd.socket
    sudo rm -rf /var/run/libvirt*
    sudo systemctl start virtlogd.socket
    sudo systemctl start libvirtd
}

changehostname() {
    newone=$1
    filesystem="disk01.ext4"

    if [ ! -d $zfsmount/$newone ]; then echo "no new zfs dir found"; exit 1; fi
    cd $zfsmount/$newone
    if [ ! -f $filesystem ]; then echo "no filesystem found"; exit 1; fi
    sudo mkdir /tmp/$filesystem.$$
    if [ ! -d /tmp/$filesystem.$$ ]; then echo "could not create tmp dir"; exit 1; fi
    sudo mount -o loop $filesystem /tmp/$filesystem.$$
    if [ ! -f /tmp/$filesystem.$$/etc/hostname ]; then echo "no hostname file"; exit 1; fi
    echo $newone | sudo tee /tmp/$filesystem.$$/etc/hostname
    sudo umount /tmp/$filesystem.$$
    if [ -f /tmp/$filesystem.$$/etc/hostname ]; then echo "umount did not succeed"; exit 1; fi
    sudo rmdir /tmp/$filesystem.$$
    cd $basedir
}

if [ $# -ne 2 ] && [ "$1" != "list" ]; then
    echo "$0 [list|template->] [newvm]"
    exit 1
fi

checkvirtclone

oldone=$1
newone=$2

gettemplates
checktemplate $oldone
checkexists $newone

zfssnap $oldone $newone
virtclone $oldone $newone
fixxml $newone
changehostname $newone
