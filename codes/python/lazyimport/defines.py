import hashlib

from contextlib import contextmanager
from traceback import print_exception
from sys import exc_info
from files import *

taskhashs = set()

def md5(lines):

    m = hashlib.md5()

    for line in lines:
        m.update(line)

    val = str(m.hexdigest())
    "".join(i for i in val if i in "0123456789")

    return val

def case(x):
    return {
            'Jan' : '01',
            'Feb' : '02',
            'Mar' : '03',
            'Apr' : '04',
            'May' : '05',
            'Jun' : '06',
            'Jul' : '07',
            'Aug' : '08',
            'Sep' : '09',
            'Oct' : '10',
            'Nov' : '11',
            'Dec' : '12',
            }.get(x)

def getdate(var):

    var = clearspace(var)
    val = var.split(" ")
    date = "{}-{}-{} {}".format(val[5], case(val[1]), val[2], val[3])
    print date
    return date

def gettimestamp(var):

    val = var.split(" ")
    date = "{}{}{}{}".format(val[5], case(val[1]), val[2], val[3].replace(":", ""))
    return date

@contextmanager
def ignored():

    try:
        yield

    except:
        pass

@contextmanager
def verboseignored():
    try:
        yield

    except Exception, e:
        if str(e) or str(e) is not "":
            print str(e)

        return

@contextmanager
def notignored():

    try:
        yield

    except Exception, e:
        exc_type, exc_value, exc_tb = exc_info()
        print_exception(exc_type, exc_value, exc_tb)

	if str(e) or str(e) is not "":
	    print str(e)
        exit()

def_maindir = "/home/rafael/codes/workspace/example/"
def_tempdir = "/ramdisk/"

bdir_short = "short/"
bdir_medium = "medium/"
bdir_long = "long/"
