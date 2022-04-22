
from pika import adapters
from pika import URLParameters
from pika import spec

class async_broker(object):
	"""
	Async broker consumer/producer class
	"""

	#
	# General
	#

	def __init__(self):
		"""
		Because it has to start somewhere
		"""
		print "! Initializing"

		self._url = "amqp://devel:devel@localhost/myvhost"

		self._connection = False
		self._channel = False

		self._topic = None
		self._user = None

	#
	# Connection
	#

	def new_connection(self):
		"""
		Creates a connection handler
		"""
		print "! Starting a new connection"

		params = URLParameters(self._url)
		callback = self.new_connection_done
		self._connection = adapters.TornadoConnection(params, callback)

	def new_connection_done(self, unused):
		"""
		Executed after connection is established
		"""
		print "! Connected"
		self.new_channel()

	#
	# Channel
	#

	def new_channel(self):
		"""
		Creates a channel handler
		"""
		print "! Creating a new channel"

		callback = self.new_channel_done
		self._connection.channel(on_open_callback=callback)

	def new_channel_done(self, channel):
		"""
		Executed after channel is created
		"""
		print "! Channel created"

		self._channel = channel

	#
	# Exchanges
	#

	def setup_exchange(self, exchange_name):
		"""
		Setup a fanout exchange
		"""
		# reschedule myself if not ready
		if not self._channel:
			self._connection.add_timeout(0, lambda: self.setup_exchange(exchange_name))
			return

		print "! Creating exchange: %s" % exchange_name

		self._channel.exchange_declare(
					callback=None,
					exchange=exchange_name,
					exchange_type='fanout',
					passive=False,
					durable=True,
					auto_delete=False,
					nowait=False
					)

	def delete_exchange(self, exchange_name):
		"""
		Delete an exchange
		"""
		# reschedule myself if not ready
		if not self._channel:
			self._connection.add_timeout(0, lambda: self.delete_exchange(exchange_name))
			return

		print "! Deleting exchange: %s" % exchange_name

		self._channel.exchange_delete(
					callback=None,
					exchange=exchange_name,
					if_unused=False,
					nowait=False
					)

	def query_exchange(self, exchange_name):
		"""
		Query existence of a fanout exchange
		"""
		# reschedule myself if not ready
		if not self._channel:
			self._connection.add_timeout(0, lambda: self.query_exchange(exchange_name))
			return

		print "! Querying exchange: %s" % exchange_name

	#
	# Queues
	#

	def setup_queue(self, queue_name):
		"""
		Setup a queue
		"""
		# reschedule myself if not ready
		if not self._channel:
			self._connection.add_timeout(0, lambda: self.setup_queue(queue_name))
			return

		print "! Creating queue: %s" % queue_name

		self._channel.queue_declare(
					callback=None,
					queue=queue_name,
					passive=False,
					durable=True,
					auto_delete=False,
					nowait=False
					)

	def purge_queue(self, queue_name):
		"""
		Purges all messages from the queue
		"""
		# reschedule myself if not ready
		if not self._channel:
			self._connection.add_timeout(0, lambda: self.purge_queue(queue_name))
			return

		print "! Purging queue: %s" % queue_name

		self._channel.queue_purge(
					callback=None,
					queue=queue_name,
					nowait=False
					)

	def delete_queue(self, queue_name):
		"""
		Delete a queue
		"""
		# reschedule myself if not ready
		if not self._channel:
			self._connection.add_timeout(0, lambda: self.delete_queue(queue_name))
			return

		print "! Deleting queue: %s" % queue_name

		self._channel.queue_delete(
					callback=None,
					queue=queue_name,
					if_unused=False,
					nowait=False
					)

	def query_queue(self, queue_name):
		"""
		Query existence of a queue
		"""
		# reschedule myself if not ready
		if not self._channel:
			self._connection.add_timeout(0, lambda: self.query_queue(queue_name))
			return

		print "! Querying queue: %s" % queue_name

	#
	# Bindings
	#

	def bind_queue(self, queue_name, exchange_name):
		"""
		Binds given queue to given exchange
		"""
		# reschedule myself if not ready
		if not self._channel:
			self._connection.add_timeout(0, lambda: self.bind_queue(queue_name, exchange_name))
			return

		print "! Binding queue %s to exchange %s" % (queue_name, exchange_name)

		self._channel.queue_bind(
					callback=None,
					queue=queue_name,
					exchange=exchange_name,
					nowait=False
					)

	def unbind_queue(self, queue_name, exchange_name):
		"""
		Unbinds given queue from given exchange
		"""
		# reschedule myself if not ready
		if not self._channel:
			self._connection.add_timeout(0, lambda: self.unbind_queue(queue_name, exchange_name))
			return

		print "! Unbinding queue %s from exchange %s" % (queue_name, exchange_name)

		self._channel.queue_unbind(
					callback=None,
					queue=queue_name,
					exchange=exchange_name
					)

	#
	# Messages
	#

	def send_msg(self, exchange_name, msg):
		"""
		Send a single msg to a given exchange
		"""
		# reschedule myself if not ready
		if not self._channel:
			self._connection.add_timeout(0, lambda: self.send_msg(exchange_name, msg))
			return

		print "! Sending msg to exchange %s" % (exchange_name)

		self._channel.basic_publish(
					exchange=exchange_name,
					routing_key='',
					body=msg
					)

	def recv_msg(self, queue_name, ok, notok):
		"""
		Receive a single message from a given queue
		"""
		# reschedule myself if not ready
		if not self._channel:
			self._connection.add_timeout(0, lambda: self.recv_msg(queue_name, ok, notok))
			return

		print "! Receiving msg from queue %s" % (queue_name)

		self._msg_ok = ok
		self._msg_notok = notok

		self._channel.callbacks.add(
					self._channel.channel_number,
					spec.Basic.GetEmpty,
					self.recv_msg_empty,
					False
					)

		self._channel.basic_get(
					callback=self.recv_msg_done,
					queue=queue_name,
					no_ack=True
					)

	def recv_msg_done(self, channel, header, properties, body):
		print "! Received one msg"
		self._msg_ok(message=body)

	def recv_msg_empty(self, seila):
		print "! No more messages to collect"
		self._msg_notok(code=204)

	########

	#
	# SUBSCRIBE - DONE
	#

	def subscribe(self, topic, user, ok, notok):
		"""
		* Define one exchange called "topic";
		* Define one queue called "topic_user";
		* Bind queue "topic_user" to exchange "topic": 200;
		"""

		if not topic or not user:
			notok()
			return

		queue = "%s_%s" % (topic, user)

		self.setup_exchange(topic)
		self.setup_queue(queue)
		self.bind_queue(queue, topic)

		ok()

	#
	# UNSUBSCRIBE - DONE
	#
	def unsubscribe(self, topic, user, ok, notok):
		"""
		* Check if queue "topic_user" is bound to "topic": 404;
		* Unbind queue "topic_user" from exchange "topic": 200;

		TODO: Implement Unsubscribe 404
		"""

		if not topic or not user:
			notok(code=400)
			return

		queue = "%s_%s" % (topic, user)

		self.unbind_queue(queue, topic)

		ok()

	#
	# PUBLISH - DONE
	#

	def publish(self, topic, msg, ok, notok):
		"""
		* Define one exchange called "topic";
		* Send message to exchange "topic": 200;
		"""

		if not topic:
			notok()
			return

		self.setup_exchange(topic)
		self.send_msg(topic, msg)

		ok()
	#
	# RETRIEVE - DONE
	#

	def retrieve(self, topic, user, ok, notok):
		"""
		* Check if queue "user" exists and is bound to exchange "topic": 404;
		* Check if there are any messages on queue "user": 204;
		* Receive next message from queue "user": 200;

		TODO: Implement Retrieve 404
		"""

		if not topic or not user:
			notok(code=400)
			return
		
		# I'm setting up exchange & queue to avoid channel being closed
		# TODO: Handle channel being close due to exchange and/or queue not existing
		
		queue = "%s_%s" % (topic, user)
		
		self.setup_exchange(topic)
		self.setup_queue(queue)
		
		# I'm not binding queue to exchange by default
		# If user is not subscribe he will always get 0 messages instead of 404
		# TODO: Implement a way to discover if queue is subscribed
		
		self.recv_msg(queue, ok, notok)
