
from defines import *
from files import *
from data import *
from base import *
from filesystem import *

class time():

    def __init__(self, tod, server):

        self.serverid = server.getid()

        todstartf = file_line(tod.file("todstart"))
        todendf = file_line(tod.file("todend"))
        datef = file_line(tod.file("date"))

        self.todstart = todstartf.get()
        self.todend = todendf.get()
        self.date = datef.get()

    def build(self):

        serverid = self.serverid
        todstart = self.todstart
        todend = self.todend
        date = self.date

        self.data = {
        'time_id' : todstart,
        'server_id' : serverid,
        'date' : getdate(date),
        'delta': todend,
        }

    def sql(self, con):

        query = dbinsert("time", self.all(), "time_id")
        dbquery(con, query)

    def getid(self):
        return self.data['time_id']

    def get(self, key):
        return self.data[key]

    def all(self):
        return self.data

#
# SERVER INFORMATION
#

class server():

    def __init__(self, base):

        self.hostnamef = file_line(base.file("hostname"))
        self.cpuinfof = file_keyvalue(base.file("cpuinfo"))
        self.sysinfof = file_keyvalue(base.file("sysinfo"))
        self.versionf = file_line(base.file("version"))
        self.cmdlinef = file_line(base.file("cmdline"))

        self.serverid = 0

    def build(self):

        hostnamef = self.hostnamef
        cpuinfof = self.cpuinfof
        sysinfof = self.sysinfof
        versionf = self.versionf
        cmdlinef = self.cmdlinef

        hostname = hostnamef.get()

        is_dedicate = sysinfof.get("LPAR Characteristics"),
        if is_dedicate == "Shared": is_dedicate = "0"
        else: is_dedicate = "1"

        checksum = md5([hostname])

        self.data = {
        'p_server_id' : "0",
        'hostname' : hostname,
        'mach_type' : sysinfof.get("Type"),
        'mach_model' : " ".join(sysinfof.get("Model").split()),
        'mach_cpu_total' : sysinfof.get("CPUs Total"),
        'mach_cpu_configured' : sysinfof.get("CPUs Configured"),
        'mach_cpu_standby' : sysinfof.get("CPUs Standby") ,
        'mach_cpu_reserved' : sysinfof.get("CPUs Reserved"),
        'lpar_number' : sysinfof.get("LPAR Number"),
        'lpar_name' : sysinfof.get("LPAR Name"),
        'lpar_dedicated' : is_dedicate,
        'lpar_cpu_total' : sysinfof.get("LPAR CPUs Total"),
        'lpar_cpu_configured' : sysinfof.get("LPAR CPUs Configured"),
        'lpar_cpu_standby' : sysinfof.get("LPAR CPUs Standby"),
        'lpar_cpu_reserved' : sysinfof.get("LPAR CPUs Reserved"),
        'lpar_cpu_dedicated' : sysinfof.get("LPAR CPUs Dedicated"),
        'lpar_cpu_shared' : sysinfof.get("LPAR CPUs Shared"),
        'vm_adjustment' : sysinfof.get("VM00 Adjustment"),
        'vm_cpu_total' : sysinfof.get("VM00 CPUs Total"),
        'vm_cpu_configured' : sysinfof.get("VM00 CPUs Configured"),
        'vm_cpu_standby' : sysinfof.get("VM00 CPUs Standby"),
        'vm_cpu_reserved' : sysinfof.get("VM00 CPUs Reserved"),
        'os_cmd_line' : cmdlinef.get(),
        'os_kernel_version' : versionf.get(),
        'os_cpu_configured' : cpuinfof.get("# processors"),
        'checksum' : checksum,
        }

    def sql(self, con):

        query = dbinsert("server", self.all(), "server_id")
        dbquery(con, query)
        self.setid(dblastid(con))

    def hostname(self):
        return self.data['hostname']

    def setid(self, id):
        self.data['p_server_id'] = id

    def getid(self):
        return self.data['p_server_id']

    def get(self, key):
        return self.data[key]

    def all(self):
        return self.data

#
# ALL DISKS INFORMATION
#

class disks():

    def __init__(self, base, server):

        self.hostname = server.hostname()

        self.partitionsf = file_matrix(base.file("partitions"))
        self.serverid  = server.getid()
        self.disks = []

    def __iter__(self):

        for disk in self.disks:
            yield disk

    def build(self):

        hostname = self.hostname
        serverid = self.serverid
        partitionsf = self.partitionsf

        # iterate jumping one line

        iterator = iter(partitionsf)
        iterator.next()

        for l in iterator:

            disk = l[3]
            major = l[0]
            minor = l[1]
            blocks = l[2]

            disk = self.disk(hostname, serverid, disk, major, minor, blocks)
            self.disks.append(disk)

    def sql(self, con):

        for disk in self.disks:

            query = dbinsert("disk", disk.all(), "disk_id")
            dbquery(con, query)
            disk.setid(dblastid(con))

    def getid(self, wanted):

        for disk in self.disks:
            if disk.get('disk') == wanted:
                return disk.getid()

    class disk(object):

        def __init__(self, hostname, serverid, disk, major, minor, blocks):

            checksum = md5([hostname, disk, major, minor, blocks])

            self.data = {
            'p_disk_id' : "0",
            'server_id' : serverid,
            'disk' : disk,
            'major' : major,
            'minor' : minor,
            'blocks' : blocks,
            'checksum' : checksum,
            }

        def setid(self, id):
            self.data['p_disk_id'] = id

        def getid(self):
            return self.data['p_disk_id']

        def get(self, key):
            return self.data[key]

        def all(self):
            return self.data

class irqs():

    def __init__(self, base, tod, server):

        self.hostname = server.hostname()

        interruptsf = file_matrix(tod.file("interrupts"))
        self.interruptsiter = iter(interruptsf)

        self.servercpus = server.get("os_cpu_configured")
        self.serverid = server.getid()
        self.irqs = []

    def __iter__(self):

        for irq in self.irqs:
            yield irq

    def build(self):

        hostname = self.hostname
        serverid = self.serverid
        servercpus = self.servercpus
        intiter = self.interruptsiter
        intiter.next()

        for l in intiter:

            irqtype = l[0]
            irq = self.irq(hostname, serverid, irqtype)
            self.irqs.append(irq)

    def sql(self, con):

        for irq in self.irqs:

            query = dbinsert("irq", irq.all(), "irq_id")
            dbquery(con, query)
            irq.setid(dblastid(con))

    def getid(self, wanted):

        for irq in self.irqs:
            if irq.get('type') == wanted:
                return irq.getid()
        return ""

    class irq():

        def __init__(self, hostname, serverid, irqtype):

            checksum = md5([hostname, irqtype])

            self.data = {
            'p_irq_id' : "0",
            'server_id' : serverid,
            'type' : irqtype,
            'checksum' : checksum,
            }

        def setid(self, id):
            self.data['p_irq_id'] = id

        def getid(self):
            return self.data['p_irq_id']

        def get(self, key):
            return self.data[key]

        def all(self):
            return self.data

class sirqs():

    def __init__(self, base, tod, server):

        self.hostname = server.hostname()

        sirqf = file_matrix(tod.file("softirqs"))
        self.sirqiter = iter(sirqf)

        self.serverid = server.getid()
        self.sirqs = []

    def __iter__(self):

        for softirq in self.softirqs:
            yield softirq

    def build(self):

        hostname = self.hostname
        serverid = self.serverid
        sirqiter = self.sirqiter

        sirqiter.next()

        for l in sirqiter:

            sirqtype = l[0]
            sirq = self.sirq(hostname, serverid, sirqtype)
            self.sirqs.append(sirq)

    def sql(self, con):

        for sirq in self.sirqs:

            query = dbinsert("sirq", sirq.all(), "sirq_id")
            dbquery(con, query)
            sirq.setid(dblastid(con))

    def getid(self, wanted):

        for sirq in self.sirqs:

            if sirq.get('type') == wanted:
                return sirq.getid()

    class sirq(object):

        def __init__(self, hostname, serverid, sirqtype):

            checksum = md5([hostname, sirqtype])

            self.data = {
            'p_sirq_id' : "0",
            'server_id' : serverid,
            'type' : sirqtype,
            'checksum' : checksum
            }

        def setid(self, id):
            self.data['p_sirq_id'] = id

        def getid(self):
            return self.data['p_sirq_id']

        def get(self, key):
            return self.data[key]

        def all(self):
            return self.data

#
# NUMA DOMAINS INFORMATION
#

class domains():

    def __init__(self, base, tod, server):

        self.hostname = server.hostname()

        self.buddyinfof = file_matrix(tod.file("buddyinfo"))
        self.serverid = server.getid()
        self.domains = []
        self.numbers = []

    def __iter__(self):

        for domain in self.domains:
            yield domain

    def build(self):

        hostname = self.hostname
        serverid = self.serverid
        buddyinfof = self.buddyinfof

        for l in buddyinfof:

            if l[1] not in self.numbers:
                domain = self.domain(hostname, serverid, l[1])
                self.domains.append(domain)
                self.numbers.append(l[1])

        # all domains = 999

        domain = self.domain(hostname, serverid, "999")
        self.domains.append(domain)

    def sql(self, con):

        for domain in self.domains:

            query = dbinsert("domain", domain.all(), "domain_id")
            dbquery(con, query)
            domain.setid(dblastid(con))

    def getid(self, wanted):

        for domain in self.domains:

            if domain.get("domain") == wanted:
                return domain.getid()

    class domain():

        def __init__(self, hostname, serverid, domain):

            checksum = md5([hostname, domain])

            self.data = {
            'p_domain_id' : "0",
            'server_id' : serverid,
            'domain' : domain,
            'checksum' : checksum,
            }

        def setid(self, id):
            self.data['p_domain_id'] = id

        def getid(self):
            return self.data['p_domain_id']

        def get(self, key):
            return self.data[key]

        def all(self):
            return self.data

class cpus():

    def __init__(self, base, tod, server, domains):

        self.hostname = server.hostname()

        cpuinfof = file_matrix(base.file("cpuinfo"), "processor")
        schedstatf = file_matrix(tod.file("schedstat"))
        self.cpuinfoiter = iter(cpuinfof)
        self.schedstatiter = iter(schedstatf)

        self.serverid = server.getid()
        self.domains = domains
        self.cpus = []

    def __iter__(self):

        for cpu in self.cpus:
            yield cpu

    def build(self):

        hostname = self.hostname

        serverid = self.serverid
        cpuinfoiter = self.cpuinfoiter
        schedstatiter = self.schedstatiter

        schedstatiter.next()
        schedstatiter.next()

        for l in cpuinfoiter:

            schedstatiter.next()
            d = schedstatiter.next()

            cpu = l[1]
            domain = d[0].replace("domain", "")
            domainid = self.domains.getid(domain)

            cpu = self.cpu(hostname, serverid, domainid, cpu)
            self.cpus.append(cpu)

        domainid = self.domains.getid("999")
        cpu = self.cpu(hostname, serverid, domainid, "999")
        self.cpus.append(cpu)

    def sql(self, con):

        for cpu in self.cpus:

            query = dbinsert("cpu", cpu.all(), "cpu_id")
            dbquery(con, query)
            cpu.setid(dblastid(con))

    def getid(self, wanted):

        for cpu in self.cpus:

            if cpu.get('cpu') == wanted:
                return cpu.getid()

    class cpu():

        def __init__(self, hostname, serverid, domainid, cpu):

            checksum = md5([hostname, cpu])

            self.data = {
              'p_cpu_id' : "0",
              'server_id' : serverid,
              'domain_id' : domainid,
              'cpu' : cpu,
              'checksum' : checksum,
            }

        def setid(self, id):
            self.data['p_cpu_id'] = id

        def getid(self):
            return self.data['p_cpu_id']

        def get(self, key):
            return self.data[key]

        def all(self):
            return self.data

class users():

    def __init__(self, server):

        self.hostname = server.hostname()

        self.serverid = server.getid()
        self.users = []
        self.uids = []

    def __iter__(self):

        if len(self.users) == 0:
            raise StopIteration

        for user in self.users:
            yield user

    def add(self, proc):

        hostname = self.hostname

        try:
            serverid = self.serverid
            statusf = file_keyvalue(proc.file("status"))
            uid = statusf.get("Uid", split=" ")

            if uid not in self.uids:
                user = self.user(hostname, serverid, uid)
                self.users.append(user)
                self.uids.append(uid)
                return user

        except:
            pwd = proc.pwd().split("/")[-2]
            raise Exception("-> could not create user, proc: {}".format(pwd))

    def sql(self, con):

        for user in self.users:

            if user.pending is False: continue

            query = dbinsert("user", user.all(), "user_id")
            dbquery(con, query)
            user.setid(dblastid(con))
            user.pending = False

    def getid(self, wanted):

        for user in self.users:

            if user.get('type') == wanted:
                return user.getid()

    class user():

        def __init__(self, hostname, serverid, uid):

            checksum = md5([hostname, uid])

            self.pending = True

            self.data = {
            'p_user_id' : "0",
            'server_id' : serverid,
            'uid' : uid,
            'checksum' : checksum
            }

        def setid(self, id):
            self.data['p_user_id'] = id

        def getid(self):
            return self.data['p_user_id']

        def get(self, key):
            return self.data[key]

        def all(self):
            if self.data:
                return self.data
            else:
                return

class nets():

    def __init__(self, base, tod, server):

        self.hostname = server.hostname()

        devf = file_matrix(tod.nfile("dev"))
        self.deviter = iter(devf)

        self.serverid = server.getid()
        self.nets = []

    def __iter__(self):

        for net in self.nets:
            yield net

    def build(self):

        hostname = self.hostname
        serverid = self.serverid
        deviter = self.deviter

        deviter.next()
        deviter.next()

        for l in deviter:
            net = self.net(hostname, serverid, l[0])
            self.nets.append(net)

    def sql(self, con):

        for net in self.nets:

            query = dbinsert("net", net.all(), "net_id")
            dbquery(con, query)
            net.setid(dblastid(con))

    def getid(self, wanted):

        for net in self.nets:

            if net.get('net') == wanted:
                return net.getid()

    class net(object):

        def __init__(self, hostname, serverid, net):

            checksum = md5([hostname, net])

            self.data = {
            'p_net_id' : "0",
            'server_id' : serverid,
            'net' : net,
            'checksum' : checksum,
            }

        def setid(self, id):
            self.data['p_net_id'] = id

        def getid(self):
            return self.data['p_net_id']

        def get(self, key):
            return self.data[key]

        def all(self):
            return self.data

class tasks():


    def __init__(self, server):

        self.hostname = server.hostname()
        self.serverid = server.getid()
        self.tasks = []

    def __iter__(self):

        if len(self.tasks) == 0: raise StopIteration

        for task in self.tasks:
            yield task

    def add(self, proc):

        hostname = self.hostname

        try:

            serverid = self.serverid
            statusf = file_keyvalue(proc.file("status"))
            statf = file_line(proc.file("stat"))

            try:
                cmdlinef = file_line(proc.file("cmdline"))
                cmdline = cmdlinef.get()

            except:
                cmdline = ""

            pid = statusf.get("Pid")
            ppid = statusf.get("PPid")
            name = statusf.get("Name")
            uid = statusf.get("Uid", split=" ")
            start = statf.get().split(" ")[21]

            task = self.task(hostname, serverid, uid, start, name,
                                ppid, pid, cmdline)
            self.tasks.append(task)

            return task

        except:

            pwd = proc.pwd().split("/")[-2]
            raise Exception("-> could not create task, proc: {}".format(pwd))

    # link all tasks to its parents

    def sql(self, con):

        for task in self.tasks:

            thishash = task.getid()
            if thishash in taskhashs:
                continue

            query = dbinsert("task", task.all())
            dbquery(con, query)

            taskhashs.add(thishash)

    def link(self):

        for child in self.tasks:

            ppid = child.get('ppid')
            pid = child.get('pid')

            for parent in self.tasks:
                if parent.get('pid') == ppid:
                    child.setparent(parent.getid())

    # def sqlu(self, con):

    #     for task in self.tasks:

    #         thishash = task.gethash()
    #         if thishash in taskhashs: return

    #         dictwhere = {'task_id' : task.getid()}
    #         dictwhat = {'ptask_id' : task.get('ptask_id')}

    #         query = dbupdate("task", dictwhere, dictwhat)
    #         dbquery(con, query)

    #         taskhashs.add(thishash)

    class task():

        # ppid id is the same as pid id until parent->link is called

        def __init__(self, hostname, serverid, uid, start, name, ppid, pid, cmdline):

            self.hash = md5([hostname, serverid, uid, start, name, pid, cmdline])

            self.data = {
            'task_id' : self.hash,
            'ptask_id' : "0",
            'server_id' : serverid,
            'user_id' : uid,
            'start' : start,
            'name' : name,
            'ppid' : ppid,
            'pid' : pid,
            'cmdline' : clearaspas(cmdline),
            # 'checksum' : self.hash,
            }

        # def setid(self, id):
        #     self.data['task_id'] = id

        def setparent(self, id):
            self.data['ptask_id'] = id

        def getid(self):
            return self.data['task_id']

        def get(self, key):
            return self.data[key]

        def all(self):
            return self.data

