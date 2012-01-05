acpi_file = "/proc/acpi/thermal_zone/THRM/temperature"

def temp_handler(name):  
    try:
        f = open(acpi_file, 'r')

    except IOError:
        return 0

    for l in f:
        line = l.split()

    return int(line[1])

def metric_init(params):
    global descriptors, acpi_file

    if 'acpi_file' in params:
        acpi_file = params['acpi_file']

    d1 = {'name': 'temp',
        'call_back': temp_handler,
        'time_max': 90,
        'value_type': 'uint',
        'units': 'C',
        'slope': 'both',
        'format': '%u',
        'description': 'Temperature of host',
        'groups': 'health'}

    descriptors = [d1]

    return descriptors

def metric_cleanup():
    '''Clean up the metric module.'''
    pass

#This code is for debugging and unit testing
if __name__ == '__main__':
    metric_init({})
    for d in descriptors:
        v = d['call_back'](d['name'])
        print 'value for %s is %u' % (d['name'],  v)
