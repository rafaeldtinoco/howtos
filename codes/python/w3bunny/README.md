# w3bunny

[Check TODOs](https://github.com/inaddy/w3bunny/blob/master/TODOs.md)

###1. ASYNC WEB SERVER USING TORNADO & PIKA

**Subscribe user to topic**
```
COMM:	POST /<topic>/<username>
RESP:	200 = Success	 |	Subscription succeeded
BODY:	-
```

**Unsubscribe user from topic**
```
COMM:	DELETE /<topic>/<username>
RESP:	200 = Success    |	Unsubscribe succeeded
        404 = Error      |	The subscription does not exist
BODY:	-
```

**Publish a message to topic**
```	
COMM:	POST /<topic>
RESP:	200 = Success    |	Publish succeeded
BODY:	Message
```

**Retrieve one msg from topic**
```
COMM:	GET /<topic>/<username>
RESP:	200 = Success    |	Retrieval succeeded
        204 = Success    |	There are no messages available
        404 = Error      |	The subscription does not exist
BODY:	Message
```

###2. INSTALLATION

Make sure you have a fresh Ubuntu Vivid Installation:

```
inaddy@superhost:~$ sudo lxc-ls
freshvivid
```

####Python

Install python-tornado and python-pip:
```
inaddy@freshvivid:~$ sudo apt-get install -y python-tornado python-pip
```

Install pika:
```
inaddy@freshvivid:~$ sudo pip install pika
```

Check versions:
```
PIKA == 0.9.14 (pip list)
TORNADO == 3.2.0-1ubuntu (dpkg -l)
```

####AMQP Server

Install RabbitMQ server:
```
inaddy@freshvivid:~$ sudo apt-get install -y rabbitmq-server
```

Enable RabbitMQ management:
```
inaddy@freshvivid:~$ sudo rabbitmq-plugins enable rabbitmq_management
```

Create a new RabbitMQ vhost:
```
inaddy@freshvivid:~$ sudo rabbitmqctl add_vhost myvhost
```

Create RabbitMQ admin user:
```
inaddy@freshvivid:~$ sudo rabbitmqctl add_user admin admin
inaddy@freshvivid:~$ sudo rabbitmqctl set_user_tags admin administrator
inaddy@freshvivid:~$ sudo rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
inaddy@freshvivid:~$ sudo rabbitmqctl set_permissions -p myvhost admin ".*" ".*" ".*"
```

Create RabbitMQ devel user:
```
inaddy@freshvivid:~$ sudo rabbitmqctl add_user devel devel
inaddy@freshvivid:~$ sudo rabbitmqctl set_permissions -p myvhost devel ".*" ".*" ".*"
```

####Executing

Get w3bunny source code:
```
inaddy@freshvivid:~$ git clone https://github.com/inaddy/w3bunny.git
```

Execute w3bunny binary in one shell:
```
inaddy@freshvivid:w3bunny$ ./w3bunny.py
! Initializing
! Starting a new connection
! Connected
! Creating a new channel
! Channel created
! Creating exchange: topic
! Sending msg to exchange topic
! Initializing
! Starting a new connection
! Connected
! Creating a new channel
! Channel created
! Unbinding queue topic_user from exchange topic
! Initializing
! Starting a new connection
! Connected
! Creating a new channel
! Channel created
! Creating exchange: topic
! Creating queue: topic_user
! Receiving msg from queue topic_user
! No more messages to collect
! Initializing
! Starting a new connection
! Connected
! Creating a new channel
! Channel created
! Creating exchange: topic
! Creating queue: topic_user
! Binding queue topic_user to exchange topic
! Initializing
! Starting a new connection
! Connected
! Creating a new channel
! Channel created
! Creating exchange: topic
! Creating queue: topic_user
! Receiving msg from queue topic_user
! No more messages to collect
! Initializing
! Starting a new connection
! Connected
! Creating a new channel
! Channel created
! Creating exchange: topic
! Sending msg to exchange topic
! Initializing
! Starting a new connection
! Connected
! Creating a new channel
! Channel created
! Creating exchange: topic
! Creating queue: topic_user
! Receiving msg from queue topic_user
! Received one msg
! Initializing
! Starting a new connection
! Connected
! Creating a new channel
! Channel created
! Unbinding queue topic_user from exchange topic
```

Execute w3bunny test script in the other shell:
```
inaddy@freshvivid:w3bunny$ ./scripts/testme.sh
> POST /topic HTTP/1.1
< HTTP/1.1 200 POST: Publish succeded.
> DELETE /topic/user HTTP/1.1
< HTTP/1.1 200 DELETE: Unsubscribe succeeded.
> GET /topic/user HTTP/1.1
< HTTP/1.1 204 GET: No messages available!
> POST /topic/user HTTP/1.1
< HTTP/1.1 200 POST: Subscription succeeded.
> GET /topic/user HTTP/1.1
< HTTP/1.1 204 GET: No messages available!
> POST /topic HTTP/1.1
< HTTP/1.1 200 POST: Publish succeded.
> GET /topic/user HTTP/1.1
< HTTP/1.1 200 GET: Retrieval succeeded.
> DELETE /topic/user HTTP/1.1
< HTTP/1.1 200 DELETE: Unsubscribe succeeded.
```
-> make sure to have "curl" installed


