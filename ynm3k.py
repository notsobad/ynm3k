#!/usr/bin/env python
# coding: utf-8
import sys
import time
import datetime
import mimetypes
import random
import httplib
import pprint
import tornado.ioloop
import tornado.web
from tornado.options import define, options
import tornado
from tornado import gen
import json


class MyHandler(tornado.web.RequestHandler):
	def head(self, *args, **kwargs):
		return self.get(*args, **kwargs)

	def set_default_headers(self):
		self.set_header("Server", "YNM3k")
		self.set_header("Set-Cookie", "csrftoken=8e0f2f299fede170969578ebceec0967; expires=Thu, 09-Jan-2018 06:29:39 GMT; Max-Age=31449600; Path=/")
		
class MainHandler(MyHandler):
	def get(self):
		self.write('<pre>%s</pre>' % pprint.pformat( self.request.headers ))
		self.write("<hr/>YNM3k")

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
		'''Generate random content for dynamic page'''
		self.set_header("Content-Type", "text/html")
		d = {}
		d['headers'] = self.request.headers
		d['path'] = self.request.path
		d['query'] = self.request.query
		d['uri'] = self.request.uri
		d['body'] = self.request.body
		d['arguments'] = self.request.arguments

		s = json.dumps(d, indent=4, ensure_ascii=False)
		self.write('hello :-)<hr/>%s\n%s' % (random.randint(0,99999), s))

	def post(self):
		self.set_header("Content-Type", "text/html")
		d = {}
		d['headers'] = self.request.headers
		d['path'] = self.request.path
		d['query'] = self.request.query
		d['uri'] = self.request.uri
		d['body'] = self.request.body
		d['arguments'] = self.request.arguments

		s = json.dumps(d, indent=4, ensure_ascii=False)
		self.write('hello :-)<hr/>%s\n%s' % (random.randint(0,99999), s))

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

		self.set_header('Content-Description', 'File Transfer')
		self.set_header('Content-Type', 'application/octet-stream')
		#self.set_header('attachment','attachment; filename="a.zip"')
		self.set_header('Content-Transfer-Encoding','binary')
		self.write('f' * s)

class SlowHandler(MyHandler):
	@tornado.web.asynchronous
	@gen.engine
	def get(self, start, end=0):
		'''
		Check https://gist.github.com/lbolla/3826189
		'''
		self.write("Start at: %s<br/>" % datetime.datetime.now())
		_start = int(start)
		_end = 0
		
		if end:
			_end = int(end)

		if _end and _end > _start:
			s = random.uniform(_start, _end)
		else:
			s = _start

		yield gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + s)

		self.write("End at: %s<br/>" % datetime.datetime.now() )
		self.finish()


class RedirectHandler(MyHandler):
	def get(self, method):
		url = self.get_argument('url')
		if method in ('301', '302'):
			self.redirect(url, permanent=(method == '301'))
		elif method == 'js':
			self.write('<script>location.href="%s"</script>' % url)
		elif method == 'meta':
			self.write('<meta http-equiv="refresh" content="0; url=%s" />' % url)
		else:
			self.write('wrong argument')


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
	(r'/slow/(\d+)-?(\d+)?.*', SlowHandler),
	(r'/redirect/(.*)', RedirectHandler),
	(r'/*', MainHandler),
], **settings)

if __name__ == "__main__":
	if not options.port:
		options.print_help()
		sys.exit()
	application.listen(options.port, address=options.ip)
	
	tornado.ioloop.IOLoop.instance().start()
