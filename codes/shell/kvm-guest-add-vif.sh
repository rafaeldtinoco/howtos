#!/bin/bash

if [ $UID -ne 0 ]
then
    sudo ${0/\.sh/}.py $@
else
    ${0/\.sh/}.py $@
fi

exit 0
