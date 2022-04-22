#!/usr/bin/python

from nvd3 import *
from structs import *

# --------

#        888888b.          d8888  .d8888b.  8888888888
#        888  "88b        d88888 d88P  Y88b 888
#        888  .88P       d88P888 Y88b.      888
#        8888888K.      d88P 888  "Y888b.   8888888
#        888  "Y88b    d88P  888     "Y88b. 888
#        888    888   d88P   888       "888 888
#        888   d88P  d8888888888 Y88b  d88P 888
#        8888888P"  d88P     888  "Y8888P"  8888888888

# mysql connection

md = mydata("lazydb")

#
# servers
#

servidores = values()

query = "select server_id, hostname from server"
md.query(query)

for row in md:
	server = servidor()
	name = "%s:%s" % (row['server_id'], row['hostname'])
	server.setname(name)
	servidores.add(server)

#
# processors (per server)
#

for server in servidores:
	id = server.get().getname().split(":")[0]
	name = server.get().getname().split(":")[1]

	query = "select cpu_id, cpu from cpu where server_id = '%s' order by cpu_id" % id
	md.query(query)

	for row in md:
		cpuname = "%s:%s" % (row['cpu_id'], row['cpu'])
		c = cpu()
		c.setname(cpuname)
		server.get().cpus().add(c)

#
# disks (per server)
#

# --- disk by disk
#
# for server in servidores:
# 	id = server.get().getname().split(":")[0]
# 	name = server.get().getname().split(":")[1]
# 	query = "select * from disk where server_id = '%s' and disk regexp '[a-z]$'" % id
# 	md.query(query)
# 	for row in md:
# 		diskname = "%s:%s" % (row['disk_id'], row['disk'])
# 		d = disk()
# 		d.setname(diskname)
# 		d.setblocks(long(row['blocks']))
# 		server.get().disks().add(d)

# --- disk by sizes

for server in servidores:
	id = server.get().getname().split(":")[0]
	name = server.get().getname().split(":")[1]

	query = "select * from disk where server_id = '%s' and disk regexp '[a-z]$' group by blocks" % id
	md.query(query)

	for row in md:
		d = disk()
		d.setbysize()
		d.setname(row['blocks'])
		d.setblocks(long(row['blocks']))
		server.get().disks().add(d)

for server in servidores:
	id = server.get().getname().split(":")[0]

	for disk in server.get().disks():
		q = "select * from disk where server_id = '%s' and blocks = '%s'" % (id, disk.get().getname())
		md.query(q)
		for row in md:
			print "server %s, disk %s, id %s" % (id, disk.get().getname(), row['disk_id'])
			disk.get().ids().add(str(row['disk_id']))

#
# days (per server)
#

for server in servidores:
	id = server.get().getname().split(":")[0]

	query = "select date(date) as d from time where server_id = '%s' " \
	"group by d" % id
	md.query(query)

	for row in md:
		d = dia()
		d.setname("%s-%s-%s" % (row['d'].year, row['d'].month, row['d'].day))
		server.get().dias().add(d)

#
# times (per day, per server)
#

for server in servidores:
	id = server.get().getname().split(":")[0]

	for dia in server.get().dias():
		data = "{}%".format(dia.get().getname())

		query = "select time_id, date from time where server_id = '%s' and date like '%s' order by time_id" % (id, data)
		md.query(query)

		for row in md:
			t = tempo()
			t.tod().set(row['time_id'])
			i = row['date']
			t.datetime().set(unix_time_ms(i))
			hora = "%02d:%02d:%02d" % (i.hour, i.minute, i.second)
			t.time().set(hora)
			dia.get().tempos().add(t)

# --------

#         .d8888b.  8888888b.  888     888
#        d88P  Y88b 888   Y88b 888     888
#        888    888 888    888 888     888
#        888        888   d88P 888     888
#        888        8888888P"  888     888
#        888    888 888        888     888
#        Y88b  d88P 888        Y88b. .d88P
#         "Y8888P"  888         "Y88888P"

#
# cpu usage (per server, per day, per cpu)
#

# for each server
for server in servidores:

	serverid = server.get().getname().split(":")[0]
	hostname = server.get().getname().split(":")[1]

	# for each monitored day
	for dia in server.get().dias():

		data = "{}".format(dia.get().getname())

		# first and last monitored time
		fsttod = dia.get().tempos().first().get().tod().get()
		fsttime = dia.get().tempos().first().get().time().get()
		lsttod = dia.get().tempos().last().get().tod().get()
		lsttime = dia.get().tempos().last().get().time().get()

		labs = []
		for l in dia.get().tempos().get():
			labs.append(l.get().datetime().get())

		# for each server cpu
		for cpu in server.get().cpus():

			cpuid = cpu.get().getname().split(":")[0]
			cpunum = cpu.get().getname().split(":")[1]

			# get all measurements for this cpu, on selected day, on selected server

			query = "select time_id, cpu_id, user, nice, system, idle,iowait, irq, softirq, steal from gcpu where server_id = '%s' and time_id > '%s' and time_id < '%s' and cpu_id = '%s' order by time_id" % (serverid, fsttod, lsttod, cpuid)
			md.query(query)

			if cpunum == "999": cpunum = "all"

			rowvelha = None

			for row in md:

				# first does not count
				if rowvelha is None:
					rowvelha = row
					continue

				# delta (for each measure)

				user = long(row['user']) - long(rowvelha['user'])
				system = long(row['system']) - long(rowvelha['system'])
				nice = long(row['nice']) - long(rowvelha['nice'])
				irq = long(row['irq']) - long(rowvelha['irq'])
				softirq = long(row['softirq']) - long(rowvelha['softirq'])
				iowait = long(row['iowait']) - long(rowvelha['iowait'])
				idle = long(row['idle']) - long(rowvelha['idle'])
				steal = long(row['steal']) - long(rowvelha['steal'])

				jiffies = user + nice + system + idle + iowait + irq + softirq + steal
				jiffies = float(jiffies)

				# delta percentage (for each measure)

				cpu.get().user().add(round((float(user) / jiffies * 100),2))
				cpu.get().system().add(round((float(system) / jiffies * 100),2))
				cpu.get().nice().add(round((float(nice) / jiffies * 100),2))
				cpu.get().irq().add(round((float(irq) / jiffies * 100),2))
				cpu.get().softirq().add(round((float(softirq) / jiffies * 100),2))
				cpu.get().iowait().add(round((float(iowait) / jiffies * 100),2))
				cpu.get().idle().add(round((float(idle) / jiffies * 100),2))
				cpu.get().steal().add(round((float(steal) / jiffies * 100),2))

				rowvelha = row

			# chart (for each cpu)

			filename = "./cpu/{}-{}-cpu-{}-usage".format(hostname, data, cpunum)
			ofile = open(filename + ".html", 'w')
			xdata = labs[:-3]

			# debug
			# print "xdata = {}".format(len(labs[:-3]))
			# print "ydata = {}".format(len(cpu.get().user().getlist()))

			chart = stackedAreaChart(name='stackedAreaChart', width=1024, height=768,x_is_date=True, x_axis_format="%X", color_category='category10')

			chart.charttooltip_dateformat="%X"

			es = {"tooltip": {"y_start": "", "y_end": "%"}}

			chart.add_serie(name="Nice", x=xdata, y=cpu.get().nice().getlist(), extra=es)
			chart.add_serie(name="User", x=xdata, y=cpu.get().user().getlist(), extra=es)
			chart.add_serie(name="System", x=xdata, y=cpu.get().system().getlist(), extra=es)
			chart.add_serie(name="SoftIRQ", x=xdata, y=cpu.get().softirq().getlist(), extra=es)
			chart.add_serie(name="IRQ", x=xdata, y=cpu.get().irq().getlist(), extra=es)
			chart.add_serie(name="IOwait", x=xdata, y=cpu.get().iowait().getlist(), extra=es)
			chart.add_serie(name="Idle", x=xdata, y=cpu.get().idle().getlist(), extra=es)
			chart.add_serie(name="Steal", x=xdata, y=cpu.get().steal().getlist(), extra=es)

			title = "CPU Usage<BR>Hostname: %s, Date: %s (From: %s, To: %s), CPU: %s<BR><BR>" % (hostname, data, fsttime, lsttime, cpunum)

			chart.buildhtml()
			ofile.write("<HTML><BODY BGCOLOR=WHITE FONT=BLACK><CENTER>")
			ofile.write("<H3><BOLD>" + title + "</BOLD><BR>")
			ofile.write(chart.htmlcontent)
			ofile.write("</BODY></HTML>")
			ofile.close()

			cpu.get().clear()

# --------

#        888b     d888 8888888888 888b     d888
#        8888b   d8888 888        8888b   d8888
#        88888b.d88888 888        88888b.d88888
#        888Y88888P888 8888888    888Y88888P888
#        888 Y888P 888 888        888 Y888P 888
#        888  Y8P  888 888        888  Y8P  888
#        888   "   888 888        888   "   888
#        888       888 8888888888 888       888

#
# mem usage (per server, per day)
#

# for each server
for server in servidores:

	serverid = server.get().getname().split(":")[0]
	hostname = server.get().getname().split(":")[1]

	# for each monitored day
	for dia in server.get().dias():

		data = "{}".format(dia.get().getname())

		# first and last monitored time
		fsttod = dia.get().tempos().first().get().tod().get()
		fsttime = dia.get().tempos().first().get().time().get()
		lsttod = dia.get().tempos().last().get().tod().get()
		lsttime = dia.get().tempos().last().get().time().get()

		labs = []
		for l in dia.get().tempos().get():
			labs.append(l.get().datetime().get())

		query = "select * from gmem where server_id = '%s' and time_id > '%s' and time_id < '%s' order by time_id" % (serverid, fsttod, lsttod)
		md.query(query)

		for row in md:

			memtotal = long(row['memtotal'])
			memfree = long(row['memfree'])
			buffers = long(row['buffers'])
			cached = long(row['cached'])
			swapcached = long(row['swapcached'])
			active = long(row['active'])
			inactive = long(row['inactive'])
			dirty = long(row['dirty'])
			anonpages = long(row['anonpages'])
			slab = long(row['slab'])
			pagetables = long(row['pagetables'])
			vmallocused = long(row['vmallocused'])
			committedas = long(row['committed_as'])
			commitlimit = long(row['commitlimit'])
			writeback = long(row['writeback'])
			hugetotal = long(row['hugepages_total']) * 2048 # huge pagesize
			hugefree = long(row['hugepages_free']) * 2048
			hugersvd = long(row['hugepages_rsvd']) * 2048
			hugesurp = long(row['hugepages_surp']) * 2048
			swaptotal = long(row['swap_total'])
			swapfree = long(row['swap_free'])
			mapped = long(row['mapped'])

			server.get().mem().memtotal().add(memtotal)
			server.get().mem().memfree().add(memfree)
			server.get().mem().buffers().add(buffers)
			server.get().mem().cached().add(cached)
			server.get().mem().swapcached().add(swapcached)
			server.get().mem().active().add(active)
			server.get().mem().inactive().add(inactive)
			server.get().mem().dirty().add(dirty)
			server.get().mem().anonpages().add(anonpages)
			server.get().mem().slab().add(slab)
			server.get().mem().pagetables().add(pagetables)
			server.get().mem().vmallocused ().add(vmallocused)
			server.get().mem().committedas().add(committedas)
			server.get().mem().commitlimit().add(commitlimit)
			server.get().mem().hugetotal().add(hugetotal)
			server.get().mem().hugefree().add(hugefree)
			server.get().mem().hugersvd().add(hugersvd)
			server.get().mem().hugesurp().add(hugesurp)
			server.get().mem().writeback().add(writeback)
			server.get().mem().swaptotal().add(swaptotal)
			server.get().mem().swapfree().add(swapfree)
			server.get().mem().mapped().add(mapped)


		#
		# chart 1 - memtotal = active + inactive + slab + pagetables + vmallocused + "extras"
		#

		filename = "./mem/{}-{}-memtotal".format(hostname, data)
		ofile = open(filename + ".html", 'w')
		xdata = labs[:-2]

		# debug
		# print "xdata = {}".format(len(labs[:-2]))
		# print "ydata = {}".format(len(server.get().mem().memtotal().getlist()))

		chart = stackedAreaChart(name='stackedAreaChart', width=1024, height=768,x_is_date=True, x_axis_format="%X", color_category='category10')

		chart.charttooltip_dateformat="%X"

		es = {"tooltip": {"y_start": "", "y_end": "%"}}

		mt = server.get().mem().memtotal().getlist()
		mf = server.get().mem().memfree().getlist()
		ac = server.get().mem().active().getlist()
		ic = server.get().mem().inactive().getlist()
		sl = server.get().mem().slab().getlist()
		pt = server.get().mem().pagetables().getlist()
		vm = server.get().mem().vmallocused().getlist()
		ht = server.get().mem().hugetotal().getlist()
		hf = server.get().mem().hugefree().getlist()

		pmf = [ round(float(f) / float(m) * 100, 2) for m, f in zip(mt, mf)]
		pac = [ round(float(a) / float(m) * 100, 2) for m, a in zip(mt, ac)]
		pic = [ round(float(i) / float(m) * 100, 2) for m, i in zip(mt, ic)]
		psl = [ round(float(s) / float(m) * 100, 2) for m, s in zip(mt, sl)]
		ppt = [ round(float(p) / float(m) * 100, 2) for m, p in zip(mt, pt)]
		pvm = [ round(float(v) / float(m) * 100, 2) for m, v in zip(mt, vm)]
		pht = [ round((float(h) - float(f)) / float(m) * 100, 2) for m, h, f in zip(mt, ht, hf)]
		phf = [ round(float(h) / float(m) * 100, 2) for m, h in zip(mt, hf)]

		pex = [ round(100 - (a+b+c+d+e+f+g+h), 2) for a,b,c,d,e,f,g,h in zip(pac, pic, psl, ppt, pvm, pht, phf, pmf)]

		chart.add_serie(name="Active", x=xdata, y=pac, extra=es)
		chart.add_serie(name="Inactive", x=xdata, y=pic, extra=es)
		chart.add_serie(name="Slab", x=xdata, y=psl, extra=es)
		chart.add_serie(name="VmallocUsed", x=xdata, y=pvm, extra=es)
		chart.add_serie(name="PageTables", x=xdata, y=ppt, extra=es)
		chart.add_serie(name="KernelExtra", x=xdata, y=pex, extra=es)
		chart.add_serie(name="HugeUsed", x=xdata, y=pht, extra=es)
		chart.add_serie(name="HugeFree", x=xdata, y=phf, extra=es)
		chart.add_serie(name="Free", x=xdata, y=pmf, extra=es)

		total = float(server.get().mem().memtotal().getlist()[0]) / 1024 / 1024

		title = "MemTotal (%.2f GB)<BR>Hostname: %s, Date: %s (From: %s, To: %s)<BR><BR>" % (total, hostname, data, fsttime, lsttime)

		chart.buildhtml()
		ofile.write("<HTML><BODY BGCOLOR=WHITE FONT=BLACK><CENTER>")
		ofile.write("<H3><BOLD>" + title)
		ofile.write(chart.htmlcontent)
		ofile.write("MemTotal = Active + Inactive + Slab + PageTables + VmallocUsed + HugePages")
		ofile.write("</BODY></HTML>")
		ofile.close()

		#
		# chart 2 - active + inactive = buffers + cached + swapcached + anonpages
		#

		filename = "./mem/{}-{}-activeinactive".format(hostname, data)
		ofile = open(filename + ".html", 'w')
		xdata = labs[:-2]

		# debug
		# print "xdata = {}".format(len(labs[:-2]))
		# print "ydata = {}".format(len(server.get().mem().memtotal().getlist()))

		chart = stackedAreaChart(name='stackedAreaChart', width=1024, height=768,x_is_date=True, x_axis_format="%X", color_category='category10')

		chart.charttooltip_dateformat="%X"

		es = {"tooltip": {"y_start": "", "y_end": "%"}}

		# todo: somar buffers + cached + swapcached + anonpages como 100%
		# todo: fazer grafico de active/inactive e grafico dos itens acima

		mt = server.get().mem().memtotal().getlist()
		ac = server.get().mem().active().getlist()
		ic = server.get().mem().inactive().getlist()
		bu = server.get().mem().buffers().getlist()
		ca = server.get().mem().cached().getlist()
		sc = server.get().mem().swapcached().getlist()
		an = server.get().mem().anonpages().getlist()

		pai = [ round(float(a) + float(i), 2) for a, i in zip(ac, ic)]
		pbu = [ round(float(b) / float(m) * 100, 2) for m, b in zip(mt, bu)]
		pca = [ round(float(c) / float(m) * 100, 2) for m, c in zip(mt, ca)]
		psc = [ round(float(s) / float(m) * 100, 2) for m, s in zip(mt, sc)]
		pan = [ round(float(a) / float(m) * 100, 2) for m, a in zip(mt, an)]
		res = [ round((float(t) - float(u)) / float(t) * 100, 2) for u, t in zip(pai, mt) ]

		chart.add_serie(name="Buffers", x=xdata, y=pbu, extra=es)
		chart.add_serie(name="Cached", x=xdata, y=pca, extra=es)
		chart.add_serie(name="SwapCached", x=xdata, y=psc, extra=es)
		chart.add_serie(name="AnonPages", x=xdata, y=pan, extra=es)
		kargs= {'color' : 'white'}
		chart.add_serie(name="Free", x=xdata, y=res, **kargs)

		total = float(server.get().mem().memtotal().getlist()[0]) / 1024 / 1024

		title = "MemTotal (%.2f GB) - Active + Inactive<BR>Hostname: %s, Date: %s (From: %s, To: %s)<BR><BR>" % (total, hostname, data, fsttime, lsttime)

		chart.buildhtml()
		ofile.write("<HTML><BODY BGCOLOR=WHITE FONT=BLACK><CENTER>")
		ofile.write("<H3><BOLD>" + title)
		ofile.write(chart.htmlcontent)
		ofile.write("Active + Inactive = Buffers + Cached + SwapCached + AnonPages")
		ofile.write("</BODY></HTML>")
		ofile.close()

		#
		# chart 3 - committed_as (anon and huge) from memtotal + swap
		#

		filename = "./mem/{}-{}-committedas".format(hostname, data)
		ofile = open(filename + ".html", 'w')
		xdata = labs[:-2]

		# debug
		# print "xdata = {}".format(len(labs[:-2]))
		# print "ydata = {}".format(len(server.get().mem().committedas().getlist()))

		chart = lineChart(name='lineChart', width=1024, height=768,x_is_date=True, x_axis_format="%X", color_category='category10')

		chart.charttooltip_dateformat="%X"

		es = {"tooltip": {"y_start": "", "y_end": "GB"}}

		mt = [round(float(x)/1048576, 2) for x in server.get().mem().memtotal().getlist()]
		st = [round(float(x)/1048576, 2) for x in server.get().mem().swaptotal().getlist()]
		cl = [round(float(x)/1048576, 2) for x in server.get().mem().commitlimit().getlist()]
		cs = [round(float(x)/1048576, 2) for x in server.get().mem().committedas().getlist()]
		an = [round(float(x)/1048576, 2) for x in server.get().mem().anonpages().getlist()]

		ht = [round(float(x)/1048576, 2) for x in server.get().mem().hugetotal().getlist()]
		hf = [round(float(x)/1048576, 2) for x in server.get().mem().hugefree().getlist()]
		hr = [round(float(x)/1048576, 2) for x in server.get().mem().hugersvd().getlist()]
		hs = [round(float(x)/1048576, 2) for x in server.get().mem().hugersvd().getlist()]

		hu = [ t - f for t, f in zip(ht, hf)]				# used = total - free
		su = [ a + b for a, b in zip(ht, hs)]				# surp = total + surp
		rs = [ a + b for a, b in zip(hu, hr)]				# rsvd = used + rsvd

		mem = [ round(m + s, 2) for m,s in zip(mt, st) ]	# total memory + swap

		chart.add_serie(name="Total+Swap", x=xdata, y=mem, extra=es)		# total memory + swap
		chart.add_serie(name="Total", x=xdata, y=mt, extra=es)				# total memory
		chart.add_serie(name="CommitLimit", x=xdata, y=cl, extra=es)		# commit limit
		chart.add_serie(name="Committed", x=xdata, y=cs, extra=es)			# committed
		chart.add_serie(name="Used(AnonPages)", x=xdata, y=an, extra=es)	# used (anon)

		chart.add_serie(name="HugeTotal", x=xdata, y=ht, extra=es)			# total hugepages
		chart.add_serie(name="HugeUsed", x=xdata, y=hu, extra=es)			# used hugepages
		chart.add_serie(name="HugeRsvd", x=xdata, y=rs, extra=es)			# reserved hugepages
		chart.add_serie(name="HugeSurp", x=xdata, y=su, extra=es)			# overcommitted hps

		# missing x axis (bug ?)
		axis = [ 0 for x in range(len(labs[:-2])) ]
		kargs= {'color' : 'black'}
		chart.add_serie(name=" ", x=xdata, y=axis, **kargs)

		title = "Committed<BR>Hostname: %s, Date: %s (From: %s, To: %s)<BR><BR>" % (hostname, data, fsttime, lsttime)

		chart.buildhtml()
		ofile.write("<HTML><BODY BGCOLOR=WHITE FONT=BLACK><CENTER>")
		ofile.write("<H3><BOLD>" + title)
		ofile.write(chart.htmlcontent)
		ofile.write("Committed (Anon or Huge pages) from MemTotal + Swap.</H3>")
		ofile.write("<H6>CommitLimit is valid only if vm.overcommit_memory = 2</H6>")
		ofile.write("</BODY></HTML>")
		ofile.close()

		#
		# chart 4 - pagecache vs mapped vs dirty
		#

		filename = "./mem/{}-{}-mapped-dirty".format(hostname, data)
		ofile = open(filename + ".html", 'w')
		xdata = labs[:-2]

		chart = lineChart(name='lineChart', width=1024, height=768,x_is_date=True, x_axis_format="%X", color_category='category10')

		chart.charttooltip_dateformat="%X"

		es = {"tooltip": {"y_start": "", "y_end": "GB"}}

		# pagecache
		buf = [round(float(x)/1048576, 2) for x in server.get().mem().buffers().getlist()]
		cac = [round(float(x)/1048576, 2) for x in server.get().mem().cached().getlist()]
		swp = [round(float(x)/1048576, 2) for x in server.get().mem().swapcached().getlist()]
		pac = [ b+c+s for b,c,s in zip(buf, cac, swp) ]
		# dirty
		drt = [round(float(x)/1048576, 2) for x in server.get().mem().dirty().getlist()]
		# mapped
		mpd = [round(float(x)/1048576, 2) for x in server.get().mem().mapped().getlist()]

		chart.add_serie(name="PageCache", x=xdata, y=pac, extra=es)
		chart.add_serie(name="Dirty", x=xdata, y=drt, extra=es)
		chart.add_serie(name="Mapped", x=xdata, y=mpd, extra=es)

		# missing x axis (bug ?)
		axis = [ 0 for x in range(len(labs[:-2])) ]
		kargs= {'color' : 'black'}
		chart.add_serie(name=" ", x=xdata, y=axis, **kargs)

		title = "Committed<BR>Hostname: %s, Date: %s (From: %s, To: %s)<BR><BR>" % (hostname, data, fsttime, lsttime)

		chart.buildhtml()
		ofile.write("<HTML><BODY BGCOLOR=WHITE FONT=BLACK><CENTER>")
		ofile.write("<H3><BOLD>" + title)
		ofile.write(chart.htmlcontent)
		ofile.write("Committed (Anon or Huge pages) from MemTotal + Swap.</H3>")
		ofile.write("<H6>CommitLimit is valid only if vm.overcommit_memory = 2</H6>")
		ofile.write("</BODY></HTML>")
		ofile.close()

		server.get().mem().clear()

# --------

#		 8888888b. 8888888  .d8888b.  888    d8P
#		 888  "Y88b  888   d88P  Y88b 888   d8P
#		 888    888  888   Y88b.      888  d8P
#		 888    888  888    "Y888b.   888d88K
#		 888    888  888       "Y88b. 8888888b
#		 888    888  888         "888 888  Y88b
#		 888  .d88P  888   Y88b  d88P 888   Y88b
#		 8888888P" 8888888  "Y8888P"  888    Y88b


# disk usage (per server, per day)


# for each server
for server in servidores:
	serverid = server.get().getname().split(":")[0]
	hostname = server.get().getname().split(":")[1]

	# for each monitored day
	for dia in server.get().dias():
		data = "{}".format(dia.get().getname())

		# first and last monitored time
		fsttod = dia.get().tempos().first().get().tod().get()
		fsttime = dia.get().tempos().first().get().time().get()
		lsttod = dia.get().tempos().last().get().tod().get()
		lsttime = dia.get().tempos().last().get().time().get()

		labs = []
		for l in dia.get().tempos().get():
			labs.append(l.get().datetime().get())

		#
		# CPU WALL CLOCK : only need 1 cpu to get total jiffies
		#

		totalseconds = []

		numcpus = len(server.get().cpus().getlist()) - 1

		query = "select cpu_id, server_id, cpu from cpu where server_id = '%s' and cpu = '999'" % (serverid)
		md.query(query)

		for row in md:
			cpuid = row['cpu_id']

		query = "select * from gcpu where server_id = '%s' and time_id > '%s' and time_id < '%s' and cpu_id = '%s' order by time_id" % (serverid, fsttod, lsttod, cpuid)
		md.query(query)

		rowvelha = None

		for row in md:
			if rowvelha is None:
				rowvelha = row
				continue

			user = (long(row['user']) - long(rowvelha['user'])) / numcpus
			system = (long(row['system']) - long(rowvelha['system'])) / numcpus
			nice = (long(row['nice']) - long(rowvelha['nice'])) / numcpus
			irq = (long(row['irq']) - long(rowvelha['irq'])) / numcpus
			softirq = (long(row['softirq']) - long(rowvelha['softirq'])) / numcpus
			iowait = (long(row['iowait']) - long(rowvelha['iowait']))/ numcpus
			idle = (long(row['idle']) - long(rowvelha['idle']))/ numcpus
			steal = (long(row['steal']) - long(rowvelha['steal']))/ numcpus

			jiffies = user + nice + system + idle + iowait + irq + softirq + steal

			totalseconds.append(round(float(jiffies) * 0.0167,2))

			rowvelha = row

		#
		# END OF CPU WALL CLOCK
		#

		#
		# FOR EACH DISK
		#

		# for each server disk
		for disk in server.get().disks():


			if disk.get().getbysize() is False:

				diskid = disk.get().getname().split(":")[0]
				diskname = disk.get().getname().split(":")[1]
				query = "select * from gdisk where server_id = '%s' and time_id > '%s' and time_id < '%s' and disk_id = '%s' order by time_id" % (serverid, fsttod, lsttod, diskid)

			else:

				diskid = None
				diskname = disk.get().getname()
				query = "select sum(reads_completed) as reads_completed, sum(reads_merged) as reads_merged, sum(sectors_read) as sectors_read, sum(time_spent_reading) as time_spent_reading, sum(writes_completed) as writes_completed, sum(writes_merged) as writes_merged, sum(sectors_written) as sectors_written, sum(time_spent_writing) as time_spent_writing, sum(ios_current) as ios_current, sum(time_spent_doing_io) as time_spent_doing_io, sum(wtime_spent_doing_io) as wtime_spent_doing_io from gdisk where server_id = '%s' and time_id > '%s' and time_id < '%s' and disk_id in (%s) group by time_id order by time_id" % (serverid, fsttod, lsttod, ",".join(disk.get().ids().getlist()))

			print "server: %s, disk: %s, diskid: %s" % (serverid, diskname, diskid)
			print disk.get().ids().getlist()

			md.query(query)

			rowvelha = None

			for row in md:

				#
				# FOR EACH MEASUREMENT
				#

				# first does not count
				if rowvelha is None:
					rowvelha = row
					continue

				rdcomp = long(row['reads_completed']) - long(rowvelha['reads_completed'])					   #1
				rdmerg = long(row['reads_merged']) - long(rowvelha['reads_merged'])								   #2
				sectrd = long(row['sectors_read']) - long(rowvelha['sectors_read'])             	   #3
				tsread = long(row['time_spent_reading']) - long(rowvelha['time_spent_reading']) 	   #4
				wrcomp = long(row['writes_completed']) - long(rowvelha['writes_completed'])     	   #5
				wrmerg = long(row['writes_merged']) - long(rowvelha['writes_merged'])           	   #6
				sectwr = long(row['sectors_written']) - long(rowvelha['sectors_written'])       	   #7
				tswrit = long(row['time_spent_writing']) - long(rowvelha['time_spent_writing']) 	   #8
				ioscur = long(row['ios_current']) - long(rowvelha['ios_current'])               	   #9
				tisdio = long(row['time_spent_doing_io']) - long(rowvelha['time_spent_doing_io'])	   #10
				wtsdio = long(row['wtime_spent_doing_io']) - long(rowvelha['wtime_spent_doing_io'])  #11

				# delta percentage (for each measure)

				disk.get().rdcomp().add(rdcomp)
				disk.get().rdmerg().add(rdmerg)
				disk.get().sectrd().add(sectrd)
				disk.get().tsread().add(tsread)
				disk.get().wrcomp().add(wrcomp)
				disk.get().wrmerg().add(wrmerg)
				disk.get().sectwr().add(sectwr)
				disk.get().tswrit().add(tswrit)
				disk.get().ioscur().add(ioscur)
				disk.get().tisdio().add(tisdio)
				disk.get().wtsdio().add(wtsdio)

				rowvelha = row

			# debug
			print "xdata = {}".format(len(labs[:-3]))
			print "ydata = {}".format(len(disk.get().rdcomp().getlist()))

			#
			# FOR EACH DISK GET MEASUREMENTS
			#

			trdcomp = disk.get().rdcomp().getlist()
			trdmerg = disk.get().rdmerg().getlist()
			tsectrd = disk.get().sectrd().getlist()
			ttsread = disk.get().tsread().getlist()
			twrcomp = disk.get().wrcomp().getlist()
			twrmerg = disk.get().wrmerg().getlist()
			tsectwr = disk.get().sectwr().getlist()
			ttswrit = disk.get().tswrit().getlist()
			tioscur = disk.get().ioscur().getlist()
			ttisdio = disk.get().tisdio().getlist()
			twtsdio = disk.get().wtsdio().getlist()

			#
			# FOR EACH DISK SUM MEASUREMENTS
			#

			rdps = [ round(float(x) / y, 2) for x, y in zip(trdcomp, totalseconds)]
			rdavgkb = [ round(2 * float(y) / float(x), 2) if x > 0 else 0 for x, y in zip(trdcomp, tsectrd)]
			rdmbs = [ round(2 * float(x) / 1024 / y, 2) for x, y in zip(tsectrd, totalseconds)]
			rdmrg = [ round(100 * float(y) / (float(x) + float(y)), 2) if (x > 0 or y > 0) else 0 for x, y in zip(trdcomp, trdmerg)]
			rdcnc = [ round(float(x) / float(y) / 1000, 2) for x, y in zip(ttsread, totalseconds)]
			rddrt = [ round(float(z) / (x + y), 2) if (x > 0 or y > 0) else 0  for x,y,z in zip(trdcomp, trdmerg, ttsread)]

			wdps = [ round(float(x) / y, 2) for x, y in zip(twrcomp, totalseconds)]
			wravgkb = [ round(2 * float(y) / float(x), 2) if x > 0 else 0 for x, y in zip(twrcomp, tsectwr)]
			wrmbs = [ round(2 * float(x) / 1024 / y, 2) for x, y in zip(tsectwr, totalseconds)]
			wrmrg = [ round(100 * float(y) / (float(x) + float(y)), 2) if (x > 0 or y > 0) else 0 for x, y in zip(twrcomp, twrmerg)]
			wrcnc = [ round(float(x) / float(y) / 1000, 2) for x, y in zip(ttswrit, totalseconds)]
			wrdrt = [ round(float(z) / (x + y), 2) if (x > 0 or y > 0) else 0 for x,y,z in zip(twrcomp, twrmerg, ttswrit)]

			busy = [ round(float((100 * x)) / (1000 * y) , 2) if y > 0 else 0 for x, y in zip(ttisdio, totalseconds)]
			inprg = [ round(float(x)) for x in tioscur ]
			iops = [ x + y for x, y in zip(rdps, wdps) ]

			compact = zip(trdcomp, trdmerg, twrcomp, twrmerg, ttisdio)
			stime = [ float(e) / (a+b+c+d) if (a > 0 or b > 0 or c > 0 or d > 0) else 0 for a,b,c,d,e in compact ]
			compact = zip(trdcomp, trdmerg, twrcomp, twrmerg, tioscur, ttisdio, twtsdio)
			qtime = [ round((float(z)/(a+b+c+d+x))-(float(y)/(a+b+c+d)),2) if (a > 0 or b > 0 or c > 0 or d > 0) else 0 for a,b,c,d,x,y,z in compact]

			rtime = [ a + b for a,b in zip(rddrt, wrdrt)]

			#
			# FOR EACH DISK CREATE CHARTS
			#

			# chart 1

			filename = "./disk/{}-{}-disk-{}-readwrite".format(hostname, data, diskname)
			ofile = open(filename + ".html", 'w')
			xdata = labs[:-3]

			chart = lineChart(name='lineChart', width=1024, height=768,x_is_date=True, x_axis_format="%X", color_category='category10')

			chart.charttooltip_dateformat="%X"

			es = {"tooltip": {"y_start": "", "y_end": "IOs"}}

			chart.add_serie(name="Read", x=xdata, y=rdps, extra=es)
			chart.add_serie(name="Writes", x=xdata, y=wdps, extra=es)
			chart.add_serie(name="ReadMerge", x=xdata, y=rdmrg, extra=es)
			chart.add_serie(name="WriteMerge", x=xdata, y=wrmrg, extra=es)

			title = "Reads & Writes (per Second)<BR>Hostname: %s, Disk: %s, Date: %s (From: %s, To: %s)<BR><BR>" % (hostname, diskname, data, fsttime, lsttime)

			chart.buildhtml()
			ofile.write("<HTML><BODY BGCOLOR=WHITE FONT=BLACK><CENTER>")
			ofile.write("<H3><BOLD>" + title)
			ofile.write(chart.htmlcontent)
			# ofile.write("Committed (Anon or Huge pages) from MemTotal + Swap.</H3>")
			# ofile.write("<H6>CommitLimit is valid only if vm.overcommit_memory = 2</H6>")
			ofile.write("</BODY></HTML>")
			ofile.close()

			# chart 2

			filename = "./disk/{}-{}-disk-{}-readwritembs".format(hostname, data, diskname)
			ofile = open(filename + ".html", 'w')
			xdata = labs[:-3]

			chart = lineChart(name='lineChart', width=1024, height=768,x_is_date=True, x_axis_format="%X", color_category='category10')

			chart.charttooltip_dateformat="%X"

			es = {"tooltip": {"y_start": "", "y_end": "MBs"}}

			chart.add_serie(name="Reads", x=xdata, y=rdmbs, extra=es)
			chart.add_serie(name="Writes", x=xdata, y=wrmbs, extra=es)

			title = "Reads & Writes (MB per Second)<BR>Hostname: %s, Disk: %s, Date: %s (From: %s, To: %s)<BR><BR>" % (hostname, diskname, data, fsttime, lsttime)

			chart.buildhtml()
			ofile.write("<HTML><BODY BGCOLOR=WHITE FONT=BLACK><CENTER>")
			ofile.write("<H3><BOLD>" + title)
			ofile.write(chart.htmlcontent)
			# ofile.write("Committed (Anon or Huge pages) from MemTotal + Swap.</H3>")
			# ofile.write("<H6>CommitLimit is valid only if vm.overcommit_memory = 2</H6>")
			ofile.write("</BODY></HTML>")
			ofile.close()

			# chart 3

			filename = "./disk/{}-{}-disk-{}-readwriteavgsz".format(hostname, data, diskname)
			ofile = open(filename + ".html", 'w')
			xdata = labs[:-3]

			chart = lineChart(name='lineChart', width=1024, height=768,x_is_date=True, x_axis_format="%X", color_category='category10')

			chart.charttooltip_dateformat="%X"

			es = {"tooltip": {"y_start": "", "y_end": "KB"}}

			chart.add_serie(name="Reads", x=xdata, y=rdavgkb, extra=es)
			chart.add_serie(name="Writes", x=xdata, y=wravgkb, extra=es)

			title = "Reads & Writes (AvgSize KB)<BR>Hostname: %s, Disk: %s, Date: %s (From: %s, To: %s)<BR><BR>" % (hostname, diskname, data, fsttime, lsttime)

			chart.buildhtml()
			ofile.write("<HTML><BODY BGCOLOR=WHITE FONT=BLACK><CENTER>")
			ofile.write("<H3><BOLD>" + title)
			ofile.write(chart.htmlcontent)
			# ofile.write("Committed (Anon or Huge pages) from MemTotal + Swap.</H3>")
			# ofile.write("<H6>CommitLimit is valid only if vm.overcommit_memory = 2</H6>")
			ofile.write("</BODY></HTML>")
			ofile.close()

			# chart 4

			filename = "./disk/{}-{}-disk-{}-respqueueservtime".format(hostname, data, diskname)
			ofile = open(filename + ".html", 'w')
			xdata = labs[:-3]

			chart = lineChart(name='lineChart', width=1024, height=768,x_is_date=True, x_axis_format="%X", color_category='category10')

			chart.charttooltip_dateformat="%X"

			es = {"tooltip": {"y_start": "", "y_end": "ms"}}

			chart.add_serie(name="Response", x=xdata, y=rtime, extra=es)
			chart.add_serie(name="Service", x=xdata, y=stime, extra=es)
			chart.add_serie(name="Queue", x=xdata, y=qtime, extra=es)

			title = "Response = Service + Queue (Time in ms)<BR>Hostname: %s, Disk: %s, Date: %s (From: %s, To: %s)<BR><BR>" % (hostname, diskname, data, fsttime, lsttime)

			chart.buildhtml()
			ofile.write("<HTML><BODY BGCOLOR=WHITE FONT=BLACK><CENTER>")
			ofile.write("<H3><BOLD>" + title)
			ofile.write(chart.htmlcontent)
			# ofile.write("Committed (Anon or Huge pages) from MemTotal + Swap.</H3>")
			# ofile.write("<H6>CommitLimit is valid only if vm.overcommit_memory = 2</H6>")
			ofile.write("</BODY></HTML>")
			ofile.close()

			disk.get().clear()

