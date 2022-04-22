#!/usr/bin/python

import pytz
import MySQLdb as mdb

from datetime import datetime

#
# needed abstractions
#

class value(object):

	def __init__(self, v=None):
		self.v = v

	def get(self):
		return self.v

	def set(self, v):
		self.v = v

class values(object):

	def __init__(self):
		self.vs = []

	def __iter__(self):
		for v in self.vs:
			yield v

	def add(self, o=None):
		v = value(o)
		self.vs.append(v)
		return v

	def get(self):
		return self.vs

	def getlist(self):
		t = []
		for v in self.vs:
			t.append(v.get())
		return t

	def first(self):
		return self.vs[0]

	def last(self):
		return self.vs[-1]

class tempo(object):

	def __init__(self):
		self.td = value()
		self.tm = value()
		self.dt = value()

	def tod(self):
		return self.td

	def time(self):
		return self.tm

	def datetime(self):
		return self.dt

class dia(object):

	def __init__(self):
		self.str = ""
		self.tps = values()

	def setname(self, s):
		self.str = s

	def getname(self):
		return self.str

	def tempos(self):
		return self.tps

class cpu(object):

	def __init__(self):
		self.str = ""
		self.clear()

	def clear(self):
		self.ni = values()
		self.us = values()
		self.sy = values()
		self.ir = values()
		self.so = values()
		self.io = values()
		self.id = values()
		self.st = values()

	def setname(self, s):
		self.str = s

	def getname(self):
		return self.str

	def nice(self):
		return self.ni

	def user(self):
		return self.us

	def system(self):
		return self.sy

	def irq(self):
		return self.ir

	def softirq(self):
		return self.so

	def iowait(self):
		return self.io

	def idle(self):
		return self.id

	def steal(self):
		return self.st

class disk(object):

	def __init__(self):
		self.bysize = False
		self.str = ""
		self.blks = 0
		self.clear()
		self.sids = values()

	def setbysize(self):
		self.bysize = True

	def getbysize(self):
		return self.bysize

	def setname(self, s):
		self.str = s

	def getname(self):
		return self.str

	def setblocks(self, b):
		self.blks = b

	def getblocks(self):
		return self.blks

	def clear(self):
		self.srdcomp = values()
		self.srdmerg = values()
		self.ssectrd = values()
		self.stsread = values()
		self.swrcomp = values()
		self.swrmerg = values()
		self.ssectwr = values()
		self.stswrit = values()
		self.sioscur = values()
		self.stisdio = values()
		self.swtsdio = values()

	def ids(self):
		return self.sids
	def rdcomp(self):
		return self.srdcomp
	def rdmerg(self):
		return self.srdmerg
	def sectrd(self):
		return self.ssectrd
	def tsread(self):
		return self.stsread
	def wrcomp(self):
		return self.swrcomp
	def wrmerg(self):
		return self.swrmerg
	def sectwr(self):
		return self.ssectwr
	def tswrit(self):
		return self.stswrit
	def ioscur(self):
		return self.sioscur
	def tisdio(self):
		return self.stisdio
	def wtsdio(self):
		return self.swtsdio

class memoria(object):

	def __init__(self):
		self.total = None
		self.clear()

	def settotal(self, n):
		self.total = n

	def gettotal(self):
		return self.total

	def clear(self):
		self.mt = values()
		self.mf = values()
		self.bu = values()
		self.cc = values()
		self.sc = values()
		self.ac = values()
		self.ic = values()
		self.di = values()
		self.ap = values()
		self.sl = values()
		self.pt = values()
		self.vm = values()
		self.ca = values()
		self.cl = values()
		self.ht = values()
		self.hf = values()
		self.hr = values()
		self.hs = values()
		self.wb = values()
		self.st = values()
		self.sf = values()
		self.cs = values()
		self.mp = values()

	def memtotal(self):
		return self.mt
	def memfree(self):
		return self.mf
	def buffers(self):
		return self.bu
	def cached(self):
		return self.ca
	def swapcached(self):
		return self.sc
	def active(self):
		return self.ac
	def inactive(self):
		return self.ic
	def dirty(self):
		return self.di
	def anonpages(self):
		return self.ap
	def slab(self):
		return self.sl
	def pagetables(self):
		return self.pt
	def vmallocused(self):
		return self.vm
	def committedas(self):
		return self.cs
	def commitlimit(self):
		return self.cl
	def hugetotal(self):
		return self.ht
	def hugefree(self):
		return self.hf
	def hugersvd(self):
		return self.hr
	def hugesurp(self):
		return self.hs
	def writeback(self):
		return self.wb
	def swaptotal(self):
		return self.st
	def swapfree(self):
		return self.sf
	def mapped(self):
		return self.mp

class servidor(object):

	def __init__(self):
		self.str = ""
		self.cs = values()
		self.ds = values()
		self.dk = values()
		self.me = memoria()

	def setname(self, s):
		self.str = s

	def getname(self):
		return self.str

	def dias(self):
		return self.ds

	def cpus(self):
		return self.cs

	def disks(self):
		return self.dk

	def mem(self):
		return self.me



#
# support functions
#

# unix time in seconds
def unix_time(dt):
	epoch = datetime.utcfromtimestamp(0)
	tzbr = pytz.timezone("America/Sao_Paulo")
	tzutc = pytz.timezone("UTC")
	dt = tzbr.localize(dt)
	epoch = tzutc.localize(epoch)
	delta = dt - epoch
	return delta.total_seconds()

# unix time in ms
def unix_time_ms(dt):
    return unix_time(dt) * 1000.0

#
# database functions
#

# mysql connection

class mydata(object):

	def __init__(self, database):

		self.con = mdb.connect('localhost', 'inerddy', '', database)
		self.cur = self.con.cursor(mdb.cursors.DictCursor)

	def query(self, query):

		self.cur.execute(query)

	def __iter__(self):

		for i in range(self.cur.rowcount):
			yield self.cur.fetchone()

