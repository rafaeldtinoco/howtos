#!/usr/bin/python3 -B

import sys
import os

sys.path.append(os.path.abspath("/home/inaddy/work/codes/scripts"))
from myfunctions import *

def syntax():
    print("%s [container]" % sys.argv[0])
    sys.exit(1)

def fileaptsources(c):
    contents = """## /etc/apt/sources.list

deb http://ftp.us.debian.org/debian/ sid main contrib non-free
deb-src http://ftp.us.debian.org/debian/ sid main contrib non-free

# deb http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main
# deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main

## end of file"""

    filed = open("/tmp/sources.list", "w")
    filed.write(contents)
    filed.close()
    transferlxc(c, "/tmp/sources.list", "/etc/apt/sources.list")

def fileaptconf(c):
    contents = """## /etc/apt/apt.conf

Acquire::http::Proxy "";
APT::Install-Recommends "true";
# APT::Install-Suggests "false";
# APT::Get::Assume-Yes "true";
# APT::Get::Show-Upgraded "true";
# APT::Quiet "true";
DPkg::Options {"--force-confdef";"--force-confmiss";"--force-confold"};
Debug::pkgProblemResolver "true";
Acquire::Languages "none";

## end of file"""

    filed = open("/tmp/apt.conf", "w")
    filed.write(contents)
    filed.close()
    transferlxc(c, "/tmp/apt.conf", "/etc/apt/apt.conf")

def filesudoers(c):
    contents = """## /etc/sudoers

Defaults env_reset
Defaults mail_badpass
Defaults secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Defaults logfile=/var/log/sudo.log,loglinelen=0
Defaults !syslog, !pam_session
root ALL=(ALL:ALL) ALL
%admin ALL=(ALL) ALL
%sudo ALL=(ALL:ALL) ALL
inaddy ALL=(ALL) NOPASSWD: ALL
#includedir /etc/sudoers.d

## end of file"""

    filed = open("/tmp/sudoers", "w")
    filed.write(contents)
    filed.close()
    transferlxc(c, "/tmp/sudoers", "/etc/sudoers", uid=0, gid=0, fmode="0440")

if __name__ == '__main__':

    inicio(debug=True)

    if len(sys.argv) < 2:
        syntax()

    c = sys.argv[1]

    packages = []

    packages.append("bash-completion")
    packages.append("vim")
    packages.append("wget")
    packages.append("rsync")
    packages.append("ccze")
    packages.append("git")
    packages.append("build-essential")
    packages.append("gdb")
    packages.append("gdbserver")
    packages.append("crash")
    packages.append("git-email")
    packages.append("ctags")
    packages.append("cscope")
    packages.append("ccache")

    srcpkgs = []

    srcpkgs.append("hello")
    srcpkgs.append("linux-image-amd64")

    executa("lxc stop %s" % c)
    executa("lxc config set %s security.privileged true" % c)
    executa("lxc start %s" % c)

    executalxc(c, "locale-gen en_US.UTF-8")
    executalxc(c, "userdel -r ubuntu")
    executalxc(c, "passwd -d root")
    executalxc(c, "useradd -d /home/inaddy -s /bin/bash inaddy")
    executalxc(c, "passwd -d inaddy")
    executalxc(c, "echo root:root | chpasswd")
    executalxc(c, "echo inaddy:inaddy | chpasswd")

    fileaptsources(c)
    fileaptconf(c)
    filesudoers(c)

    executalxc(c, "rm -f /etc/apt/apt.conf.d/70debconf")
    executalxc(c, "dpkg-reconfigure debconf -f noninteractive -p critical")

    executalxc(c, "dpkg --configure -a")
    executalxc(c, "apt-get -f -y install")
    executalxc(c, "apt-get --purge autoremove -y")

    executalxc(c, "apt-get update")
    executalxc(c, "apt-get dist-upgrade -y")

    executalxc(c, "apt-get install -y %s" % " ".join(packages))
    executalxc(c, "apt-get build-dep -y %s" % " ".join(srcpkgs))

    executalxc(c, "apt-get --purge -y autoremove")
    executalxc(c, "apt-get autoclean")
