#!/usr/bin/env python
# coding: utf-8
import sys
import time
import uuid
import datetime
import mimetypes
import random
import socket
import hashlib
import json
import tornado.ioloop
import tornado.web
from tornado.options import define, options
import tornado
from tornado import gen

def get_host_hash():
    hostname = socket.gethostname()
    m = hashlib.md5()
    m.update(hostname)
    return m.hexdigest()[:7]

class MyHandler(tornado.web.RequestHandler):

    def head(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def set_default_headers(self):
        self.set_header("Server", "YNM3K-%s" % SETTINGS['node_id'])
        self.set_header(
            "Set-Cookie",
            "csrftoken=8e0f2f299fede170969578ebceec0967; "
            "expires=Thu, 09-Jan-2020 06:29:39 GMT; Max-Age=31449600; Path=/")


class MainHandler(MyHandler):

    def get(self):
        try:
            headers = self.request.headers._dict
        except:
            headers = self.request.headers

        links = [
            '/trace/',
            '/static/abc.js',
            '/static/abc/xyz.css',
            '/static/abc/xyz/uvw.txt',
            '/static/abc.html',
            '/static/abc.jpg',
            '/dynamic/abc.php',
            '/dynamic/abc.asp',
            '/code/200',
            '/code/400',
            '/code/404',
            '/code/502',
            '/size/11k.zip',
            '/size/1k.bin',
            '/slow/3',
            '/slow/4-10',
            '/redirect/301?url=http://www.notsobad.me',
            '/redirect/302?url=http://www.notsobad.me',
            '/redirect/js?url=http://www.notsobad.me',
        ]
        tpl = '''
        <h1>YNM3K Test site</h1>
        <h2>Request header</h2>
        <pre>{% for h in headers %}{{ h }}: {{ headers[h] }}
            {% end %}
        </pre>
        <h2>Links</h2>
        <ul>
            {% for link in links %}
            <li><a href="{{ link }}">{{ link }}</a></li>
            {% end %}
        </ul>
        <footer>
            <hr/>SERVER-ID: {{ node_id }}, Powered by YNM3K <a href="https://github.com/notsobad/ynm3k">Fork me</a> on Github
        </footer>
        '''
        i = tornado.template.Template(tpl, whitespace="single")
        out = i.generate(headers=headers, node_id=SETTINGS['node_id'], links=links)
        self.write(out)

class TraceHandler(MyHandler):
    def get(self):
        self.set_header("Content-Type", "text/plain")
        out = "{method} {url} {version}\r\n{headers}\r\n\r\n".format(method=self.request.method, 
            url=self.request.uri, version=self.request.version, headers=str(self.request.headers))
        self.write(out)

    def post(self):
        self.get()


class FileHandler(MyHandler):

    def get(self, file_name):
        modified = datetime.datetime.now()
        self.set_header("Last-Modified", modified)
        mime_type, encoding = mimetypes.guess_type(file_name)
        if mime_type:
            self.set_header("Content-Type", mime_type)
        try:
            cache_time = int(self.request.headers.get('Cache', '95270'))
        except:
            cache_time = 95270
        if cache_time:
            self.set_header("Expires", datetime.datetime.utcnow() +
                            datetime.timedelta(seconds=cache_time))
            self.set_header("Cache-Control", "max-age=" + str(cache_time))
        self.write(file_name)


class DynamicHandler(MyHandler):

    def get(self, file_name):
        '''Generate random content for dynamic page'''
        self.set_header("Content-Type", "text/html")
        d = {}
        d['headers'] = dict(self.request.headers)
        d['path'] = self.request.path
        d['query'] = self.request.query
        d['uri'] = self.request.uri
        d['body'] = self.request.body
        d['arguments'] = str(self.request.arguments)

        try:
            i = int(self.request.headers.get('Cache', 0))
            assert i
            self.set_header(
                'Expires',
                datetime.datetime.utcnow() + datetime.timedelta(seconds=i))
            self.set_header('Cache-Control', 'max-age=%s' % i)
        except:
            pass

        j = json.dumps(d, indent=4, ensure_ascii=False)
        self.write('hello :-)<pre>%s</pre><hr>%s' % (j, uuid.uuid4()))

    post = get


class CodeHandler(MyHandler):

    def get(self, code):
        '''pass'''
        code = int(code)
        self.send_error(code)

    def write_error(self, code):
        self.write(
            '<h1>Http %s</h1> <hr/>Generated at %s' %
            (code, str(
                datetime.datetime.now())))

    def set_status(self, status_code, reason=None):
        try:
            super(CodeHandler, self).set_status(status_code, reason)
        except:
            tornado.web.RequestHandler._status_code = status_code
            tornado.web.RequestHandler._reason = "unknown service error"


class SizeHandler(MyHandler):

    def get(self, size):
        '''Generate certain size file'''
        size = size.lower()
        try:
            if 'k' in size:
                i = int(size.replace('k', '')) * 1024
            elif 'm' in size:
                i = int(size.replace('m', '')) * 1024 * 1024
            else:
                i = int(size)
        except ValueError:
            return self.write('Wrong argument')

        self.set_header('Content-Description', 'File Transfer')
        self.set_header('Content-Type', 'application/octet-stream')
        #self.set_header('attachment','attachment; filename="a.zip"')
        self.set_header('Content-Transfer-Encoding', 'binary')
        return self.write('f' * i)


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
            i = random.uniform(_start, _end)
        else:
            i = _start

        yield gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + i)

        self.write("End at: %s<br/>" % datetime.datetime.now())
        self.finish()


class RedirectHandler(MyHandler):

    def get(self, method):
        url = self.get_argument('url')
        if method in ('301', '302'):
            self.redirect(url, permanent=(method == '301'))
        elif method == 'js':
            self.write('<script>location.href="%s"</script>' % url)
        elif method == 'meta':
            self.write(
                '<meta http-equiv="refresh" content="0; url=%s" />' %
                url)
        else:
            self.write('wrong argument')


define("ip", help="ip to bind", default="0.0.0.0")
define("port", help="port to listen", default=9527)
define("debug", default=False, help="enable debug?")
tornado.options.parse_command_line()
SETTINGS = {
    'debug': options.debug,
    'node_id': get_host_hash(),
    'gzip': True
}

APP = tornado.web.Application([
    (r'/', MainHandler),
    (r'/trace/?.*', TraceHandler),
    (r'/static/(.*)', FileHandler),
    (r'/dynamic/(.*)', DynamicHandler),
    (r'/code/(\d+).*', CodeHandler),
    (r'/size/([\d|k|m]+).*', SizeHandler),
    (r'/slow/(\d+)-?(\d+)?.*', SlowHandler),
    (r'/redirect/(.*)', RedirectHandler),
    (r'/*', MainHandler),
], **SETTINGS)

if __name__ == "__main__":
    if not options.port:
        options.print_help()
        sys.exit()
    APP.listen(options.port, address=options.ip)

    tornado.ioloop.IOLoop.instance().start()
