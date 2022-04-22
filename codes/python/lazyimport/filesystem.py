from defines import *
from base import *
from files import *
from os import *

#
# BASE FILESYSTEM
#

class base():

    def __init__(self, maindir, tempdir):

        self.maindir = maindir
        self.tempdir = tempdir
        self.files = self._files()

    # iterate tods over all possible base dirs (short, medium, long)

    def __iter__(self):

        # for dirtype in (bdir_short, bdir_medium, bdir_long):
        # for dirtype in ([bdir_long]):
        for dirtype in ([bdir_medium]):
            yield self._base(dirtype, self.maindir, self.tempdir)

    # return existent files on a base directory

    def _files(self):

        files = {}

        for something in os.listdir(self.maindir):

            if os.path.isfile(self.maindir + something):
                files[something] = self.maindir + something

        return files

    # return a base filename's full path

    def file(self, filename):
        return self.files[filename]

    # internal class to abstract ziped tod files and
    # make them iterable (extracting them before yielding)
    # and cleaning after used

    class _base():

        def __init__(self, dirtype, maindir, tempdir):

            self.maindir = maindir
            self.tempdir = tempdir
            self.dirtype = dirtype
            self.files = self._files()

        # get all ziped (.tar.gz or .zip) files inside a tod directory

        def _files(self):

            files = []

            for something in os.listdir(self.maindir + self.dirtype):
                if os.path.isfile(self.maindir + self.dirtype + something):
                    if something[-3:] == "zip" or something[-6:] == "tar.gz":
                        files.append(something)

            return files

        # iterate over all tod files, moving them to temporary dir,
        # extracting them, creating an object describing them and
        # cleaning them at the end

        def __iter__(self):

            for file in self.files:

                zfile = workfile(file, self.maindir + self.dirtype, self.tempdir)
                zfile.move()
                yield tod(zfile.getworkdir())
                zfile.erase()
                zfile.ok()

        def gettype(self):
            return self.dirtype

#
# GLOBAL DIRECTORY (1 TOD INTERVAL)
#

class tod():

    def __init__(self, workdir):

        self.workdir = workdir
        self.dirs = self._dirs()
        self.files = self._files()
        self.nfiles = self._nfiles()

    # iterate over all processes directories creating objects describing them

    def __iter__(self):

        for procdir in self.dirs:
            yield proc(self.workdir + procdir + "/")

    # all dirs inside timestamp work directory

    def _dirs(self):

        dirs = []

        for something in os.listdir(self.workdir):
            if os.path.isdir(self.workdir + something):
                if "net" not in something:
                    dirs.append(something)

        return dirs

    # all files inside timestamp work directory

    def _files(self):

        files = {}

        for something in os.listdir(self.workdir):
            if os.path.isfile(self.workdir + something):
                files[something] = self.workdir + something

        return files

    # all files inside timestamp network work directory

    def _nfiles(self):

        nfiles = {}
        ndir = self.workdir + "net/"

        for something in os.listdir(ndir):
            if os.path.isfile(ndir + something):
                nfiles[something] = ndir + something

        return nfiles

    # return workdir (tempdir + tod directory)

    def pwd(self):
        return self.workdir

    # return global file

    def file(self, filename):
        return self.files[filename]

    # return network file

    def nfile(self, filename):
        return self.nfiles[filename]

#
# LOCAL DIRECTORY (1 PROCESS OR TASK)
#

class proc():

    def __init__(self, procdir):

        arr = procdir.split("/")
        self.myproc = arr[-2]
        # print self.myproc

        self.procdir = procdir
        self.dirs = self._dirs()
        self.files = self._files()

    # iterate over all thread dirs inside this process working directory

    def __iter__(self):

        if self.dirs is None: raise StopIteration

        for procdir in self.dirs:
            if procdir not in self.myproc:
                yield proc(self.procdir + "task/" + procdir + "/")

    # all thread directories inside this process working directory

    def _dirs(self):

        dirs = []

        if not os.path.isdir(self.procdir + "task/"): return

        for something in os.listdir(self.procdir + "task/"):
            if os.path.isdir(self.procdir + "task/" + something):
                    dirs.append(something)

        return dirs

    # all files inside this process working directory

    def _files(self):

        files = {}

        for something in os.listdir(self.procdir):
            if os.path.isfile(self.procdir + something):
                files[something] = self.procdir + something

        return files

    # this process working directory

    def pwd(self):
        return self.procdir

    # return local file

    def file(self, filename):

        try:
            return self.files[filename]

        except:
            raise Exception("!! {}/{}".format(self.pwd(), filename))

