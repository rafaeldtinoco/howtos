#!/bin/bash
set -ex

release=$1

if [ "$release" == "" ];
then
	echo "$0 [release]"
	exit 1
fi

where="/var/lib/libvirt/images/"
whererel="${where}/${release}"

if [ ! -d $whererel ]; then
	echo "directory $whererel doesn't exist!!"
	echo "it should be zfs filesystem!!"
	exit 1
fi

sudo qemu-img create -f qcow2 $whererel/disk01.qcow2 20G
sudo modprobe nbd max_part=16
sudo qemu-nbd -c /dev/nbd0 $whererel/disk01.qcow2
printf "n\np\n1\n\n\nw\n" | sudo fdisk /dev/nbd0
sudo mkfs.ext4 -LROOT /dev/nbd0p1

if [ ! -d /target ]; then
	sudo mkdir /target
fi

sudo mount /dev/nbd0p1 /target

sudo debootstrap --include=less,vim,sudo,openssh-server,bash-completion,wget,rsync,git,build-essential,gdb,crash $release /target http://us.ports.ubuntu.com/ubuntu-ports/

sudo mount -o bind /dev /target/dev
sudo mount -o bind /sys /target/sys
sudo mount -o bind /proc /target/proc
sudo mount -o bind /dev/pts /target/dev/pts

sudo chroot /target /bin/bash -c "locale-gen en_US.UTF-8"
echo $release | sudo tee /target/etc/hostname

sudo chroot /target /bin/bash -c "passwd -d root"
sudo chroot /target /bin/bash -c "useradd -d /home/inaddy -s /bin/bash inaddy"
sudo chroot /target /bin/bash -c "passwd -d inaddy"

sudo chroot /target /bin/bash -c "echo root:root | chpasswd"
sudo chroot /target /bin/bash -c "echo inaddy:inaddy | chpasswd"

echo """## /etc/sudoers

Defaults env_keep += "LANG LANGUAGE LINGUAS LC_* _XKB_CHARSET"
Defaults env_keep += "HOME EDITOR PAGER"
Defaults env_keep += "XAPPLRESDIR XFILESEARCHPATH XUSERFILESEARCHPATH"
Defaults env_keep += "QTDIR KDEDIR"
Defaults env_keep += "XDG_SESSION_COOKIE"
Defaults env_keep += "XMODIFIERS GTK_IM_MODULE QT_IM_MODULE QT_IM_SWITCHER"

Defaults secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

Defaults logfile=/var/log/sudo.log,loglinelen=0
Defaults !syslog, !pam_session

root ALL=(ALL) NOPASSWD: ALL
inaddy ALL=(ALL) NOPASSWD: ALL
%wheel ALL=(ALL) NOPASSWD: ALL

## end of file""" | sudo tee /target/etc/sudoers

echo """## /etc/fstab

LABEL=ROOT / ext4 errors=remount-ro 0 1

## end of file""" | sudo tee /target/etc/fstab

echo """## /etc/apt/sources.list

deb http://us.ports.ubuntu.com/ubuntu-ports/ xenial main restricted universe multiverse
deb-src http://us.ports.ubuntu.com/ubuntu-ports/ xenial main restricted universe multiverse
deb http://us.ports.ubuntu.com/ubuntu-ports/ xenial-updates main restricted universe multiverse
deb-src http://us.ports.ubuntu.com/ubuntu-ports/ xenial-updates main restricted universe multiverse
# deb http://us.ports.ubuntu.com/ubuntu-ports/ xenial-proposed main restricted universe multiverse
# deb-src http://us.ports.ubuntu.com/ubuntu-ports/ xenial-proposed main restricted universe multiverse
# deb http://ports.ubuntu.com/ubuntu-ports xenial-security main restricted universe multiverse
# deb-src http://ports.ubuntu.com/ubuntu-ports xenial-security main restricted universe multiverse
# deb http://us.ports.ubuntu.com/ubuntu-ports/ xenial-backports main restricted universe multiverse
# deb-src http://us.ports.ubuntu.com/ubuntu-ports/ xenial-backports main restricted universe multiverse
# deb http://ddebs.ubuntu.com/ xenial main restricted universe multiverse
# deb http://ddebs.ubuntu.com/ xenial-updates main restricted universe multiverse
# deb http://ddebs.ubuntu.com/ xenial-proposed main restricted universe multiverse
# deb http://ppa.launchpad.net/canonical-kernel-team/ppa/ubuntu xenial main
# deb-src http://ppa.launchpad.net/canonical-kernel-team/ppa/ubuntu xenial main

## end of file""" | sudo tee /target/etc/apt/sources.list

sudo sed -i "s:RELEASE:$release:g" /target/etc/apt/sources.list

echo """## /etc/apt/apt.conf

Acquire::http::Proxy \"\";
APT::Install-Recommends \"true\";
APT::Install-Suggests \"false\";
# APT::Get::Assume-Yes \"true\";
# APT::Get::Show-Upgraded \"true\";
APT::Quiet \"true\";
DPkg::Options {\"--force-confdef\";\"--force-confmiss\";\"--force-confold\"};
Debug::pkgProblemResolver \"true\";
Acquire::Languages \"none\";

## end of file""" | sudo tee /target/etc/apt/apt.conf

echo """## /etc/default/grub

GRUB_DEFAULT=0
GRUB_HIDDEN_TIMEOUT_QUIET=true
GRUB_TIMEOUT=2
GRUB_DISTRIBUTOR=`lsb_release -i -s 2> /dev/null || echo Debian`
GRUB_CMDLINE_LINUX_DEFAULT=\"root=/dev/vda1 console=tty0 console=ttyS0,38400n8 apparmor=0 crashkernel=384M-:256M\"
GRUB_CMDLINE_LINUX=\"\"
GRUB_TERMINAL=serial
GRUB_SERIAL_COMMAND=\"serial --speed=38400 --unit=0 --word=8 --parity=no --stop=1\"
GRUB_DISABLE_LINUX_UUID=\"true\"
GRUB_DISABLE_RECOVERY=\"false\"

## end of file""" | sudo tee /target/etc/default/grub

#sudo chroot /target /bin/bash -c "systemctl enable getty@ttyS0.service"
sudo chroot /target /bin/bash -c "apt-get update"
sudo chroot /target /bin/bash -c "apt-get install -y linux-image-generic linux-headers-generic s390-tools"

#sudo grub-install /dev/nbd0

sudo umount /target/dev/pts
sudo umount /target/dev
sudo umount /target/sys
sudo umount /target/proc
sudo umount /target

sudo qemu-nbd -d /dev/nbd0
