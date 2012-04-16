import optparse
import sys
import time
import glob
import os.path
import logging
import json
import urllib2, urllib

import yaml

def push_once(url, tree):
    s = json.dumps({'foo.54': tree})
    s = urllib.urlencode({"json": s})
    f = urllib2.urlopen(url, s)
    f.read()

class PythonModules():
    def __init__(self):
        self._modules = {}

    def modules(self, path=None):
        if path is None:
            path = os.path.join(os.path.dirname(__file__), 'modules')

        for f in glob.glob('%s/*.py' % path):
            name,_ =  os.path.splitext(os.path.basename(f))
            if name == '__init__':
                continue

            yield 'peach.agent.modules.%s' % name

    def load(self, module_name):
        try:
            mod = __import__(module_name, None, None, ['metric_init'])
            # print module_name, dir(mod)
        except ImportError, err:
            logging.exception('%s import failed' % mod_name)
            raise

        self._modules[module_name] = mod
        return mod

    def load_all(self):
        for name in self.modules():
            self.load(name)

    def run(self):
        tree = {}
        for mod_name, mod in self._modules.iteritems():
            try:
                desc = mod.metric_init([]) # TODO: use pyconf as params

                for d in desc:
                    name = d['name']
                    r = d['call_back'](name)
                    tree.setdefault(name, float(d['format'] % r))
            except Exception:
                logging.exception('%s run failed' % mod_name)
                logging.debug(dir(mod))
        return tree

def main(args):
    logging.basicConfig(level=logging.DEBUG)

    parser = optparse.OptionParser()
    parser.add_option("-l", "--list", action="store_true", 
                      dest="list_only",
                      help="list all python modules")
    parser.add_option("-c", "--config", 
                      help="config file")
    parser.add_option("-f", "--foreground", dest="daemon", 
                      action='store_false',
                      help="run in foregroud(not daemon)")
    parser.add_option("-i", "--interval", dest="interval", 
                      default=30,
                      help="run modules once every seconds")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    parser.add_option("-m", "--module", dest="modules", action="append",
                      help="run module once")
    parser.add_option("-s", "--server", dest="server",
                      help="server to push")

    (options, agent_args) = parser.parse_args(args)

    pm = PythonModules()

    if options.list_only:
        for x in pm.modules():
            print '\t', x
        return 0

    if options.modules:
        for mod_name in options.modules:
            pm.load(mod_name)
    else:
        pm.load_all()

    if not options.server:
        # print 'load modules', pm._modules
        tree = pm.run()
        yaml.dump(tree, sys.stdout, explicit_start=True)#, canonical=True)
        return 0

    if options.daemon:
        createDaemon()

    url = options.server
    interval = options.interval
    while pm._modules:
        start = time.time()

        tree = pm.run()
        push_once(url, tree)

        
        time.sleep(max(interval, interval - (time.time() - start)))
