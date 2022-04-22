#!/bin/bash

#
# this script builds a debian package from upstream code
#

NCPU=$(nproc)
DEBARCH=$(dpkg-architecture -qDEB_BUILD_ARCH)

CHOICE=$(basename $1)
CHOICE2=$2

OLDDIR=$PWD
MAINDIR=$HOME/work/sources/trees/$CHOICE
DEBIANIZER="$HOME/work/sources/debianizer/"
DESTDIR="$HOME/work/pkgs"

# global (to machine) lock since this runs inside containers
# only one build (1 container) at a time, it uses all ncpu
# WARN: ONLY ONE BUILD at a time

LOCKFILE=$MAINDIR/../.lockfile

export DEBFULLNAME="Rafael David Tinoco"
export DEBEMAIL="rafael.tinoco@linaro.org"
export DEB_BUILD_OPTIONS="parallel=$NCPU nostrip noopt nocheck debug"

getoutlockup() {
    lockup
    getout $@
}

getout() {
    gitcleanup
    echo ERROR: $@
    exit 1
}

cleanout() {
    echo EXIT: $@
    exit 0
}

cleanoutlockup() {
    lockup
    echo EXIT: $@
    exit 0
}

gitcleanup() {
    cd $MAINDIR
    #git reset --hard
    #git clean -fd
    cat debian/changelog.initial > debian/changelog
}

# this is stupid, i know. will fix later
# for this a total racy impl just for testing

lockdown() {
    while true; do
        if [ ! -f $LOCKFILE ]; then
            echo $$ > $LOCKFILE
            sync
            break
        fi

        echo "trying to acquire the lock..."

        # WARN: wait for the lock
        # WARN: 900 second is the min cron interval

        sleep 15
        i=$((i+15))
        if [ $i -eq 900 ]; then
            echo "could not obtain the lock, exiting"
            exit 1
        fi

    done
}

lockup() {

    rm -f $LOCKFILE
    sync
}

lockdown

cd $MAINDIR

gitcleanup

# initial checks

[ ! -d .git ] && getoutlockup "not a git repo"
[ ! -s debian ] && ln -s $DEBIANIZER/$(basename $PWD) ./debian
[ ! -f debian/changelog.initial ] && getoutlockup "no initial changelog"

# checks

GITDESC=$(git describe --long | sed 's:^[a-zA-Z]*-::g')
[ $? != 0 ] && getoutlockup "git describe error"

WHERETO=$DESTDIR/$DEBARCH/$(basename $PWD)
[ ! -d $WHERETO ] && getoutlockup "dir $WHERETO not found"

# is it already built ?

FOUND=$(find $WHERETO -maxdepth 1 -name *$GITDESC*.deb | wc -l)
[ $FOUND -eq 1 ] && cleanoutlockup "already built";

# pkg cleaning

fakeroot debian/rules clean

# debian generic changelog file

dch -p -v "$GITDESC" -D unstable "Upstream commit $GITDESC"
sleep 3 ; sync
CHECKVER=$(head -1 debian/changelog | sed -E 's:.*\((.*)\).*:\1:g')
if [ $CHECKVER == "0.0" ]; then getoutlockup "changelog hasn't changed!"; fi
sync

# build debian package

#fakeroot debian/rules build
#fakeroot debian/rules install
fakeroot debian/rules binary

# BUG ? changelog not changed ? (race ?)
fileerror=$(find .. -maxdepth 1 -name *0.0*_$DEBARCH.deb)
[ $fileerror ] && { rm $fileerror ; getoutlockup "GOT A 0.0 package. changelog broken ?"; }

# debian package

mkdir -p $WHERETO
filename=$(find .. -maxdepth 1 -name *$GITDESC*_$DEBARCH.deb)
echo $filename
[ $filename ] && filename=$(basename $filename) || filename="nenenene"
echo $filename
find .. -maxdepth 1 -name $filename -exec mv {} $WHERETO/ \;

ls $WHERETO/$filename && {
        echo "$GITDESC generated"
        echo $GITDESC > $WHERETO/.gitdesc
    } || {
        echo "$GITDESC NOT generated"
        echo > $WHERETO/.gitdesc
    }

# clean debian/ and git repo

fakeroot debian/rules clean
gitcleanup
cd $OLDDIR
lockup
