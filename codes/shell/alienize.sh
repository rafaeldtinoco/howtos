#!/bin/bash

#
# this script generates rpm and tgz pkgs from deb ones
#

# global to host since only host should run this script
# WARN: dont run this script inside containers

OLDDIR=$PWD
MAINDIR="$HOME/work/pkgs"
LOCKFILE=/tmp/.alienize.lock
TEMPDIR="/tmp/$$"
USER=inaddy # $USER is having problems w/ cron

PATH=$PATH:/usr/local/bin:/usr/local/sbin
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

#
# functions
#

getout() {
    echo ERROR: $@
    exit 1
}

destroytmp() {
    [ -d $TEMPDIR ] && sudo umount $TEMPDIR && sudo rmdir $TEMPDIR || \
        { rm $LOCKFILE ; getout "could not umount temp dir"; }
}

createtmp() {
    sudo mkdir $TEMPDIR || { rm $LOCKFILE ; getout "could not create temp dir"; }
    sudo mount -t tmpfs -o size=3G tmpfs $TEMPDIR || { rm $LOCKFILE ; getout "could not mount temp dir"; }
    sudo chown -R $USER $TEMPDIR
    sync
}

cleantmp() {
    WHEREAMI=$PWD
    cd $OLDDIR
    destroytmp
    createtmp
    cd $WHEREAMI
    sync
}

ctrlc() {
    [ -d $TEMPDIR ] && sudo umount $TEMPDIR 2>&1 > /dev/null 2>&1
    lockup
    exit 1
}

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

        # wait a bit for the lock
        # WARN: cron should not be less than 120 sec

        sleep 5
        i=$((i+5))
        if [ $i -eq 60 ]; then
            echo "could not obtain the lock, exiting"
            exit 1
        fi

    done
}

lockup() {
    rm -f $LOCKFILE
    sync
}

#
# begin
#

lockdown
trap "ctrlc" 2

# check existing .deb files and see if associated .tgz and .rpm exist
# if not, convert .deb files using alien tool

createtmp
cd $TEMPDIR

for arch in $(ls -1 $MAINDIR); do

    for pkg in $(ls -1 $MAINDIR/$arch); do

        if [ "$pkg" == "kselftest" ]; then

            for txz in $(ls -1 $MAINDIR/$arch/kselftest/*.txz 2> /dev/null); do

                filename=${txz/\.txz}
                rpm=$filename.rpm
                deb=$filename.deb

                #
                # get info from package using filename
                #

                package="kselftest"
                #version=$(echo $filename | cut -d'-' -f2,3,4 | sed 's:^v::g')
                #architecture=$(echo $filename | cut -d'-' -f5)
                version=$(echo $(basename $filename) | sed -E 's:kselftest-(.*)-(amd64|armhf|arm64|i686):\1:g')
                version=$(echo $version | sed -E 's:^[a-z]+-::g' | sed -E 's:^[a-z]::g')
                architecture=$(echo $(basename $filename) | sed -E 's:^.*-(amd64|armhf|arm64|i686):\1:')

                if [ "$architecture" == "amd64" ]; then
                    altarch="x86_64"
                elif [ "$architecture" == "arm64" ]; then
                    altarch="aarch64"
                elif [ "$architecture" == "armhf" ]; then
                    altarch="armhfp"
                elif [ "$architecture" == "i386" ]; then
                    altarch="i386"
                fi

                echo $deb being checked...

                # deb

                if [ ! -f $deb ]; then
                    echo $deb being generated...
                    sudo tar xfJ $txz .
                    sudo fpm -t deb -s dir -n $package -v "$version" -a $architecture --prefix=/opt .
                    tempfile=$(ls -1 *.deb 2>/dev/null) && {
                        mv $tempfile $deb
                        sudo rm -rf tools
                        sudo chown $USER $deb
                    } || echo "file $txz was not converted to deb!"

                    cleantmp
                else
                    echo $deb already generated!
                fi

                # deb

                if [ ! -f $rpm ]; then
                    echo $rpm being generated...
                    sudo tar xfJ $txz .
                    sudo fpm -t rpm -s dir -n $package --rpm-compression xz -v "$version" -a $altarch --prefix=/opt .
                    tempfile=$(ls -1 *.rpm 2>/dev/null) && {
                        mv $tempfile $rpm
                        sudo rm -rf tools
                        sudo chown $USER $rpm
                    } || echo "file $txz was not converted to rpm!"

                    cleantmp
                else
                    echo $rpm already generated!
                fi

            done

            continue;
        fi

        #
        # for each existing .deb package
        #

        for deb in $(ls -1 $MAINDIR/$arch/$pkg/*.deb 2> /dev/null); do

            filename=${deb/\.deb}
            rpm=$filename.rpm
            txz=$filename.txz

            #
            # query info from .deb package
            #

            package=$(dpkg-deb -f $deb Package)
            version=$(dpkg-deb -f $deb Version)
            architecture=$(dpkg-deb -f $deb Architecture)

            if [ "$architecture" == "amd64" ]; then
                altarch="x86_64"
            elif [ "$architecture" == "arm64" ]; then
                altarch="aarch64"
            elif [ "$architecture" == "armhf" ]; then
                altarch="armhfp"
            elif [ "$architecture" == "i386" ]; then
                altarch="i386"
            fi

            # debug:
            #
            # echo $filename
            # echo $package
            # echo $version
            # echo $architecture

            echo $deb being checked...

            # txz

            if [ ! -f $txz ]; then
                echo $txz being generated...
                sudo dpkg -x $deb .
                sudo fpm -C $TEMPDIR -s dir -t tar -n $package .
                tempfile=$(ls -1 *.tar 2>/dev/null) && {
                    sudo tar cvfJ $filename.txz $tempfile
                    sudo rm $tempfile
                    sudo chown $USER $filename.txz
                } || echo "file $deb was not converted to txz!"

                cleantmp
            else
                echo $txz already generated!
            fi

            # rpm

            if [ ! -f $rpm ]; then
                echo $rpm being generated...
                dpkg -x $deb .
                sudo fpm -C $TEMPDIR -s dir -t rpm -n $package --rpm-compression xz -v $version -a $altarch .
                tempfile=$(ls -1 *.rpm 2>/dev/null) && {
                    sudo mv $tempfile $filename.rpm;
                    sudo chown $USER $filename.rpm
                } || echo "file $deb was not converted to rpm!"

                cleantmp
            else
                echo $rpm already generated!
            fi

        done
    done
done

cd $OLDDIR
destroytmp
lockup
exit 0
