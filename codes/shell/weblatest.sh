#!/bin/bash

MAINDIR="/var/www/html"


getout() {
    echo ERROR: $@
    exit 1
}

[ ! -d $MAINDIR ] && getout "no maindir found"

OLDDIR=$PWD
cd $MAINDIR

[ ! -d latest ] && mkdir latest
rm -rf latest/*


for arch in $(ls -1 archs); do

    mkdir latest/$arch

    firstrun=0

    for pkg in $(ls archs/$arch | grep -v kselftest); do

        mkdir latest/$arch/$pkg

        deb=$(ls -t1 archs/$arch/$pkg/*.deb 2>/dev/null | sort -u | tail -1)
        rpm=$(ls -t1 archs/$arch/$pkg/*.rpm 2>/dev/null | sort -u | tail -1)
        txz=$(ls -t1 archs/$arch/$pkg/*.txz 2>/dev/null | sort -u | tail -1)

        [ $deb ] && ln -s ../../../$deb ./latest/$arch/$pkg/$(basename $deb)
        [ $rpm ] && ln -s ../../../$rpm ./latest/$arch/$pkg/$(basename $rpm)
        [ $txz ] && ln -s ../../../$txz ./latest/$arch/$pkg/$(basename $txz)

        PKGS=""
        PKGS+="$(ls -1t archs/$arch/kselftest/*v4.17*.txz | sort -u | tail -1) "
        PKGS+="$(ls -1t archs/$arch/kselftest/*v4.18.*.txz | sort -u | tail -1) "
        PKGS+="$(ls -1t archs/$arch/kselftest/*v4.19.*.txz | sort -u | tail -1) "
        PKGS+="$(ls -1t archs/$arch/kselftest/*v4.19-*.txz | sort -u | tail -1) "
        PKGS+="$(ls -1t archs/$arch/kselftest/*v4.14.*.txz | sort -u | tail -1) "
        PKGS+="$(ls -1t archs/$arch/kselftest/*next-*.txz | sort -u | tail -1) "

        if [ $firstrun -eq 1 ]; then continue; fi

        firstrun=1

        mkdir latest/$arch/kselftest

        for pkg in $PKGS; do

            txz=$pkg
            rpm=${pkg/\.txz/\.rpm}
            deb=${pkg/\.txz/\.deb}

            [ $deb ] && ln -s ../../../$deb ./latest/$arch/kselftest/$(basename $deb)
            [ $rpm ] && ln -s ../../../$rpm ./latest/$arch/kselftest/$(basename $rpm)
            [ $txz ] && ln -s ../../../$txz ./latest/$arch/kselftest/$(basename $txz)
        done

    done
done

