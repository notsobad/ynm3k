#!/usr/bin/env python
# coding: utf-8
import sys
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

# pylint: disable=W0223
# pylint: disable=C0115
# pylint: disable=C0116

def get_host_hash():
    """Generate hash from hostname"""
    hostname = socket.gethostname()
    m = hashlib.md5()
    m.update(hostname.encode("utf-8"))
    return m.hexdigest()[:7]

class MyHandler(tornado.web.RequestHandler):
    def head(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def set_default_headers(self):
        self.set_header("Server", f"YNM3K-{SETTINGS['node_id']}")
        self.set_header(
            "Set-Cookie",
            "csrftoken=8e0f2f299fede170969578ebceec0967; "
            "expires=Thu, 09-Jan-2020 06:29:39 GMT; Max-Age=31449600; Path=/",
        )


class MainHandler(MyHandler):
    def get(self):
        headers = self.request.headers
        links = [
            "/trace/",
            "/static/abc.js",
            "/static/abc/xyz.css",
            "/static/abc/xyz/uvw.txt",
            "/static/abc.html",
            "/static/abc.jpg",
            "/dynamic/abc.php",
            "/dynamic/abc.asp",
            "/code/200",
            "/code/400",
            "/code/404",
            "/code/502",
            "/size/11k.zip",
            "/size/1k.bin",
            "/slow/3",
            "/slow/4-10",
            "/redirect/301?url=https://github.com/notsobad/ynm3k",
            "/redirect/302?url=https://github.com/notsobad/ynm3k",
            "/redirect/js?url=https://github.com/notsobad/ynm3k",
        ]
        tpl = """
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
        """
        i = tornado.template.Template(tpl, whitespace="single")
        out = i.generate(headers=headers, node_id=SETTINGS["node_id"], links=links)
        self.write(out)


class TraceHandler(MyHandler):
    def get(self):
        self.set_header("Content-Type", "text/plain")
        out = f"{self.request.method} {self.request.uri} {self.request.version}\r\n{self.request.headers}\r\n\r\n" 
        self.write(out)

    def post(self):
        self.get()


class FileHandler(MyHandler):
    def get(self, file_name):
        modified = datetime.datetime.now()
        self.set_header("Last-Modified", modified)
        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type:
            self.set_header("Content-Type", mime_type)
        try:
            cache_time = int(self.request.headers.get("Cache", "95270"))
        except ValueError:
            cache_time = 95270

        if cache_time:
            self.set_header(
                "Expires",
                datetime.datetime.utcnow() + datetime.timedelta(seconds=cache_time),
            )
            self.set_header("Cache-Control", f"max-age={cache_time}")
        self.write(f"{file_name}\n")


class DynamicHandler(MyHandler):
    def get(self):
        """Generate random content for dynamic page"""
        self.set_header("Content-Type", "text/html")
        d = {}
        d["headers"] = dict(self.request.headers)
        d["path"] = self.request.path
        d["query"] = self.request.query
        d["uri"] = self.request.uri
        d["body"] = self.request.body.decode("utf-8")
        d["arguments"] = str(self.request.arguments)

        try:
            i = int(self.request.headers.get("Cache", 0))
        except ValueError:
            i = 0

        if i > 0:
            self.set_header(
                "Expires", datetime.datetime.utcnow() + datetime.timedelta(seconds=i)
            )
            self.set_header("Cache-Control", f"max-age={i}")

        j = json.dumps(d, indent=4, ensure_ascii=False)
        self.write(f"<pre>{j}</pre><hr/>{uuid.uuid4()}\n")

    post = get


class CodeHandler(MyHandler):
    def get(self, code):
        """pass"""
        code = int(code)
        self.send_error(code)

    def write_error(self, status_code, **kargs):
        self.finish(
            f"<h1>Http {status_code}</h1><hr/>Generated at {datetime.datetime.now()}\n"
        )


class SizeHandler(MyHandler):
    def get(self, size):
        """Generate certain size file"""
        size = size.lower()
        try:
            if "k" in size:
                i = int(size.replace("k", "")) * 1024
            elif "m" in size:
                i = int(size.replace("m", "")) * 1024 * 1024
            else:
                i = int(size)
        except ValueError:
            return self.write("Wrong argument\n")

        self.set_header("Content-Description", "File Transfer")
        self.set_header("Content-Type", "application/octet-stream")
        # self.set_header('attachment','attachment; filename="a.zip"')
        self.set_header("Content-Transfer-Encoding", "binary")
        return self.write("f" * i)


class SlowHandler(MyHandler):
    async def get(self, start, end=0):
        self.write(f"Start at: {datetime.datetime.now()}<br/>\n")
        _start = int(start)
        _end = 0

        if end:
            _end = int(end)

        if _end and _end > _start:
            i = random.uniform(_start, _end)
        else:
            i = _start

        await gen.sleep(i)

        self.write(f"End at: {datetime.datetime.now()}<br/>\n")


class RedirectHandler(MyHandler):
    def get(self, method):
        url = self.get_argument("url")
        if method in ("301", "302"):
            self.redirect(url, status=int(method))
        elif method == "js":
            self.write(f'<script>location.href="{url}"</script>\n' % url)
        elif method == "meta":
            self.write(f'<meta http-equiv="refresh" content="0; url={url}" />\n')
        else:
            self.write("wrong argument\n")


define("ip", help="ip to bind", default=None)
define("port", help="port to listen", default=9527)
define("debug", default=False, help="enable debug?")
tornado.options.parse_command_line()
SETTINGS = {"debug": options.debug, "node_id": get_host_hash(), "gzip": True}

APP = tornado.web.Application(
    [
        (r"/", MainHandler),
        (r"/trace/?.*", TraceHandler),
        (r"/static/(.*)", FileHandler),
        (r"/dynamic/.*", DynamicHandler),
        (r"/code/(\d+).*", CodeHandler),
        (r"/size/([\d|k|m]+).*", SizeHandler),
        (r"/slow/(\d+)-?(\d+)?.*", SlowHandler),
        (r"/redirect/(.*)", RedirectHandler),
        (r"/*", MainHandler),
    ],
    **SETTINGS,
)

if __name__ == "__main__":
    if not options.port:
        options.print_help()
        sys.exit()

    if options.ip:
        APP.listen(options.port, address=options.ip)
    else:
        APP.listen(options.port)

    tornado.ioloop.IOLoop.instance().start()
