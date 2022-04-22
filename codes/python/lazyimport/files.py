import zipfile
import tarfile
import os
import shutil

#
# text transformation
#

def clearspace(line):
    line = line.replace("     ", " ").replace("    ", " ").     \
                replace("   ", " ").replace("  ", " ").         \
                replace("\t", " ")
    return line

def clearchars(line, chars=[":", ","]):
    for char in chars:
        line = line.replace(char, " ")
    return line

def clearstrip(line):
    line = line.rstrip().lstrip()
    return line

def clearaspas(line):
    line = line.replace("\"", " ")
    line = line.replace("\'", " ")
    return line
#
# zipped files
#

class workfile():

    def __init__(self, filename, basedir, tempdir):

        self.filename = filename
        self.basedir = basedir
        self.tempdir = tempdir

    # copy from base to temp, unpack and remove packed file

    def move(self):

        # copy from base to temp
        # TODO: copy using rsync

        shutil.copyfile(self.basedir + self.filename, self.tempdir + self.filename)
        self.workdir  = ""
        os.chdir(self.tempdir)

        # for zip files copy & extract to temp

        if(self.filename[-3:] == "zip"):
            os.system("nice -20 unzip -qu " + self.filename)
            self.workdir = self.filename[:-4] + "/"

        # for tar files copy & extract to temp

        if(self.filename[-6:] == "tar.gz"):
            os.system("nice -20 tar xfzm " + self.filename)
            self.workdir = self.filename[:-7] + "/"

        # delete zip/tar file from temp

        if os.path.isfile(self.tempdir + self.filename):
            os.system("rm -rf " + self.tempdir + self.filename)

        os.system("sudo chmod -R 777 " + self.workdir)

    # return unpacked directory

    def getworkdir(self):
        return self.tempdir + self.workdir

    def ok(self):
        pass
        # os.rename(self.basedir + self.filename, self.basedir + self.filename + ".ok")

    def erase(self):
        dir_to_delete = self.tempdir + self.workdir
        if os.path.isdir(dir_to_delete) and self.tempdir in dir_to_delete:
            os.system("rm -rf " + dir_to_delete)

#
# parsing files
#

class file_line(object):

    # open file with filename and read it

    def __init__(self, filename):

        try:
             filed = open(filename)
             self.line = filed.read()

        except:
            raise Exception("!! error opening line file")

    # return pos in line array from spliting file with sep

    def get(self):
        return clearstrip(self.line)

    # def get(self, sep="", val=0):
    #     return clearstrip(self.line)

class file_keyvalue(object):

    # read all file creating key=value dictionary

    def __init__(self, filename, sep=":"):

        try:
            filed = open(filename)

        except:
            raise Exception("!! error opening keyvalue file")

        self.filekeys = {}

        for line in filed:

            if line == '\n': continue
            if not sep in line: continue

            try:
                key, sep, value = line.partition(sep)
                key = clearchars(key)
                key = clearspace(key)
                key = clearstrip(key)
                value = clearchars(value)
                value = clearspace(value)
                value = clearstrip(value)
                self.filekeys[key] = value
                # print "key = {}, value = {}".format(key, value)

            except:
                raise Exception("?? keyvalue file split error")

    # iterate through dictionary keys

    def __iter__(self):

        for key in self.filekeys:
            yield key

    # get values from keys, it is possible to split values

    def get(self, key, split="", pos=0, clean=""):

        # if not key in self.filekeys:
        #    raise Exception("no key")

        value = self.filekeys[key]

        if clean is not "":
            value = value.replace(clean, "")

        if split is not "":
            value = value.split(split)
            value = value[pos]

        return "".join(value)

        # if len(value) >= pos:
        #     return value[pos]
        # else:
        #     return value[0]

class file_matrix(object):

    # split all lines from file and put all into a list

    def __init__(self, filename, starts=None):

        self.filelines = []

        try:
            filed = open(filename)

        except:
            raise Exception("!! error opening matrix file")

        for line in filed:

            if not line: continue
            if line == "\n": continue
            if starts and not line.startswith(starts): continue

            line = clearchars(line)
            line = clearspace(line)
            line = clearstrip(line)
            self.filelines.append(line.split())

    # iterate over lists from bigger list

    def __iter__(self):
        for line in self.filelines:
            yield line

    # get me specific line containing

    # def getcontain(self):
    #     for l in self.filelines:
    #         if
    #     pass
