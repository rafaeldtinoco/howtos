from defines import *
from base import *
from files import *

class gpages():

    def __init__(self, tod, server, time, domains):

        self.serverid = server.getid()
        self.timeid = time.getid()
        self.domains = domains
        self.gpages = []

        pagetypeinfof = file_matrix(tod.file("pagetypeinfo"), "Node")
        self.ptinfoiter = iter(pagetypeinfof)

    def __iter__(self):

        for gpage in self.gpages:
            yield gpage

    def build(self):

        timeid = self.timeid
        serverid = self.serverid
        domains = self.domains

        ptinfoiter = self.ptinfoiter

        for i in range(0, 10):

            l = ptinfoiter.next()

            domainnum = l[1].lower()
            zone = l[3].lower()
            type = l[5].lower()

            domainid = domains.getid(domainnum)

            if zone == "dma": zone = "0"
            if zone == "normal": zone = "1"
            if zone == "high": zone = "2"

            if type == "total": type = "0"
            if type == "unmovable": type = "1"
            if type == "reclaimable": type = "2"
            if type == "movable": type = "3"
            if type == "reserve": type = "4"
            if type == "isolate": type = "5"

            gpage = self.gpage(
                             timeid, serverid, domainid, zone, type,
                             l[6], l[7], l[8], l[9], l[10], l[11], l[12],
                             l[13], l[14]
                             )

            self.gpages.append(gpage)

    def sql(self, con):

        for gpage in self.gpages:

            query = dbinsert("gpage", gpage.all())
            dbquery(con, query)

    class gpage(object):

        def __init__(self, timeid, serverid, domainid, zone, type,
                        a, b, c, d, e, f, g, h, i
                     ):

            self.data = {
            'time_id' : timeid,
            'server_id' : serverid,
            'domain_id' : domainid,
            'zone' : zone,
            'type' : type,
            'zero' : a,
            'one' : b,
            'two' : c,
            'three' : d,
            'four' : e,
            'five' : f,
            'six' : g,
            'seven' : h,
            'eight' : i,
            }

        def get(self, key):
            return self.data[key]

        def all(self):
            return self.data

class gmem (object):

    def __init__(self, tod, server, time):

        self.timeid = time.getid()
        self.serverid = server.getid()

        self.meminfof = file_keyvalue(tod.file("meminfo"))

    def sql(self, con):

        query = dbinsert("gmem", self.all())
        dbquery(con, query)

    def build(self):

        timeid = self.timeid
        serverid = self.serverid
        meminfof = self.meminfof

        self.data = {

        'time_id' : timeid,
        'server_id' : serverid,
        'memtotal' : meminfof.get("MemTotal", clean=" kB"),
        'memfree' : meminfof.get("MemFree", clean=" kB"),
        'buffers' : meminfof.get("Buffers", clean=" kB"),
        'cached' : meminfof.get("Cached", clean=" kB"),
        'swapcached' : meminfof.get("SwapCached", clean=" kB"),
        'active' : meminfof.get("Active", clean=" kB"),
        'inactive' : meminfof.get("Inactive", clean=" kB"),
        'swap_total' : meminfof.get("SwapTotal", clean=" kB"),
        'swap_free' : meminfof.get("SwapFree", clean=" kB"),
        'dirty' : meminfof.get("Dirty", clean=" kB"),
        'writeback' : meminfof.get("Writeback", clean=" kB"),
        'anonpages' : meminfof.get("AnonPages", clean=" kB"),
        'mapped' : meminfof.get("Mapped", clean=" kB"),
        'slab' : meminfof.get("Slab", clean=" kB"),
        'pagetables' : meminfof.get("PageTables", clean=" kB"),
        'nfs_unstable' : meminfof.get("NFS_Unstable", clean=" kB"),
        'bounce' : meminfof.get("Bounce", clean=" kB"),
        'commitlimit' : meminfof.get("CommitLimit", clean=" kB"),
        'committed_as' : meminfof.get("Committed_AS", clean=" kB"),
        'vmalloctotal' : meminfof.get("VmallocTotal", clean=" kB"),
        'vmallocused' : meminfof.get("VmallocUsed", clean=" kB"),
        'vmallocchunk' : meminfof.get("VmallocChunk", clean=" kB"),
        'hugepages_total' : meminfof.get("HugePages_Total", clean=" kB"),
        'hugepages_free' : meminfof.get("HugePages_Free", clean=" kB"),
        'hugepages_rsvd' : meminfof.get("HugePages_Rsvd", clean=" kB"),

        #
        # rhel6/suse11
        #

        # 'active_anon' : meminfof.get("Active(anon)", clean=" kB"),
        # 'inactive_anon' : meminfof.get("Inactive(anon)", clean=" kB"),
        # 'active_file' : meminfof.get("Active(file)", clean=" kB"),
        # 'inactive_file' : meminfof.get("Inactive(file)", clean=" kB"),
        # 'unevictable' : meminfof.get("Unevictable", clean=" kB"),
        # 'mlocked' : meminfof.get("Mlocked", clean=" kB"),
        # 'sreclaim' : meminfof.get("SReclaimable", clean=" kB"),
        # 'sunreclaim' : meminfof.get("SUnreclaim", clean=" kB"),
        # 'kernelstack' : meminfof.get("KernelStack", clean=" kB"),
        # 'shmem' : meminfof.get("Shmem", clean=" kB"),
        # 'writebacktmp' : meminfof.get("WritebackTmp", clean=" kB"),
        # 'hugepages_surp' : meminfof.get("HugePages_Surp", clean=" kB"),

        }

    def get(self, key):
        return self.data[key]

    def all(self):
        return self.data

class gvm(object):

    def __init__(self, tod, server, time):

        self.timeid = time.getid()
        self.serverid = server.getid()

        self.vmstatf = file_keyvalue(tod.file("vmstat"), sep=" ")

    def sql(self, con):

        query = dbinsert("gvm", self.all())
        dbquery(con, query)

    def build(self):

        timeid = self.timeid
        serverid = self.serverid
        vmstatf = self.vmstatf

        self.data = {
        'time_id' : timeid,
        'server_id' : serverid,
        'nr_anon_pages' : vmstatf.get('nr_anon_pages'),
        'nr_mapped' : vmstatf.get('nr_mapped'),
        'nr_file_pages' : vmstatf.get('nr_file_pages'),
        'nr_dirty' : vmstatf.get('nr_dirty'),
        'nr_writeback' : vmstatf.get('nr_writeback'),
        'nr_page_table_pages' : vmstatf.get('nr_page_table_pages'),
        'nr_unstable' : vmstatf.get('nr_unstable'),
        'nr_bounce' : vmstatf.get('nr_bounce'),
        'pgpgin' : vmstatf.get('pgpgin'),
        'pgpgout' : vmstatf.get('pgpgout'),
        'pswpin' : vmstatf.get('pswpin'),
        'pswpout' : vmstatf.get('pswpout'),
        'pgalloc_dma' : vmstatf.get('pgalloc_dma'),
        'pgalloc_normal' : vmstatf.get('pgalloc_normal'),
        'pgfree' : vmstatf.get('pgfree'),
        'pgactivate' : vmstatf.get('pgactivate'),
        'pgdeactivate' : vmstatf.get('pgdeactivate'),
        'pgfault' : vmstatf.get('pgfault'),
        'pgmajfault' : vmstatf.get('pgmajfault'),
        'pgrefill_dma' : vmstatf.get('pgrefill_dma'),
        'pgrefill_normal' : vmstatf.get('pgrefill_normal'),
        'pgsteal_dma' : vmstatf.get('pgsteal_dma'),
        'pgsteal_normal' : vmstatf.get('pgsteal_normal'),
        'pgscan_kswapd_dma' : vmstatf.get('pgscan_kswapd_dma'),
        'pgscan_kswapd_normal' : vmstatf.get('pgscan_kswapd_normal'),
        'pgscan_direct_dma' : vmstatf.get('pgscan_direct_dma'),
        'pgscan_direct_normal' : vmstatf.get('pgscan_direct_normal'),
        'pginodesteal' : vmstatf.get('pginodesteal'),
        'slabs_scanned' : vmstatf.get('slabs_scanned'),
        'kswapd_steal' : vmstatf.get('kswapd_steal'),
        'kswapd_inodesteal' : vmstatf.get('kswapd_inodesteal'),
        'pageoutrun' : vmstatf.get('pageoutrun'),
        'allocstall' : vmstatf.get('allocstall'),
        'pgrotated' : vmstatf.get('pgrotated'),

        # rhel6/suse11: always zero

        'nr_immediate' : "0",
        'nr_dirtied' : "0",
        'nr_written' : "0",
        'pgrescued' : "0",
        'nr_anon_trans_hugepgs' : "0",
        'nr_dirty_threshold' : "0",
        'nr_dirty_bg_threshold' : "0",
        'pgscan_direct_throttle' : "0",

        # rhel6/suse11

        # 'nr_slab_reclaimable' : vmstatf.get('nr_slab_reclaimable'),
        # 'nr_slab_unreclaimable' : vmstatf.get('nr_slab_unreclaimable'),
        # 'nr_kernel_stack' : vmstatf.get('nr_kernel_stack'),
        # 'nr_free_pages' : vmstatf.get('nr_free_pages'),
        # 'nr_inactive_anon' : vmstatf.get('nr_inactive_anon'),
        # 'nr_active_anon' : vmstatf.get('nr_active_anon'),
        # 'nr_inactive_file' : vmstatf.get('nr_inactive_file'),
        # 'nr_active_file' : vmstatf.get('nr_active_file'),
        # 'nr_unevictable' : vmstatf.get('nr_unevictable'),
        # 'nr_mlock' : vmstatf.get('nr_mlock'),
        # 'pgalloc_movable' : vmstatf.get('pgalloc_movable'),
        # 'pgrefill_movable' : vmstatf.get('pgrefill_movable'),
        # 'pgsteal_movable' : vmstatf.get('pgsteal_movable'),
        # 'pgscan_kswapd_movable' : vmstatf.get('pgscan_kswapd_movable'),
        # 'pgscan_direct_movable' : vmstatf.get('pgscan_direct_movable'),
        # 'nr_vmscan_write' : vmstatf.get('nr_vmscan_write'),
        # 'nr_writeback_temp' : vmstatf.get('nr_writeback_temp'),
        # 'nr_isolated_anon' : vmstatf.get('nr_isolated_anon'),
        # 'nr_isolated_file' : vmstatf.get('nr_isolated_file'),
        # 'nr_shmem' : vmstatf.get('nr_shmem'),
        # 'compact_blocks_moved' : vmstatf.get('compact_blocks_moved'),
        # 'compact_pgs_moved' : vmstatf.get('compact_pages_moved'),
        # 'compact_pgmigrate_failed' : vmstatf.get('compact_pagemigrate_failed'),
        # 'compact_stall' : vmstatf.get('compact_stall'),
        # 'compact_fail' : vmstatf.get('compact_fail'),
        # 'compact_success' : vmstatf.get('compact_success'),
        # 'htlb_buddy_alloc_success' : vmstatf.get('htlb_buddy_alloc_success'),
        # 'htlb_buddy_alloc_fail' : vmstatf.get('htlb_buddy_alloc_fail'),
        # 'unevictable_pgs_culled' : vmstatf.get('unevictable_pgs_culled'),
        # 'unevictable_pgs_scanned' : vmstatf.get('unevictable_pgs_scanned'),
        # 'unevictable_pgs_rescued' : vmstatf.get('unevictable_pgs_rescued'),
        # 'unevictable_pgs_mlocked' : vmstatf.get('unevictable_pgs_mlocked'),
        # 'unevictable_pgs_munlckd' : vmstatf.get('unevictable_pgs_munlocked'),
        # 'unevictable_pgs_cleared' : vmstatf.get('unevictable_pgs_cleared'),
        # 'unevictable_pgs_stranded' : vmstatf.get('unevictable_pgs_stranded'),
        # 'kswapd_lwmark_hit_quickly' : vmstatf.get('kswapd_low_wmark_hit_quickly'),
        # 'kswapd_hwmark_hit_quickly' : vmstatf.get('kswapd_high_wmark_hit_quickly'),
        # 'kswapd_skip_conges_wait' : vmstatf.get('kswapd_skip_congestion_wait'),

        # suse11

        # 'nr_immediate' : vmstatf.get('nr_immediate'),
        # 'nr_dirtied' : vmstatf.get('nr_dirtied'),
        # 'nr_written' : vmstatf.get('nr_written'),
        # 'pgscan_direct_throttle' : vmstatf.get('pgscan_direct_throttle'),
        # 'pgrescued' : vmstatf.get('pgrescued'),
        # 'nr_anon_trans_hugepgs' : vmstatf.get('nr_anon_transparent_hugepages'),
        # 'nr_dirty_threshold' : vmstatf.get('nr_dirty_threshold'),
        # 'nr_dirty_bg_threshold' : vmstatf.get('nr_dirty_background_threshold'),
        }

    def get(self, key):
        return self.data[key]

    def all(self):
        return self.data

class tmem(object):

    def __init__(self, proc, server, time, task):

        self.hostname = server.hostname()

        self.timeid = time.getid()
        self.serverid = server.getid()
        self.taskid = task.getid()

        try:
            self.statf = file_line(proc.file("stat"))
            self.statusf = file_keyvalue(proc.file("status"))

        except:
            pwd = proc.pwd().split("/")[-2]
            raise Exception("-> could not create tmem, proc: {}".format(pwd))

    def build(self):

        hostname = self.hostname
        timeid = self.timeid
        serverid = self.serverid
        taskid = self.taskid
        statf = self.statf
        statusf = self.statusf

        l = statf.get().split(" ")

        minflt = l[9]
        cminflt = l[10]
        majflt = l[11]
        cmajflt = l[12]

        try:

            vmpeak = statusf.get('VmPeak', clean=" kB")
            vmsize = statusf.get('VmSize', clean=" kB")
            vmlck = statusf.get('VmLck', clean=" kB")
            vmhwm = statusf.get('VmHWM', clean=" kB")
            vmrss = statusf.get('VmRSS', clean=" kB")
            vmdata = statusf.get('VmData', clean=" kB")
            vmstk = statusf.get('VmStk', clean=" kB")
            vmexe = statusf.get('VmExe', clean=" kB")
            vmlib = statusf.get('VmLib', clean=" kB")
            vmpte = statusf.get('VmPTE', clean=" kB")
            vmswap = statusf.get('VmSwap', clean=" kB")

            self.data = {
            'time_id' : timeid,
            'server_id' : serverid,
            'task_id' : taskid,
            'vmpeak' : vmpeak,
            'vmsize' : vmsize,
            'vmlck' : vmlck,
            'vmhwm' : vmhwm,
            'vmrss' : vmrss,
            'vmdata' : vmdata,
            'vmstk' : vmstk,
            'vmexe' : vmexe,
            'vmlib' : vmlib,
            'vmpte' : vmpte,
            'vmswap' : vmswap,
            'min_flt' : minflt,
            'cmin_flt' : cminflt,
            'maj_flt' : majflt,
            'cmaj_flt' : cmajflt,
            }

        except:

            # kernel tasks dont have virtual memory :D

            self.data = {
            'time_id' : timeid,
            'server_id' : serverid,
            'task_id' : taskid,
            'min_flt' : l[9],
            'cmin_flt' : l[10],
            'maj_flt' : l[11],
            'cmaj_flt' : l[12],
            }

    def sql(self, con):

        query = dbinsert("tmem", self.all())
        dbquery(con, query)

    def get(self, key):
        return self.data[key]

    def all(self):
        return self.data

