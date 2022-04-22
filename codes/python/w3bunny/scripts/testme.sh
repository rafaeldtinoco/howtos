#!/bin/bash

filter()
{
	$@ 2>&1 | grep "HTTP/1.1"
}

SUBSCRIBE="curl --verbose -X POST http://localhost:8888/topic/user"
SUBMIT="curl --verbose -X POST -d message http://localhost:8888/topic"
GET="curl -o /dev/null --verbose http://localhost:8888/topic/user"
UNSUBSCRIBE="curl --verbose -X DELETE http://localhost:8888/topic/user"

#
# FUNCTIONAL TESTS
#

# send message to non-existent exchange

filter $SUBMIT		# will get a 200

# try to unsubscribe queue NOT subscribed to exchange

filter $UNSUBSCRIBE	# will get a 200 (v1.0 = should get a 404)

# try to get message from non-existent/unbound queue

filter $GET		# will get a 204 (v1.0 = should get a 404)

# normal operation

filter $SUBSCRIBE 	# will get a 200
filter $GET 		# will get a 204
filter $SUBMIT		# will get a 200
filter $GET		# will get a 200
filter $UNSUBSCRIBE	# will get a 200

