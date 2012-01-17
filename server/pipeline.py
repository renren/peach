import os, sys, glob
import logging

import apachelog
import core

_pipes = []

format = r'%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\" \"{Forward}\"'
parser = apachelog.parser(format)

def run(f):
    for line in f:
        if not line:
            continue
        data = parser.parse(line)

        for p in _pipes:
            # TODO: try
            p.process(data.values())

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

_init()


if __name__ == '__main__':
    import sys
    logging.basicConfig(level=logging.DEBUG)

    _init()
    logging.debug('installed pipes via init:  %r', _pipes)

    name = '/data/nginx/logs/access.log'
    if len(sys.argv) > 1:
        name = sys.argv[1]
    f = open(name, 'rb')
    run(f)

    print 'result:\n', core.tree