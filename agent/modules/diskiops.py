import os
import re
import sys
import time


last_poll_time = 0

old_stats = {
    'block_read_rate':0,
    'block_write_rate':0,
    'block_read_write_rate':0,
}

new_stats = {
    'block_read_rate':0,
    'block_write_rate':0,
    'block_read_write_rate':0,
}

iops = {
    'block_read_rate':0.0,
    'block_write_rate':0.0,
    'block_read_write_rate':0.0,
}

disk_dev = ['sda', 'sdb', 'sdc', 'sdd', 'sde', 'sdf', 'sdg']


def metric_update(time):
    global old_stats
    global new_stats
    global iops

    p = re.compile(r'[\s]+')
    f = open('/proc/diskstats', 'r')

    new_stats['block_read_rate'] = 0
    new_stats['block_write_rate'] = 0

    for l in f:
	line = p.split(l.strip())
	if line[2] in disk_dev:
            new_stats['block_read_rate'] += int(line[3])
            new_stats['block_write_rate'] += int(line[7])
        else:
            continue
        
    new_stats['block_read_write_rate'] = new_stats['block_read_rate'] + new_stats['block_write_rate']

    iops['block_read_rate'] = (float)(new_stats['block_read_rate'] - old_stats['block_read_rate']) / time
    old_stats['block_read_rate'] = new_stats['block_read_rate']
    
    iops['block_write_rate'] = (float)(new_stats['block_write_rate'] - old_stats['block_write_rate']) / time
    old_stats['block_write_rate'] = new_stats['block_write_rate']
    
    iops['block_read_write_rate'] = (float)(new_stats['block_read_write_rate'] - old_stats['block_read_write_rate']) / time
    old_stats['block_read_write_rate'] = new_stats['block_read_write_rate']

    f.close()


def metric_read(name):
    global last_poll_time
    global iops
        
    cur_time = time.time()
    
    if cur_time < last_poll_time:
        last_poll_time = cur_time
        return 0
    
    if cur_time - last_poll_time > 2:
        elapsed_time = cur_time - last_poll_time
        last_poll_time = cur_time
        metric_update(elapsed_time)
    
    return iops[name]


descriptors = [
    {
        'name':'block_read_rate',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'blk_read/s',
        'slope':'both',
        'format':'%f',
        'description':'Block Read Rate',
        'groups':'disk'
    },

    {
        'name':'block_write_rate',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'blk_wrtn/s',
        'slope':'both',
        'format':'%f',
        'description':'Block Write Rate',
        'groups':'disk'
    },

    {
        'name':'block_read_write_rate',
        'call_back': metric_read,
        'time_max':10,
        'value_type':'float',
        'units':'blk_rw/s',
        'slope':'both',
        'format':'%f',
        'description':'Block Read Write Rate',
        'groups':'disk'
    }
]

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
