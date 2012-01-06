import os, glob, logging
import json
import urllib2, urllib


def push_once(url):
    tree = Agent().run()
    s = json.dumps(tree)
    s = urllib.urlencode({"json": s})
    print s
    f = urllib2.urlopen(url, s)
    print f.read()

def register(f):
    pass


class Agent():
    def __init__(self):
        self.modules = []
        self.init()

    def init(self):
        for f in glob.glob('modules/*.py'):
            name,_ =  os.path.splitext(f)
            name = name.replace('/', '.')
            try:
                m = __import__(name, globals())
            except Exception,e:
                logging.debug('module %s load failure %r' % (name, e))
                continue

            _, base = name.split('.')
            self.modules.append(getattr(m, base))

    def run(self):
        tree = {}
        for m in self.modules:
            try:
                desc = m.metric_init([]) # TODO: use pyconf as params

                for d in desc:
                    name = d['name']
                    r = d['call_back'](name)
                    tree.setdefault(name, d['format'] % r)
            except Exception,e:
                logging.debug('run module %r failed %r' % (m,e))
        return tree

def main():
    push_once('http://10.2.76.28:8000/push')

if __name__ == '__main__':
    # --push
    # --debug -d
    logging.basicConfig(level=logging.DEBUG)
    main()
