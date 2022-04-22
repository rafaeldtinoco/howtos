#!/usr/bin/python3 -B

import logging, sys
import subprocess

def inicio(debug=False):
    if debug is True:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def executa(cmd):
    args = []
    for word in [x.strip() for x in cmd.split(" \"")]:
        if not "\"" in word:
            for x in word.split(" "):
                if len(x) > 0:
                    args.append(x)
        else:
            rest = word.split("\"")
            args.append(rest[0])
            for x in rest[1].strip().split(" "):
                args.append(x)

    logging.debug("EXEC: %s" % args)

    proc = subprocess.Popen(args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True,
                            shell=False)
    try:
        outs, errs = proc.communicate(timeout=600)
        outs = outs[:-1]
        errs = errs[:-1]
        if len(outs) != 0:
            logging.debug("OUT: %s" % outs)
        if len(errs) != 0:
            logging.debug("ERR: %s" % errs)
        return outs

    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
        logging.debug("EXEC: TIMEOUT")
        if len(errs) != 0:
            logging.debug("ERR: %s" % errs)
        return errs

def executalxc(container, cmd):
    args = "lxc exec %s -- %s" % (container, cmd)
    logging.debug("LXC: %s" % args)
    return executa(args)

def transferlxc(container, fname, dname, fmode=None, uid=-1, gid=-1):
    cmd = "lxc file push %s %s%s" % (fname, container, dname)

    fmodestr = ""
    uidstr = ""
    gidstr = ""

    if (fmode):
        fmodestr = "--mode=%s" % fmode
    if (uid >= 0):
        uidstr = "--uid=%s" % uid
    if (gid >=0):
        gidstr = "--gid=%s" % gid

    cmdbegin = "lxc file push"
    cmdend = "%s %s%s" % (fname, container, dname)
    cmd = "%s %s %s %s %s" % (cmdbegin, uidstr, gidstr, fmodestr, cmdend)
    logging.debug("LXC: %s" % cmd)

    return executa(cmd)
