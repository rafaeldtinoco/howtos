#!/bin/bash

#
# this script updates the git submodules (directories) inside
# a specific directory. without arguments it updates all dirs
#

CHOICE=$(echo $1 | sed 's:/$::')

OLDDIR=$PWD
MAINDIR=$PWD

LOCKFILE=$MAINDIR/.lockfile

#
# FUNCTIONS
#

getout() {
    echo ERROR: $@
    exit 1
}

gitclean() {
    find . -name *.orig -exec rm {} \;
    find . -name *.rej -exec rm {} \;
    git clean -f 2>&1 > /dev/null
    git reset --hard 2>&1 > /dev/null
}

lockdown() {
    while true; do

        if [ ! -f $LOCKFILE ]; then
            echo $$ > $LOCKFILE
            sync
            break
        fi

        echo "trying to acquire $LOCKFILE"

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

# BEGIN

lockdown

cd $MAINDIR

[ ! -d $FILEDIR ] && getout something went wrong

DIRS=$(find . -maxdepth 4 -iregex .*/.git | grep -v mine | sed 's:\./::g' | sed 's:/.git::g')

for dir in $DIRS; do

    basedir=$(basename $dir)

    [ ! -d $dir ] && getout $dir is not a dir ?

    [ ! -e $dir/.git ] && getout $dir/.git does not exist ?

    [ $CHOICE ] && [ ! "$dir" == "$CHOICE" ] && continue;

    OLDDIR=$(pwd)

    cd $dir

    echo ++++++++ ENTERING $dir ...

    echo "# $dir"

    git branch | grep -q "HEAD detached" && {
        echo CHECK THIS MANUALLY
        cd $OLDDIR
        continue
    }

    gitclean
    git fetch -a 2>&1 | grep -v "redirecting to"
    BRANCH=$(git branch | grep "*" | sed 's:* ::g')
    git reset --hard origin/$BRANCH
    echo -------- CLOSING $dir

    cd $OLDDIR

done

#cd $OLDDIR

lockup
