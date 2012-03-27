import os, sys, glob
import logging

import lazy
import apachelog
import core

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
    count_line, count_failed = 0, 0
    for line in f:
        if not line:
            continue
        try:
            count_line += 1
            data = parser.parse(line)
            data = [v for k,v in data]
        except apachelog.ApacheLogParserError:
            #logging.exception('pipeline parse')
            count_failed += 1
            continue

        for p in pipes():
            try:
                p.process(data)
            except:
                logging.exception('pipeline process')

    for p in pipes():
        for k, d in p.result():
            core.update(k, d)
            
    logging.debug('pipe process %d line, %d failed', count_line, count_failed)

@lazy.memoized
def pipes():
    _pipes = []
    # TODO:  walk all pipes.*.py files and auto import it
    arr = ['pipes.to_ua', 'pipes.time']
    for name in arr:
        try:
            __import__(name)
        except ImportError:
            sys.modules.pop(name, None)
            continue

        m = sys.modules[name]
        if m.can_register:
            _pipes.append(m)
        else:
            sys.modules.pop(name, None)

    logging.debug('installed pipes: %r', _pipes)
    return _pipes


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

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
        apachelog.parser(f).parse(log)

    import sys
    if len(sys.argv) > 1:
        f = open(sys.argv[1], 'rb')
    else:
        f = sys.stdin

    run(f)

    print 'result:\n',
    import pprint
    pprint.pprint(core._tree)
