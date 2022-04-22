#!/usr/bin/env python

import sys

from tornado import web
from tornado import ioloop
from tornado import httpserver

from handler import wrapper_handler

def main():

	wrapper = web.Application([
				web.url(r"/(.*)/(.*)", wrapper_handler),
				web.url(r"/(.*)", wrapper_handler)
				])

	http_server = httpserver.HTTPServer(wrapper)
	http_server.listen(8888)

	try:
		ioloop.IOLoop.current().start()

	except KeyboardInterrupt:
		sys.exit(0)

if __name__ == '__main__':

	main()
