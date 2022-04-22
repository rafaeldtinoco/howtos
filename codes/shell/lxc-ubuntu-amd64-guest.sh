#!/bin/bash -x

apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 04EE7237B7D453EC
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 7638D0442B90D010
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C8CAB6595FDFF622

flavor=$(lsb_release -c -s)

echo """## /etc/apt/sources.list

deb http://ubuntu.c3sl.ufpr.br/ubuntu/ disco main restricted universe multiverse
deb-src http://ubuntu.c3sl.ufpr.br/ubuntu/ disco main restricted universe multiverse
deb http://ubuntu.c3sl.ufpr.br/ubuntu/ disco-updates main restricted universe multiverse
deb-src http://ubuntu.c3sl.ufpr.br/ubuntu/ disco-updates main restricted universe multiverse
deb http://ubuntu.c3sl.ufpr.br/ubuntu/ disco-proposed main restricted universe multiverse
deb-src http://ubuntu.c3sl.ufpr.br/ubuntu/ disco-proposed main restricted universe multiverse
# deb http://ubuntu.c3sl.ufpr.br/ubuntu/ disco-backports main restricted universe multiverse
# deb-src http://ubuntu.c3sl.ufpr.br/ubuntu/ disco-backports main restricted universe multiverse
# deb http://security.ubuntu.com/ubuntu disco-security main restricted universe multiverse
# deb-src http://security.ubuntu.com/ubuntu disco-security main restricted universe multiverse

deb http://ddebs.ubuntu.com disco main restricted universe multiverse
deb http://ddebs.ubuntu.com disco-updates main restricted universe multiverse
deb http://ddebs.ubuntu.com disco-proposed main restricted universe multiverse

## end of file""" | tee /etc/apt/sources.list

apt-get update -y
apt-get dist-upgrade -y

sudo apt-get install -y gnupg
sudo apt-get install -y gnupg1
sudo apt-get install -y gnupg2
sudo apt-get install -y bridge-utils net-tools vlan ifupdown resolvconf

set -e

# http_proxy="http://172.16.0.1:3142/" ; export http_proxy ;
# https_proxy="https://172.16.0.1:3142/" ; export https_proxy ;
# ftp_proxy="ftp://172.16.0.1:3142/" ; export ftp_proxy ;

PACKAGES="""\
locales less vim sudo openssh-server bash-completion \
wget rsync git bridge-utils vlan xterm ncurses-term \
build-essential mtr-tiny iputils-arping lsof strace ltrace \
iputils-ping iputils-tracepath dnsutils bridge-utils lsb-release \
tcpdump curl openssh-server openssh-client gdebi-core git \
devscripts gnupg vlan
"""

apt-get install -y $PACKAGES

echo en_US.UTF-8 > /etc/locale.gen
locale-gen en_US.UTF-8

set +e

passwd -d root
useradd -d /home/inaddy -m -s /bin/bash inaddy
passwd -d inaddy

echo root:root | chpasswd
echo inaddy:inaddy | chpasswd

groupdel dialout
groupmod -g 20 -o inaddy
usermod -u 501 -g 20 -o inaddy
#chown -R inaddy:inaddy /home/inaddy

usermod -a -G root inaddy
usermod -a -G sudo inaddy
usermod -a -G shadow inaddy
usermod -a -G staff inaddy
usermod -a -G users inaddy
usermod -a -G nogroup inaddy
usermod -a -G syslog inaddy
usermod -a -G crontab inaddy
usermod -a -G libvirt inaddy
usermod -a -G libvirtd inaddy
usermod -a -G libvirt-qemu inaddy
usermod -a -G kvm inaddy

set -e

echo """## /etc/apt/apt.conf

# Acquire::http::Proxy \"http://172.16.0.1:3142/\";

## end of file""" | tee /etc/apt/apt.conf

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

## end of file""" | tee /etc/sudoers

echo """## /etc/modules
## end of file""" | tee /etc/modules

echo """## /etc/initramfs-tools/modules
## end of file""" | tee /etc/initramfs-tools/modules


echo """## /etc/network/interfaces

auto lo
iface lo inet loopback
    dns-nameservers 192.168.100.1
    post-up sysctl -w net.ipv4.conf.all.forwarding=0
    post-up sysctl -w net.ipv4.conf.default.forwarding=0
    pre-down sysctl -w net.ipv4.conf.all.forwarding=0
    pre-down sysctl -w net.ipv4.conf.default.forwarding=0

iface eth0 inet manual
    post-up sysctl -w net.ipv6.conf.eth0.disable_ipv6=1
    post-up sysctl -w net.ipv4.conf.eth0.forwarding=0
    pre-down sysctl -w net.ipv4.conf.eth0.forwarding=0
    pre-down sysctl -w net.ipv6.conf.eth0.disable_ipv6=0

auto bridge0
iface bridge0 inet dhcp
    bridge_ports eth0
    bridge_waitport 0
    bridge_fd 0
    bridge_stp off
    bridge_maxwait 0
    hwaddress 52:54:00:BC:17:80
    post-up sysctl -w net.ipv6.conf.bridge0.disable_ipv6=1
    post-up sysctl -w net.ipv4.conf.bridge0.forwarding=0
    pre-down sysctl -w net.ipv4.conf.bridge0.forwarding=0
    pre-down sysctl -w net.ipv6.conf.bridge0.disable_ipv6=0

## end of file""" | tee /etc/network/interfaces

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

ARCH=$(uname -r | cut -d'-' -f3)

apt-get install -y linux-image-generic linux-headers-generic
apt-get build-dep -y hello

set +e

apt-get install -y libvirt0 libvirt-bin
apt-get install -y libvirt-clients libvirt-daemon libvirt-daemon-system
apt-get install -y qemu-system-x86 qemu-user-static qemu-utils qemu-kvm
apt-get install -y qemu-block-extra

set -e

echo """## /etc/libvirt/qemu.conf

user = \"root\"
group = \"root\"
dynamic_ownership = 0
clear_emulator_capabilities = 0
seccomp_sandbox = 0

## end of file """ | tee /etc/libvirt/qemu.conf
