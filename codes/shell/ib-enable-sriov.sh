#!/bin/bash

if [ $UID -ne 0 ]
then
    sudo $0
    exit 0
fi

NUMVFS=32
IBFACE="mlx5_2"

quiet()
{
    $@ 2>&1 > /dev/null 2>&1
}

quiet mst start

echo
echo making sure firmware is configured
echo

for device in $(mst status | grep "/dev/mst" | awk '{print $1}')
do

    echo -n "$device: "

    mlxconfig -d $device q | egrep "VFS" | egrep -q $NUMVFS && {
        echo virtual functions already configured!
    } || {
        echo virtual functions unconfigured, configuring now...
        echo configuring $device to have $NUMVFS virtual functions...
        quiet mlxconfig -y -d $device set SRIOV_EN=1 NUM_OF_VFS=$NUMVFS
        echo WARNING: resetting IB device for new configuration...
        quiet mlxfwreset -y --device $device reset
    }

done

echo
echo interfaces to be configured for sr-iov: $IBFACE
echo

for ibface in $IBFACE
do

    total=$(cat /sys/class/infiniband/$ibface/device/sriov_totalvfs)
    numvfs=$(cat /sys/class/infiniband/$ibface/device/sriov_numvfs)

    if [ "$total" != "$NUMVFS" ]
    then
        echo WARNING: firmware was configured with $NUMVFS virtual functions,
        echo WARNING: but card $ibface, after reset, shows only $total available!
        exit 1
    fi

    if [ "$numvfs" != "$NUMVFS" ]
    then
        echo changing number of available virtual functions of interface $ibface...
        echo $total > /sys/class/infiniband/$ibface/device/sriov_numvfs
    else
        echo number of virtual interfaces of $ibface is already $NUMVFS!
    fi

done

echo
echo interfaces available to the host
echo

ibdev2netdev -v | sort -k 2n

echo
echo configuring sr-iov policy
echo

for ibface in $IBFACE
do
    for policydir in /sys/class/infiniband/$ibface/device/sriov/*
    do
        currentpolicy=$(cat $policydir/policy)
        if [ "$currentpolicy" == "Follow" ]
        then
            echo $ibface VIF $(basename $policydir) policy already configured
        else
            echo configuring $ibface VIF $(basename $policydir) policy to Follow
            echo Follow > $policydir/policy
        fi
    done
done

echo
echo setting numbers for VIFs port and node GUIDs
echo

NUM=$(printf "%d" $(ibstat | grep "Port GUID" | grep -v "0x0000000000000000" | awk '{print $3}' | sort | tail -1))

for ibface in $IBFACE
do
    for sriovdir in /sys/class/infiniband/$ibface/device/sriov/*
    do
        NODE=$(cat $sriovdir/node)

        NUM=$(($NUM+1))

        if [ "$NODE" != "00:00:00:00:00:00:00:00" ]; then
            echo $ibface VIF $(basename $sriovdir) already has a node guid set to $NODE
        else
            NODE=$(printf "%x" $NUM)
            echo -n "$ibface VIF $(basename $sriovdir) setting node guid to 0x$NODE "
            NODE=$(echo $NODE | sed -E 's:(..)(..)(..)(..)(..)(..)(..)(..):\1\:\2\:\3\:\4\:\5\:\6\:\7\:\8:g')
            echo "($NODE)"
            echo $NODE > $sriovdir/node
        fi

        PORT=$(cat $sriovdir/port)

        NUM=$(($NUM+1))

        if [ "$PORT" != "00:00:00:00:00:00:00:00" ]; then
            echo $ibface VIF $(basename $sriovdir) already has a port guid set to $PORT
        else
            PORT=$(printf "%x" $NUM)
            echo -n "$ibface VIF $(basename $sriovdir) setting port guid to 0x$PORT "
            PORT=$(echo $PORT | sed -E 's:(..)(..)(..)(..)(..)(..)(..)(..):\1\:\2\:\3\:\4\:\5\:\6\:\7\:\8:g')
            echo "($PORT)"
            echo $PORT > $sriovdir/port
        fi
    done
done

echo
echo re-binding virtual functions
echo

FILE=/tmp/ibdev2netdev.$$

ibdev2netdev -v | sort -k 2n > $FILE

for ibface in $IBFACE
do
    for vifpciaddr in /sys/class/infiniband/$ibface/device/virtfn*
    do
        pciaddr=$(ls -lah $vifpciaddr | awk '{print $11}' | sed 's:\.\.\/::g')
        mlxdev=$(cat $FILE | grep $pciaddr | awk '{print $2}')
        mlxibdev=$(cat $FILE | grep $pciaddr | cut -d'>' -f2 | awk '{print $1}')

        [ x$(cat /sys/class/infiniband/$mlxdev/node_guid | sed 's:\:::g') == x"0000000000000000" ] && {

            echo "re-binding pci-addr $pciaddr of VIF $mlxdev (net device: $mlxibdev)"
            echo $pciaddr > /sys/bus/pci/drivers/mlx5_core/unbind
            echo $pciaddr > /sys/bus/pci/drivers/mlx5_core/bind

        } || {
            echo "pci-addr $pciaddr of VIF $mlxdev (net device: $mlxibdev) already with node/port guid"
        }

    done
done

echo
echo VIFs summary to make your life easier
echo

for ibface in $IBFACE
do
    for vifpciaddr in /sys/class/infiniband/$ibface/device/virtfn*
    do
        pciaddr=$(ls -lah $vifpciaddr | awk '{print $11}' | sed 's:\.\.\/::g')
        mlxdev=$(cat $FILE | grep $pciaddr | awk '{print $2}')
        mlxibdev=$(cat $FILE | grep $pciaddr | cut -d'>' -f2 | awk '{print $1}')
        echo "$mlxdev $mlxibdev $pciaddr"
    done
done

rm $FILE

echo
echo "run \"ibstat -s\" to get status for each device (all of them should be online now)"
echo

