#!/usr/bin/python

import sys
import os
import tempfile

from termcolor import colored

def syntax(progname):

    print("""syntax:

    %s [guest name] [add|remove] [add: ibiface name]

    [guest name]   = virsh list output
    [add | remove]
    [ibface]       = IB interface like listed in "ibstat -l" output

    Example: %s guest add mlx5_2
    Example: %s guest remove

    Result:
    """ %  (progname, progname, progname))
    sys.exit(1)

def exiterr(given):

    print ""
    print colored("ERROR: %s" % given, "red")
    print ""

    sys.exit(1)

## all kvm guests

class kvm_vms():

    " all existing KVM guests "

    allvms = []

    def __str__(self):
        return '\n'.join([str(x) for x in self.allvms])

    def __init__(self):

        cmd = "/usr/bin/virsh list --name --all"

        p = os.popen(cmd, "r")

        lines = p.read().strip().split("\n")

        for line in lines:
            self.allvms.append(kvm_vm(line))

        p.close()

    def __iter__(self):
        for onevm in self.allvms:
            yield onevm

    def pci_used(self, pci):
        for onevm in self.allvms:
            if onevm.used(pci) is True:
                return True
        return False

    def find(self, guest):
        for onevm in self.allvms:
            if str(onevm) == guest:
                return onevm

## one kvm guest

class kvm_vm():

    xml="""<hostdev mode='subsystem' type='pci' managed='yes'>
    <source><address domain='%s' bus='%s' slot='%s' function='%s'/>
    </source></hostdev>"""

    def __init__(self, value):
        self.name = value
        self._readxml()
        self.tmpfile = None

    def _readxml(self):

        cmd = "virsh dumpxml %s" % self.name
        p = os.popen(cmd, "r")
        found = 0

        while 1:
            line = p.readline().strip()
            if not line: break
            if "<hostdev mode='subsystem' type='pci' managed='yes'>" in line: found = 1
            if found == 1 and "<address domain=" in line: break

        if found:
            _ = line.replace("0x","").split("'")

            self.ibpci = "%s:%s:%s.%s" % (_[1], _[3], _[5], _[7])
            self.ibpci_domain = "0x%s" % _[1]
            self.ibpci_bus = "0x%s" %  _[3]
            self.ibpci_slot = "0x%s" %  _[5]
            self.ibpci_function = "0x%s" %  _[7]

        else:
            self.ibpci = ""

    def __str__(self):
        return self.name

    def pci(self):
        return self.ibpci

    def used(self, pci):
        if pci in self.ibpci:
            return True
        return False

    def has_virtfn(self):
        if len(self.ibpci) is 0:
            return False
        return True

    def add_virtfn(self, pciaddr):

        if self.has_virtfn():
            raise Exception("guest already has virtual function")

        _ = pciaddr.split(":")
        domain = "0x%s" % _[0]
        bus = "0x%s" % _[1]
        slot = "0x%s" % _[2].split(".")[0]
        function = "0x%s" % _[2].split(".")[1]

        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(self.xml % (domain, bus, slot, function))
        tmp.close()

        cmd = "virsh attach-device %s --file %s --config 2>&1 > /dev/null" % (self.name, tmp.name)
        ret = os.system(cmd)
        if ret:
            raise Exception("could not attach device")

        os.unlink(tmp.name)

        self._readxml()

    def del_virtfn(self):

        if not self.has_virtfn():
            raise Exception("guest does not have virtual function")

        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(self.xml % (self.ibpci_domain, self.ibpci_bus, self.ibpci_slot, self.ibpci_function))
        tmp.close()

        cmd = "virsh detach-device %s --file %s --config 2>&1 > /dev/null 2>&1" % (self.name, tmp.name)
        ret = os.system(cmd)
        if ret:
            raise Exception("could not detach device")

        os.unlink(tmp.name)

        self._readxml()

## all IB interfaces

class ib_ifaces():

    ibifaces = []

    def __str__(self):
        return '\n'.join([x for x in self.ibifaces])

    def __init__(self, values):
        for value in values[-1:]:
            self.ibifaces.append(ib_iface(value))

    def __iter__(self):
        for ibiface in self.ibifaces:
            yield ibiface

## one IB interface

class ib_iface():

    ibiface = ""
    num_vfs = 0
    ibvirtfns = []

    def __str__(self):
        return self.ibiface

    def __init__(self, value):

        self.ibiface = value

        dir = "/sys/class/infiniband/%s/device/" % self.ibiface
        uevent = "%s/uevent" % dir
        netdir = "%s/net" % dir

        try:
            self.num_vfs = open("%s/mlx5_num_vfs" % dir).read().strip()
        except:
            raise Exception("%s does not look like a physical function" % self.ibiface)

        self.ibvirtfnpci = [line for line in open(uevent).read().split('\n') \
                            if line.startswith('PCI_SLOT')][0].replace("PCI_SLOT_NAME=","")

        for file in os.listdir(netdir):
            if file.startswith("ib"):
                self.ibnetdev = file

        for file in os.listdir(dir):
            if file.startswith("virtfn"):
                self.ibvirtfns.append(ib_virtfn(file, self))

    def __iter__(self):
        for ibvirtfn in self.ibvirtfns:
            yield ibvirtfn

    def pci(self):
        return self.ibvirtfnpci

    def dev(self):
        return self.ibiface

    def netdev(self):
        return self.ibnetdev

## one IB virtual function

class ib_virtfn():

    ibvirtfn = ""
    inuse = False

    def __str__(self):
        return self.ibvirtfn

    def __init__(self, value, parent):
        self.ibvirtfn = value
        self.ibiface = parent

        dir = "/sys/class/infiniband/%s/device/%s" % (self.ibiface, self.ibvirtfn)
        uevent = "%s/uevent" % dir
        ibdevdir = "%s/infiniband" % dir
        netdir = "%s/net" % dir

        self.ibvirtfnpci = [line for line in open(uevent).read().split('\n') \
                            if line.startswith('PCI_SLOT')][0].replace("PCI_SLOT_NAME=","")

        try:
            for file in os.listdir(ibdevdir):
                if file.startswith("mlx"):
                    self.ibvirtfndev = file
        except:
            self.inuse = True
            self.ibvirtfndev = None

        try:
            for file in os.listdir(netdir):
             if file.startswith("ib"):
                    self.ibnetdev = file
        except:
            self.inuse = True
            self.ibnetdev = None

    def parent(self):
        return self.ibiface

    def pci(self):
        return self.ibvirtfnpci

    def dev(self):
        return self.ibvirtfndev

    def netdev(self):
        return self.ibnetdev

## main

if __name__ == '__main__':

    if os.getuid() is not 0:
        exiterr(Exception("not root"))

    progname = sys.argv[0]
    sys.argv.pop(0)

    if len(sys.argv) <= 1:
        syntax(progname)

    if len(sys.argv) <= 2 and "remove" not in sys.argv[1]:
        syntax(progname)

    guestname = sys.argv[0]
    sys.argv.pop(0)
    command = sys.argv[0]
    sys.argv.pop(0)

    givenibfaces = []
    for arg in sys.argv:
        givenibfaces.append(arg)

    ibfaces = []

    if "add" not in command and "remove" not in command:
        syntax(progname)

    if "add" in command:

        try:
            ibfaces = ib_ifaces(givenibfaces)
        except Exception as error:
            exiterr(error)

    vms = kvm_vms()

    if "remove" in command:

        thevm = vms.find(guestname)
        try:
            thevm.del_virtfn()
        except Exception as error:
            exiterr(error)
        sys.exit(0)

    first = False

    print ""
    print "Available Functions and Virtual Functions:"
    print ""

    for ibface in ibfaces:

        print " Physical Function %s:" % ibface.dev()
        print ""

        string = "\t%s\t\tPCI: %s\tNET: %s" % (ibface.dev(), ibface.pci(), ibface.netdev())

        print colored(string, "blue")

        print ""
        print "Virtual Functions for %s:" % ibface.dev()
        print ""

        for ibvirtfn in ibface:

            used = vms.pci_used(ibvirtfn.pci())

            if used: color = 'magenta'
            else: color = 'green'

            if not used and not first:
                first = True
                color = 'yellow'
                thevm = vms.find(guestname)

                try:
                    thevm.add_virtfn(ibvirtfn.pci())
                except Exception as error:
                    exiterr(error)

            string = "\t%s\t\tPCI: %s\tNET: %s" % (ibvirtfn.dev(), ibvirtfn.pci(), ibvirtfn.netdev())

            print colored(string, color)

    print ""
    print colored(" blue means function is real", "blue")
    print colored(" green means virtual function is free", "green")
    print colored(" magenta means virtual function is being used by a KVM guest", "red")
    print colored(" yellow is the virtual function to be added to given KVM guest", "yellow")
    print ""

