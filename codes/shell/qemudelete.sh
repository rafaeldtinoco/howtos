#!/bin/bash

# sudo zfs list -t snapshot -r %s" % library
# sudo zfs destroy %s/%s" % (library, name
# sudo zfs destroy %s" % snapshot
# sudo virsh undefine %s" % name

zfspool="pool/var_lib_libvirt_images"
zfsmount="/var/lib/libvirt/images"

checkvm() {
    name=$1
    sudo virsh list --state-shutoff --name | grep -q $name
    if [ $? -ne 0 ]; then
        echo $name not an offline vm
        exit 1
    fi
}

undefinevm() {
    name=$1
    sudo virsh undefine $name 2>&1 > /dev/null && echo vm undefined
}

removevm() {
    name=$1
    what=$(basename $(zfs list -t snapshot | grep $name | awk '{print $1}'))
    if [ "$what" == "" ] || [ "$what" == "/" ]; then echo nothing to destroy; exit 1; fi
    echo -n "you really wish to destroy: $zfspool/$what ? (ctrl+c to abort) "
    read
    sudo zfs destroy -R $zfspool/$what
}

cleanlibvirt() {
    name=$1
    if [ "$name" == "" ]; then echo "name is null"; exit 1; fi
    sudo rm -f /etc/libvirt/storage/$name.xml
    sudo rm -f /etc/libvirt/storage/autostart/$name.xml

    sudo systemctl stop libvirtd
    sudo systemctl stop virtlogd.socket
    sudo rm -rf /var/run/libvirt*
    sudo systemctl start virtlogd.socket
    sudo systemctl start libvirtd
}

if [ $# -ne 1 ]; then
    echo "$0 [vm]"
    exit 1
fi

name=$1

checkvm $name
undefinevm $name
removevm $name
cleanlibvirt $name
