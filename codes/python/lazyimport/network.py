from defines import *
from base import *
from files import *

# TODO: transform ip, tcp, udp and icmp into one class
# TODO: transform ipstat and tcpstat into one class

class gnets(object):

    def __init__(self, tod, server, time, nets):

        self.serverid = server.getid()
        self.timeid = time.getid()
        self.nets = nets

        self.gnets = []

        devf = file_matrix(tod.nfile("dev"))

        self.deviter = iter(devf)
        self.deviter.next()
        self.deviter.next()

    def __iter__(self):

        for gnet in self.gnets:
            yield gnet

    def build(self):

        serverid = self.serverid
        timeid = self.timeid
        nets = self.nets

        for l in self.deviter:

            net = l[0]
            netid = nets.getid(net)

            gnet = self.gnet(timeid, serverid, netid,
                                l[1], l[2], l[3], l[4], l[5], l[6],
                                l[7], l[8], l[9], l[10], l[11], l[12],
                                l[13], l[14], l[15], l[16])

            self.gnets.append(gnet)

    def sql(self, con):

        for gnet in self.gnets:

            query = dbinsert("gnet", gnet.all())
            dbquery(con, query)

    class gnet():

        def __init__(self, timeid, serverid, netid,
                        a, b, c, d, e, f, g, h,
                        i, j, l, m, n, o, p, q):

            self.data = {
            'time_id' : timeid,
            'server_id' : serverid,
            'net_id' : netid,
            'rx_bytes' : a,
            'rx_packets' : b,
            'rx_errors' : c,
            'rx_dropped' : d,
            'rx_fifo_errors' : e,
            'rx_frame' : f,
            'rx_compressed' : g,
            'multicast' : h,
            'tx_bytes' : i,
            'tx_packets' : j,
            'tx_errors' : l,
            'tx_dropped' : m,
            'tx_fifo_errors' : n,
            'collisions' : o,
            'tx_carrier' : p,
            'tx_compressed' : q ,
            }

        def get(self, key):
            return self.data[key]

        def all(self):
            return self.data

class gsockets():

    def __init__(self, tod, server, time):

        self.timeid = time.getid()
        self.serverid = server.getid()

        sockstatf = file_matrix(tod.nfile("sockstat"))
        self.sockstatiter = iter(sockstatf)

    def build(self):

        timeid = self.timeid
        serverid = self.serverid
        sockstatiter = self.sockstatiter

        sockstatiter.next()
        tcp = sockstatiter.next()
        udp = sockstatiter.next()
        # udplite = sockstatiter.next()
        # raw = sockstatiter.next()
        # frag = sockstatiter.next()

        self.data = {
        'time_id' : timeid,
        'server_id' : serverid,
        'tcp_in_use' : tcp[2],
        'tcp_orphan' : tcp[4],
        'tcp_tw' : tcp[6],
        'tcp_alloc' : tcp[8],
        'tcp_mem' : tcp[10],
        'udp_in_use' : udp[2],
        'udp_mem' : udp[4],
        }

    def sql(self, con):

        query = dbinsert("gsocket", self.all())
        dbquery(con, query)

    def get(self, key):
        return self.data[key]

    def all(self):
        return self.data

class gip():

    def __init__(self, tod, server, time):

        self.timeid = time.getid()
        self.serverid = server.getid()

        snmpf = file_matrix(tod.nfile("snmp"), "Ip")

        self.snmpiter = iter(snmpf)
        self.snmpiter.next()

    def build(self):

        timeid = self.timeid
        serverid = self.serverid
        snmpiter = self.snmpiter

        ip = snmpiter.next()

        self.data = {
        'time_id' : timeid,
        'server_id' : serverid,
        'Forwarding_b' : ip[1],
        'DefaultTTL' : ip[2],
        'InReceives' : ip[3],
        'InHdrErrors' : ip[4],
        'InAddrErrors' : ip[5],
        'ForwDatagrams' : ip[6],
        'InUnknownProtos' : ip[7],
        'InDiscards' : ip[8],
        'InDelivers' : ip[9],
        'OutRequests' : ip[10],
        'OutDiscards' : ip[11],
        'OutNoRoutes' : ip[12],
        'ReasmTimeout' : ip[13],
        'ReasmReqds' : ip[14],
        'ReasmOKs' : ip[15],
        'ReasmFails' : ip[16],
        'FragOKs' : ip[17],
        'FragFails' : ip[18],
        'FragCreates' : ip[19],
        }

    def sql(self, con):

        query = dbinsert("gip", self.all())
        dbquery(con, query)

    def get(self, key):
        return self.data[key]

    def all(self):
        return self.data

class gtcp():

    def __init__(self, tod, server, time):

        self.timeid = time.getid()
        self.serverid = server.getid()

        snmpf = file_matrix(tod.nfile("snmp"), "Ip")

        self.snmpiter = iter(snmpf)
        self.snmpiter.next()

    def build(self):

        timeid = self.timeid
        serverid = self.serverid
        snmpiter = self.snmpiter

        tcp = snmpiter.next()

        self.data = {
        'time_id' : timeid,
        'server_id' : serverid,
        'rtoalgorithm' : tcp[1],
        'rtomin' : tcp[2],
        'rtomax' : tcp[3],
        'maxconn' : tcp[4],
        'activeopens' : tcp[5],
        'passiveopens' : tcp[6],
        'attemptfails' : tcp[7],
        'estabresets' : tcp[8],
        'currestab' : tcp[9],
        'insegs' : tcp[10],
        'outsegs' : tcp[11],
        'retranssegs' : tcp[12],
        'inerrs' : tcp[13],
        'outrsts' : tcp[14],
        }

    def sql(self, con):

        query = dbinsert("gtcp", self.all())
        dbquery(con, query)

    def get(self, key):
        return self.data[key]

    def all(self):
        return self.data

class gipstats():

    def __init__(self, tod, server, time):

        self.timeid = time.getid()
        self.serverid = server.getid()

        netstatf = file_matrix(tod.nfile("netstat"), "IpExt")

        self.netstatiter = iter(netstatf)
        self.netstatiter.next()

    def build(self):

        timeid = self.timeid
        serverid = self.serverid
        netstatiter = self.netstatiter

        ips = netstatiter.next()

        self.data = {
        'time_id' : timeid,
        'server_id' : serverid,
        'InNoRoutes' : ips[1],
        'InTruncatedPkts' : ips[2],
        'InMcastPkts' : ips[3],
        'OutMcastPkts' : ips[4],
        'InBcastPkts' : ips[5],
        'OutBcastPkts' : ips[6],

        #
        # rhel6/suse11
        #

        # 'InOctets' : ips[7],
        # 'OutOctets' : ips[8],
        # 'InMcastOctets' : ips[9],
        # 'OutMcastOctets' : ips[10],
        # 'InBcastOctets' : ips[11],
        # 'OutBcastOctets' : ips[12],

        }

    def sql(self, con):

        query = dbinsert("gipstat", self.all())
        dbquery(con, query)

    def get(self, key):
        return self.data[key]

    def all(self):
        return self.data

class gtcpstats():

    def __init__(self, tod, server, time):

        self.timeid = time.getid()
        self.serverid = server.getid()

        netstatf = file_matrix(tod.nfile("netstat"), "TcpExt")

        self.netstatiter = iter(netstatf)
        self.netstatiter.next()

    def build(self):

        timeid = self.timeid
        serverid = self.serverid
        netstatiter = self.netstatiter

        tcps = netstatiter.next()

        self.data = {
        'time_id' : timeid,
        'server_id' : serverid,
        'syncookiessent' : tcps[1],
        'syncookiesrecv' : tcps[2],
        'syncookiesfailed' : tcps[3],
        'embryonicrsts' : tcps[4],
        'prunecalled' : tcps[5],
        'rcvpruned' : tcps[6],
        'ofopruned' : tcps[7],
        'outofwindowicmps' : tcps[8],
        'lockdroppedicmps' : tcps[9],
        'arpfilter' : tcps[10],
        'tw' : tcps[11],
        'twrecycled' : tcps[12],
        'twkilled' : tcps[13],
        'pawspassive' : tcps[14],
        'pawsactive' : tcps[15],
        'pawsestab' : tcps[16],
        'delayedacks' : tcps[17],
        'delayedacklocked' : tcps[18],
        'delayedacklost' : tcps[19],
        'listenoverflows' : tcps[20],
        'listendrops' : tcps[21],
        'tcpprequeued' : tcps[22],
        'tcpdirectcopyfrombacklog' : tcps[23],
        'tcpdirectcopyfromprequeue' : tcps[24],
        'tcpprequeuedropped' : tcps[25],
        'tcphphits' : tcps[26],
        'tcphphitstouser' : tcps[27],
        'tcppureacks' : tcps[28],
        'tcphpacks' : tcps[29],
        'tcprenorecovery' : tcps[30],
        'tcpsackrecovery' : tcps[31],
        'tcpsackreneging' : tcps[32],
        'tcpfackreorder' : tcps[33],
        'tcpsackreorder' : tcps[34],
        'tcprenoreorder' : tcps[35],
        'tcptsreorder' : tcps[36],
        'tcpfullundo' : tcps[37],
        'tcppartialundo' : tcps[38],
        'tcpdsackundo' : tcps[39],
        'tcplossundo' : tcps[40],
        'tcploss' : tcps[41],
        'tcplostretransmit' : tcps[42],
        'tcprenofailures' : tcps[43],
        'tcpsackfailures' : tcps[44],
        'tcplossfailures' : tcps[45],
        'tcpfastretrans' : tcps[46],
        'tcpforwardretrans' : tcps[47],
        'tcpslowstartretrans' : tcps[48],
        'tcptimeouts' : tcps[49],
        'tcprenorecoveryfail' : tcps[50],
        'tcpsackrecoveryfail' : tcps[51],
        'tcpschedulerfailed' : tcps[52],
        'tcprcvcollapsed' : tcps[53],
        'tcpdsackoldsent' : tcps[54],
        'tcpdsackofosent' : tcps[55],
        'tcpdsackrecv' : tcps[56],
        'tcpdsackoforecv' : tcps[57],
        'tcpabortonsyn' : tcps[58],
        'tcpabortondata' : tcps[59],
        'tcpabortonclose' : tcps[60],
        'tcpabortonmemory' : tcps[61],
        'tcpabortontimeout' : tcps[62],
        'tcpabortonlinger' : tcps[63],
        'tcpabortfailed' : tcps[64],
        'tcpmemorypressures' : tcps[65],

        'tcpbacklogdrop' : "0",
        'tcpminttldrop' : "0",
        'tcpdeferacceptdrop' : "0",
        'ipreversepathfilter' : "0",
        'tcptimewaitoverflow' : "0",

        # do not exist on kernel 2.6.18

        # 'tcpsackdiscard' : tcps[66],
        # 'tcpdsackignoredold' : tcps[67],
        # 'tcpdsackignorednoundo' : tcps[68],
        # 'tcpspuriousrtos' : tcps[69],
        # 'tcpmd5notfound' : tcps[70],
        # 'tcpmd5unexpected' : tcps[71],
        # 'tcpsackshifted' : tcps[72],
        # 'tcpsackmerged' : tcps[73],
        # 'tcpsackshiftfallback' : tcps[74],

	    # do not exit on kernel 2.6.32

        # 'tcpbacklogdrop' : tcps[75],
        # 'tcpminttldrop' : tcps[76],
        # 'tcpdeferacceptdrop' : tcps[77],
        # 'ipreversepathfilter' : tcps[78],
        # 'tcptimewaitoverflow' : tcps[79],
        }

    def sql(self, con):

        query = dbinsert("gtcpstat", self.all())
        dbquery(con, query)

    def get(self, key):
        return self.data[key]

    def all(self):
        return self.data

class gudp():

    def __init__(self, tod, server, time):

        self.timeid = time.getid()
        self.serverid = server.getid()

        snmpf = file_matrix(tod.nfile("snmp"), "Udp")

        self.snmpiter = iter(snmpf)
        self.snmpiter.next()

    def build(self):

        timeid = self.timeid
        serverid = self.serverid
        snmpiter = self.snmpiter

        udp = snmpiter.next()

        self.data = {
        'time_id' : timeid,
        'server_id' : serverid,
        'InDatagrams' : udp[1],
        'NoPorts' : udp[2],
        'InErrors' : udp[3],
        'OutDatagrams' : udp[4],

        # do not exist on 2.6.18

        # 'RcvbufErrors' : udp[5],
        # 'SndbufErrors' : udp[6],

        }

    def sql(self, con):

        query = dbinsert("gudp", self.all())
        dbquery(con, query)

    def get(self, key):
        return self.data[key]

    def all(self):
        return self.data

class gicmp():

    def __init__(self, tod, server, time):

        self.timeid = time.getid()
        self.serverid = server.getid()

        snmpf = file_matrix(tod.nfile("snmp"), "Icmp")

        self.snmpiter = iter(snmpf)
        self.snmpiter.next()

    def build(self):

        timeid = self.timeid
        serverid = self.serverid
        snmpiter = self.snmpiter

        icmp = snmpiter.next()
        snmpiter.next()
        icmpmsg = snmpiter.next()

        self.data = {
        'time_id' : timeid,
        'server_id' : serverid,
        'inmsgs' : icmp[1],
        'inerrors' : icmp[2],
        'indestunreachs' : icmp[3],
        'intimeexcds' : icmp[4],
        'inparmprobs' : icmp[5],
        'insrcquenchs' : icmp[6],
        'inredirects' : icmp[7],
        'inechos' : icmp[8],
        'inechoreps' : icmp[9],
        'intimestamps' : icmp[10],
        'intimestampreps' : icmp[11],
        'inaddrmasks' : icmp[12],
        'inaddrmaskreps' : icmp[13],
        'outmsgs' : icmp[14],
        'outerrors' : icmp[15],
        'outdestunreachs' : icmp[16],
        'outtimeexcds' : icmp[17],
        'outparmprobs' : icmp[18],
        'outsrcquenchs' : icmp[19],
        'outredirects' : icmp[20],
        'outechos' : icmp[21],
        'outechoreps' : icmp[22],
        'outtimestamps' : icmp[23],
        'outtimestampreps' : icmp[24],
        'outaddrmasks' : icmp[25],
        'outaddrmaskreps' : icmp[26],
        'intype0' : "0",
        'intype3' : "0",
        'intype8' : "0",
        'outtype0' : "0",
        'outtype3' : "0",
        'outtype8' : "0",

	# problems on 2.6.32 (some of them exist and some of them don't)

        # 'intype0' : "0",
        # 'intype3' : icmpmsg[1],
        # 'intype8' : icmpmsg[2],
        # 'outtype0' : icmpmsg[3],
        # 'outtype3' : icmpmsg[4],
        # 'outtype8' : "0",
        }

    def sql(self, con):

        query = dbinsert("gicmp", self.all())
        dbquery(con, query)

    def get(self, key):
        return self.data[key]

    def all(self):
        return self.data
