#!/bin/bash

filter()
{
	$@ 2>&1 | grep "HTTP/1.1"
}

SUBSCRIBE="curl --verbose -X POST http://localhost:8888/topic/user"
SUBMIT="curl --verbose -X POST -d message http://localhost:8888/topic"
GET="curl -o /dev/null --verbose http://localhost:8888/topic/user"

# subscribe, get nothing, submit, get one

filter $SUBSCRIBE

for s in `seq 1 10000`; do
	filter $SUBMIT
done
