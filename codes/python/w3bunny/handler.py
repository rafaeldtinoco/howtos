#!/usr/bin/env python

from tornado import ioloop
from tornado import web

from broker import async_broker

class wrapper_handler(web.RequestHandler):
	"""
	Tornado HTTP RequestHandler for AMQP wrapper
	"""

	def initialize(self):

		# TODO: do not create one connection per request :o)

		self._abroker = async_broker()

		self._ioloop = ioloop.IOLoop.instance()
		self._ioloop.add_timeout(0, async_broker.new_connection(self._abroker))

		# TODO: close file desriptors at the end
	#
	# SUBSCRIBE
	#

	@web.asynchronous
	def post_subscribe(self, topic, user):
		"""
		WHAT:	Subscribe to a topic
		COMM:	POST /<topic>/<username>
		RESP:	200 = Success	|	Subscription succeeded
		BODY:	-
		"""
		if not topic:
			self.set_status(400, "POST: No topic informed!")
			self.finish()
			return

		if not user:
			self.set_status(400, "POST: No username informed!")
			self.finish()
			return

		self._abroker.subscribe(
				topic=topic,
				user=user,
				ok=self.subscribe_ok,
				notok=self.subscribe_notok
				)

	def subscribe_ok(self):

		self.set_status(200, "POST: Subscription succeeded.")
		self.finish()

	def subscribe_notok(self):

		self.set_status(400, "POST: General error!")
		self.finish()

	#
	# UNSUBSCRIBE
	#

	@web.asynchronous
	def delete(self, topic=None, user=None):
		"""
		WHAT:	Unsubscribe from a topic
		COMM:	DELETE /<topic>/<username>
		RESP:	200 = Success 	|	Unsubscribe succeeded
			404 = Error	|	The subscription does not exist
		BODY:	-
		"""

		if not topic:
			self.set_status(400, "DELETE: No topic informed!")
			self.finish()
			return

		if not user:
			self.set_status(400, "DELETE: No username informed!")
			self.finish()
			return

		self._abroker.unsubscribe(
				topic=topic,
				user=user,
				ok=self.unsubscribe_ok,
				notok=self.unsubscribe_notok
				)

	def unsubscribe_ok(self):

		self.set_status(200, "DELETE: Unsubscribe succeeded.")
		self.finish()

	def unsubscribe_notok(self, code=None):

		if code is 404:
			self.set_status(404, "DELETE: The subscription does not exist!")
			self.finish()
			return

		self.set_status(400, "DELETE: General error!")
		self.finish()

	#
	# PUBLISH
	#

	@web.asynchronous
	def post_topic(self, topic):
		"""
		WHAT:	Publish a message
		COMM:	POST /<topic>
		RESP:	200 = Success	|	Publish succeeded
		BODY:	Message
		"""

		if not topic:
			self.set_status(400, "POST: No topic informed!")
			self.finish()
			return

		msg = self.request.body

		self._abroker.publish(
				topic=topic,
				msg=msg,
				ok=self.publish_ok,
				notok=self.publish_notok
				)

	def publish_ok(self):

		self.set_status(200, "POST: Publish succeded.")
		self.finish()

	def publish_notok(self):

		self.set_status(400, "POST: General error!")
		self.finish()

	#
	# RETRIEVE
	#

	@web.asynchronous
	def get(self, topic=None, user=None):
		"""
		DOES:	Retrieve the next message from a topic
		COMM:	GET /<topic>/<username>
		RESP:	200 = Success	|	Retrieval succeeded
			204 = Success	|	There are no messages available for this topic on this user
			404 = Error 	|	The subscription does not exist
		BODY:	Message
		"""
		if not topic:
			self.set_status(400, "GET: No topic informed!")
			self.finish()
			return

		if not user:
			self.set_status(400, "GET: No username informed!")
			self.finish()
			return

		self._abroker.retrieve(
				topic=topic,
				user=user,
				ok=self.retrieve_ok,
				notok=self.retrieve_notok
				)

	def retrieve_ok(self, message):

		self.write(message)
		self.set_status(200, "GET: Retrieval succeeded.")
		self.finish()

	def retrieve_notok(self, code):

		if code is 204:
			self.set_status(204, "GET: No messages available!")
			self.finish()
			return

		if code is 404:
			self.set_status(404, "GET: Subscription does not exist!")
			self.finish()
			return

		self.set_status(400, "GET: General Error!")

	# other functions

	@web.asynchronous
	def post(self, topic, user=None):
		if topic and not user:
			self.post_topic(topic)
		if topic and user:
			self.post_subscribe(topic, user)
