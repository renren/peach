from httpagentparser import DetectorsHub, DetectorBase, detect, detectorshub, Browser

def init():
    #import sys
    #for v in globals().values():
    #	print v, type(v), getattr(v, '__mro__', [])
    if 'vendor' in detectorshub._known_types:
    	return
    detectors = [v() for v in globals().values() if DetectorBase in getattr(v, '__mro__', [])]
    for d in detectors:
        if d.can_register:
            detectorshub.register(d)

class Vendor(DetectorBase):
    info_type = "vendor"
    can_register = False

STRIPED = '); \r\n'

class Maxthon(Vendor):
    look_for = 'Maxthon'
    prefs = dict(browser=['MSIE', 'Safari'])

    def getVersion(self, agent):
        if "%s/" % self.look_for in agent:
            return agent.split('%s/' % self.look_for)[-1].split(' ')[0].strip(STRIPED)
        else:
            return agent.split('%s ' % self.look_for)[-1].split(' ')[0].strip(STRIPED)

class Tencent(Vendor):
    look_for = 'TencentTraveler'
    prefs = dict(browser=['MSIE', 'Safari'])
    def getVersion(self, agent):
        if "%s/" % self.look_for in agent:
            return agent.split('%s/' % self.look_for)[-1].split(' ')[0].strip(STRIPED)
        else:
            return agent.split('%s ' % self.look_for)[-1].split(' ')[0].strip(STRIPED)

class Sogou(Vendor):
    look_for = 'MetaSr'
    prefs = dict(browser=['MSIE', 'Safari'])
    def getVersion(self, agent):
        return agent.split('%s ' % self.look_for)[-1].split(' ')[0].strip(STRIPED)

class Baidu(Vendor):
    look_for = 'baidubrowser'
    prefs = dict(browser=['MSIE', 'Safari'])
    def getVersion(self, agent):
        return agent.split('%s ' % self.look_for)[-1].split(' ')[0].strip(STRIPED)

class UCWEB(Browser):
    look_for = 'UCWEB'
    #prefs = dict(browser=['Opera'])
    def getVersion(self, agent):
        # NokiaE63/UCWEB7.2.2.51/28/800
        # UCWEB8.2.0.116/50/999
        # Nokia 5320/UCWEB7.5.0.66/28/800
        a = agent.find(self.look_for)
        b = agent.find('/', a)
        return agent[a + len(self.look_for) : b]

class Nokia(Vendor):
    look_for = 'Nokia'
    prefs = dict(browser=['Safari'])
    def getVersion(self, agent):
        # Nokia500/010.029
        a = agent.find(self.look_for)
        b = agent.find('/', a)
        if b == -1:
            b = agent.find('"', a)
        if b != -1:
            return agent[a + len(self.look_for) : b].strip('); ')
        else:
            return 'Unknown'

init()

if __name__ == '__main__':
    import time
    import unittest

    data = (
("Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; Maxthon 2.0)",
       ('Windows NT 5.1', 'MSIE 7.0'),
       {'os': {'version': 'NT 5.1', 'name': 'Windows'}, 'browser': {'version': '7.0', 'name': 'MSIE'}}),
("Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; MyIE2)",
    (),{}),
("Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.4 (KHTML, like Gecko) Maxthon/3.0.6.27 Safari/532.4",
    (),{}),
)

    class TestHAP(unittest.TestCase):
        def setUp(self):
            self.harass_repeat = 1000
            self.data = data

        def test_simple_detect(self):
            for agent, simple_res, res in data:
                self.assertEqual(simple_detect(agent), simple_res)

        def test_detect(self):
            for agent, simple_res, res in data:
                self.assertEqual(detect(agent), res)

        def test_harass(self):
            then = time.time()
            for agent, simple_res, res in data * self.harass_repeat:
                detect(agent)
            time_taken = time.time() - then
            no_of_tests = len(self.data) * self.harass_repeat
            print "\nTime taken for %s detecttions: %s" % (no_of_tests, time_taken)
            print "Time taken for single detecttion: ", time_taken / (len(self.data) * self.harass_repeat)

    # unittest.main()
    """
    for agent, simple_res, res in data:
        print detect(agent)

    print 
    print '\n\n'
    print detectorshub
    """

    import sys
    for line in sys.stdin:
        #print line
    	#print detect(line)['engine']
        if 'engine' not in detect(line):
            print line
