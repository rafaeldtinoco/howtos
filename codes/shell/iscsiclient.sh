#!/bin/bash

# Script to configure an iSCSI client
# Author: Rafael David Tinoco <rafael.tinoco@canonical.com>
# Copyright: Who Cares Inc. 2016
#
# Usage:
# $0 [show]    - show all configured luns
# $0 [install] - install open-iscsi-utils
# $0 [new]     - discover new luns
# $0 [login]   - create new luns
# $0 [logout]  - remove created luns
# $0 [destroy] - clear discovered luns
#
# Obs: Always run [prepare] before [create].
#

SERVER1="192.168.49.23"
SERVER2=""

#ETH1="eth0"
#ETH2="eth2"

#ETH1_IP=`ip addr show dev $ETH1 primary | grep "inet " | awk '{print $2}' | cut -d'/' -f1`
#ETH2_IP=`ip addr show dev $ETH2 primary | grep "inet " | awk '{print $2}' | cut -d'/' -f1`

if [ "$1" == "help" ] || [ "$1" == "" ]; then

cat<<EOF
Usage:
$0 [show]    - show all configured luns
$0 [details] - show iSCSI details
$0 [install] - install open-iscsi-utils
$0 [new]     - discover new luns
$0 [login]   - create new luns
$0 [logout]  - remove created luns
$0 [destroy] - clear discovered luns

Obs: Always run [new] before [login].

EOF

fi

if [ "$1" == "show" ]; then
    sudo iscsiadm -m session
fi

if [ "$1" == "details" ]; then
    sudo iscsiadm -m session -P 1
fi

if [ "$1" == "details2" ]; then
    sudo iscsiadm -m session -P 2
fi

if [ "$1" == "details3" ]; then
    sudo iscsiadm -m session -P 3
fi

if [ "$1" == "install" ]; then
    sudo apt-get install open-iscsi-utils
fi

if [ "$1" == "new" ]; then
	if [ "$SERVER1" != "" ]; then
		sudo iscsiadm -m discovery --op=new --op=del --type sendtargets --portal $SERVER1
	fi

	if [ "$SERVER2" != "" ]; then
    	sudo iscsiadm -m discovery --op=new --op=del --type sendtargets --portal $SERVER2
	fi
fi

if [ "$1" == "login" ]; then
    sudo iscsiadm -m node -l
fi

if [ "$1" == "logout" ]; then
    sudo iscsiadm -m node -u
fi

if [ "$1" == "destroy" ]; then
	if [ "$SERVER1" != "" ]; then
		sudo iscsiadm -m discovery --op=del --type sendtargets --portal $SERVER1
	fi
	if [ "$SERVER2" != "" ]; then
		sudo iscsiadm -m discovery --op=del --type sendtargets --portal $SERVER2
	fi
fi



