# A dynamic website for test purpose

集多种杀人武器于一身的终极武器：“要你命3000”！

用torando搭建的一个web应用，模拟某些规则的url，可以用于cdn、waf系统的测试用途。

客户端请求符合某些规则的url，服务端能做出适当响应，输出对应内容。

样例：

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

## 静态文件

同一url, 不同请求会输出相同响应。

/static/$RANDOM.$EXT

* /static/abc.zip
* /static/xyz.html
* /static/1234.js

## 动态文件

同一url, 不同请求会输出不同响应。

/dynamic/$RANDOM.$EXT

*  /dynamic/abc.php
*  /dynamic/abc.jsp

## HTTP状态码
/code/$CODE.$EXT

* /code/500.php
* /code/404.asp

## 指定大小文件

可以输出指定大小的文件。

/size/$SIZE.$EXT

* /size/11k.zip
* /size/1m.bin
* /size/1024.rar

## 模拟慢后端
模拟一个需要n秒的响应`/slow/$SECONDS`, 模拟一个耗时在一个时间范围内的响应`/slow/$START-$END`

* /slow/3
* /slow/4-10

python版本这个高并发下可能性能较弱，增加了一个nginx-lua版本，参考nginx-ynm3k.conf, 接口如下：
* /slow?r=3
* /slow?r=3-10

## 模拟HTTP跳转
模拟各种情况的HTTP跳转

* /redirect/301?url=http://www.notsobad.me  301跳转
* /redirect/302?url=http://www.notsobad.me  302跳转
* /redirect/js?url=http://www.notsobad.me javascript跳转
* /redirect/meta?url=http://www.notsobad.me html meta跳转

样例：

    curl -v 'localhost:9527/redirect/301?url=file:///etc/passwd'
    curl -v 'localhost:9527/redirect/302?url=http://www.jiasule.com'
