import os, sys, glob
import logging

import apachelog
import core

_pipes = []
"""
log_format tjmain '[$time_local] $status $host '
                      '$upstream_addr $upstream_response_time $request_time '
                      '$remote_addr $remote_user $request '
                      '$bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"'
[17/Jan/2012:17:00:55 +0800] 304 10.2.76.28 - - 0.000 10.2.76.25 - GET /highcharts/js/modules/exporting.js HTTP/1.1 158 "http://10.2.76.28/highcharts/examples/bar-basic.htm" "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.75 Safari/535.7" "-"sendfileon

format = r'%t %>s %h %uh %urt %addr %ru \"%r\" %b \"%{Referer}i\" \"%{User-Agent}i\" \"{Forward}\"'

#default
format = r'%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\" \"{Forward}\"'
"""

format = r'%t %>s %h %ua %ub %uc %v %vu %m %mu %mv %b \"%{Referer}i\" \"%{User-Agent}i\" \"{Forward}\"'
parser = apachelog.parser(format)

def run(f):
    for line in f:
        if not line:
            continue
        try:
            data = parser.parse(line)
            data = [v for k,v in data]
        except apachelog.ApacheLogParserError:
            continue

        for p in _pipes:
            # TODO: try
            p.process(data)

    for p in _pipes:
        for k, d in p.result():
            core.update(k, d)

        logging.debug('pipe run %s: %r', k, d)

def add(m):
    _pipes.append(m)

def _init():
    # dir = os.path.join(os.path.dirname(__file__), 'pipes')
    dir = 'pipes'
    pattern = os.path.join(dir, '*.py')
    for f in glob.glob(pattern):
        name,_ =  os.path.splitext(f)
        name = name.replace('/', '.')

        if name[-1] == '_': continue # remove __init__.py
        try:
            # print name
            m = __import__(name, globals())
        except Exception,e:
            logging.debug('module %s load failure %r' % (name, e))
            continue

        _, base = name.split('.')
        _pipes.append(getattr(m, base))

    logging.debug('installed pipes via init:  %r', _pipes)
    print _pipes

print 'import once'
_init()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    """
    _init()
    logging.debug('installed pipes via init:  %r', _pipes)

    

    name = '/data/nginx/logs/access.log'
    if len(sys.argv) > 1:
        name = sys.argv[1]
    f = open(name, 'rb')
    run(f)

    print 'result:\n', core._tree
    """

    format = r'%t %>s %h %ua %ub %uc %v %vu %m %mu %mv %b \"%{Referer}i\" \"%{User-Agent}i\" \"{Forward}\"'

    temp_log = '[17/Jan/2012:17:00:55 +0800] 304 10.2.76.28 - - 0.000 10.2.76.25 - GET /highcharts/js/modules/exporting.js HTTP/1.1 158 "http://10.2.76.28/highcharts/examples/bar-basic.htm" "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.75 Safari/535.7" "-"'

    arr = [
           (r'%t %>s %h %ua',               '[17/Jan/2012:17:37:26 +0800] 200 hdn.xnimg.cn 10.22.200.100:80'),
           (r'%t %>s %h %ua %ub %uc',       '[17/Jan/2012:17:37:26 +0800] 200 hdn.xnimg.cn 10.22.200.100:80 0.001 0.001'),
           (r'%t %>s %h %ua %ub %uc %v',    '[17/Jan/2012:17:37:26 +0800] 200 hdn.xnimg.cn 10.22.200.100:80 0.001 0.001 183.213.96.62'),
           (r'%t %>s %h %ua %ub %uc %v %vu %m %mu %mv',          '[17/Jan/2012:17:37:26 +0800] 200 hdn.xnimg.cn 10.22.200.100:80 0.001 0.001 183.213.96.62 - GET /photos/hdn421/20120110/1550/h_head_FluE_718e0002e7ff2f76.jpg HTTP/1.1'),
           (r'%t %>s %h %ua %ub %uc %v %vu %m %mu %mv %b \"%{Referer}i\" \"%{User-Agent}i\" \"{Forward}\"',          '[17/Jan/2012:17:37:26 +0800] 200 hdn.xnimg.cn 10.22.200.100:80 0.001 0.001 183.213.96.62 - GET /photos/hdn421/20120110/1550/h_head_FluE_718e0002e7ff2f76.jpg HTTP/1.1 4428 "http://www.renren.com/419816894" "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; 360SE)" "-"'),
           # (format, '[17/Jan/2012:17:37:26 +0800] 400 _* - - 0.000 117.136.16.118 - - 0 "-" "-" "-"'),
           (format, '[17/Jan/2012:17:37:26 +0800] 200 hdn.xnimg.cn 10.22.200.100:80 0.001 0.001 183.213.96.62 - GET /photos/hdn421/20120110/1550/h_head_FluE_718e0002e7ff2f76.jpg HTTP/1.1 4428 "http://www.renren.com/419816894" "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; 360SE)" "-"')
           ]

    for f, log in arr:
        print apachelog.parser(f).parse(log)

    import sys
    if len(sys.argv) > 1:
        run(open(sys.argv[1], 'rb'))
    print 'result:\n', core._tree