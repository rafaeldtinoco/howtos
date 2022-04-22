#!/bin/bash -x

if [ $UID -ne 0 ]; then
    # re-run as root

    sudo $0
    exit 0
fi

apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 04EE7237B7D453EC
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 7638D0442B90D010
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C8CAB6595FDFF622

flavor=$(lsb_release -c -s)
myarch=$(uname -i)

case $myarch in

s390x|armv8l|aarch64)

echo """## /etc/apt/sources.list

deb http://ports.ubuntu.com/ubuntu-ports $flavor main restricted universe multiverse
deb http://ports.ubuntu.com/ubuntu-ports $flavor-updates main restricted universe multiverse
deb http://ports.ubuntu.com/ubuntu-ports $flavor-proposed main restricted universe multiverse
# deb http://ports.ubuntu.com/ubuntu-ports $flavor-backports main restricted universe multiverse
# deb http://security.ubuntu.com/ubuntu $flavor-security main restricted universe multiverse

deb-src http://ports.ubuntu.com/ubuntu-ports $flavor main restricted universe multiverse
deb-src http://ports.ubuntu.com/ubuntu-ports $flavor-updates main restricted universe multiverse
deb-src http://ports.ubuntu.com/ubuntu-ports $flavor-proposed main restricted universe multiverse
# deb-src http://ports.ubuntu.com/ubuntu-ports $flavor-backports main restricted universe multiverse
# deb-src http://security.ubuntu.com/ubuntu $flavor-security main restricted universe multiverse

deb http://ddebs.ubuntu.com $flavor main restricted universe multiverse
deb http://ddebs.ubuntu.com $flavor-updates main restricted universe multiverse
deb http://ddebs.ubuntu.com $flavor-proposed main restricted universe multiverse

## end of file""" | tee /etc/apt/sources.list

;;

*)
echo """## /etc/apt/sources.list

deb http://br.archive.ubuntu.com/ubuntu/ $flavor main restricted universe multiverse
deb http://br.archive.ubuntu.com/ubuntu/ $flavor-updates main restricted universe multiverse
deb http://br.archive.ubuntu.com/ubuntu/ $flavor-proposed main restricted universe multiverse
# deb http://br.archive.ubuntu.com/ubuntu/ $flavor-backports restricted universe multiverse
# deb http://security.ubuntu.com/ubuntu/ $flavor-security main restricted universe multiverse

deb-src http://br.archive.ubuntu.com/ubuntu/ $flavor main restricted universe multiverse
deb-src http://br.archive.ubuntu.com/ubuntu/ $flavor-updates main restricted universe multiverse
deb-src http://br.archive.ubuntu.com/ubuntu/ $flavor-proposed main restricted universe multiverse
# deb-src http://br.archive.ubuntu.com/ubuntu/ $flavor-backports restricted universe multiverse
# deb-src http://security.ubuntu.com/ubuntu/ $flavor-security main restricted universe multiverse

deb http://ddebs.ubuntu.com $flavor main restricted universe multiverse
deb http://ddebs.ubuntu.com $flavor-updates main restricted universe multiverse
deb http://ddebs.ubuntu.com $flavor-proposed main restricted universe multiverse

## end of file""" | tee /etc/apt/sources.list
;;

esac

apt update -y
apt dist-upgrade -y

# locales

apt-get install -y locales
echo """LANG=\"en_US.UTF-8\"
LANGUAGE=\"en_US:en\"""" | tee /etc/default/locale
echo """en_US.UTF-8 UTF-8
en_GB.UTF-8 UTF-8""" | tee /etc/locale.gen
locale-gen

# gnupg

apt install -y gnupg
apt install -y gnupg1
apt install -y gnupg2

http_proxy="http://192.168.100.252:3128/" ; export http_proxy ;
https_proxy="http://192.168.100.252:3128/" ; export https_proxy ;
ftp_proxy="http://192.168.100.252:3128/" ; export ftp_proxy ;

apt install -y locales less vim sudo openssh-server bash-completion
apt install -y bridge-utils vlan ifupdown resolvconf net-tools
apt install -y wget rsync git curl tcpdump
apt install -y snapd squashfuse
apt install -y xterm ncurses-term
apt install -y mtr-tiny iputils-arping iputils-ping iputils-tracepath traceroute
apt install -y dnsutils
apt install -y openssh-client
apt install -y gdebi-core
apt install -y gtk2-engines gtk3-engines-breeze gnome-themes-standard
apt install -y x11-xserver-utils
apt install -y haveged

# users

passwd -d root
echo root:root | chpasswd

id rafaeldtinoco || {
        useradd -d /home/rafaeldtinoco -m -s /bin/bash rafaeldtinoco
        passwd -d rafaeldtinoco
        echo rafaeldtinoco:rafaeldtinoco | chpasswd
        usermod -a -G root rafaeldtinoco
        usermod -a -G sudo rafaeldtinoco
        usermod -a -G shadow rafaeldtinoco
        usermod -a -G staff rafaeldtinoco
        usermod -a -G users rafaeldtinoco
        usermod -a -G nogroup rafaeldtinoco
        usermod -a -G syslog rafaeldtinoco
        usermod -a -G crontab rafaeldtinoco
        usermod -a -G libvirt rafaeldtinoco
        usermod -a -G libvirtd rafaeldtinoco
        usermod -a -G libvirt-qemu rafaeldtinoco
        usermod -a -G kvm rafaeldtinoco
}

echo """## /etc/apt/apt.conf

Acquire::http::Proxy \"http://192.168.100.252:3128/\";

## end of file""" | tee /etc/apt/apt.conf

# echo """## /etc/network/interfaces
# 
# auto lo
# iface lo inet loopback
#     dns-nameservers 8.8.8.8
#     dns-nameservers 8.8.4.4
#     post-up sysctl -w net.ipv4.conf.all.forwarding=0
#     post-up sysctl -w net.ipv4.conf.default.forwarding=0
#     post-up sysctl -w net.ipv6.conf.all.disable_ipv6=1
#     post-up sysctl -w net.ipv6.conf.default.disable_ipv6=1
#     pre-down sysctl -w net.ipv4.conf.all.forwarding=0
#     pre-down sysctl -w net.ipv4.conf.default.forwarding=0
#     pre-down sysctl -w net.ipv6.conf.all.disable_ipv6=0
#     pre-down sysctl -w net.ipv6.conf.default.disable_ipv6=0
# 
# iface eth0 inet manual
#     mtu 1472
#     post-up sysctl -w net.ipv6.conf.eth0.disable_ipv6=1
#     post-up sysctl -w net.ipv4.conf.eth0.forwarding=0
#     pre-down sysctl -w net.ipv4.conf.eth0.forwarding=0
#     pre-down sysctl -w net.ipv6.conf.eth0.disable_ipv6=0
# 
# auto bridge0
# iface bridge0 inet dhcp
#     bridge_ports eth0
#     bridge_waitport 0
#     bridge_fd 0
#     bridge_stp off
#     bridge_maxwait 0
#     mtu 1472
#     post-up sysctl -w net.ipv6.conf.bridge0.disable_ipv6=1
#     post-up sysctl -w net.ipv4.conf.bridge0.forwarding=0
#     pre-down sysctl -w net.ipv4.conf.bridge0.forwarding=0
#     pre-down sysctl -w net.ipv6.conf.bridge0.disable_ipv6=0
# 
# ## end of file""" | tee /etc/network/interfaces

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
rafaeldtinoco ALL=(ALL) NOPASSWD: ALL

## end of file""" | tee /etc/sudoers

echo """## /etc/modules
nbd
## end of file""" | tee /etc/modules

echo """## /etc/initramfs-tools/modules
nbd
## end of file""" | tee /etc/initramfs-tools/modules

echo "" | tee /etc/motd
echo "" | tee /etc/issue
echo "" | tee /etc/issue.net

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
# UseLogin no
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

## end of file""" | tee /etc/ssh/sshd_config

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

## end of file""" | tee /etc/ssh/ssh_config

echo """## /etc/hosts

127.0.0.1 localhost
127.0.1.1 $HOSTNAME

::1 localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

## end of file""" | tee /etc/hosts

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

## end of file""" | tee /etc/pam.d/sshd

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

## end of file """ | tee /etc/pam.d/login

apt install -y libvirt0 libvirt-bin
apt install -y libvirt-clients libvirt-daemon libvirt-daemon-system

if [ "$myarch" == "aarch64" ] || [ "$myarch" == "armv8l" ]; then
    apt install -y qemu-system-arm
elif [ "$myarch" == "s390x" ]; then
    apt install -y qemu-system-s390x
else
    apt install qemu-system-x86
fi
apt install -y qemu-user-static qemu-utils qemu-kvm
apt install -y qemu-block-extra

echo """## /etc/libvirt/qemu.conf

user = \"root\"
group = \"root\"
dynamic_ownership = 0
clear_emulator_capabilities = 0
seccomp_sandbox = 0

## end of file """ | tee /etc/libvirt/qemu.conf

## final stage

# cloud-init removal

apt remove --purge -y cloud-guest-utils
apt remove --purge -y cloud-init
apt remove --purge -y cloud-initramfs-copymods
apt remove --purge -y cloud-initramfs-dyn-netconf

# leftovers

apt remove --purge -y unattended-upgrades
apt remove --purge -y irqbalance
apt remove --purge -y open-iscsi
apt remove --purge -y multipath-tools
apt remove --purge -y thermald
apt remove --purge -y pollinate
apt remove --purge -y ufw

# services

systemctl disable systemd-resolved
systemctl disable accounts-daemon.service
systemctl disable apparmor.service
systemctl disable apport-autoreport.path
systemctl disable apport-forward.socket
systemctl disable apt-daily-upgrade.timer
systemctl disable apt-daily.timer
systemctl disable dbus-org.freedesktop.thermald.service
systemctl disable dbus-org.freedesktop.timesync1.service
systemctl disable ebtables.service
systemctl disable irqbalance.service
systemctl disable iscsi.service
systemctl disable iscsid.socket
systemctl disable motd-news.timer
systemctl disable multipath-tools.service
systemctl disable multipathd.service
systemctl disable multipathd.socket
systemctl disable open-iscsi.service
systemctl disable pollinate.service
systemctl disable rsync.service
systemctl disable thermald.service
systemctl disable ufw.service
systemctl disable unattended-upgrades.service
systemctl disable systemd-networkd-wait-online.service;

systemctl disable lvm2-lvmpolld.socket
systemctl disable lvm2-monitor.service
systemctl disable man-db.timer
systemctl disable networkd-dispatcher.service
systemctl disable secureboot-db.service
systemctl disable libvirtd.service
systemctl disable libvirt-guests.service
systemctl disable qemu-kvm.service
systemctl disable virtlockd.socket
systemctl disable virtlogd.socket
systemctl disable virtlockd-admin.socket
systemctl disable virtlogd-admin.socket
systemctl disable ureadahead.service
systemctl disable lvm2-lvmetad.socket
systemctl disable e2scrub_all.timer
systemctl disable e2scrub_reap.service

# development

apt install -y linux-headers-generic
apt install -y build-essential
apt install -y devscripts
apt install -y ubuntu-dev-tools

apt-get build-dep -y hello
apt-get build-dep -y linux-image-$(uname -r)

# snapd

apt install -y snapd
snap install hello-world
snap install --edge --clasic git-ubuntu

# perf tools

apt install -y htop atop iotop
systemctl disable atop.service
systemctl disable atopacct.service
