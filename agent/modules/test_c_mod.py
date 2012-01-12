import ctypes

from lazy import memoized

class foo(ctypes.Structure):
    _fields_ = (('v', ctypes.c_int),
               ('c', ctypes.c_char))

def test_hello():
    m = ctypes.cdll.LoadLibrary('./foo.so')

    f = foo.in_dll(m, 'crash')
    print f.v, f.c

    hello = m.hello
    hello.argtypes = [ctypes.POINTER(ctypes.c_char_p), ctypes.c_int]
    hello.restype = ctypes.c_int

    p = ctypes.c_char_p(0)
    r = hello(ctypes.pointer(p), 7)
    print r, repr(p.value)

    destory = m.destory
    destory.argtypes = [ctypes.c_char_p]
    destory(p)

    world = m.world
    world.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_int]
    world.restype = ctypes.c_int

    p = ctypes.c_void_p(0)
    r = world(ctypes.pointer(p), 7)
    print r, repr(p.value)

    destory(ctypes.c_char_p(p.value))

# test_hello()

class apr(object):
    @classmethod
    def init(cls):
        cls.mod = ctypes.cdll.LoadLibrary('libapr-1.so.0')
        cls.apr_pool_initialize = cls.mod.apr_pool_initialize
        cls.apr_pool_terminate = cls.mod.apr_pool_terminate

        cls.apr_pool_create = cls.mod.apr_pool_create_ex
        cls.apr_pool_create.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p,  ctypes.c_void_p, ctypes.c_void_p]
        cls.apr_pool_create.restype = ctypes.c_int

        #
        cls.apr_pool_destroy = cls.mod.apr_pool_destroy
        cls.apr_pool_destroy.argtypes = [ctypes.c_void_p]

    @classmethod
    def pool_create(cls):
        cls.apr_pool_initialize()
        nil = ctypes.c_void_p(0)
        pool = ctypes.c_void_p(0)
        status = cls.apr_pool_create(ctypes.pointer(pool), nil, nil, nil)
        return pool

    @classmethod
    def pool_destroy(cls, pool):
        cls.apr_pool_destroy(pool)
        cls.apr_pool_terminate()

def test_class_apr():
    apr.init()
    p = apr.pool_create()
    apr.pool_destroy(p)

def test_apr():
    apr = ctypes.cdll.LoadLibrary('libapr-1.so.0')

    #
    apr_pool_initialize = apr.apr_pool_initialize
    apr_pool_initialize.restype = ctypes.c_int

    #
    apr_pool_terminate = apr.apr_pool_terminate

    #
    apr_pool_create = apr.apr_pool_create_ex
    apr_pool_create.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p,  ctypes.c_void_p, ctypes.c_void_p]
    apr_pool_create.restype = ctypes.c_int

    #
    apr_pool_destroy = apr.apr_pool_destroy
    apr_pool_destroy.argtypes = [ctypes.c_void_p]

    #
    apr_pool_initialize()

    nil = ctypes.c_void_p(0)

    pool = ctypes.c_void_p(0)
    ppool = ctypes.pointer(pool)
    print pool, ppool.contents

    status = apr_pool_create(ppool, nil, nil, nil)
    print status, pool

    apr_pool_destroy(pool)

    apr_pool_terminate()


class Ganglia_25metric(ctypes.Structure):
    _fields_ = [('key', ctypes.c_int),
                ('name', ctypes.c_char_p),
                ('tmax', ctypes.c_int),
                ('type', ctypes.c_int), # Ganglia_value_types
                ('units', ctypes.c_char_p),
                ('slope', ctypes.c_char_p),
                ('fmt', ctypes.c_char_p),
                ('msg_size', ctypes.c_int),
                ('desc', ctypes.c_char_p),
                ('metadata', ctypes.POINTER(ctypes.c_int))
                ]
    def __repr__(self):
        return "<metric> %s(%s) %s %d" % (self.name, self.desc, 
                                          self.key, self.type)
MAX_G_STRING_SIZE = 32

class val(ctypes.Union):
    _fields_ = [('int8',  ctypes.c_char),
                ('int16', ctypes.c_int16),
                ('uint16', ctypes.c_uint16),
                ('int32', ctypes.c_int32),
                ('uint32', ctypes.c_uint32),
                ('f', ctypes.c_float),
                ('d', ctypes.c_double),
                ('str', ctypes.c_char * MAX_G_STRING_SIZE)
                ]

    def raw(self, type):
        table = {1: 'str',
                 2: 'uint16',
                 3: 'int16',
                 4: 'uint32',
                 5: 'int32',
                 6: 'f',
                 7: 'd'}
        if type in table:
            return getattr(self, table[type])
        else:
            raise ValueError('type %r error' % type)

MMODULE_MAGIC_COOKIE = 0x474D3331

class mmodule(ctypes.Structure):
    _fields_ = [('version', ctypes.c_int),
                ('minor_version', ctypes.c_int),
                ('name', ctypes.c_char_p),
                ('dynamic_load_handle', ctypes.c_void_p),
                ('module_name', ctypes.c_char_p),           # None
                ('metric_name', ctypes.c_char_p),           # None
                ('module_params', ctypes.c_char_p),         # None
                ('module_params_list', ctypes.c_void_p),    # None
                ('config_file', ctypes.c_void_p),           # None
                ('next', ctypes.c_void_p), # TODO: cast
                ('magic', ctypes.c_ulong),
                ('init', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)), #
                ('cleanup', ctypes.CFUNCTYPE(None)), #
                ('metrics_info', ctypes.POINTER(Ganglia_25metric)),
                ('handler', ctypes.CFUNCTYPE(val, ctypes.c_int))
                ]
    def __repr__(self):
        return '<mmodule> %s %r' % (self.name, self.metrics_info.contents)

    def build_metric_list(self):
        cbs = []
        i = 0
        while True:
            cbs.append((i, self.metrics_info[i], self.handler))

            i += 1
            if not self.metrics_info[i].name:
                break
        return cbs

    def __len__(self):
        if not hasattr(self, '_ml'):
            setattr(self, '_ml', self.build_metric_list())
        return len(self._ml)

    def run(self, index):
        if not hasattr(self, '_ml'):
            setattr(self, '_ml', self.build_metric_list())

        i, info, handler = self._ml[index]
        r = handler(i)
        return info.name, info.fmt % r.raw(info.type)

@memoized
def global_pool():
    apr.init()
    return apr.pool_create()

def test_load(preload, name = 'load_module', so = './modload.so'):
    # 1 load
    if preload:
        g = ctypes.cdll.LoadLibrary(preload)
    print g.debug_msg
    mod = ctypes.cdll.LoadLibrary(so)
    mm = mmodule.in_dll(mod, name)
    print repr(mm)
    
    # 2 setup_metric_callbacks
    ret = mm.init(global_pool())
    assert ret == 0
    
    i = 0
    while True:
        print i, mm.metrics_info[i].name, mm.handler(i)

        i += 1
        if not mm.metrics_info[i].name:
            break
    
    print len(mm)

    # 3 run once
    for x in xrange(len(mm)):
        print mm.run(x)

import sys
try:
    test_load(sys.argv[1], sys.argv[2], sys.argv[3])
except:
    pass

f= open('/proc/self/maps', 'rb')
print f.read()
