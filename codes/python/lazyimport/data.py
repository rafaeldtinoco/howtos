# import zipfile
# import tarfile
# import os
# import shutil
# import gzip
# from defines import *
#
# import sys
# import inspect
# import traceback
# import _mysql

from defines import *

import _mysql
import MySQLdb

def dbstart():

    con = _mysql.connect('localhost', 'inerddy', 'pass', 'medium')

    # for name in [ "cpu", "disk", "domain", "gcpu", "gdisk", "gicmp", "gip" ,
    #               "gipstat", "girq", "gmem", "gnet", "gpage", "gschedc" ,
    #               "gschedd", "gsirq", "gsocket", "gtcp", "gtcpstat", "gudp" ,
    #               "gvm", "irq", "net", "server", "sirq", "task", "tcpu" ,
    #               "tdisk", "time", "tmem", "tsched", "user" ]:

    #     con.query("delete from {} where 1".format(name))

    return con

def dbinsert(table, dictionary, id=""):

    query = "INSERT INTO " + table + "("

    for key in dictionary:
        if key.startswith('p_'): continue
        query = query + key + ","

    query = query[:-1] + ") VALUES ("

    for key, value in dictionary.iteritems():
        if key.startswith('p_'): continue
        query = query + "\"" + value + "\","

    query = query[:-1] + ") "

    if id is not "":
        query = query + "ON DUPLICATE KEY UPDATE " + id + "=LAST_INSERT_ID(" + id + ");"

    return query

def dbupdate(table, dictwhere, dictionary):

    query = "UPDATE " + table + " set "

    for key, value in dictionary.iteritems():
        query = query + "{} = {}, ".format(key, value)

    query = query[:-2] + " WHERE "

    for key, value in dictwhere.iteritems():
        query = query + "{} = {} AND ".format(key, value)

    query = query[:-4]

    return query

def dblastid(con):
    return str(con.insert_id())

def dbquery(con, string):

    try:
        con.query(string)

    except MySQLdb.IntegrityError, i:
        print "!! duplicate: {}".format(string)

    except Exception, e:
        # print string
        print "!! sql error: {}".format(e)
