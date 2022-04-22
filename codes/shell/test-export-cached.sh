#!/bin/bash

TEMPNODE=${1}               # /dev/bcacheN
DEVNAME=${TEMPNODE##*/}     # /dev/bcacheN -> bcacheN

for slave in "/sys/class/block/$DEVNAME/slaves"/*; do
    [ -d "$slave" ] || continue
    /usr/sbin/bcache-super-show "/dev/${slave##*/}" |
       awk '$1 == "sb.version" { sbver=$2; }
            $1 == "dev.uuid" { uuid=$2; }
            $1 == "dev.label" && $2 != "(empty)" { label=$2; }
            END {
                if (sbver == 1 && uuid) {
                    print("CACHED_UUID=" uuid)
                    if (label) print("CACHED_LABEL=" label)
                    exit(0)
                }
                exit(1);
            }'
    # awk exits 0 if it found a backing device.
    [ $? -eq 0 ] && exit 0
done

