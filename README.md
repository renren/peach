
core / engine
=============
The system contain a HUGE tree in memroy.

<pre>
[
{'cpu': {'10.3.1.12': {'idle': 32,
                       'sytem': 29,
                       'user': 900,
                       'marker': 'sth. wrong happened'}},
  'defaultaction': 'average'},
{'br':  {'ie':  {'6': 3},
                {'7': 8, {'venders':{'sogou':2}}},
                {'7' : {'venders':{'sogou':1}}}},
      {'webkit': {'14.0': 40},
                {'13.0': 20}},
  'defaultaction': 'add'}
]
</pre>

Query by key name as form like:

* br,webkit

* br,ie,,venders,sogou


More detail in [server/tree.py](blob/master/server/tree.py)



server
======
directory layout
-----------------
<pre>
server/
  main.py
  tree.py -> async store in trend db
  treedb.py
  pushviahttp.py
  pushviasocket.py

server/pipes/*.py
server/web
  web/pages.py
  web/trend.py
server/web/static/*.js *.css *.html
server/web/templates/*.html
server/graph
server/graph/styles.py
  cpu|net|url|default
  input: tree
    bar|line|x-axis|marker range,picture|theme...|format
  output: png|pdf


# relay server
--relay
? agent/conf/relay.conf
</pre>

url map
=======
request argument name style like: e or a,b or a,,c
<pre>
/push
  form field support json/accesslog
  json -> merge into core tree
  accesslog -> pipes -> tree -> merge into core tree

/pull/?key-br
/pull/?key-br,ie
/pull/?key-br,ie,7
  comet, repsonse in json list
    [{br,ie,7 : 2328},
    {br,ie,sogou,3 : 323}]
/get/<name>
  response immediatly in json list
/realtime/<key>
  page, init with /get/<key>
  then comet by /pull/<key>
/realtime/view/<key>
  view by name, per user's specify

/trend/view/
  [default in one year]
  left tree | right (multi) js graph (zoomable highcharts/examples/dynamic-master-detail.htm)
/trend/view/<name>?
  one js graph
  add compare | zoomable | setting style ...
/trend/<name>?time
/setting/view
  add | remove view


/diff/keya/keyb
/graph/<name>[.jpg|.png|.svg]
</pre>

pipes
------
<pre>web access log
  browser type  -> tree
  os type       -> tree
  upstream time  -> tree
  request time
  response bytes
  url count
  error count
  ? geo

write your own pipe.py
  def init()
  def process(arr)
  def cleanup()

running mode:
init:
  for m in pipes/*.py:
    pipes.push(m)
    m.init()

run:
  for line in log.read():
    arr - weblog.parse(line)
    for m in pipes:
      m.process(arr)	
</pre>

server push
-----------
* udp

* tcp

* http post in form



Agent
=====
directory
---------
<pre>
agent/
agent/modules/*.py *.so  
  support ganglia module
agent/conf/*.conf *.on *.off
agent/agent.conf

agent/setup.py
</pre>

modules
-------
<pre>
web access log(raw)
url(time to first byte, status code, bytes, ...)
  nginx stats

write your own module(same as [ganglia python module](http://sourceforge.net/apps/trac/ganglia/wiki/ganglia_gmond_python_modules#WritingcustomPythonmodules)):
  def metric_init({})
  def metric_cleanup()
</pre>

reminder 
=====================
A: use ganglia-plugin.
build a package named 'ganglia-plugin'
? use ganglia-plugin only

1) LD_PRELOAD=libganglia.so python
  modload.so
  modcpu.so

2) rebuild modxxx.so
3) ganglia install path/*.so 



A: PUT/POST, socket

x post file in form
? HTTP POST raw body
? HTTP PUT
 socket
  tornado socket
  libevent socket + flask
x web socket

A:
1 web log => graph
 


