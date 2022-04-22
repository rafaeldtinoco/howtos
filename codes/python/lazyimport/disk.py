from defines import *
from base import *
from files import *

class gdisks():

    def __init__(self, tod, server, time, disks):

        self.diskstatsf = file_matrix(tod.file("diskstats"))
        self.serverid = server.getid()
        self.timeid = time.getid()
        self.disks = disks

        self.gdisks = []

    def __iter__(self):

        for gdisk in self.gdisks:
            yield gdisk

    def build(self):

        serverid = self.serverid
        timeid = self.timeid
        disks = self.disks

        for l in self.diskstatsf:
            if "loop" in l[2]: continue
            if "ram" in l[2]: continue
            disk = l[2]
            diskid = disks.getid(disk)
            if not diskid: continue

            gdisk = self.gdisk(timeid, serverid, diskid,
                               l[0], l[1], l[2], l[3], l[4], l[5], l[6],
                               l[7], l[8], l[9], l[10], l[11], l[12],
                               l[13]
                             )
            self.gdisks.append(gdisk)

    def sql(self, con):

        for gdisk in self.gdisks:
            query = dbinsert("gdisk", gdisk.all())
            dbquery(con, query)

    class gdisk():

        def __init__(self, timeid, serverid, diskid,
                     a, b, c, d, e, f, g, h, i, j, l, m, n, o):

            self.data = {
            'time_id' : timeid,
            'server_id' : serverid,
            'disk_id' : diskid,
            'reads_completed' : d,
            'reads_merged' : e,
            'sectors_read' : f,
            'time_spent_reading' : g,
            'writes_completed' : h,
            'writes_merged' : i,
            'sectors_written' : j,
            'time_spent_writing' : l,
            'ios_current' : m,
            'time_spent_doing_io' : n,
            'wtime_spent_doing_io' : o,
            }

        def get(self, key):
            return self.data[key]

        def all(self):
            return self.data

class tdisk(object):

    def __init__(self, proc, server, time, task):

        self.hostname = server.hostname()
        self.timeid = time.getid()
        self.serverid = server.getid()
        self.taskid = task.getid()

        try:
            self.iof = file_keyvalue(proc.file("io"))

        except:
            pwd = proc.pwd().split("/")[-2]
            raise Exception("-> could not create tdisk, proc: {}"\
                            .format(pwd))

    def build(self):

        hostname = self.hostname
        timeid = self.timeid
        serverid = self.serverid
        taskid = self.taskid
        iof = self.iof

        rchar = iof.get('rchar')
        wchar = iof.get('wchar')
        syscr = iof.get('syscr')
        syscw = iof.get('syscw')
        rbytes = iof.get('read_bytes')
        wbytes = iof.get('write_bytes')
        cwbytes = iof.get('cancelled_write_bytes')

        # timeid is tod, so it can be used

        self.data = {
        'time_id' : timeid,
        'server_id' : serverid,
        'task_id' : taskid,
        'rchar' : rchar,
        'wchar' : wchar,
        'syscr' : syscr,
        'syscw' : syscw,
        'read_bytes' : rbytes,
        'write_bytes' : wbytes,
        'cancelled_write_bytes' : cwbytes,
        }

    def sql(self, con):

        query = dbinsert("tdisk", self.all())
        dbquery(con, query)

    def get(self, key):
        return self.data[key]

    def all(self):
        return self.data
