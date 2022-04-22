#!/usr/bin/python2.7

from defines import *
# from basedir import *
# from base import *
# from cpu import *
# from disk import *
# from memory import *
# from network import *
# from files import *
# from db import *
# import datetime
# import os

import sys

from base import *
from cpu import *
from memory import *
from disk import *
from network import *

from filesystem import *
from defines import *
from files import *
from data import *

if __name__ == '__main__':

    # connect to mysql

    con = dbstart()

    # just to clean database
    # exit()

    # check main and temp dirs

    if len(sys.argv) < 3:
        maindir = def_maindir
        tempdir = def_tempdir

    else:
        maindir = sys.argv[1] + "/"
        tempdir = sys.argv[2] + "/"

        if not os.path.isdir(maindir) or not os.path.isdir(tempdir):
            exit()

    _base = base(maindir, tempdir)

    _server = server(_base)
    _server.build()
    _server.sql(con)

    # print "base"

    #
    # BASE COMPONENTS
    #

    _disks = disks(_base, _server)
    _disks.build()
    _disks.sql(con)


    # all other base structures need first collect
    # getting first tod on "short"

    _tod = iter(iter(_base).next()).next()

    _domains = domains(_base, _tod, _server)
    _domains.build()
    _domains.sql(con)

    _cpus = cpus(_base, _tod, _server, _domains)
    _cpus.build()
    _cpus.sql(con)

    _irqs = irqs(_base, _tod, _server)
    _irqs.build()
    _irqs.sql(con)

    # rhel6/suse11
    # _sirqs = sirqs(_base, _tod, _server)
    # _sirqs.build()
    # _sirqs.sql(con)

    _nets = nets(_base, _tod, _server)
    _nets.build()
    _nets.sql(con)

    # TODO: bring all sqls here

    _users = users(_server)

    for _period in _base:

        print "!! type: {}".format(_period.gettype())[:-1]

        for _tod in _period:

            print "-- tod: {}".format(_tod.pwd().split("/")[-2])

            # print "global"

            #
            # TIMESTAMP
            #

            _time = time(_tod, _server)
            _time.build()
            _time.sql(con)

            #
            # CPU
            #

            # print "cpu"

            _gcpus = gcpus(_tod, _server, _time, _cpus)
            _gcpus.build()
            _gcpus.sql(con)

            _girqs = girqs(_tod, _server, _time, _cpus, _irqs, soft=False)
            _girqs.build()
            _girqs.sql(con)

            # rhel6/suse11
            # _girqs = girqs(_tod, _server, _time, _cpus, _sirqs, soft=True)
            # _girqs.build()
            # _girqs.sql(con)

            _gschedds = gschedds(_tod, _server, _time, _domains, _cpus)
            _gschedds.build()
            _gschedds.sql(con)

            _gschedcs = gschedcs(_tod, _server, _time, _domains, _cpus)
            _gschedcs.build()
            _gschedcs.sql(con)

            #
            # DISK
            #

            # print "disk"

            _gdisks = gdisks(_tod, _server, _time, _disks)
            _gdisks.build()
            _gdisks.sql(con)

            #
            # MEMORY
            #

            # print "memory"

            # rhel6/suse11
            # _gpages = gpages(_tod, _server, _time, _domains)
            # _gpages.build()
            # _gpages.sql(con)

            _gmem = gmem(_tod, _server, _time)
            _gmem.build()
            _gmem.sql(con)

            _gvm = gvm(_tod, _server, _time)
            _gvm.build()
            _gvm.sql(con)

            #
            # NETWORK
            #

            # print "network"

            # with verboseignored():
            _gnets = gnets(_tod, _server, _time, _nets)
            _gnets.build()
            _gnets.sql(con)

            # with verboseignored():
            _gsockets = gsockets(_tod, _server, _time)
            _gsockets.build()
            _gsockets.sql(con)

            # with verboseignored():
            _gip = gip(_tod, _server, _time)
            _gip.build()
            _gip.sql(con)

            # with verboseignored():
            _gipstats = gipstats(_tod, _server, _time)
            _gipstats.build()
            _gipstats.sql(con)

            # with verboseignored():
            _gtcp = gtcp(_tod, _server, _time)
            _gtcp.build()
            _gtcp.sql(con)

            # with verboseignored():
            _gtcpstats = gtcpstats(_tod, _server, _time)
            _gtcpstats.build()
            _gtcpstats.sql(con)

            # with verboseignored():
            _gudp = gudp(_tod, _server, _time)
            _gudp.build()
            _gudp.sql(con)

            # with verboseignored():
            _gicmp = gicmp(_tod, _server, _time)
            _gicmp.build()
            _gicmp.sql(con)

            #
            # TASKS
            #

            _tasks = tasks(_server)

            for _proc in _tod:

                with verboseignored():
                    _user = _users.add(_proc)

                with verboseignored():
                    _task = _tasks.add(_proc)

                if _task:

                    with verboseignored():
                        _tcpu = tcpu(_proc, _server, _time, _task)
                        _tcpu.build()
                        _tcpu.sql(con)

                    # not in kernel 2.6.18

                    # with verboseignored():
                    # _tsched = tsched(_proc, _server, _time, _task)
                    # _tsched.build()
                    # _tsched.sql(con)

                    with verboseignored():
                        _tmem = tmem(_proc, _server, _time, _task)
                        _tmem.build()
                        _tmem.sql(con)

                    with verboseignored():
                        _tdisk = tdisk(_proc, _server, _time, _task)
                        _tdisk.build()
                        _tdisk.sql(con)

                    # for _thread in _proc:

                    #     with verboseignored():
                    #         _child = _tasks.add(_thread)

                    #     if _child:

                    #         # print _child
                    #         # _child.sql(con)

                    #         with verboseignored():
                    #             _tcpu = tcpu(_proc, _server, _time, _child)
                    #             _tcpu.build()
                    #             _tcpu.sql(con)

                    #         # with verboseignored():
                    #         # _tsched = tsched(_proc, _server, _time, _child)
                    #         # _tsched.build()
                    #         # _tsched.sql(con)

                    #         with verboseignored():
                    #             _tmem = tmem(_proc, _server, _time, _child)
                    #             _tmem.build()
                    #             _tmem.sql(con)

                    #         with verboseignored():
                    #             _tdisk = tdisk(_proc, _server, _time, _child)
                    #             _tdisk.build()
                    #             _tdisk.sql(con)

            # _tasks.sql(con)
            _tasks.link()
            _tasks.sql(con)
            _users.sql(con)

            # break

