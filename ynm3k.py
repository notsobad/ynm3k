#!/usr/bin/env python
# coding: utf-8
import sys
import datetime
import mimetypes
import httplib
import pprint
import tornado.ioloop
import tornado.web
from tornado.options import define, options


class MyHandler(tornado.web.RequestHandler):
	def head(self, *args, **kwargs):
		return self.get(*args, **kwargs)

	def set_default_headers(self):
		self.set_header("Server", "YNM3000")
		self.set_header("Set-Cookie", "csrftoken=8e0f2f299fede170969578ebceec0967; expires=Thu, 09-Jan-2018 06:29:39 GMT; Max-Age=31449600; Path=/")
		
class MainHandler(MyHandler):
	def get(self):
		self.write('<pre>%s</pre>' % pprint.pformat( self.request.headers ))
		self.write("<hr/>YNM3000")

class FileHandler(MyHandler):
	def get(self, file_name):
		arr = file_name.split('.')
		modified = datetime.datetime.now()
		self.set_header("Last-Modified", modified)
		mime_type, encoding = mimetypes.guess_type(file_name)
		if mime_type:
			self.set_header("Content-Type", mime_type)
		cache_time = 95270
		self.set_header("Expires", datetime.datetime.utcnow() +
								   datetime.timedelta(seconds=cache_time))
		self.set_header("Cache-Control", "max-age=" + str(cache_time))
		self.write(file_name)

class DynamicHandler(MyHandler):
	def get(self, file_name):
		'''pass'''
		self.set_header("Content-Type", "text/html")
		self.set_header("Set-Cookie", "csrftoken=8e0f2f299fede170969578ebceec0967; expires=Thu, 09-Jan-2014 06:29:39 GMT; Max-Age=31449600; Path=/")
		self.write('hello :-)')

class CodeHandler(MyHandler):
	def get(self, code):
		'''pass'''
		code = int(code)
		msg = httplib.responses.get(code, "Unknown")
		self.send_error(code)
	
	def write_error(self, code):
		self.write('<h1>Http %s</h1> <hr/>Generated at %s' % (code, str(datetime.datetime.now())))


class SizeHandler(MyHandler):
	def get(self, size):
		'''Generate certain size file'''
		size = size.lower()
		try:
			if 'k' in size:
				s = int(size.replace('k', '')) * 1024
			elif 'm' in size:
				s = int(size.replace('m', '')) * 1024 * 1024
			else:
				s = int(size)
		except ValueError:
			return self.write('Wrong argument')

		self.write('f' * s)

define("ip", help="ip to bind", default="0.0.0.0")
define("port", help="port to listen", default=9527)
define("debug", default=False, help="enable debug?")
tornado.options.parse_command_line()
settings = {
	#'template_path' : os.path.join(os.path.dirname(__file__), 'templates'),
	'debug' : options.debug,
	'gzip' : True
}

application = tornado.web.Application([
	(r'/', MainHandler),
	(r'/static/(.*)', FileHandler),
	(r'/dynamic/(.*)', DynamicHandler),
	(r'/code/(\d+).*', CodeHandler),
	(r'/size/([\d|k|m]+).*', SizeHandler),
	(r'/*', MainHandler),
], **settings)

if __name__ == "__main__":
	if not options.port:
		options.print_help()
		sys.exit()
	application.listen(options.port, address=options.ip)
	
	tornado.ioloop.IOLoop.instance().start()
