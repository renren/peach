import os
import re
import sys
import time

last_uptime = 0
last_poll_time = 0

old_stats = {
    'io_util_sda':0.0,
    'io_util_sdb':0.0,
    'io_util_sdc':0.0,
    'io_util_sdd':0.0,
    'io_util_sde':0.0,
    'io_util_sdf':0.0,
    'io_util_sdg':0.0,
    'io_util_sdh':0.0,
    'io_util_sdi':0.0,
    'io_util_sdj':0.0,
    'io_util_sdk':0.0,
    'io_util_sdl':0.0,
    'io_util_c0d0':0.0,
    'io_util_c0d1':0.0,
    'io_util_c0d2':0.0,
    'io_util_c0d3':0.0,
    'io_util_c0d4':0.0,
    'io_util_c0d5':0.0,
    'io_util_c0d6':0.0,
    'io_util_c0d7':0.0,
    'io_util_c0d8':0.0,
    'io_util_c0d9':0.0,
    'io_util_c0d10':0.0,
    'io_util_c0d11':0.0,
}

new_stats = {
    'io_util_sda':0.0,
    'io_util_sdb':0.0,
    'io_util_sdc':0.0,
    'io_util_sdd':0.0,
    'io_util_sde':0.0,
    'io_util_sdf':0.0,
    'io_util_sdg':0.0,
    'io_util_sdh':0.0,
    'io_util_sdi':0.0,
    'io_util_sdj':0.0,
    'io_util_sdk':0.0,
    'io_util_sdl':0.0,
    'io_util_c0d0':0.0,
    'io_util_c0d1':0.0,
    'io_util_c0d2':0.0,
    'io_util_c0d3':0.0,
    'io_util_c0d4':0.0,
    'io_util_c0d5':0.0,
    'io_util_c0d6':0.0,
    'io_util_c0d7':0.0,
    'io_util_c0d8':0.0,
    'io_util_c0d9':0.0,
    'io_util_c0d10':0.0,
    'io_util_c0d11':0.0,
}

ioutil = {
    'io_util_sda':0.0,
    'io_util_sdb':0.0,
    'io_util_sdc':0.0,
    'io_util_sdd':0.0,
    'io_util_sde':0.0,
    'io_util_sdf':0.0,
    'io_util_sdg':0.0,
    'io_util_sdh':0.0,
    'io_util_sdi':0.0,
    'io_util_sdj':0.0,
    'io_util_sdk':0.0,
    'io_util_sdl':0.0,
    'io_util_c0d0':0.0,
    'io_util_c0d1':0.0,
    'io_util_c0d2':0.0,
    'io_util_c0d3':0.0,
    'io_util_c0d4':0.0,
    'io_util_c0d5':0.0,
    'io_util_c0d6':0.0,
    'io_util_c0d7':0.0,
    'io_util_c0d8':0.0,
    'io_util_c0d9':0.0,
    'io_util_c0d10':0.0,
    'io_util_c0d11':0.0,
}

disk_dev = ['sda', 'sdb', 'sdc', 'sdd', 'sde', 'sdf', 'sdg', 'sdh', 'sdi', 'sdj', 'sdk', 'sdl', 
	'c0d0', 'c0d1', 'c0d2', 'c0d3', 'c0d4', 'c0d5', 'c0d6', 'c0d7', 'c0d8', 'c0d9', 'c0d10', 'c0d11' ]


def metric_update(time):
    global old_stats
    global new_stats
    global last_uptime
    global ioutil

    p = re.compile(r'[\s]+')

    uptime_d = time;

    f = open('/proc/uptime', 'r')
    for l in f:
        line = p.split(l.strip())
        uptime = float(line[0])

        uptime_d = uptime - last_uptime
        last_uptime = uptime
    f.close()


    f = open('/proc/diskstats', 'r')

    new_stats['block_read_rate'] = 0
    new_stats['block_write_rate'] = 0

    for l in f:
	line = p.split(l.strip())
        line[2] = line[2].replace("cciss/", "");
	if line[2] in disk_dev:
            name = 'io_util_' + line[2]

            new_stats[name] = float(line[12])
            ioutil[name] = ( new_stats[name] - old_stats[name] ) / uptime_d / 10
            old_stats[name] =  new_stats[name]
        else:
            continue

    f.close()


def metric_read(name):
    global last_poll_time
    global ioutil
        
    cur_time = time.time()
    
    if cur_time < last_poll_time:
        last_poll_time = cur_time
        return 0
    
    if cur_time - last_poll_time > 2:
        elapsed_time = cur_time - last_poll_time
        last_poll_time = cur_time
        metric_update(elapsed_time)
    
    return ioutil[name]

io_util_sda = {
        'name':'io_util_sda',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }

io_util_sdb = {
        'name':'io_util_sdb',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }

io_util_sdc = {
        'name':'io_util_sdc',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }

io_util_sdd = {
        'name':'io_util_sdd',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }

io_util_sde = {
        'name':'io_util_sde',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }

io_util_sdf = {
        'name':'io_util_sdf',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }

io_util_sdg = {
        'name':'io_util_sdg',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }

io_util_sdh = {
        'name':'io_util_sdh',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }

io_util_sdi = {
        'name':'io_util_sdi',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }

io_util_sdj = {
        'name':'io_util_sdj',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }

io_util_sdk = {
        'name':'io_util_sdk',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }

io_util_sdl = {
        'name':'io_util_sdl',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }

io_util_c0d0 = {
        'name':'io_util_c0d0',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }

io_util_c0d1 = {
        'name':'io_util_c0d1',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }           

io_util_c0d2 = {
        'name':'io_util_c0d2',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }           

io_util_c0d3 = {
        'name':'io_util_c0d3',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }           

io_util_c0d4 = {
        'name':'io_util_c0d4',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }           

io_util_c0d5 = {
        'name':'io_util_c0d5',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }           

io_util_c0d6 = {
        'name':'io_util_c0d6',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }           

io_util_c0d7 = {
        'name':'io_util_c0d7',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }           

io_util_c0d8 = {
        'name':'io_util_c0d8',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }           

io_util_c0d9 = {
        'name':'io_util_c0d9',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }           

io_util_c0d10 = {
        'name':'io_util_c0d10',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }           

io_util_c0d11 = {
        'name':'io_util_c0d11',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'%',
        'slope':'both',
        'format':'%f',
        'description':'io util',
        'groups':'disk'
    }           


descriptors = [];
f = open('/proc/diskstats', 'r')
    
p = re.compile(r'[\s]+')
for l in f:
	line = p.split(l.strip())
	line[2] = line[2].replace("cciss/", "");
        if line[2] in disk_dev:
		disk_name = "io_util_" + line[2]
		descriptors.append(locals()[disk_name])

f.close()


def metric_init(params):
    return descriptors

   
def metric_cleanup():
    pass


if __name__ == '__main__':
    metric_init(None)

    while 1:
        for d in descriptors:
            v = d['call_back'](d['name'])
            print '%s = %f' % (d['name'], v)
        
        time.sleep(3)
        print '-'*11
