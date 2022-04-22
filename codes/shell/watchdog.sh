#!/bin/bash

cleanup() {
        exec 3>&-
        exit 0
}

exec 3<>/dev/watchdog

trap cleanup EXIT

while true; do
        sleep 2
        echo 1>&3
done

exec 3>&-
