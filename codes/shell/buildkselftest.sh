#!/bin/bash

#
# this script builds kselftest using this repo's dir structure
#

CHOICE=$(echo $1 | sed 's:/$::')

OLDDIR=$PWD
FILEDIR="$HOME/work/files"
MAINDIR="$HOME/work/sources/linux"
TEMPDIR="/tmp/$$"

NCPU=$(nproc)
MYARCH=$(dpkg-architecture -qDEB_BUILD_ARCH)

# FUNCTIONS

getout() {
    echo ERROR: $@
    exit 1
}

getoutlockup() {
    lockup
    getout $@
}

destroytmp() {
    [ -d $TEMPDIR ] && sudo umount $TEMPDIR && sudo rmdir $TEMPDIR || \
        { rm -f $LOCKFILE ; getout "could not umount temp dir"; }
}

createtmp() {
    sudo mkdir $TEMPDIR || { rm -f $LOCKFILE ; getout "could not create temp dir"; }
    sudo mount -t tmpfs -o size=1G tmpfs $TEMPDIR || { rm -f $LOCKFILE ; getout "could not mount temp dir"; }
    sudo chown -R $USER $TEMPDIR
}

cleantmp() {
    WHEREAMI=$PWD
    cd $OLDDIR
    destroytmp
    createtmp
    cd $WHEREAMI
}

ctrlc() {
    [ -d $TEMPDIR ] && sudo umount $TEMPDIR 2>&1 > /dev/null 2>&1
}

gitclean() {
    find . -name *.orig -exec rm {} \;
    find . -name *.rej -exec rm {} \;
    git clean -fd 2>&1 > /dev/null
    git reset --hard 2>&1 > /dev/null
}

# LOCKS

i=0
lockdown() {
    # totally racy locking function

    while true; do
        if [ ! -f $LOCKFILE ]; then
            echo $$ > $LOCKFILE
            sync
            break
        fi

        echo "trying to acquire the lock"

        # TIMEOUT: 10 mins

        sleep 5
        i=$((i+5))
        if [ $i -eq 600 ]; then
            echo "could not obtain the lock, exiting"
            exit 1
        fi
    done
}

lockup() {
    rm -f $LOCKFILE
    sync
}

# COMPILE FLAGS

COMPILE="make V=1 -j$NCPU"

# PACKAGE WILL BE PLACED

TARGET="$HOME/work/pkgs/$MYARCH/kselftest"
[ ! -d $TARGET ] && mkdir -p $TARGET

# BEGIN

trap "ctrlc" 2
createtmp

cd $MAINDIR

[ ! -d $FILEDIR ] && getout "FILEDIR: something went wrong"

# don't include stable-rc automatically

if [ "$CHOICE" == "" ]; then
    DIRS=$(find . -maxdepth 4 -iregex .*/.git -not -iregex .*stable-rc/stable-rc.* | sed 's:\./::g' | sed 's:/.git::g')
else
    DIRS=$(find . -maxdepth 4 -iregex .*/.git | sed 's:\./::g' | sed 's:/.git::g')
fi

# iterate all dirs

for dir in $DIRS; do

    basedir=$(basename $dir)

    [ ! -d $dir ] && getout "ERROR: $dir is not a dir ?"

    [ ! -e $dir/.git ] && getout "ERROR: $dir/.git does not exist ?"

    [ $CHOICE ] && [ ! "$dir" == "$CHOICE" ] && continue;

    OLDDIR=$(pwd)

    LOCKFILE="$dir/.local.lock"

    lockdown
    cd $dir
    echo ++++++++ ENTERING $dir ...

    gitclean

    DESCRIBE=$(git describe --long)

    # kselftests generation

    # examples:
    #
    # $COMPILE -C tools clean
    # $COMPILE -C tools gpio
    # $COMPILE -C tools selftests
    # $COMPILE -C tools/testing/selftests TARGETS=gpio all
    # $COMPILE -C tools/testing/selftests TARGETS=zram all
    # $COMPILE -C tools/testing/selftests clean

    if [ ! -f $TARGET/kselftest-$DESCRIBE-$MYARCH.txz ]; then

        # generating a new .txz file

        echo "INFO: kselftest $DESCRIBE-$MYARCH being generated."

        $COMPILE -C tools clean
        CFLAGS="-fPIC" $COMPILE -C tools/testing/selftests all
        RET=$?

        # TODO: check for compilation errors

        if [ $RET -eq 0 ]; then
            tar cfJ $TARGET/kselftest-$DESCRIBE-$MYARCH.txz ./tools
            ls $TARGET/kselftest-$DESCRIBE-$MYARCH.txz
            [ ! -f $TARGET/kselftest-$DESCRIBE-$MYARCH.txz ] && echo "ERROR: kselftest $DESCRIBE-$MYARCH not created."
        else
            echo "ERROR: kselftest $DESCRIBE-$MYARCH could not be compiled."
        fi

        gitclean
    else
        # no need to re-generate

        echo "INFO: kselftest-$DESCRIBE-$MYARCH already exists"
    fi

    echo -------- CLOSING $dir
    cd $OLDDIR
    lockup

    cleantmp
done

cd $OLDDIR
destroytmp
lockup
exit 0
