#!/bin/bash
set -ex

where="/var/lib/libvirt/images/debian"

if [ ! -d $where ]; then
	echo "directory $where doesn't exist!!"
	echo "it should be zfs filesystem!!"
	exit 1
fi

sudo qemu-img create -f qcow2 $where/disk01.qcow2 20G
sudo modprobe nbd max_part=16
sudo qemu-nbd -c /dev/nbd0 $where/disk01.qcow2
printf "n\np\n1\n\n\nw\n" | sudo fdisk /dev/nbd0
sudo mkfs.ext4 -LROOT /dev/nbd0p1

if [ ! -d /target ]; then
	sudo mkdir /target
fi

sudo mount /dev/nbd0p1 /target

#HTTP_PROXY="http_proxy=http://0.0.0.0:3128/"
HTTP_PROXY=""
sudo $HTTP_PROXY debootstrap --include=less,vim,sudo,openssh-server,bash-completion,wget,rsync,git,build-essential,gdb,crash sid /target http://ftp.us.debian.org/debian/

sudo mount -o bind /dev /target/dev
sudo mount -o bind /sys /target/sys
sudo mount -o bind /proc /target/proc
sudo mount -o bind /dev/pts /target/dev/pts

#sudo chroot /target /bin/bash -c "locale-gen en_US.UTF-8"
echo debian | sudo tee /target/etc/hostname

sudo chroot /target /bin/bash -c "passwd -d root"
sudo chroot /target /bin/bash -c "useradd -d /home/inaddy -s /bin/bash inaddy"
sudo chroot /target /bin/bash -c "passwd -d inaddy"

sudo chroot /target /bin/bash -c "echo root:root | chpasswd"
sudo chroot /target /bin/bash -c "echo inaddy:inaddy | chpasswd"

echo """## /etc/sudoers

Defaults env_reset
Defaults mail_badpass
Defaults secure_path=\"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\"

Defaults logfile=/var/log/sudo.log,loglinelen=0
Defaults !syslog, !pam_session

root ALL=(ALL:ALL) ALL
%admin ALL=(ALL) ALL
%sudo ALL=(ALL:ALL) ALL
inaddy ALL=(ALL) NOPASSWD: ALL

#includedir /etc/sudoers.d

## end of file""" | sudo tee /target/etc/sudoers

echo """## /etc/fstab

LABEL=ROOT / ext4 errors=remount-ro 0 1

## end of file""" | sudo tee /target/etc/fstab

echo """## /etc/apt/sources.list

deb http://debian.c3sl.ufpr.br/debian/ sid main non-free contrib
deb-src http://debian.c3sl.ufpr.br/debian/ sid main non-free contrib

## end of file""" | sudo tee /target/etc/apt/sources.list

echo """## /etc/apt/apt.conf

#Acquire::http::Proxy "http://0.0.0.0:3128/";
APT::Install-Recommends "true";
APT::Install-Suggests "false";
# APT::Get::Assume-Yes "true";
# APT::Get::Show-Upgraded "true";
APT::Quiet "true";
DPkg::Options { "--force-confdef";"--force-confmiss";"--force-confold"};
Debug::pkgProblemResolver "true";
Acquire::Languages "none";

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
sudo chroot /target /bin/bash -c "apt-get install -y linux-image-amd64 linux-headers-amd64"

sudo grub-install /dev/nbd0

sudo umount /target/dev/pts
sudo umount /target/dev
sudo umount /target/sys
sudo umount /target/proc
sudo umount /target

sudo qemu-nbd -d /dev/nbd0
