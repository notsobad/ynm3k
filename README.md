# YNM3K
A Fakesite for http test, see also [go-fakesite](https://github.com/notsobad/go-fakesite).

	docker run -p 9527:80 notsobad/ynm3k

    curl http://127.0.0.1:9527/


Also you can build it yourself

	cd ynm3k
	docker build -t ynm3k .
	docker run -it --rm -p 9527:80 ynm3k


A demo page with http 502 response:

	wangxh:~/myapp/ynm3k$ curl 127.1:9527/code/502.jpg -vv
	> GET /code/502.jpg HTTP/1.1
	> User-Agent: curl/7.30.0
	> Host: 127.1:9527
	> Accept: */*
	>
	< HTTP/1.1 502 Bad Gateway
	< Content-Length: 62
	< Set-Cookie: csrftoken=8e0f2f299fede170969578ebceec0967; expires=Thu, 09-Jan-2014 06:29:39 GMT; Max-Age=31449600; Path=/
	< Vary: Accept-Encoding
	< Server: YNM3000
	< Date: Wed, 14 May 2014 09:25:11 GMT
	< Content-Type: text/html; charset=UTF-8
	<
	<h1>Http 502</h1> <hr/>Generated at 2014-05-14 17:25:11.603423

## Trace

Show raw request header.

/trace/

* http://ynm3k.notsobad.vip/trace/123.php


# Static file

Visit same url, get same result

/static/$RANDOM.$EXT

* http://ynm3k.notsobad.vip/static/abc.zip
* http://ynm3k.notsobad.vip/static/xyz.html
* http://ynm3k.notsobad.vip/static/1234.js

## Dynamic url

Visit same url, get different result

/dynamic/$RANDOM.$EXT

* http://ynm3k.notsobad.vip/dynamic/abc.php
* http://ynm3k.notsobad.vip/dynamic/abc.jsp

## HTTP status code
/code/$CODE.$EXT

* http://ynm3k.notsobad.vip/code/500.php
* http://ynm3k.notsobad.vip/code/404.asp

## Specified size response
You can output a file of the specified size.

/size/$SIZE.$EXT

* http://ynm3k.notsobad.vip/size/11k.zip
* http://ynm3k.notsobad.vip/size/1m.bin
* http://ynm3k.notsobad.vip/size/1024.rar

## A server with a slow response

Visit `/slow/$SECONDS`, the url will take $SECONDS time to render.

* http://ynm3k.notsobad.vip/slow/3
* http://ynm3k.notsobad.vip/slow/4-10


## URL redirect
All kinds of url redirect method

* http://ynm3k.notsobad.vip/redirect/301?url=http://www.notsobad.vip  301
* http://ynm3k.notsobad.vip/redirect/302?url=http://www.notsobad.vip  302
* http://ynm3k.notsobad.vip/redirect/js?url=http://www.notsobad.vip javascript
* http://ynm3k.notsobad.vip/redirect/meta?url=http://www.notsobad.vip html meta

DEMO:

    curl -v 'localhost:9527/redirect/301?url=file:///etc/passwd'
    curl -v 'localhost:9527/redirect/302?url=http://www.jiasule.com'
