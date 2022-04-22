from defines import *
from base import *
from files import *

class gcpus ():

    def __init__(self, tod, server, time, cpus):

        self.statf = file_matrix(tod.file("stat"), "cpu")
        self.serverid = server.getid()
        self.timeid = time.getid()
        self.cpus = cpus
        self.gcpus = []

    def __iter__(self):

        for cpu in self.gcpus:
            yield cpu

    def build(self):

        serverid = self.serverid
        timeid = self.timeid
        cpus = self.cpus

        for l in self.statf:

            cpu = l[0].replace("cpu", "")
            if cpu is "": cpu = "999"

            cpuid = cpus.getid(cpu)

            user = l[1]
            nice = l[2]
            system = l[3]
            idle = l[4]
            iowait = l[5]
            irq = l[6]
            softirq = l[7]
            steal = l[8]

            gcpu = self.gcpu(timeid, serverid, cpuid, user, nice, system, idle,
                                iowait, irq, softirq, steal)

            self.gcpus.append(gcpu)

    def sql(self, con):

        for gcpu in self.gcpus:

            query = dbinsert("gcpu", gcpu.all())
            dbquery(con, query)

    class gcpu(object):

        def __init__(self, timeid, serverid, cpuid, user, nice, system, idle,
                        iowait, irq, softirq, steal):

            self.data = {
            'time_id' : timeid,
            'server_id' : serverid,
            'cpu_id' : cpuid,
            'user' : user,
            'nice' : nice,
            'system' : system,
            'idle' : idle,
            'iowait' : iowait,
            'irq' : irq,
            'softirq' : softirq,
            'steal' : steal,
            }

        def get(self, key):
            return self.data[key]

        def all(self):
            return self.data

class girqs (object):

    def __init__(self, tod, server, time, cpus, irqs, soft=False):

        self.serverid = server.getid()
        self.timeid = time.getid()
        self.cpus = cpus
        self.irqs = irqs
        self.soft = soft
        self.girqs = []

        if soft is False: filename = "interrupts"
        else: filename = "softirqs"

        irqf = file_matrix(tod.file(filename))
        self.irqiter = iter(irqf)
        self.irqiter.next()

    def __iter__(self):

        for irq in self.girqs:
            yield irq

    def build(self):

        soft = self.soft
        serverid = self.serverid
        timeid = self.timeid
        cpus = self.cpus
        irqs = self.irqs

        for l in self.irqiter:

            type = l[0]

            for cpu in self.cpus:

                cpuid = cpu.getid()
                cpunum = cpu.get('cpu')
                if(cpunum is "999"): continue

                count = l[int(cpunum) + 1]
                irqid = irqs.getid(type)

                girq = self.girq(timeid, serverid, cpuid, irqid, count, soft)

                self.girqs.append(girq)

    def sql(self, con):

        if self.soft is False: table = "girq"
        else: table = "gsirq"

        for girq in self.girqs:

            query = dbinsert(table, girq.all())
            dbquery(con, query)


    class girq():

        def __init__(self, timeid, serverid, cpuid, irqid, count, soft):

            if soft is False: field = 'irq_id'
            else: field = 'sirq_id'

            self.data = {
            'time_id' : timeid,
            'server_id' : serverid,
            'cpu_id' : cpuid,
             field : irqid,
            'count' : count,
            }

        def get(self, key):
            return self.data[key]

        def all(self):
            return self.data

class gschedds(object):

    def __init__(self, tod, server, time, domains, cpus):

        dschedstatf = file_matrix(tod.file("schedstat"), "domain")
        cschedstatf = file_matrix(tod.file("schedstat"), "cpu")
        self.dschediter = iter(dschedstatf)
        self.cschediter = iter(cschedstatf)

        self.serverid = server.getid()
        self.timeid = time.getid()
        self.domains = domains
        self.cpus = cpus

        self.gschedds = []

    def __iter__(self):

        for gschedd in self.gschedds:
            yield gschedd

    def build(self):

        serverid = self.serverid
        timeid = self.timeid
        domains = self.domains
        cpus = self.cpus

        dschediter = self.dschediter
        cschediter = self.cschediter

        for d in dschediter:
            c = cschediter.next()

            domainnum = d[0].replace("domain", "")
            cpunum = c[0].replace("cpu", "")

            domainid = domains.getid(domainnum)
            cpuid = cpus.getid(cpunum)

            sdom = self.gschedd(serverid, timeid, domainid, cpuid,
                          d[2], d[3], d[4], d[5], d[6], d[7], d[8],
                          d[9], d[10], d[11], d[12], d[13], d[14], d[15],
                          d[16], d[17], d[18], d[19], d[20], d[21], d[22],
                          d[23], d[24], d[25], d[26], d[27], d[28], d[35],
                          d[36]
                          )

            self.gschedds.append(sdom)

    def sql(self, con):

        for gschedd in self.gschedds:

            query = dbinsert("gschedd", gschedd.all())
            dbquery(con, query)

    class gschedd():

        def __init__ (self, serverid, timeid, domainid, cpuid,
                     a, b, c, d, e, f, g, h, i, j, l, m, n, o, p, q,
                     r, s, t, u, v, x, z, aa, ab, ac, ad, ae, af):

            self.data = {
            'time_id' : timeid,
            'server_id' : serverid,
            'domain_id' : domainid,
            'cpu_id' : cpuid,
            'load_balance_called_idle' : a,
            'load_balance_notreq_idle' : b,
            'load_balance_failed_idle' : c,
            'load_balance_imbl_idle' : d,
            'pull_task_idle' : e,
            'pull_task_cache_hot_idle' : f,
            'load_blc_not_busier_idle' : g,
            'busier_qu_not_b_grp_idle' : h,
            'load_balance_called_busy' : i,
            'load_balance_notreq_busy' : j,
            'load_balance_failed_busy' : l,
            'load_balance_imb_busy' : m,
            'pull_task_busy' : n,
            'pull_task_cache_hot_busy' : o,
            'load_balance_not_b_busy' : p,
            'busier_queue_n_b_grp_busy' : q,
            'load_bal_called_becidle' : r,
            'load_bal_notreq_becidle' : s,
            'load_bal_failed_becidle' : t,
            'load_bal_imb_becidle' : u,
            'pull_task_becidle' : v,
            'pull_tsk_cche_hot_becidle' : x,
            'load_bal_n_b_becidle' : z,
            'busier_q_n_b_group_becidle' : aa,
            'active_lb_called' : ab,
            'active_lb_failed_task' : ac,
            'active_lb_ok_task' : ad,
            'try_to_wake_dif_cpu_last' : ae,
            'try_to_wake_cpu_cache_hot' : af,
            }

        def get(self, key):
            return self.data[key]

        def all(self):
            return self.data

class gschedcs(object):

    def __init__(self, tod, server, time, domains, cpus):

        dschedstatf = file_matrix(tod.file("schedstat"), "domain")
        cschedstatf = file_matrix(tod.file("schedstat"), "cpu")
        self.dschediter = iter(dschedstatf)
        self.cschediter = iter(cschedstatf)

        self.serverid = server.getid()
        self.timeid = time.getid()
        self.domains = domains
        self.cpus = cpus

        self.gschedcs = []

    def __iter__(self):

        for gschedc in self.gschedcs:
            yield gschedc

    def build(self):

        serverid = self.serverid
        timeid = self.timeid
        domains = self.domains
        cpus = self.cpus

        dschediter = self.dschediter
        cschediter = self.cschediter

        for d in dschediter:
            c = cschediter.next()

            domainnum = d[0].replace("domain", "")
            cpunum = c[0].replace("cpu", "")

            domainid = domains.getid(domainnum)
            cpuid = cpus.getid(cpunum)

            gschedc = self.gschedc(
                                 serverid, timeid, domainid, cpuid,
                                 c[1], c[3], c[4], c[5], c[6], c[7], c[8], c[9],
                                 )

            self.gschedcs.append(gschedc)

    def sql(self, con):

        for gschedc in self.gschedcs:

            query = dbinsert("gschedc", gschedc.all())
            dbquery(con, query)

    class gschedc(object):

        def __init__ (self, serverid, timeid, domainid, cpuid,
                     a, b, c, d, e, f, g, h
                     ):

            self.data = {
            'time_id' : timeid,
            'server_id' : serverid,
            'domain_id' : domainid,
            'cpu_id' : cpuid,
            'sched_yield' : a,
            'schedule_called' : b,
            'schedule_idle' : c,
            'try_wake_up_called' : d,
            'try_wake_up_called_local' : e,
            'time_run_tasks' : f,
            'time_wait_tasks' : g,
            'timeslice_run' : h,
            }

        def get(self, key):
            return self.data[key]

        def all(self):
            return self.data

class tcpu(object):

    def __init__(self, proc, server, time, task):

        self.hostname = server.hostname()

        self.timeid = time.getid()
        self.serverid = server.getid()
        self.taskid = task.getid()

        try:
            self.statf = file_line(proc.file("stat"))

        except:
            pwd = proc.pwd().split("/")[-2]
            raise Exception("-> could not create tcpu, proc: {}".format(pwd))

    def build(self):

        hostname = self.hostname
        timeid = self.timeid
        serverid = self.serverid
        taskid = self.taskid
        statf = self.statf

        l = statf.get().split(" ")

        state = l[2]
        utime = l[13]
        stime = l[14]
        cutime = l[15]
        cstime = l[16]
        numthreads = l[19]
        processor = l[38]

        self.data = {
        'time_id' : timeid,
        'server_id' : serverid,
        'task_id' : taskid,
        'state' : state,
        'utime' : utime,
        'stime' : stime,
        'cutime' : cutime,
        'cstime' : cstime,
        'num_threads' : numthreads,
        'processor' : processor,
        }

    def sql(self, con):

        query = dbinsert("tcpu", self.all())
        dbquery(con, query)

    def get(self, key):
        return self.data[key]

    def all(self):
        return self.data

class tsched(object):

    def __init__(self, proc, server, time, task):

        self.hostname = server.hostname()
        self.timeid = time.getid()
        self.serverid = server.getid()
        self.taskid = task.getid()

        try:
            self.schedf = file_keyvalue(proc.file("sched"))

        except:
            pwd = proc.pwd().split("/")[-2]
            raise Exception("-> could not create tsched, proc: {}".format(pwd))

    def build(self):

        hostname = self.hostname
        timeid = self.timeid
        serverid = self.serverid
        taskid = self.taskid
        schedf = self.schedf

        execstart = schedf.get('se.exec_start')
        waitstart = schedf.get('se.wait_start')
        execmax = schedf.get('se.exec_max')
        iowcount = schedf.get('se.iowait_count')
        nrmigrat = schedf.get('se.nr_migrations')

	# kernel 3 changed to "*.statistics.*"

        #waitstart = schedf.get('se.statistics.wait_start')
        #execmax = schedf.get('se.statistics.exec_max')
        #iowcount = schedf.get('se.statistics.iowait_count')

        # timeid is tod, so it can be used

        self.data = {
            'time_id' : timeid,
            'server_id' : serverid,
            'task_id' : taskid,
            'exec_max' : execmax,
            'exec_start' : execstart,
            'iowait_count' : iowcount,
            'nr_migrat' : nrmigrat,
            'wait_start' : waitstart,
            'vruntime' : schedf.get('se.vruntime'),
            'sum_exec_runtime' : schedf.get('se.sum_exec_runtime'),

	    # kernel 3 changed to "*.statistics.*"

            # 'sleep_start' : schedf.get('se.statistics.sleep_start'),
            # 'block_start' : schedf.get('se.statistics.block_start'),
            # 'sleep_max' : schedf.get('se.statistics.sleep_max'),
            # 'block_max' : schedf.get('se.statistics.block_max'),
            # 'slice_max' : schedf.get('se.statistics.slice_max'),
            # 'wait_max' : schedf.get('se.statistics.wait_max'),
            # 'wait_sum' : schedf.get('se.statistics.wait_sum'),
            # 'wait_count' : schedf.get('se.statistics.wait_count'),
            # 'iowait_sum' : schedf.get('se.statistics.iowait_sum'),
            # 'nr_migrat_cold' : schedf.get('se.statistics.nr_migrations_cold'),
            # 'nr_failed_migrat_affine' : schedf.get('se.statistics.nr_failed_migrations_affine'),
            # 'nr_failed_migrat_running' : schedf.get('se.statistics.nr_failed_migrations_running'),
            # 'nr_failed_migrat_hot' : schedf.get('se.statistics.nr_failed_migrations_hot'),
            # 'nr_forced_migrat' : schedf.get('se.statistics.nr_forced_migrations'),
            # 'nr_wakeups' : schedf.get('se.statistics.nr_wakeups'),
            # 'nr_wakeups_sync' : schedf.get('se.statistics.nr_wakeups_sync'),
            # 'nr_wakeups_migrate' : schedf.get('se.statistics.nr_wakeups_migrate'),
            # 'nr_wakeups_local' : schedf.get('se.statistics.nr_wakeups_local'),
            # 'nr_wakeups_remote' : schedf.get('se.statistics.nr_wakeups_remote'),
            # 'nr_wakeups_affine' : schedf.get('se.statistics.nr_wakeups_affine'),
            # 'nr_wakeups_affine_attempts' : schedf.get('se.statistics.nr_wakeups_affine_attempts'),
            # 'nr_wakeups_passive' : schedf.get('se.statistics.nr_wakeups_passive'),
            # 'nr_wakeups_idle' : schedf.get('se.statistics.nr_wakeups_idle'),

            'sleep_start' : schedf.get('se.sleep_start'),
            'block_start' : schedf.get('se.block_start'),
            'sleep_max' : schedf.get('se.sleep_max'),
            'block_max' : schedf.get('se.block_max'),
            'slice_max' : schedf.get('se.slice_max'),
            'wait_max' : schedf.get('se.wait_max'),
            'wait_sum' : schedf.get('se.wait_sum'),
            'wait_count' : schedf.get('se.wait_count'),
            'iowait_sum' : schedf.get('se.iowait_sum'),
            'nr_migrat_cold' : schedf.get('se.nr_migrations_cold'),
            'nr_failed_migrat_affine' : schedf.get('se.nr_failed_migrations_affine'),
            'nr_failed_migrat_running' : schedf.get('se.nr_failed_migrations_running'),
            'nr_failed_migrat_hot' : schedf.get('se.nr_failed_migrations_hot'),
            'nr_forced_migrat' : schedf.get('se.nr_forced_migrations'),
            'nr_wakeups' : schedf.get('se.nr_wakeups'),
            'nr_wakeups_sync' : schedf.get('se.nr_wakeups_sync'),
            'nr_wakeups_migrate' : schedf.get('se.nr_wakeups_migrate'),
            'nr_wakeups_local' : schedf.get('se.nr_wakeups_local'),
            'nr_wakeups_remote' : schedf.get('se.nr_wakeups_remote'),
            'nr_wakeups_affine' : schedf.get('se.nr_wakeups_affine'),
            'nr_wakeups_affine_attempts' : schedf.get('se.nr_wakeups_affine_attempts'),
            'nr_wakeups_passive' : schedf.get('se.nr_wakeups_passive'),
            'nr_wakeups_idle' : schedf.get('se.nr_wakeups_idle'),

            'avg_atom' : schedf.get('avg_atom'),
            'avg_per_cpu' : schedf.get('avg_per_cpu'),
            'nr_switches' : schedf.get('nr_switches'),
            'nr_voluntary_switches' : schedf.get('nr_voluntary_switches'),
            'nr_involuntary_switches' : schedf.get('nr_involuntary_switches'),
            'clock_delta' : schedf.get('clock-delta'),
        }

    def sql(self, con):

        query = dbinsert("tsched", self.all())
        dbquery(con, query)

    def get(self, key):
        return self.data[key]

    def all(self):
        return self.data

