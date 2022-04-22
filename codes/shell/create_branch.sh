#!/bin/bash

#
# initializes the git submodule based on the 1_<DIR> file
# found in <DIR>. contents describe the submodules to be
# initialized. this has to be done mainly for those submodules
# that were never added to .gitmodules
#
# special: this initializes specific branch
#

OLDDIR=$PWD
MAINDIR=$(dirname $0)

getout() {
    echo ERROR: $@
    exit 1
}

gitclone() {
    name=$1
    url=$2
    branch=$3

    echo ====
    echo CLONING: $1

    git clone $url -b $branch $name --single-branch
}

cd $MAINDIR

FILE=$(ls -1 1_* | head -1)

[ ! -f $FILE ] && getout no trees file found

while read name url branch
do
    [ -d $name ] && continue
    gitclone $name $url $branch

done < $FILE

cd $OLDDIR
