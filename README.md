Q: Why named sloth?  
A: An animal, just pick from film of Ice Age.  
  
tree  
----  
<pre>
{'cpu': {'10.3.1.12': {'idle': {'count': 32},  
                       'sytem': {'count': 29},  
                       'user': {'count': 900,  
                                'marker': 'sth. wrong happened'}}},  
 'defaultaction': 'average'}  
  
br--  ie--  6-- {count: 3}  
            7-- {count: 8}  
            7-- venders-- sogou-- {count 1}  
      webkit--  chrome--  14.0--  {count: 40}  
                          13.0--  {count: 20}  
</pre>  
  
br,,chrome  
br,ie,6  
  
  
  
directory layout
================
# agent  
agent/  
agent/modules/*.py *.so  
  support ganglia module  
agent/conf/*.conf *.on *.off  
agent/agent.conf  

setup.py  
easy_install | pip install   
big [egg|zip] with pip and dependence packages ...  
  
  
# server
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
/get/?key-br,ie,7  
  response immediatly in json list  
/realtime/view/name  
  view by name, per user's specify  
  
/trend/view/ [default in one year]  
  left tree | right (multi) js graph (zoomable highcharts/examples/dynamic-master-detail.htm)  
/trend/view/name?  
  one js graph  
  add compare | zoomable | setting style ...  
/setting/view  
  add | remove view  
  
  
/diff/keya/keyb  
/graph  
</pre>
  
  
  
server push
-----------
udp  
tcp  
http post in form  
  
socket
------
  
  
  
modules
-------
<pre>
web access log(raw)  
nginx stats  
  network traffic(bytes, same as gangalia)  
url(time to first byte, status code, bytes, ...)  
? cpu/load  
  
? python modules/*.py --check --test ....  
  
write your own module(same as ganglia module):  
  def metric_init({})  
  def metric_cleanup()  
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
  
interval
--------
agent push  
pipe process  
