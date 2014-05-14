# ynm3k 

集多种杀人武器于一身的终极武器：“要你命3000”！

用torando搭建的一个web服务器，模拟某些规则的url，可以用于cdn、waf系统的测试用途。

客户端请求符合某些规则的url，服务端能做出适当响应，输出合适文件头，输出正文可以为空。

## 任意静态文件
* /static/$RANDOM.zip

## 任意动态文件
*  /dynamic/abc.php
*  /dynamic/abc.jsp

## 任意状态码
* /code/500.php
* /code/404.asp

## 任意大小文件
todo

