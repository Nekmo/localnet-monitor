from subprocess import check_output

import re

BINARY = 'arp-scan'
MAC_PATTERN = re.compile('\:'.join(['[0-9A-Fa-f]{2}'] * 6))


def get_default_interface():
    import netifaces
    return list(netifaces.gateways()['default'].values())[0][1]


def process_line(line):
    columns = line.split('\t', 3)
    if not len(columns) == 3 or not MAC_PATTERN.match(columns[1]):
        return
    name = columns[2] if not columns[2].startswith('(Unknown)') else None
    return {'ip': columns[0], 'mac': columns[1], 'name': name}


def update_devices(devices, device):
    mac = device['mac']
    exists = False
    for dev in devices:
        if dev['mac'] == mac:
            exists = True
        if dev['mac'] == mac and not dev['name']:
            dev['name'] = device['name']
    if not exists:
        devices.append(device)


def scan_network(network='local', interface=None, sudo=True):
    interface = interface or get_default_interface()
    net_param = '--localnet' if network == 'local' else ''
    output = check_output((['sudo'] if sudo else []) + \
                          [BINARY, '--interface={}'.format(interface), net_param]).decode('utf-8')
    devices = []
    for device in output.split('\n'):
        device = process_line(device)
        if device:
            update_devices(devices, device)
    return devices


def scan_networks(networks=None, interface=None, sudo=True):
    for network in networks or ['local']:
        yield scan_network(network, interface, sudo)
