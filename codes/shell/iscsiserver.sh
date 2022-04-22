#!/bin/bash

# Script to configure an iSCSI server
# Author: Rafael David Tinoco <rafael.tinoco@canonical.com>
# Copyright: Who Cares Inc. 2016
#
# Usage:
# $0 [show]    - show all targets and luns created
# $0 [install] - install tgt daemon
# $0 [prepare] - create backend luns
# $0 [clear]   - delete backend luns
# $0 [create]  - create all targets and luns
# $0 [destroy] - destroy all luns and targets
#
# Obs: Always run [prepare] before [create].
#

NRLUNS=5					# 1 LUN per TARGET
LUNSIZE=500				    # How many MBs
LUNPLACE="/iscsi"		    # Where to place the LUN file

# NO MORE CHANGES vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

if [ "$1" == "help" ] || [ "$1" == "" ]; then

cat<<EOF

Usage:
$0 [show]    - show all targets and luns created
$0 [install] - install tgt daemon
$0 [prepare] - create backend luns
$0 [clear]   - delete backend luns
$0 [create]  - create all targets and luns
$0 [destroy] - destroy all luns and targets

Obs: Always run [prepare] before [create].

EOF

fi

if [ "$1" == "show" ]; then
    sudo tgtadm --lld iscsi --op show --mode target | grep Target
fi


if [ "$1" == "install" ]; then
    sudo apt-get install tgt
fi

if [ "$1" == "clear" ]; then
    for nr in `seq 1 $NRLUNS`; do
	sudo rm -rf $LUNPLACE/tid$nr-lun
    done
fi

if [ "$1" == "prepare" ]; then
    for nr in `seq 1 $NRLUNS`; do
	sudo rm -rf $LUNPLACE/tid$nr-lun
	sudo dd if=/dev/zero bs=1M seek=$LUNSIZE count=0 of=/$LUNPLACE/tid$nr-lun
    done
fi

if [ "$1" == "create" ]; then

    for nr in `seq 1 $NRLUNS`; do
	if [ -f "$LUNPLACE/tid$nr-lun" ]; then
	    sudo tgtadm --lld iscsi --op new --mode target --tid $nr -T iqn.2017.tgtd:tid$nr.lun
	    sudo tgtadm --lld iscsi --op new --mode logicalunit --tid $nr --lun 1 -b $LUNPLACE/tid$nr-lun
	    sudo tgtadm --lld iscsi --op bind --mode target --tid $nr -I ALL
	else
	    echo "you should \"prepare\" before trying to create"
	    exit 1
	fi
    done

fi

if [ "$1" == "destroy" ]; then

    for nr in `seq 1 $NRLUNS`; do
	sudo tgtadm --lld iscsi --op unbind --mode target --tid $nr -I ALL
	sudo tgtadm --lld iscsi --op delete --mode logicalunit --tid $nr --lun 1
	sudo tgtadm --lld iscsi --op delete --mode target --tid $nr
    done

fi
