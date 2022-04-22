#!/bin/bash

URL="http://archive.ubuntu.com/ubuntu"

## root

if [ $UID -ne 0 ]
then
    sudo $0 $@
    exit 0
fi

## variables

HOSTNAME=$1	# default: "ubuntu"
VCPUS=$2	# default: 4
RAMGB=$3	# default: 4 (GB)
INTERFACE=$4	# default: bridge0 (bridge)
FLAVOR=$5	# default: "xenial"

ALLFLAVORS="xenial bionic cosmic disco"

PACKAGES="""\
locales,less,vim,sudo,openssh-server,bash-completion,\
wget,rsync,git,bridge-utils,vlan,net-tools,xterm,ncurses-term,\
build-essential,mtr-tiny,iputils-arping,lsof,strace,ltrace,\
iputils-ping,iputils-tracepath,dnsutils,bridge-utils,lsb-release,\
tcpdump,curl,openssh-server,openssh-client,gdebi-core,git,\
devscripts,gnupg,vlan
"""

## unlikely to be changed

IMGDIR="/var/lib/libvirt/images"
TARGET="/target"
NBDDEV="/dev/nbd7"

http_proxy="http://172.16.0.1:3142/"
https_proxy="https://172.16.0.1:3142/"
ftp_proxy="ftp://172.16.0.1:3142/"

export http_proxy
export https_proxy
export ftp_proxy

## end of variables

if [ $# -eq 0 ]; then
	HOSTNAME="ubuntu"
	VCPUS=4
	RAMGB=4
	INTERFACE="bridge0"
	FLAVOR="xenial"
fi

if [ "$HOSTNAME" == "" ] || [ "$INTERFACE" == "" ] || [ "$FLAVOR" == "" ]; then
	echo $(basename $0) [hostname] [vcpus] [ramgb] [bridge] [flavor]
	exit 1
fi

if [[ $VCPUS == *[a-zA-Z]* ]]; then
	echo unknown number of vcpus
	exit 1
fi

if [[ $RAMGB == *[a-zA-Z]* ]]; then
	echo unknown memory size
	exit 1
fi

found=0

for flavor in $ALLFLAVORS; do
	if [ "$FLAVOR" == "$flavor" ]; then
		found=1
	fi
done

if [ $found -eq 0 ]; then
	echo unknown flavor $FLAVOR
	exit 1
fi

set -x
set +e

if [ ! -d $IMGDIR ]
then
    exit 1
fi

if [ -d $IMGDIR/$HOSTNAME ]
then
    exit 1
fi

set -e

modprobe nbd max_part=16

# make sure leftovers are cleaned

if [ ! -d $TARGET ]; then
	mkdir $TARGET
fi

set +e

umount $TARGET 2>&1 /dev/null
umount $TARGET 2>&1 /dev/null

set -e

qemu-nbd -d $NBDDEV 2>&1 > /dev/null
qemu-nbd -d $NBDDEV 2>&1 > /dev/null

# move on

TMPDIR="$IMGDIR/$HOSTNAME"
TMPFILE="$IMGDIR/$HOSTNAME/disk01.ext4.qcow2"

mkdir $TMPDIR

qemu-nbd -d $NBDDEV 2>&1 > /dev/null
qemu-nbd -d $NBDDEV 2>&1 > /dev/null

[ -f $TMPFILE ] && rm $TMPFILE

qemu-img create -f qcow2 $TMPFILE 30G
qemu-nbd -c $NBDDEV $TMPFILE
mkfs.ext4 -LROOT $NBDDEV

set +e

umount $TARGET 2>&1 /dev/null
umount $TARGET 2>&1 /dev/null

set -e

mount $NBDDEV $TARGET

debootstrap --include=$PACKAGES \
            $FLAVOR \
            $TARGET \
            $URL

mount -o bind /dev $TARGET/dev
mount -o bind /dev/pts $TARGET/dev/pts
mount -o bind /sys $TARGET/sys
mount -o bind /proc $TARGET/proc

chroot $TARGET /bin/bash -c "echo en_US.UTF-8 > /etc/locale.gen"
chroot $TARGET /bin/bash -c "locale-gen en_US.UTF-8"

echo $HOSTNAME | tee $TARGET/etc/hostname

chroot $TARGET /bin/bash -c "passwd -d root"
chroot $TARGET /bin/bash -c "useradd -d /home/inaddy -m -s /bin/bash inaddy"
chroot $TARGET /bin/bash -c "passwd -d inaddy"

chroot $TARGET /bin/bash -c "echo root:root | chpasswd"
chroot $TARGET /bin/bash -c "echo inaddy:inaddy | chpasswd"

chroot $TARGET /bin/bash -c "groupdel dialout"
chroot $TARGET /bin/bash -c "groupmod -g 20 -o inaddy"
chroot $TARGET /bin/bash -c "usermod -u 501 -g 20 -o inaddy"
chroot $TARGET /bin/bash -c "chown -R inaddy:inaddy /home/inaddy"

set +e

chroot $TARGET /bin/bash -c "usermod -a -G root inaddy"
chroot $TARGET /bin/bash -c "usermod -a -G sudo inaddy"
chroot $TARGET /bin/bash -c "usermod -a -G shadow inaddy"
chroot $TARGET /bin/bash -c "usermod -a -G staff inaddy"
chroot $TARGET /bin/bash -c "usermod -a -G users inaddy"
chroot $TARGET /bin/bash -c "usermod -a -G nogroup inaddy"
chroot $TARGET /bin/bash -c "usermod -a -G syslog inaddy"
chroot $TARGET /bin/bash -c "usermod -a -G crontab inaddy"
chroot $TARGET /bin/bash -c "usermod -a -G libvirt inaddy"
chroot $TARGET /bin/bash -c "usermod -a -G libvirtd inaddy"
chroot $TARGET /bin/bash -c "usermod -a -G libvirt-qemu inaddy"
chroot $TARGET /bin/bash -c "usermod -a -G kvm inaddy"

set -e

echo """## /etc/apt/apt.conf

Acquire::http::Proxy \"http://172.16.0.1:3142/\";
APT::Install-Recommends \"true\";
APT::Install-Suggests \"false\";
# APT::Get::Assume-Yes \"true\";
# APT::Get::Show-Upgraded \"true\";
APT::Quiet \"true\";
DPkg::Options { \"--force-confdef\";\"--force-confmiss\";\"--force-confold\"};
Debug::pkgProblemResolver \"true\";
Acquire::Languages \"none\";

## end of file""" | tee $TARGET/etc/apt/apt.conf

echo """## /etc/sudoers

Defaults env_keep += \"LANG LANGUAGE LINGUAS LC_* _XKB_CHARSET\"
Defaults env_keep += \"HOME EDITOR SYSTEMD_EDITOR PAGER\"
Defaults env_keep += \"XMODIFIERS GTK_IM_MODULE QT_IM_MODULE QT_IM_SWITCHER\"

Defaults secure_path=\"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\"

Defaults logfile=/var/log/sudo.log,loglinelen=0
Defaults !syslog, !pam_session

root ALL=(ALL) NOPASSWD: ALL
%wheel ALL=(ALL) NOPASSWD: ALL
%sudo ALL=(ALL) NOPASSWD: ALL
inaddy ALL=(ALL) NOPASSWD: ALL

## end of file""" | tee $TARGET/etc/sudoers

echo """## /etc/fstab

/dev/vda / ext4 noatime,nodiratime,relatime,discard,errors=remount-ro 0 1

# kvm share(s)

inaddy /home/inaddy 9p rw,noatime,nodiratime,relatime,sync,dirsync,trans=virtio,noauto,x-systemd.automount,version=9p2000.L,msize=262144,cache=none,access=client,posixacl 0 0
root /root 9p rw,noatime,nodiratime,relatime,sync,dirsync,trans=virtio,noauto,x-systemd.automount,version=9p2000.L,msize=262144,cache=none,access=client,posixacl 0 0
images /var/lib/libvirt/images 9p rw,noatime,nodiratime,relatime,sync,dirsync,trans=virtio,noauto,x-systemd.automount,version=9p2000.L,msize=262144,cache=none,access=client,posixacl 0 0
qemu /etc/libvirt/qemu 9p rw,noatime,nodiratime,relatime,sync,dirsync,trans=virtio,noauto,x-systemd.automount,version=9p2000.L,msize=262144,cache=none,access=client,posixacl 0 0

## end of file""" | tee $TARGET/etc/fstab

echo """## /etc/modules
9p
9pnet
9pnet_virtio
## end of file""" | tee $TARGET/etc/modules

echo """## /etc/initramfs-tools/modules
virtio_balloon
virtio_blk
virtio_net
virtio_pci
virtio_ring
virtio
ext4
9p
9pnet
9pnet_virtio
## end of file""" | tee $TARGET/etc/initramfs-tools/modules

echo """## /etc/apt/sources.list

deb http://us.archive.ubuntu.com/ubuntu xenial main restricted universe multiverse
deb http://us.archive.ubuntu.com//ubuntu xenial-updates main restricted universe multiverse
deb http://us.archive.ubuntu.com//ubuntu xenial-proposed main restricted universe multiverse
# deb http://us.archive.ubuntu.com//ubuntu xenial-backports main restricted universe multiverse
# deb http://security.ubuntu.com/ubuntu xenial-security main restricted universe multiverse

deb-src http://us.archive.ubuntu.com/ubuntu xenial main restricted universe multiverse
deb-src http://us.archive.ubuntu.com//ubuntu xenial-updates main restricted universe multiverse
deb-src http://us.archive.ubuntu.com//ubuntu xenial-proposed main restricted universe multiverse
# deb-src http://us.archive.ubuntu.com//ubuntu xenial-backports main restricted universe multiverse
# deb-src http://security.ubuntu.com/ubuntu xenial-security main restricted universe multiverse

deb http://ddebs.ubuntu.com xenial main restricted universe multiverse
deb http://ddebs.ubuntu.com xenial-updates main restricted universe multiverse
deb http://ddebs.ubuntu.com xenial-proposed main restricted universe multiverse

## end of file""" | tee $TARGET/etc/apt/sources.list

echo """## /etc/apt/apt.conf

#Acquire::http::Proxy \"http://0.0.0.0:3128/\";
APT::Install-Recommends \"true\";
APT::Install-Suggests \"false\";
# APT::Get::Assume-Yes \"true\";
# APT::Get::Show-Upgraded \"true\";
APT::Quiet \"true\";
DPkg::Options { \"--force-confdef\";\"--force-confmiss\";\"--force-confold\"};
Debug::pkgProblemResolver \"true\";
Acquire::Languages \"none\";

## end of file""" | tee $TARGET/etc/apt/apt.conf


echo """## /etc/network/interfaces

auto lo
iface lo inet loopback
    dns-nameserver 8.8.8.8
    dns-nameserver 8.8.4.4

iface eth0 inet manual

auto bridge0
iface bridge0 inet dhcp
    bridge_ports eth0
    bridge_waitport 0
    bridge_fd 0
    bridge_stp off
    bridge_maxwait 0

source /etc/network/interfaces.d/*

## end of file""" | tee $TARGET/etc/network/interfaces

echo "" | tee $TARGET/etc/motd
echo "" | tee $TARGET/etc/issue
echo "" | tee $TARGET/etc/issue.net

echo """## /etc/ssh/sshd_config

Port 22
AddressFamily inet
ListenAddress 0.0.0.0
#ListenAddress ::

#HostKey /etc/ssh/ssh_host_rsa_key
#HostKey /etc/ssh/ssh_host_ecdsa_key
#HostKey /etc/ssh/ssh_host_ed25519_key

#RekeyLimit default none

SyslogFacility AUTH
LogLevel INFO

LoginGraceTime 1m
PermitRootLogin prohibit-password
StrictModes yes
MaxAuthTries 5
MaxSessions 20

PubkeyAuthentication yes

#AuthorizedKeysFile .ssh/authorized_keys
AuthorizedPrincipalsFile none
AuthorizedKeysCommand none
AuthorizedKeysCommandUser nobody

HostbasedAuthentication no
IgnoreUserKnownHosts no
IgnoreRhosts yes

PasswordAuthentication yes
PermitEmptyPasswords no
ChallengeResponseAuthentication no
GSSAPIAuthentication no
UsePAM yes

AllowAgentForwarding yes
AllowTcpForwarding yes
GatewayPorts yes
X11Forwarding yes
X11DisplayOffset 10
X11UseLocalhost yes
PermitTTY yes
PrintMotd no
PrintLastLog no
TCPKeepAlive yes
UseLogin no
PermitUserEnvironment no
Compression delayed
#ClientAliveInterval 0
#ClientAliveCountMax 3
UseDNS no
#PidFile /var/run/sshd.pid
#MaxStartups 10:30:100
PermitTunnel yes
#ChrootDirectory none
#VersionAddendum none
Banner none

AcceptEnv LANG LC_* EDITOR PAGER SYSTEMD_EDITOR

Subsystem	sftp	/usr/lib/openssh/sftp-server

## end of file""" | tee $TARGET/etc/ssh/sshd_config

echo """## /etc/ssh/ssh_config

Host *
#   ForwardAgent no
#   ForwardX11 no
#   ForwardX11Trusted yes
#   PasswordAuthentication yes
#   HostbasedAuthentication no
#   GSSAPIAuthentication no
#   GSSAPIDelegateCredentials no
#   GSSAPIKeyExchange no
#   GSSAPITrustDNS no
#   BatchMode no
#   CheckHostIP yes
#   AddressFamily any
#   ConnectTimeout 0
#   IdentityFile ~/.ssh/id_rsa
#   IdentityFile ~/.ssh/id_dsa
#   IdentityFile ~/.ssh/id_ecdsa
#   IdentityFile ~/.ssh/id_ed25519
#   Port 22
#   Protocol 2
#   Ciphers aes128-ctr,aes192-ctr,aes256-ctr,aes128-cbc,3des-cbc
#   MACs hmac-md5,hmac-sha1,umac-64@openssh.com
#   EscapeChar ~
#   Tunnel no
#   TunnelDevice any:any
#   PermitLocalCommand no
#   VisualHostKey no
#   ProxyCommand ssh -q -W %h:%p gateway.example.com
#   RekeyLimit 1G 1h
#   GSSAPIAuthentication no
    SendEnv LANG LC_* EDITOR PAGER
    StrictHostKeyChecking no
    HashKnownHosts yes

## end of file""" | tee $TARGET/etc/ssh/ssh_config

echo """## /etc/hosts

127.0.0.1 localhost
127.0.1.1 $HOSTNAME

::1 localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

## end of file""" | tee $TARGET/etc/hosts

echo """## /etc/pam.d/sshd

@include common-auth

account    required     pam_nologin.so

@include common-account

session [success=ok ignore=ignore module_unknown=ignore default=bad]        pam_selinux.so close
session    required     pam_loginuid.so
session    optional     pam_keyinit.so force revoke

@include common-session

session    required     pam_limits.so
session    required     pam_env.so # [1]
session    required     pam_env.so user_readenv=1 envfile=/etc/default/locale
session [success=ok ignore=ignore module_unknown=ignore default=bad]        pam_selinux.so open

@include common-password

## end of file""" | tee $TARGET/etc/pam.d/sshd

echo """## /etc/pam.d/login

auth       optional   pam_faildelay.so  delay=3000000

auth [success=ok new_authtok_reqd=ok ignore=ignore user_unknown=bad default=die] pam_securetty.so

auth       requisite  pam_nologin.so

session [success=ok ignore=ignore module_unknown=ignore default=bad] pam_selinux.so close
session    required     pam_loginuid.so
session [success=ok ignore=ignore module_unknown=ignore default=bad] pam_selinux.so open
session       required   pam_env.so readenv=1
session       required   pam_env.so readenv=1 envfile=/etc/default/locale

@include common-auth

auth       optional   pam_group.so

session    required   pam_limits.so
session    optional   pam_keyinit.so force revoke

@include common-account
@include common-session
@include common-password

## end of file """ | tee $TARGET/etc/pam.d/login

ARCH=$(uname -r | cut -d'-' -f3)

set +e

chroot $TARGET /bin/bash -c "http_proxy='' apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 04EE7237B7D453EC"
chroot $TARGET /bin/bash -c "http_proxy='' apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 7638D0442B90D010"
chroot $TARGET /bin/bash -c "http_proxy='' apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C8CAB6595FDFF622"

chroot $TARGET /bin/bash -c "apt-get update"
chroot $TARGET /bin/bash -c "apt-get install -y linux-image-generic linux-headers-generic"
chroot $TARGET /bin/bash -c "apt-get build-dep -y hello"

chroot $TARGET /bin/bash -c "apt-get install -y libvirt0 libvirt-bin"
chroot $TARGET /bin/bash -c "apt-get install -y libvirt-clients libvirt-daemon libvirt-daemon-system"
chroot $TARGET /bin/bash -c "apt-get install -y qemu-system-x86 qemu-user-static qemu-utils qemu-kvm"
chroot $TARGET /bin/bash -c "apt-get install -y qemu-block-extra"

set -e

echo """## /etc/libvirt/qemu.conf

user = "root"
group = "root"
dynamic_ownership = 0
clear_emulator_capabilities = 0
seccomp_sandbox = 0

## end of file """ | tee $TARGET/etc/libvirt/qemu.conf

umount $TARGET/dev/pts
umount $TARGET/dev
umount $TARGET/sys
umount $TARGET/proc/sys/fs/binfmt_misc
umount $TARGET/proc
umount $TARGET

qemu-nbd -d $NBDDEV
qemu-nbd -d $NBDDEV 2>&1 > /dev/null
qemu-nbd -d $NBDDEV 2>&1 > /dev/null

NEWUUID=$(uuidgen)
NEWMAC=$(printf '52:54:00:%02X:%02X:%02X\n' $[RANDOM%256] $[RANDOM%256] $[RANDOM%256])

XML="""<domain type='kvm'>
  <name>$HOSTNAME</name>
  <uuid>$NEWUUID</uuid>
  <memory unit='GiB'>$RAMGB</memory>
  <currentMemory unit='GiB'>$RAMGB</currentMemory>
  <vcpu placement='static'>$VCPUS</vcpu>
  <resource>
    <partition>/machine</partition>
  </resource>
  <os>
    <type arch='x86_64' machine='pc-i440fx-2.5'>hvm</type>
    <kernel>$IMGDIR/$HOSTNAME/vmlinuz</kernel>
    <initrd>$IMGDIR/$HOSTNAME/initrd.img</initrd>
    <cmdline>root=/dev/vda noresume console=tty0 console=ttyS0,38400n8 apparmor=0 net.ifnames=0 crashkernel=256M</cmdline>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
    <apic/>
  </features>
  <cpu mode='host-passthrough' check='none'/>
  <clock offset='utc'>
    <timer name='rtc' tickpolicy='catchup'/>
    <timer name='pit' tickpolicy='delay'/>
    <timer name='hpet' present='yes'/>
  </clock>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <pm>
    <suspend-to-mem enabled='no'/>
    <suspend-to-disk enabled='no'/>
  </pm>
  <devices>
    <emulator>/usr/bin/qemu-system-x86_64</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='$IMGDIR/$HOSTNAME/disk01.ext4.qcow2'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    <controller type='usb' index='0' model='piix3-uhci'>
    </controller>
    <controller type='pci' index='0' model='pci-root'/>
    <filesystem type='mount' accessmode='passthrough'>
      <source dir='/home/inaddy'/>
      <target dir='inaddy'/>
    </filesystem>
    <filesystem type='mount' accessmode='passthrough'>
      <source dir='/root'/>
      <target dir='root'/>
    </filesystem>
    <filesystem type='mount' accessmode='passthrough'>
      <source dir='/var/lib/libvirt/images'/>
      <target dir='images'/>
    </filesystem>
    <filesystem type='mount' accessmode='passthrough'>
      <source dir='/etc/libvirt/qemu'/>
      <target dir='qemu'/>
    </filesystem>
    <interface type='bridge'>
      <mac address='$NEWMAC'/>
      <source bridge='$INTERFACE'/>
      <model type='virtio'/>
    </interface>
    <serial type='pty'>
      <target type='isa-serial' port='0'>
        <model name='isa-serial'/>
      </target>
    </serial>
    <console type='pty'>
      <target type='serial' port='0'/>
    </console>
    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
    <memballoon model='virtio'>
    </memballoon>
  </devices>
</domain>"""

echo $XML > $TMPDIR/$HOSTNAME.xml

virsh define $TMPDIR/$HOSTNAME.xml
