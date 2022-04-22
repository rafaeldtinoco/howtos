#!/bin/bash

URL="http://files.kernelpath.com:8080/latest/"

usage() {
    echo "usage:"
    echo
    echo "$0 -h | [1] [2] [3] [4] [5]"
    echo
    echo "[1] = get | install"
    echo "[2] = kselftest | ltp | libhugetlbfs"
    echo "[3] = armhf | arm64 | i386 | amd64"
    echo "[4] = rpm | deb | txz"
    echo "[5] = args"
    echo ""
    echo "[5] (kselftest): stable-4.14 | stable-4.17 stable-4.18 stable-4.19 mainline next"
    echo ""
    echo "examples:"
    echo
    echo "$0 get ltp armhf deb"
    echo "$0 get libhugetlb amd64 rpm"
    echo "$0 get kselftest i386 txz stable-4.19"
    exit 0
}

if [ "$1" == "-h" ]; then
    usage
fi

cmd=$1
pkg=$2
arch=$3
tipo=$4
kver=$5

[ "$cmd" != "get" ] && [ "$cmd" != "install" ] && usage
[ "$pkg" != "kselftest" ] && [ "$pkg" != "ltp" ] && [ "$pkg" != "libhugetlbfs" ] && usage
[ "$arch" != "armhf" ] && [ "$arch" != "arm64" ] && [ "$arch" != "i386" ] && [ "$arch" != "amd64" ] && usage
[ "$tipo" != "deb" ] && [ "$tipo" != "rpm" ] && [ "$tipo" != "txz" ] && usage

[ "$pkg" == "kselftest" ] && [ "$kver" != "stable-4.14" ] && \
    [ "$kver" != "stable-4.17" ] && [ "$kver" != "stable-4.18" ] && \
    [ "$kver" != "stable-4.19" ] && [ "$kver" != "mainline" ] && \
    [ "$kver" != "next" ] && usage

URL="$URL/$arch/$pkg"

if [ "$pkg" != "kselftest" ]; then

    # all packages

    PKG=$(w3m -dump $URL | grep ".$tipo " | awk '{print $1}' | sed 's: ::g')

    [ "$PKG" == "" ] && { echo "error: could not find package :\\"; exit 1; }

    if [ "$cmd" == "get" ]; then

        echo -n "downloading $PKG... "
        wget --quiet $URL/$PKG
        echo "complete!"

    elif [ "$cmd" == "install" ]; then
        echo "cmd: $cmd not implemented yet =)"
        exit 1
    fi

else

    # kselftest

    [ "$kver" == "stable-4.14" ] && kverstr="v4\.14\."
    [ "$kver" == "stable-4.17" ] && kverstr="v4\.17\."
    [ "$kver" == "stable-4.18" ] && kverstr="v4\.18\."
    [ "$kver" == "stable-4.19" ] && kverstr="v4\.19\."
    [ "$kver" == "mainline" ] && kverstr="v4\.19-"
    [ "$kver" == "next" ] && kverstr="-next-"

    PKG=$(w3m -dump $URL | awk '{print $1}' | grep $tipo | grep $arch | grep $kverstr)

    [ "$PKG" == "" ] && { echo "error: could not find package :\\"; exit 1; }

    if [ "$cmd" == "get" ]; then

        echo -n "downloading $PKG... "
        wget --quiet $URL/$PKG
        echo "complete!"

    elif [ "$cmd" == "install" ]; then
        echo "cmd: $cmd not implemented yet =)"
        exit 1
    fi
fi

exit 0
