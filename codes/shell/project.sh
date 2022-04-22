#!/bin/bash

#
# this script creates .project and .cproject in directories
# to be opened as Makefile projects inside eclipse. it makes
# easier to open any source directory as a project
#

CHOICE=${1/\/}

OLDDIR=$PWD
MAINDIR=$(dirname $0)
[ "$MAINDIR" == "." ] && MAINDIR=$(pwd)

getout() {
    echo ERROR: $@
    exit 1
}

cd $MAINDIR

FILEDIR=$(pwd | sed 's:work/sources/.*:work/sources/../files/:g')
PROJECT=$FILEDIR/project
CPROJECT=$FILEDIR/cproject

[ ! -d $FILEDIR ] && getout something went wrong

DIRS=$(find . -maxdepth 2 -iregex .*/.git | sed 's:/.git::g')

for dir in $DIRS; do

    [ ! -d $dir ] && getout $dir is not a dir ?

    [ ! -e $dir/.git ] && getout $dir/.git does not exist ?

    basedir=$(basename $dir)

    [ $CHOICE ] && [ ! "$basedir" == "$CHOICE" ] && continue;

    cd $dir

    echo ++++++++ ENTERING $dir ...
    cp -v $PROJECT .project
    cp -v $CPROJECT .cproject
    sed -i -E "s:CHANGEME:$basedir:g" .project
    sed -i -E "s:CHANGEME:$basedir:g" .cproject
    echo -------- CLOSING $dir

    cd $MAINDIR

done

cd $OLDDIR
