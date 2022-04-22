#!/usr/bin/python3

import sys
import os
import tempfile

def comando(cmd):
    p = os.popen(cmd, "r")
    line = p.read().strip()
    p.close()
    return line

class pkg():

    name = ""
    uver = 0
    dver = 0

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def getupver(self):
        """ get pkg version upstream """
        pass

    def getuver(self):
        """ get pkg version in ubuntu """

        if self.uver is not 0:
            return self.uver

        cmd = "rmadison -a source -u ubuntu -s focal %s" % self.name
        line = comando(cmd).split("|")[1].strip()
        self.uver = line

        return self.uver

    def getdver(self):
        """ get pkg version in debian """

        if self.dver is not 0:
            return self.dver

        print("checking package %s" % self.name)
        cmd = "rmadison -a source -u debian -s unstable %s" % self.name
        line = comando(cmd).split("|")[1].strip()
        self.dver = line

        return self.dver

    def compare(self, ver1, oper, ver2):
        """ compare pkg versions with given operator """

        cmd = "dpkg --compare-versions %s '%s' %s && echo true || echo false" % (ver1, oper, ver2)
        result = comando(cmd)
        if "true" in result:
            return True
        return False

    def needmerge(self):
        """ check if ubuntu pkg needs merge """

        if self.dver is 0:
            self.getdver()
        if self.uver is 0:
            self.getuver()

        if self.compare(self.dver, "gt", self.uver) is True:
            return True
        return False

class hapkgs():

    pkgs = []
    updated = []
    outdated = []

    def __init__(self):
        #
        # PACKAGES: https://bugs.launchpad.net/~ubuntu-server-ha/+packagebugs
        # BUGS: https://bugs.launchpad.net/~ubuntu-server-ha
        # TODO: integrate with LP
        #
        filed = open("mymerges.txt", "r+");
        buffer = filed.read()
        filed.close()

        for line in buffer.split("\n"):
            if line:
                self.pkgs.append(pkg(line.strip()))

    def __iter__(self):
        for pkg in self.pkgs:
            yield pkg

    def updated(self):
        for pkg in self.pkgs:
            if not pkg.needmerge():
                yield pkg

    def outdated(self):
        for pkg in self.pkgs:
            if pkg.needmerge():
                yield pkg

if __name__ == '__main__':

    pkgs = hapkgs()

    for pkg in pkgs.outdated():
        print("Package: %s (debian: %s, ubuntu: %s) needs merge" % (pkg, pkg.getdver(), pkg.getuver()))


