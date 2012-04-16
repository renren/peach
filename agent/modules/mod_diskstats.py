import time

def diskstats():
    file_path = '/proc/diskstats'

    """
    http://lxr.osuosl.org/source/Documentation/iostats.txt
    Field 1 -- # of reads completed
    Field 2 -- # of reads merged, field 6 -- # of writes merged
    Field 3 -- # of sectors read
    Field 4 -- # of milliseconds spent reading

    Field 5 -- # of writes completed
    Field 7 -- # of sectors written
    Field 8 -- # of milliseconds spent writing

    Field 9 -- # of I/Os currently in progress
    Field 10 -- # of milliseconds spent doing I/Os
    Field 11 -- weighted # of milliseconds spent doing I/Os
    """
    columns_disk = ['major_dev_num', 'minor_dev_num', 'device', 
                    'reads', 'reads_merged', 'sectors_read', 'ms_reading', 
                    'writes', 'writes_merged', 'sectors_written', 'ms_writing', 
                    'current_ios', 'ms_doing_io', 'weighted_ms_doing_io']
    columns_partition = ['major_dev_num', 'minor_dev_num', 'device', 'reads', 'sectors_read', 'writes', 'sectors_written']

    result = {}
    for line in (l for l in open(file_path, 'r').xreadlines() if l != ''):
        parts = line.split()
        if len(parts) == len(columns_disk):
            columns = columns_disk
        elif len(parts) == len(columns_partition):
            columns = columns_partition
        else:
            continue
        data = dict(zip(columns_disk, parts))
        result[data['device']] = dict((k, int(v)) for k, v in data.iteritems() if k != 'device')
    return result

class CachedWithTimeout(object):
    """Memoize With Timeout"""
    _caches = {}
    _timeouts = {}
    
    def __init__(self, timeout=2):
        self.timeout = timeout
        
    def collect(self):
        """Clear cache of results which have timed out"""
        for func in self._caches:
            cache = {}
            for key in self._caches[func]:
                if (time.time() - self._caches[func][key][1]) < self._timeouts[func]:
                    cache[key] = self._caches[func][key]
            self._caches[func] = cache
    
    def __call__(self, f):
        self.cache = self._caches[f] = {}
        self._timeouts[f] = self.timeout
        
        def func(*args, **kwargs):
            kw = kwargs.items()
            kw.sort()
            key = (args, tuple(kw))
            try:
                v = self.cache[key]
                if (time.time() - v[1]) > self.timeout:
                    raise KeyError
            except KeyError:
                v = self.cache[key] = f(*args,**kwargs),time.time()
            return v[0]
        func.func_name = f.func_name        
        return func

@CachedWithTimeout(timeout=2)
def stats_filter_sd():
    return dict( (k,v) for k,v in diskstats().iteritems() if k.startswith('sd') )

def metric_read(name):
    dev, key = name.split('.')
    return stats_filter_sd()[dev][key]

def metric_init(params):
    t = {'name': None,
        'call_back': metric_read,
        'time_max': 90,
        'value_type': 'uint',
        'units': 'MB',
        'slope': 'both',
        'format': '%u',
        'description': None,
        'groups': 'disk'}
    stats = stats_filter_sd()
    ret = []
    for dev, d in stats.iteritems():
        for k,v in d.iteritems():
            a = dict(t)
            a.update({'name': '%s.%s' % (dev, k), 'description':k})
            ret.append(a)
    return ret

def metric_cleanup():
    pass

if __name__ == '__main__':
    ds = metric_init(None)
    for d in ds:
        v = d['call_back'](d['name'])
        print 'value for %s is %u' % (d['name'],  v)
